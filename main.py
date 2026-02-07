from analysis import load_data, generate_country_report, generate_map
import pandas as pd

if __name__ == "__main__":
    print("🚀Starting analysis...")
    raw_data = load_data()

    list = input("📋Would you like to see a list of available countries? [type y/n] ")
    if list == "y":
        print(sorted(pd.unique(raw_data["COUNTRY"])))
    elif list == "n":
        pass
    else:
        print("No/wrong input")

    user_country = input("Which country do you want to analyze? ")
    user_country = user_country.title()

    if raw_data is not None:
        print("✅Data loaded successfully. Generating report...")
        generate_country_report(raw_data, user_country)
        generate_map(raw_data, user_country, 500)
    else:
        print("❌Error: Data could not be loaded.")