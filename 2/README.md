# Company registry search — backend setup

## What this is
A small Flask backend that loads your Company Master Data CSV into a SQLite
database once, then serves a search API + the search page. The CSV itself is
never sent to the browser — only the matching rows for whatever you search.

## Files
- `ingest_csv_to_db.py` — one-time script, turns your CSV into `companies.db`
- `app.py` — the web server (search API + serves the page)
- `static/index.html` — the search page itself
- `requirements.txt` — the two packages you need

## 1. Install
```
pip install -r requirements.txt
```

## 2. Build the database (run once, or again whenever your CSV updates)
```
python ingest_csv_to_db.py company_master_data.csv companies.db
```
This reads your CSV in chunks (so it's fine even at 3 million rows), creates
a `companies` table with whatever columns your CSV actually has, guesses
which column is the company name, indexes it, and writes `db_meta.json` so
the server knows the schema. Watch the terminal output — it prints which
column it picked as the name column; if it picks the wrong one, open
`db_meta.json` and change `"name_column"` to the right one manually.

## 3. Run it
```
python app.py
```
Open `http://localhost:5000` in your browser. Type a company name, click a
result tab, see the full record. No match shows "not on file".

## 4. Test it
- Search a company you know is in the file — confirm the right tabs show up.
- Search something that doesn't exist — confirm you get "not on file", not
  an error.
- Search a very short string (like a single letter) — confirm it doesn't
  hang or time out; if it's slow, that's expected on the very first query
  while SQLite warms its cache.
- Check the count shown under the search bar matches roughly what you
  expect from your CSV's row count.

## 5. Deploy it
The development server (`python app.py`) is for testing only — the warning
it prints in the terminal is correct, don't leave it running for real
visitors. For an actual deployment, pick based on what you have:

**Easiest for a student project (no credit card, no server to manage):**
[PythonAnywhere](https://www.pythonanywhere.com) free tier runs Flask apps
directly and lets you upload `companies.db` as a file. Good if your final
database file is under a few hundred MB. Upload all the files in this
folder (including the `.db` and `db_meta.json` you generated), point their
WSGI config at `app.py`, done.

**If you want a real production-style deploy:** [Render](https://render.com)
or [Railway](https://railway.app) both have free/cheap tiers that run a
Flask app from a GitHub repo. Run the app with `gunicorn app:app` instead of
`python app.py` in production (add `gunicorn` to requirements.txt). Note:
their free disks are often ephemeral, so if your `companies.db` is large,
you may need their paid persistent disk add-on, or commit a smaller/filtered
version of the database.

**If your guide just wants to see it working, not publicly hosted:** running
it locally on your laptop and demoing it directly, or using a tunnel tool
like `ngrok http 5000` to get a temporary public link during the
demo, is genuinely fine and avoids all the deployment complexity above.

## A note on database size
3 million rows of company master data with ~12 columns will likely produce
a SQLite file in the range of a few hundred MB to low single-digit GB. If
that's too large for your hosting tier, the ingestion script accepts a
`table_name` argument, so you can run it multiple times against filtered
CSVs (e.g. only "Active" status companies, or only one state) and keep the
working database smaller without changing any other code.
