from map_generator import MapGenerator
from analysis import load_data

if __name__ == "__testing_ground__":
    
    raw_data = load_data()
    map_gen = MapGenerator(raw_data, "ANGOLA", 500)
    map_gen.prepare_data()

# 2. Karte generieren (HIER wird self.event_colors erst zugewiesen!)
    map_gen.generate_map()
    
    map_gen.test()