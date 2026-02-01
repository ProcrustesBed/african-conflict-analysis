import kagglehub
import pandas as pd
import os

def load_data():
    try:
        path = kagglehub.dataset_download("jboysen/african-conflicts")
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith(".csv"):
                    return pd.read_csv(os.path.join(root, file), encoding="latin1")
    except Exception as e:
        print(f"Error while loading data: {e}")
        return None

def generate_country_report(df, country_name):
    # 1. Filter by country
    country_df = df[df["COUNTRY"] == country_name].copy()
    if country_df.empty:
        print(f"No data found for {country_name}.")
        return

    print(f"\n{'=' * 40}")
    print(f"🌍 CONFLICT REPORT: {country_name.upper()}")
    print(f"{'=' * 40}")

    # 2. Analysis of yearly events and fatalities
    yearly_stats = country_df.groupby("YEAR")["FATALITIES"].agg(["count", "sum", "mean"])
    yearly_stats.columns = ['Events', 'Total Deaths', 'Avg per Event']
    print("\n--- Yearly Development ---")
    print(yearly_stats.round(2))

    # 3. Identifying top actors by fatalities
    actor_impact = country_df.groupby("ACTOR1")["FATALITIES"].sum().sort_values(ascending=False)
    print("\n--- Top 5 Violent Actors ---")
    print(actor_impact.head(5))

    # 4. Comparing the top 2 actors
    if len(actor_impact) >= 2:
        top1_name = actor_impact.index[0]
        top2_name = actor_impact.index[1]

        comparison = country_df[country_df["ACTOR1"].isin([top1_name, top2_name])]
        comp_table = comparison.pivot_table(
            index="EVENT_TYPE",
            columns="ACTOR1",
            values="FATALITIES",
            aggfunc="sum"
        ).fillna(0)

        print(f"\n--- Tactical Comparison: {top1_name} vs {top2_name} ---")
        print(comp_table)

    # 5. Hotspots
    print("\n--- Top 10 Regional Hotspots (Admin1) ---")
    hotspots = country_df.groupby("ADMIN1")["FATALITIES"].sum().sort_values(ascending=False)
    print(hotspots.head(10))