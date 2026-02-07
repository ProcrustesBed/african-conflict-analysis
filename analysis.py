import kagglehub
import pandas as pd
import os
import folium
from folium.plugins import MarkerCluster

def load_data():
    try:
        path = kagglehub.dataset_download("jboysen/african-conflicts")
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith(".csv"):
                    return pd.read_csv(os.path.join(root, file), encoding="latin1", low_memory=False)
    except Exception as e:
        print(f"Error while loading data: {e}")
        return None

def generate_country_report(df, country_name):
    # 1. Filter by country
    country_df = df[df["COUNTRY"].str.lower() == country_name.lower()].copy()
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

def generate_map(df, country_name, n=100):
    top_events = df.nlargest(n, "FATALITIES").copy()
    top_events = top_events.dropna(subset=['LATITUDE', 'LONGITUDE'])

    top_events["LATITUDE"] = pd.to_numeric(top_events["LATITUDE"], errors="coerce")
    top_events["LONGITUDE"] = pd.to_numeric(top_events["LONGITUDE"], errors="coerce")

    top_events['LAT_GROUP'] = top_events['LATITUDE'].round(2)
    top_events['LON_GROUP'] = top_events['LONGITUDE'].round(2)

    top_events['EVENT_DATE'] = pd.to_datetime(
        top_events['EVENT_DATE'],
        dayfirst=True,
        errors='coerce',
    )
    grouped_events = top_events.groupby(['LAT_GROUP', 'LON_GROUP', 'EVENT_DATE']).agg({
        'FATALITIES': 'sum',
        'EVENT_TYPE': [lambda x: x.value_counts().idxmax() if not x.empty else "Unknown", 'count'],
        'COUNTRY': 'first',
        'LOCATION': 'first',
        'LATITUDE': 'mean',
        'LONGITUDE': 'mean',
        'YEAR': 'first'
    }).reset_index()

    grouped_events.columns = [
        f"{col[0]}_{col[1]}" if col[1] == 'count' else col[0]
        for col in grouped_events.columns
    ]

    grouped_events = grouped_events.sort_values(by="FATALITIES", ascending=False)
    top_events_country = grouped_events[grouped_events["COUNTRY"] == country_name].copy()

    zoom = 5
    if not top_events_country.empty:
        lat = top_events_country["LATITUDE"].mean()
        lon = top_events_country["LONGITUDE"].mean()
    else:
        lat, lon = 6.42, 20.54
        zoom = 4

    m = folium.Map(location=[lat, lon], zoom_start=zoom)

    marker_cluster = MarkerCluster(name="Events Cluster").add_to(m)

    scale = 5

    for index, row in grouped_events.iterrows():
        radius = (row["FATALITIES"]) * scale
        circle_color = 'red' if row["COUNTRY"] == country_name else 'blue'

        date_str = row['EVENT_DATE'].strftime('%d.%m.%Y')
        c = folium.Circle(
            location=[row["LATITUDE"], row["LONGITUDE"]],
            radius=radius,
            color=circle_color,
            fill=True,
            fill_color=circle_color,
            fill_opacity=0.5,
            popup=f"<b>{row['EVENT_TYPE']}</b><br>Fatalities: {int(row['FATALITIES'])}<br>Date: {date_str}",
            tooltip=f"{row['EVENT_TYPE']} ({int(row['FATALITIES'])} fatalities)"
        ).add_to(m)

        c.add_to(marker_cluster)

    file_name = f"{country_name.lower().replace(' ', '_')}_map.html"
    m.save(f"maps/{file_name}")

    if country_name not in top_events_country.values:
        print(f"ℹ️Note: {country_name} has no events in the Top {n} most fatal conflict events.")

    return m