from analyze import analyze_production_fire_risk, print_fire_risk_report

# config
LOCATION_NAME = "Seferihisar / Izmir"
LATITUDE = 38.193663
LONGITUDE = 26.853315

TARGET_DATES = [f"2025-06-{day:02d}" for day in range(22, 31)]

PRINT_FULL_REPORTS = False

def run_past_risk_test():
    print("=" * 125)
    print(f" HISTORICAL FIRE RISK TEST: {LOCATION_NAME.upper()} ({LATITUDE}, {LONGITUDE})")
    print("=" * 125)
    print(
        f"{'Date':<12} | {'Temp (°C)':<10} | {'RH (%)':<8} | {'Wind (km/h)':<12} | "
        f"{'Nearest Fire (KM)':<20} | {'Vector Align (°)':<18} | {'Risk (%)':<10} | {'Status':<12}"
    )
    print("-" * 125)

    results = []

    for date_str in TARGET_DATES:
        try:
            res = analyze_production_fire_risk(
                location_name=LOCATION_NAME,
                lat=LATITUDE,
                lon=LONGITUDE,
                target_date=date_str
            )
            results.append(res)

            temp = res.get("temperature", 0.0)
            rh = res.get("rh", 0.0)
            ws = res.get("wind_speed", 0.0)
            fire_dist = res.get("nearest_fire_dist", 100.0)
            vector_align = res.get("vector_alignment", 180.0)
            risk_score = res.get("risk_score", 0.0)
            status = res.get("status", "N/A")

            print(
                f"{date_str:<12} | "
                f"{temp:<10.1f} | "
                f"%{rh:<7.1f} | "
                f"{ws:<12.1f} | "
                f"{fire_dist:<20.2f} | "
                f"{vector_align:<18.1f} | "
                f"%{risk_score:<9.2f} | "
                f"{status:<12}"
            )

        except Exception as e:
            print(f"{date_str:<12} | ERROR RUNNING TEST: {e}")

    print("=" * 125 + "\n")

    if PRINT_FULL_REPORTS and results:
        print("\n" + "#" * 80)
        print(" DETAILED SINGLE-DAY REPORTS")
        print("#" * 80 + "\n")
        for res in results:
            print_fire_risk_report(res)


if __name__ == "__main__":
    run_past_risk_test()