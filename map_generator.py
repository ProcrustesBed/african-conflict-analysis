import pandas as pd
import numpy as np
import folium
import os
import branca
from folium.plugins import HeatMap, HeatMapWithTime


class MapGenerator:
    def __init__(self, df, country_name, n=100):
        self.df = df
        self.country_name = country_name
        self.n = n
        
        self.df_country = None
        self.top_events = None
        self.grouped_events = None
        self.aggregated_events = None
        self.single_events = None
        self.top_events_country = None
        
        self.m = None
        self.m2 = None
              
    def prepare_data(self):
        self._filter_by_country()
        if self.df_country is None:
            print(f"Country '{self.country_name}' not found in dataset.")
            return
        self._clean_data()
        self._aggregate_time_blocks()
        
        
    def _filter_by_country(self):
        match = self.df[self.df["COUNTRY"].str.lower() == self.country_name.lower()]["COUNTRY"]
        self.country_name = match.iloc[0]
        self.df_country = self.df[self.df["COUNTRY"] == self.country_name]
        
        
    def _clean_data(self):       
        top_events = self.df.nlargest(self.n, "FATALITIES").copy()
        
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
        
        top_events["HMWT"] = top_events[["LATITUDE", "LONGITUDE"]].values.tolist()
        
        self.top_events = top_events
        
        grouped_events = top_events.groupby(['LAT_GROUP', 'LON_GROUP', 'EVENT_DATE', 'COUNTRY']).agg({
            'FATALITIES': 'sum',
            'EVENT_TYPE': [lambda x: x.value_counts().idxmax() if not x.empty else "Unknown", 'count'],
            'LOCATION': 'first',
            'LATITUDE': 'mean',
            'LONGITUDE': 'mean',
            'YEAR': 'first'
        }).reset_index()

        grouped_events.columns = [
            f"{col[0]}_{col[1]}" if col[1] == 'count' else col[0]
            for col in grouped_events.columns
        ]

        grouped_events = grouped_events.sort_values(
            by=['COUNTRY', 'LATITUDE', 'LONGITUDE', 'FATALITIES', 'EVENT_DATE']
        )
        
        grouped_events['DATE_DIFF'] = grouped_events.groupby(
            ['COUNTRY', 'LATITUDE', 'LONGITUDE']
        )['EVENT_DATE'].diff().dt.days
        
        grouped_events['BLOCK_ID'] = grouped_events.groupby(
            ['COUNTRY', 'LATITUDE', 'LONGITUDE']
        )['DATE_DIFF'].transform(lambda x: (x != 1).cumsum())
        
        grouped_events['BLOCK_ID'] = (
            grouped_events['COUNTRY'] + '_' +
            grouped_events['LATITUDE'].astype(str) + '_' +
            grouped_events['LONGITUDE'].astype(str) + '_' +
            grouped_events['BLOCK_ID'].astype(str)
        )
        
        self.grouped_events = grouped_events
        
    def _aggregate_time_blocks(self):
        aggregated_events = self.grouped_events.groupby([
            'COUNTRY', 'LATITUDE', 'LONGITUDE', 'BLOCK_ID'
        ]).agg(
            START_DATE=('EVENT_DATE', 'min'),
            END_DATE=('EVENT_DATE', 'max'),
            FATALITIES=('FATALITIES', 'sum'),
            LAT_GROUP=('LAT_GROUP', 'first'),
            LON_GROUP=('LON_GROUP', 'first'),
            EVENT_TYPE=('EVENT_TYPE', 'first'),
            YEAR=('YEAR', 'first')
        ).reset_index()
        
        single_events = aggregated_events[aggregated_events['START_DATE'] == aggregated_events['END_DATE']].copy()
        aggregated_events = aggregated_events[aggregated_events['START_DATE'] != aggregated_events['END_DATE']].copy()
        
        aggregated_events = aggregated_events.reset_index(drop=True)
        
        self.single_events = single_events
        self.aggregated_events = aggregated_events
        
    def _apply_jitter(self, df):
        df_copy = df.copy()
        
        maske = df_copy.duplicated(subset=["LATITUDE", "LONGITUDE"], keep=False)
            
        anzahl = maske.sum()
        
        if anzahl > 0:
            zufall_lat = np.random.uniform(-0.03, 0.03, size=anzahl)
            zufall_lon = np.random.uniform(-0.03, 0.03, size=anzahl)
            df_copy.loc[maske, "LATITUDE"] += zufall_lat
            df_copy.loc[maske, "LONGITUDE"] += zufall_lon
        
        return df_copy

    def generate_map(self):
        if self.df_country is None:
            print(f"Abbruch: Keine Daten für '{self.country_name}' vorhanden.")
            return None, None
    
        top_events_country = self.grouped_events[self.grouped_events["COUNTRY"] == self.country_name].copy()

        zoom = 5
        
        if not top_events_country.empty:
            lat = top_events_country["LATITUDE"].mean()
            lon = top_events_country["LONGITUDE"].mean()
        else:
            lat, lon = 6.42, 20.54
            zoom = 4

        self.top_events_country = top_events_country

        m = folium.Map(
            location=[lat, lon],
            zoom_start=zoom,
            min_zoom=2,
            tiles='CartoDB Positron',
            control_scale=True,
            max_bounds=True
        )
        
        m2 = folium.Map(
            location=[lat, lon],
            zoom_start=zoom,
            min_zoom=2,
            tiles='CartoDB Positron',
            control_scale=True,
            max_bounds=True
        )
        
        colors = ["red", "blue", "green", "orange", "purple", "darkred", "lightred", "darkblue", "lightblue", "darkgreen", "lightgreen", "cadetblue", "darkpurple", "grey"
        ]
        
        self.df["EVENT_TYPE_CLEAN"] = self.df["EVENT_TYPE"].str.title().str.strip()
                
        # Doppelungen im Original-Datensatz:
        # Violence against civilians/Civilians
        # Battle-No change of territory/no change of territory
        # Remote violence/Violence
        # Strategic Development /Development/development
        
        event_types = self.df["EVENT_TYPE_CLEAN"].unique().tolist()
        event_colors = dict(zip(event_types, colors))
        
        legend_items = "".join([
            f'&nbsp; {key} &nbsp; <i class="fa fa-circle" style="color:{value}"></i><br>'
            for key, value in event_colors.items()
        ])
        
        legend_html = f'''
        {{% macro html(this, kwargs) %}}
        <div style="position: fixed; 
            bottom: 50px; left: 50px; width: 320px; height: auto; 
            border:2px solid grey; z-index:9999; font-size:14px;
            background-color:white; opacity: 0.85; padding: 8px;">
            
            &nbsp; <b>Legend</b> <br>
            {legend_items}
            
            <hr style="margin: 8px 0; border: 0; border-top: 1px solid #ccc;">
    
            <div style="font-size: 11px; color: #555; font-style: italic; line-height: 1.2;">
                Note: Jitter between -0.03 and 0.03 degrees was applied to events with identical coordinates.
            </div>
        </div>
        {{% endmacro %}}
        '''
        
        legend = branca.element.MacroElement()
        legend._template = branca.element.Template(legend_html)
        
        def color_matcher(data, event_type):
            circle_color = data[event_type]
            if event_type not in data:
                circle_color = "white"
                print("Unknown event type.")
            return circle_color
            
        min_radius = 50

        scale = 7
        
        circle_layer = folium.FeatureGroup(name="Events (Circles)", show=True)
        
        aggregated_map = self.aggregated_events.sort_values(by='FATALITIES', ascending=False)
        aggregated_map = self._apply_jitter(aggregated_map)     
        
        singles_map = self.single_events.sort_values(by='FATALITIES', ascending=False)
        singles_map = self._apply_jitter(singles_map)
        
        for _, row in aggregated_map.iterrows():
            radius = max(min_radius, int(row['FATALITIES'] * scale))
            
            date_str = f"{row['START_DATE'].strftime('%d.%m.%Y')} - {row['END_DATE'].strftime('%d.%m.%Y')}"
            
            circle_color = color_matcher(event_colors, row["EVENT_TYPE"].title().strip())
            
            folium.Circle(
                location=[row["LATITUDE"], row["LONGITUDE"]],
                radius=radius,
                color=circle_color,
                fill=True,
                fill_color=circle_color,
                fill_opacity=0.5,
                popup=f"<b>{row['EVENT_TYPE']}</b><br>Fatalities: {int(row['FATALITIES'])}<br>Date: {date_str}",
                tooltip=f"{row['EVENT_TYPE']} ({int(row['FATALITIES'])} fatalities)"
            ).add_to(circle_layer)
        circle_layer.add_to(m)
        
        for _, row in singles_map.iterrows():
            radius = max(min_radius, int(row['FATALITIES'] * scale))
            
            date_str = row['START_DATE'].strftime('%d.%m.%Y')
            
            circle_color = color_matcher(event_colors, row["EVENT_TYPE"].title().strip())
        
            folium.Circle(
                location=[row["LATITUDE"], row["LONGITUDE"]],
                radius=radius,
                color=circle_color,
                fill=True,
                fill_color=circle_color,
                fill_opacity=0.5,
                popup=f"<b>{row['EVENT_TYPE']}</b><br>Fatalities: {int(row['FATALITIES'])}<br>Date: {date_str}",
                tooltip=f"{row['EVENT_TYPE']} ({int(row['FATALITIES'])} fatalities)"
            ).add_to(m)
            
        heatmap_layer = folium.FeatureGroup(name="Heatmap (Event Occurrences)", show=False)
        heat_data = [[row["LATITUDE"], row["LONGITUDE"], row["YEAR"]] for _, row in self.top_events.iterrows()]
        HeatMap(heat_data, max_zoom=10, radius=17).add_to(heatmap_layer)
        heatmap_layer.add_to(m)
        
        heat_time_data = self.top_events.groupby("YEAR")["HMWT"].apply(list)
        time_index = heat_time_data.index.astype(str).tolist()
        heat_time_data = heat_time_data.tolist()
        hm = HeatMapWithTime(heat_time_data, index=time_index, auto_play=False)
        hm.add_to(m2)
        
        folium.LayerControl().add_to(m)
        
        m.get_root().add_child(legend)
        
        self.m = m
        self.m2 = m2
        
        
    def save_map(self):
        if self.m is None or self.m2 is None:
            print("Saving not possible: no maps generated.")
            return
        
        os.makedirs('maps', exist_ok=True)
        
        file_name = f"{self.country_name.lower().replace(' ', '_').replace('-', '_')}_map.html"
        self.m.save(f"maps/{file_name}")
        
        m2_file_name = f"{self.country_name.lower().replace(' ', '_').replace('-', '_')}_heatmap.html"
        self.m2.save(f"maps/{m2_file_name}")

        if self.country_name not in self.top_events_country.values:
            print(f"ℹ️Note: {self.country_name} has no events in the Top {self.n} most fatal conflict events.")
            
        return self.m, self.m2





