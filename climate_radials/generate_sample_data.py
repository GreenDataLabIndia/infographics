"""
Generates SAMPLE daily weather CSVs for 10 Indian cities (one file per city in ./data).
The numbers are synthetic, built from approximate monthly climate normals, so the site has
something to draw. Replace the CSVs in ./data with real observations (IMD, NASA POWER,
Open-Meteo, Meteostat ...) -- keep the same columns and the page updates by itself.
"""
import csv, math, random, datetime, os

YEAR = 2025
random.seed(7)

# name: (tmax[12], tmin[12], monthly rain mm[12], noise sd)
CITIES = {
 "mumbai":    ([31,32,33,33,33,32,30,30,31,33,33,32],[19,20,23,26,28,27,26,26,25,24,22,20],[3,1,1,2,12,520,710,430,300,70,15,3],1.3),
 "delhi":     ([21,24,30,37,40,39,35,34,34,33,28,23],[8,11,16,22,26,28,27,26,24,18,12,8],[20,18,15,10,20,70,210,230,120,15,3,8],2.4),
 "bengaluru": ([28,31,34,34,33,29,28,28,29,28,27,27],[15,17,19,22,21,20,19,19,19,19,17,15],[2,5,6,45,110,80,110,140,170,150,60,15],1.4),
 "chennai":   ([29,31,33,35,38,37,35,35,34,31,29,28],[20,21,23,26,27,27,26,25,25,24,23,21],[25,5,8,15,50,55,85,120,120,270,350,140],1.4),
 "kolkata":   ([27,30,34,36,36,34,32,32,32,32,29,26],[13,16,21,25,26,27,26,26,26,23,18,13],[10,25,30,50,140,300,330,330,250,120,15,5],1.6),
 "hyderabad": ([29,32,35,38,39,34,31,30,31,31,29,28],[15,17,21,25,27,24,23,22,22,20,17,14],[5,8,12,25,30,100,150,170,150,90,25,5],1.6),
 "jaipur":    ([22,25,31,37,41,40,35,33,34,33,28,24],[8,11,16,22,27,28,26,25,24,19,13,9],[14,9,7,5,15,55,200,230,90,15,4,5],2.2),
 "surat":     ([30,32,36,38,37,34,31,30,32,35,33,30],[14,16,20,24,27,27,26,25,25,22,18,15],[1,1,1,1,5,200,450,300,200,30,5,1],1.5),
 "shimla":    ([10,12,17,22,26,25,21,20,21,20,16,12],[2,3,7,11,15,16,15,15,13,9,5,3],[60,60,60,50,60,190,430,400,200,40,15,30],2.6),
 "leh":       ([0,3,8,14,18,23,27,26,21,14,7,2],[-14,-11,-6,-1,3,7,11,10,5,-2,-8,-12],[8,8,10,7,8,5,15,15,8,3,2,3],2.8),
}

start = datetime.date(YEAR, 1, 1)
ndays = (datetime.date(YEAR + 1, 1, 1) - start).days
dates = [start + datetime.timedelta(i) for i in range(ndays)]

def month_len(m):
    a = datetime.date(YEAR, m, 1)
    b = datetime.date(YEAR + (m == 12), m % 12 + 1, 1)
    return (b - a).days

mids, acc = [], 0
for m in range(1, 13):
    L = month_len(m); mids.append(acc + L / 2); acc += L

def smooth(vals, d):
    pts = [(mids[i] - ndays, vals[i]) for i in range(12)] + [(mids[i], vals[i]) for i in range(12)] + [(mids[i] + ndays, vals[i]) for i in range(12)]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x0 <= d + 0.5 <= x1:
            t = (d + 0.5 - x0) / (x1 - x0)
            t = (1 - math.cos(math.pi * t)) / 2
            return y0 + (y1 - y0) * t
    return vals[0]

os.makedirs("data", exist_ok=True)
for cid, (tx, tn, rain, sd) in CITIES.items():
    # daily rain
    precip = [0.0] * ndays
    idx = 0
    for m in range(1, 13):
        L = month_len(m)
        total = rain[m - 1] * random.uniform(0.6, 1.4)
        if total < 3:
            n = 1 if random.random() < 0.6 else 0
        elif total < 8:
            n = 2
        else:
            n = min(L - 2, max(2, round(total / 14)))
        if n:
            days = random.sample(range(L), n)
            w = [random.expovariate(1) + 0.1 for _ in days]
            s = sum(w)
            for dd, ww in zip(days, w):
                precip[idx + dd] = round(total * ww / s, 1)
        idx += L
    # daily temperature
    e1 = e2 = 0.0
    rows = []
    for i, d in enumerate(dates):
        e1 = 0.7 * e1 + random.gauss(0, sd)
        e2 = 0.5 * e2 + random.gauss(0, sd * 0.5)
        hi = smooth(tx, i) + e1 + e2
        lo = smooth(tn, i) + e1 - e2 * 0.6
        p = precip[i]
        if p > 5:
            hi -= min(4, 1 + p / 15); lo -= 0.5
        if hi < lo + 2.5:
            hi = lo + 2.5 + random.random()
        rows.append([d.isoformat(), round(lo, 1), round(hi, 1), round((lo + hi) / 2, 1), p])
    with open(f"data/{cid}.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "tmin", "tmax", "tmean", "precip"])
        w.writerows(rows)
    print("wrote", cid, len(rows), "days")
