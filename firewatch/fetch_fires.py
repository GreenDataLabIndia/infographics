#!/usr/bin/env python3
"""India active-fire pipeline: NASA FIRMS (VIIRS) -> district-assigned JSON for the dashboard.

First run : FIRMS_MAP_KEY=xxxx python fetch_fires.py --districts india_districts.geojson --days 5
Seed 1 yr : python fetch_fires.py --seed archive1.csv archive2.csv      (FIRMS archive downloads)
Hourly    : FIRMS_MAP_KEY=xxxx python fetch_fires.py
"""
import argparse, json, os, io
from datetime import datetime, timezone
import pandas as pd, geopandas as gpd, requests

OUT = "data"; BBOX = "68,6,98,37.5"
SRC = ["VIIRS_SNPP_NRT", "VIIRS_NOAA20_NRT", "VIIRS_NOAA21_NRT"]
LARGE, KEEP_DAYS, POINT_DAYS = 30, 366, 7
SK = ["state", "NAME_1", "st_nm", "STATE", "State", "STATE_NAME", "ST_NM", "stname"]
DK = ["district", "NAME_2", "dtname", "DISTRICT", "District", "DIST_NAME", "dt_name", "NAME_3"]
PCOLS = ["lat", "lon", "date", "time", "frp", "conf", "dn", "sat", "state", "district"]

def col(df, keys):
    for k in keys:
        if k in df.columns: return k
    raise SystemExit(f"Boundary file has none of these columns: {keys}")

def boundaries(path, rebuild):
    g = gpd.read_file(path).to_crs(4326)
    g = g.rename(columns={col(g, SK): "state", col(g, DK): "district"})[["state", "district", "geometry"]]
    g["state"] = g.state.astype(str).str.strip(); g["district"] = g.district.astype(str).str.strip()
    g = g.dissolve(by=["state", "district"]).reset_index()  # merge multi-part districts
    if rebuild:
        g["geometry"] = g.geometry.simplify(0.004, preserve_topology=True)
        g.to_file(f"{OUT}/districts.geojson", driver="GeoJSON", COORDINATE_PRECISION=4)
        g.dissolve(by="state").reset_index()[["state", "geometry"]].to_file(f"{OUT}/states.geojson", driver="GeoJSON", COORDINATE_PRECISION=4)
    return g

def norm(df, sat=None):
    df = df.rename(columns={"latitude": "lat", "longitude": "lon", "acq_date": "date", "acq_time": "time", "daynight": "dn", "confidence": "conf"})
    if sat: df["sat"] = sat
    if "sat" not in df: df["sat"] = df.get("satellite", "?")
    c = df.conf.astype(str).str.lower().str[0]
    num = pd.to_numeric(df.conf, errors="coerce")
    df["conf"] = c.where(c.isin(["l", "n", "h"]), pd.cut(num, [-1, 29, 79, 101], labels=["l", "n", "h"]).astype(str))
    df["time"] = pd.to_numeric(df.time, errors="coerce").fillna(0).astype(int)
    df["frp"] = pd.to_numeric(df.frp, errors="coerce").fillna(0).round(1)
    return df[["lat", "lon", "date", "time", "frp", "conf", "dn", "sat"]]

def fetch(key, days):
    parts = []
    for s in SRC:
        r = requests.get(f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{key}/{s}/{BBOX}/{days}", timeout=120)
        r.raise_for_status()
        if r.text.startswith("latitude"): parts.append(norm(pd.read_csv(io.StringIO(r.text)), s))
        else: print("skip", s, r.text[:80])
    return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame(columns=PCOLS[:8])

def assign(df, dist):
    if df.empty: return df.assign(state=None, district=None)
    pts = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lon, df.lat), crs=4326)
    j = gpd.sjoin(pts, dist, predicate="within", how="inner").drop(columns=["geometry", "index_right"])
    return j[~j.index.duplicated()].reset_index(drop=True)

def aggregate(p):
    if p.empty: return pd.DataFrame(columns=["d", "s", "k", "n", "f", "l"])
    g = p.groupby(["date", "state", "district"]).agg(n=("frp", "size"), f=("frp", "sum"), l=("frp", lambda x: int((x >= LARGE).sum()))).reset_index()
    g["f"] = g.f.round(1); g.columns = ["d", "s", "k", "n", "f", "l"]; return g

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--districts"); ap.add_argument("--days", type=int, default=2); ap.add_argument("--seed", nargs="*")
    a = ap.parse_args(); os.makedirs(OUT, exist_ok=True)
    dist = boundaries(a.districts or f"{OUT}/districts.geojson", bool(a.districts))
    dpath, ppath = f"{OUT}/daily.json", f"{OUT}/points_7d.json"
    old = pd.DataFrame(json.load(open(dpath))["rows"], columns=["d", "s", "k", "n", "f", "l"]) if os.path.exists(dpath) else aggregate(pd.DataFrame())
    pts = pd.DataFrame(json.load(open(ppath))["rows"], columns=PCOLS) if os.path.exists(ppath) else pd.DataFrame(columns=PCOLS)
    if a.seed:  # archive CSVs -> daily history only
        s = assign(norm(pd.concat([pd.read_csv(f) for f in a.seed])), dist)
        new = aggregate(s); old = pd.concat([old[~old.d.isin(new.d.unique())], new])
    else:
        key = os.environ["FIRMS_MAP_KEY"]
        pts = pd.concat([pts, assign(fetch(key, min(a.days, 5)), dist)], ignore_index=True)
        pts = pts.drop_duplicates(["lat", "lon", "date", "time", "sat"])
        cutoff = (pd.to_datetime(pts.date).max() - pd.Timedelta(days=POINT_DAYS - 1)).strftime("%Y-%m-%d")
        pts = pts[pts.date >= cutoff].sort_values(["date", "time"])
        new = aggregate(pts); old = pd.concat([old[~old.d.isin(new.d.unique())], new])
    old = old.sort_values("d"); old = old[old.d >= (pd.to_datetime(old.d.max()) - pd.Timedelta(days=KEEP_DAYS)).strftime("%Y-%m-%d")]
    json.dump({"cols": list(old.columns), "rows": old.values.tolist()}, open(dpath, "w"), separators=(",", ":"))
    json.dump({"cols": PCOLS, "rows": pts[PCOLS].values.tolist()}, open(ppath, "w"), separators=(",", ":"))
    json.dump({"updated": datetime.now(timezone.utc).isoformat(timespec="seconds"), "latest": old.d.max(), "first": old.d.min(),
               "sources": SRC, "large_frp": LARGE}, open(f"{OUT}/meta.json", "w"))
    print("daily rows", len(old), "| points", len(pts), "| latest", old.d.max())

if __name__ == "__main__": main()
