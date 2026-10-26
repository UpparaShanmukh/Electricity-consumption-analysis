# Electricity Consumption Analysis System

A Flask + MySQL + Pandas REST API that stores meter readings, calculates consumption, summarizes usage by month and year, and flags unusually high usage.

## Setup

Requirements: Python 3.10+, MySQL 8.0.16+, Git.

1. Clone the repository and open the folder.
2. Create and activate a virtual environment:
   ```
   python -m venv .venv
   .venv\Scripts\activate
   ```
3. Install the packages:
   ```
   pip install -r requirements.txt
   ```
4. Create a file named `.env` in the project folder with your MySQL details:
   ```
   NAME_1=your_value
   NAME_2=your_value
   HIGH_USAGE_FACTOR=1.5
   ```
5. Create the empty database:
   ```
   python init_db.py
   ```
6. Start the server:
   ```
   python app.py
   ```
   The API runs at http://127.0.0.1:5000. Check http://127.0.0.1:5000/health.

The database starts empty. To try the project with example data, run `sql/sample_data.sql` in MySQL Workbench (3 consumers, 3 meters, 6 readings each).

## Endpoints

| Method | URL | Purpose |
|---|---|---|
| POST, GET | `/consumers` | Create, list consumers |
| GET, PUT, DELETE | `/consumers/<id>` | Read, update, delete one consumer |
| POST, GET | `/meters` | Create, list meters |
| GET, PUT, DELETE | `/meters/<id>` | Read, update, delete one meter |
| POST, GET | `/readings` | Record readings, list them (`?meter_id=` filter) |
| GET, PUT, DELETE | `/readings/<id>` | Read, update, delete one reading |
| GET | `/analysis/consumption/<meter_id>` | Consumption per period |
| GET | `/analysis/summary/<meter_id>?level=monthly\|yearly` | Monthly or yearly totals |
| GET | `/analysis/high-usage/<meter_id>?factor=1.5` | Periods above average × factor |

## Example

```
Invoke-RestMethod -Uri http://127.0.0.1:5000/readings -Method Post -ContentType "application/json" -Body '{"meter_id":1,"reading_date":"2026-07-01","cumulative_kwh":1900}'
```

## Project layout

```
app.py            Flask app and blueprint registration
db.py             Database connection
utils.py          Shared error helper
init_db.py        Creates the empty database from sql/schema.sql
routes/           consumers.py, meters.py, readings.py, analysis.py
sql/              schema.sql, sample_data.sql
docs/             ER diagram, data dictionary, synopsis
```

## Documentation

- [Data dictionary](docs/data_dictionary.md)
- [Synopsis](docs/synopsis.md)
- ER diagram: `docs/er_diagram.png`