from analyze import analyze_production_fire_risk, print_fire_risk_report

TEST_LOCATIONS = [
    ("Turkey / Mugla (Marmaris Conifer Forest)", 36.8550, 28.2742),
    ("USA / California (Redding Shasta Forest)", 40.5865, -122.3917),
    ("Australia / New South Wales (Blue Mountains)", -33.7181, 150.3114),
    ("Greece / Attica (Pine Forest Zone)", 38.0493, 23.8340),
    ("Algeria / Sahara Desert (Tamanrasset)", 22.7850, 5.5228),
    ("USA / Nevada (Las Vegas Desert)", 36.1699, -115.1398),
    ("Saudi Arabia / Rub al Khali (Empty Quarter)", 20.0000, 50.0000),
    ("Chile / Atacama Desert", -23.8634, -69.1328),
    ("Null Island (Ocean Origin)", 0.0000, 0.0000),
    ("Pacific Ocean (Mid-Pacific Open Water)", 15.0000, -140.0000),
    ("Mediterranean Sea (Open Water)", 35.5000, 18.0000),
    ("Norway / Tromso (Arctic Circle Zone)", 69.6492, 18.9553),
    ("Nepal / Mount Everest Base Region", 27.9881, 86.9250),
    ("Switzerland / Alps (Zermatt)", 45.9765, 7.7491),
    ("Brazil / Manaus (Amazon Rainforest)", -3.1190, -60.0217),
    ("Indonesia / Borneo Rainforest", 0.9619, 114.5548),
    ("Congo / Central Rainforest Basin", -0.2280, 15.8277),
    ("Turkey / Canakkale (Gelibolu)", 40.4111, 26.6744),
    ("USA / Texas (Lubbock)", 33.5779, -101.8552),
    ("Spain / Madrid (Inland Plateau)", 40.4168, -3.7038),
    ("South Africa / Cape Town (Shrubland Zone)", -33.9249, 18.4241),
    ("Japan / Tokyo", 35.6762, 139.6503),
    ("Mexico / Guadalajara", 20.6597, -103.3496),
    ("United Kingdom / London", 51.5074, -0.1278),
]

def run_tests():
    for location_name, lat, lon in TEST_LOCATIONS:
        try:
            result = analyze_production_fire_risk(location_name, lat, lon)
            print_fire_risk_report(result)
        except Exception as e:
            print(f"Error testing {location_name}: {e}\n")

if __name__ == "__main__":
    run_tests()