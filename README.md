# african-conflict-analysis

A Python tool to pull and analyze ACLED conflict data across African countries. 
I built this primarily to practice the usage of pandas. The program automates the process of identifying key actors and 
mapping out violence trends.

## What it does
- Fetches an ACLED dataset automatically via kagglehub.
- Groups fatalities by year and region to show where and when things escalated.
- Compares the top 2 violent actors in a specific country (e.g., Military vs. Rebels).
- Breaks down event types (Battles vs. Violence against civilians) to see tactical shifts.

## Project Structure
- `analysis.py`: Contains the logic, data cleaning, and processing functions.
- `main.py`: The entry point. Change the `country` variable here to run a new report.

## How to run
Make sure you have pandas and kagglehub installed:
`pip install pandas kagglehub`

Then just run:
`python main.py`

## Note on Data
The script downloads the dataset to a local cache folder. The CSV itself is 
ignored by git to keep the repo light.