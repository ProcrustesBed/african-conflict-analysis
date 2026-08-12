from analysis import load_data, generate_country_report
from map_generator import MapGenerator
import pandas as pd

if __name__ == "__main__":
    print("🚀Starting analysis...")
    raw_data = load_data()
    list = input("📋Would you like to see a list of available countries? [type 'y' / 'n'] ")
    if list == "y":
        print(sorted(pd.unique(raw_data["COUNTRY"])))
    elif list == "n":
        pass
    else:
        print("Wrong input")

    user_country = input("Which country do you want to analyze? ")
    user_country = user_country.title()
    
    map_gen = MapGenerator(raw_data, user_country, 500)
    
    if raw_data is not None:
        print("✅Data loaded successfully. Generating report...")
        generate_country_report(raw_data, user_country)
        map_gen.prepare_data()
        map_gen.generate_map()
        map_gen.save_map()
    else:
        print("❌Error: Data could not be loaded.")