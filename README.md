# african-conflict-analysis

A Python tool to pull and analyze ACLED conflict data across African countries. I built this primarily to practice the usage of **pandas**. The program automates the process of identifying key actors and mapping out violence trends.

## What it does
* **Fetches an ACLED dataset** automatically via `kagglehub`.
* **Groups fatalities** by year and region to show where and when things escalated.
* **Compares the top 2 violent actors** in a specific country (e.g., Military vs. Rebels).
* **Breaks down event types** (Battles vs. Violence against civilians) to see tactical shifts.
* **Advanced Mapping:** Uses `MarkerCluster` to handle high-density data and prevents "Mega-Events" by grouping on a daily level (`EVENT_DATE`) instead of just yearly.

## Technical Improvements
* **Granular Aggregation:** Grouped data by coordinates and exact dates to ensure map markers represent specific incidents rather than inflated yearly totals.
* **Date Parsing:** Implemented `dayfirst=True` and `errors='coerce'` to handle diverse date formats without crashing the script.
* **Marker Clustering:** Integrated `folium.plugins.MarkerCluster` to keep the UI clean when analyzing hundreds of fatal events.


## Project Structure
* `analysis.py`: Contains the logic, data cleaning, and processing functions.
* `main.py`: The entry point. Interactive CLI for country selection and report generation.
* `maps/`: Directory where the interactive HTML maps are stored.

## How to run
Make sure you have pandas, folium, and kagglehub installed:
```bash
pip install pandas folium kagglehub