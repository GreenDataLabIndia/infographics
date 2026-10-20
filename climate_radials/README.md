# India Weather Radials

Files
- index.html  the whole site (D3 + CSS + JS)
- d3.min.js   D3 v7, bundled so the site also works offline
- cities.csv  list of cities shown on the page (one row = one chart)
- data/*.csv  one file per city: date,tmin,tmax,tmean,precip (tmean optional)
- generate_sample_data.py  creates the SAMPLE data; not needed once you have real data

Run locally (browsers block CSV loading from file://)
    cd india-radials
    python -m http.server 8000
    open http://localhost:8000

Update a city: overwrite data/<city>.csv. Add a city: drop a CSV in data/ and add a row to cities.csv.
Publish free: upload the folder to Netlify Drop, GitHub Pages or Cloudflare Pages.

NOTE: the included CSVs are synthetic values built from approximate monthly normals. Replace with real data
(IMD, NASA POWER, Open-Meteo archive, Meteostat) before publishing.
