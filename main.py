from analysis import load_data, generate_country_report

if __name__ == "__main__":
    print("🚀Starting analysis...")
    raw_data = load_data()
    if raw_data is not None:
        print("✅Data loaded successfully. Generating report...")
        generate_country_report(raw_data, "Angola")
    else:
        print("❌Error: Data could not be loaded.")