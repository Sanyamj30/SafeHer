import os
import pandas as pd
import joblib
import sqlite3

def validate():
    print("=========================================")
    print(" SAFEHER PLATFORM INTEGRITY CHECK ")
    print("=========================================")
    
    # Check data files
    files = {
        "state_master.csv": "datasets/state_master.csv",
        "city_stats.csv": "datasets/city_stats.csv",
        "coordinates.csv": "datasets/coordinates.csv",
        "india_district_simplified.geojson": "datasets/geojson/india_district_simplified.geojson"
    }
    
    for name, path in files.items():
        if not os.path.exists(path):
            print(f"[FAIL] {path} is missing!")
            return False
        print(f"[PASS] File found: {path}")
        
    df_state = pd.read_csv(files["state_master.csv"])
    df_city = pd.read_csv(files["city_stats.csv"])
    print(f"[PASS] Loaded state_master.csv: {len(df_state)} rows")
    print(f"[PASS] Loaded city_stats.csv: {len(df_city)} rows")
    
    # Check SQLite database
    db_path = "safeher.db"
    if not os.path.exists(db_path):
        print(f"[FAIL] {db_path} is missing! Database initialization failed.")
        return False
    print(f"[PASS] SQLite Database found: {db_path}")
    
    # Test DB connection and query
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM states")
        states_count = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM cities")
        cities_count = c.fetchone()[0]
        conn.close()
        print(f"[PASS] SQL query test: states count={states_count}, cities count={cities_count}")
    except Exception as e:
        print(f"[FAIL] Database connection or query failed: {e}")
        return False
        
    # Check models
    classifier_path = os.path.join("models", "classifier.joblib")
    if not os.path.exists(classifier_path):
        print("[FAIL] models/classifier.joblib is missing!")
        return False
        
    kmeans_path = os.path.join("models", "kmeans.joblib")
    if not os.path.exists(kmeans_path):
        print("[FAIL] models/kmeans.joblib is missing!")
        return False
        
    print("[PASS] Machine Learning models (Classifier, K-Means) found.")
    
    # Test classifier payload
    clf_payload = joblib.load(classifier_path)
    rf_model = clf_payload["rf_model"]
    lr_model = clf_payload["lr_model"]
    scaler_clf = clf_payload["scaler"]
    features_clf = clf_payload["features"]
    
    # Test rate features (8 values: Rape_Rate, KA_Rate, DD_Rate, AoW_Rate, AoM_Rate, DV_Rate, WT_Rate, Crime_Rate_Per_Lakh)
    test_rates = [[2.5, 3.0, 0.4, 15.0, 4.0, 12.0, 0.1, 40.0]]
    test_scaled = scaler_clf.transform(test_rates)
    
    pred_rf = rf_model.predict(test_scaled)[0]
    pred_lr = lr_model.predict(test_scaled)[0]
    print(f"[PASS] Random Forest prediction test: {pred_rf}")
    print(f"[PASS] Logistic Regression prediction test: {pred_lr}")
    
    # Test K-Means payload
    km_payload = joblib.load(kmeans_path)
    km_model = km_payload["model"]
    scaler_km = km_payload["scaler"]
    features_km = km_payload["features"]
    cluster_mapping = km_payload["cluster_mapping"]
    
    # Test record (4 values: Crime_Rate, Chargesheeting_Rate, Population_Lakhs, Safety_Score)
    test_km_values = [[120.0, 75.0, 15.0, 65.0]]
    test_km_scaled = scaler_km.transform(test_km_values)
    raw_cluster = km_model.predict(test_km_scaled)[0]
    mapped_cluster = cluster_mapping[raw_cluster]
    print(f"[PASS] K-Means test prediction: raw cluster={raw_cluster}, mapped cluster={mapped_cluster}")
    
    print("\n[SUCCESS] ALL INTEGRITY TESTS PASSED! APPLICATION READY TO RUN.")
    print("=========================================")
    return True

if __name__ == "__main__":
    validate()
