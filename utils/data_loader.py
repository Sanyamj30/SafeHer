import os
import json
import sqlite3
import joblib
import pandas as pd
import numpy as np
import streamlit as st

# Mappings for cities to states
CITY_TO_STATE = {
    'Agra': 'UTTAR PRADESH',
    'Amritsar': 'PUNJAB',
    'Asansol': 'WEST BENGAL',
    'Aurangabad': 'MAHARASHTRA',
    'Bhopal': 'MADHYA PRADESH',
    'Chandigarh City': 'CHANDIGARH',
    'Dhanbad': 'JHARKHAND',
    'Durg-Bhilainagar': 'CHHATTISGARH',
    'Faridabad': 'HARYANA',
    'Gwalior': 'MADHYA PRADESH',
    'Jabalpur': 'MADHYA PRADESH',
    'Jamshedpur': 'JHARKHAND',
    'Jodhpur': 'RAJASTHAN',
    'Kannur': 'KERALA',
    'Kollam': 'KERALA',
    'Kota': 'RAJASTHAN',
    'Ludhiana': 'PUNJAB',
    'Madurai': 'TAMIL NADU',
    'Malappuram': 'KERALA',
    'Meerut': 'UTTAR PRADESH',
    'Nasik': 'MAHARASHTRA',
    'Prayagraj': 'UTTAR PRADESH',
    'Raipur': 'CHHATTISGARH',
    'Rajkot': 'GUJARAT',
    'Ranchi': 'JHARKHAND',
    'Srinagar': 'JAMMU & KASHMIR',
    'Thiruvananthapuram': 'KERALA',
    'Thrissur': 'KERALA',
    'Tiruchirapalli': 'TAMIL NADU',
    'Vadodara': 'GUJARAT',
    'Varanasi': 'UTTAR PRADESH',
    'Vasai Virar': 'MAHARASHTRA',
    'Vijayawada': 'ANDHRA PRADESH',
    'Vishakhapatnam': 'ANDHRA PRADESH'
}

# Coordinate mapping database fallback key mapping for spelling mismatches
CITY_TO_DISTRICT_COORDS = {
    'Asansol': 'paschim bardhaman',
    'Chandigarh City': 'chandigarh',
    'Durg-Bhilainagar': 'durg',
    'Jamshedpur': 'east singhbhum',
    'Nasik': 'nashik',
    'Tiruchirapalli': 'tiruchirappalli',
    'Vijayawada': 'krishna',
    'Vishakhapatnam': 'visakhapatnam',
    'Vasai Virar': 'thane'
}

STATE_POPULATIONS_LAKHS = {
    'ANDHRA PRADESH': 845.8, 'ARUNACHAL PRADESH': 13.8, 'ASSAM': 312.0, 'BIHAR': 1041.0,
    'CHHATTISGARH': 255.4, 'GOA': 14.6, 'GUJARAT': 604.4, 'HARYANA': 253.5,
    'HIMACHAL PRADESH': 68.6, 'JAMMU & KASHMIR': 125.4, 'JHARKHAND': 329.9,
    'KARNATAKA': 611.0, 'KERALA': 334.1, 'MADHYA PRADESH': 726.3, 'MAHARASHTRA': 1123.7,
    'MANIPUR': 28.6, 'MEGHALAYA': 29.7, 'MIZORAM': 10.9, 'NAGALAND': 19.8,
    'ODISHA': 419.7, 'PUNJAB': 277.4, 'RAJASTHAN': 685.5, 'SIKKIM': 6.1,
    'TAMIL NADU': 721.5, 'TELANGANA': 350.0, 'TRIPURA': 36.7, 'UTTAR PRADESH': 1998.1,
    'UTTAKHAND': 100.9, 'UTTARAKHAND': 100.9, 'WEST BENGAL': 912.8, 'A & N ISLANDS': 3.8,
    'CHANDIGARH': 10.6, 'D & N HAVELI': 3.5, 'D&N HAVELI': 3.5, 'DAMAN & DIU': 2.4,
    'DELHI': 167.9, 'DELHI UT': 167.9, 'LAKSHADWEEP': 0.6, 'PUDUCHERRY': 12.5
}

def init_sqlite_db():
    db_path = "safeher.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if tables exist and have data
    try:
        cursor.execute("SELECT count(*) FROM states")
        states_count = cursor.fetchone()[0]
        cursor.execute("SELECT count(*) FROM cities")
        cities_count = cursor.fetchone()[0]
        cursor.execute("SELECT count(*) FROM coordinates")
        coords_count = cursor.fetchone()[0]
    except sqlite3.OperationalError:
        states_count = 0
        cities_count = 0
        coords_count = 0
        
    if states_count > 0 and cities_count > 0 and coords_count > 0:
        conn.close()
        return # already initialized
        
    # Drop tables if they exist to start fresh
    cursor.execute("DROP TABLE IF EXISTS states")
    cursor.execute("DROP TABLE IF EXISTS cities")
    cursor.execute("DROP TABLE IF EXISTS coordinates")
    
    # Create tables
    cursor.execute("""
        CREATE TABLE states (
            State TEXT,
            Year INTEGER,
            Rape INTEGER,
            KA INTEGER,
            DD INTEGER,
            AoW INTEGER,
            AoM INTEGER,
            DV INTEGER,
            WT INTEGER,
            Total_Crimes INTEGER,
            Population_Lakhs REAL,
            Crime_Rate REAL,
            Chargesheeting_Rate REAL,
            Historical_Trend REAL,
            Crime_Density REAL,
            Score_CR REAL,
            Score_CSR REAL,
            Score_HT REAL,
            Score_CD REAL,
            Safety_Score REAL,
            Risk_Category TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE cities (
            City TEXT,
            State TEXT,
            Year INTEGER,
            Total_Crimes INTEGER,
            Population_Lakhs REAL,
            Crime_Rate REAL,
            Chargesheeting_Rate REAL,
            Historical_Trend REAL,
            Crime_Density REAL,
            Score_CR REAL,
            Score_CSR REAL,
            Score_HT REAL,
            Score_CD REAL,
            Safety_Score REAL,
            Risk_Category TEXT,
            Latitude REAL,
            Longitude REAL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE coordinates (
            District TEXT,
            Latitude REAL,
            Longitude REAL
        )
    """)
    
    # Load coordinates CSV
    coords_path = os.path.join("datasets", "coordinates.csv")
    if os.path.exists(coords_path):
        df_coords = pd.read_csv(coords_path)
        for _, row in df_coords.iterrows():
            cursor.execute("INSERT INTO coordinates (District, Latitude, Longitude) VALUES (?, ?, ?)",
                           (str(row["District"]).strip(), float(row["Latitude"]), float(row["Longitude"])))
    
    # Load and process states data
    state_path = os.path.join("datasets", "state_master.csv")
    if os.path.exists(state_path):
        df_state = pd.read_csv(state_path)
        df_state["State"] = df_state["State"].astype(str).str.strip().str.title()
        df_state["State_Clean"] = df_state["State"].str.upper().str.strip()
        df_state["Population_Lakhs"] = df_state["State_Clean"].map(STATE_POPULATIONS_LAKHS)
        df_state["Population_Lakhs"] = df_state["Population_Lakhs"].fillna(df_state["Population_Lakhs"].mean())
        
        # Calculate raw state features
        df_city_stats = pd.read_csv(os.path.join("datasets", "city_stats.csv"))
        df_city_stats = df_city_stats[df_city_stats['City'].str.upper() != 'TOTAL 34 CITIES']
        
        city_to_csr = {}
        for _, row in df_city_stats.iterrows():
            city_to_csr[row["City"]] = row["Chargesheeting_Rate"]
            
        state_csr_map = {}
        for city, csr in city_to_csr.items():
            state = CITY_TO_STATE.get(city)
            if state:
                state_title = state.strip().title()
                if state_title not in state_csr_map:
                    state_csr_map[state_title] = []
                state_csr_map[state_title].append(csr)
                
        state_avg_csr = {}
        for s, csrs in state_csr_map.items():
            state_avg_csr[s] = sum(csrs) / len(csrs)
            
        global_avg_csr = df_city_stats["Chargesheeting_Rate"].mean()
        
        # Sort state records to calculate trend
        df_state = df_state.sort_values(by=["State", "Year"])
        
        state_records = []
        for state_name, group in df_state.groupby("State"):
            prev_rate = None
            for _, row in group.iterrows():
                pop_lakhs = row["Population_Lakhs"]
                total_crimes = row["Total_Crimes"]
                crime_rate = total_crimes / pop_lakhs
                csr = state_avg_csr.get(state_name, global_avg_csr)
                
                # Trend
                if prev_rate is None:
                    trend = 0.0
                else:
                    trend = crime_rate - prev_rate
                prev_rate = crime_rate
                
                # Density
                density = total_crimes
                
                state_records.append({
                    "State": state_name,
                    "Year": int(row["Year"]),
                    "Rape": int(row["Rape"]),
                    "KA": int(row["K&A"]),
                    "DD": int(row["DD"]),
                    "AoW": int(row["AoW"]),
                    "AoM": int(row["AoM"]),
                    "DV": int(row["DV"]),
                    "WT": int(row["WT"]),
                    "Total_Crimes": int(total_crimes),
                    "Population_Lakhs": pop_lakhs,
                    "Crime_Rate": crime_rate,
                    "Chargesheeting_Rate": csr,
                    "Historical_Trend": trend,
                    "Crime_Density": density
                })
                
        df_state_processed = pd.DataFrame(state_records)
        
        # Normalize state features
        cr_min, cr_max = df_state_processed["Crime_Rate"].min(), df_state_processed["Crime_Rate"].max()
        csr_min, csr_max = df_state_processed["Chargesheeting_Rate"].min(), df_state_processed["Chargesheeting_Rate"].max()
        trend_min, trend_max = df_state_processed["Historical_Trend"].min(), df_state_processed["Historical_Trend"].max()
        cd_min, cd_max = df_state_processed["Crime_Density"].min(), df_state_processed["Crime_Density"].max()
        
        def norm_val(val, vmin, vmax, reverse=False):
            if vmax == vmin:
                return 100.0
            ratio = (val - vmin) / (vmax - vmin)
            if reverse:
                return 100.0 * (1.0 - ratio)
            return 100.0 * ratio
            
        for idx, row in df_state_processed.iterrows():
            score_cr = norm_val(row["Crime_Rate"], cr_min, cr_max, reverse=True)
            score_csr = norm_val(row["Chargesheeting_Rate"], csr_min, csr_max, reverse=False)
            score_ht = norm_val(row["Historical_Trend"], trend_min, trend_max, reverse=True)
            score_cd = norm_val(row["Crime_Density"], cd_min, cd_max, reverse=True)
            
            safety_score = 0.40 * score_cr + 0.25 * score_csr + 0.20 * score_ht + 0.15 * score_cd
            
            if safety_score >= 80:
                risk = "Low Risk"
            elif safety_score >= 55:
                risk = "Medium Risk"
            else:
                risk = "High Risk"
                
            cursor.execute("""
                INSERT INTO states (State, Year, Rape, KA, DD, AoW, AoM, DV, WT, Total_Crimes, Population_Lakhs,
                                   Crime_Rate, Chargesheeting_Rate, Historical_Trend, Crime_Density,
                                   Score_CR, Score_CSR, Score_HT, Score_CD, Safety_Score, Risk_Category)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row["State"], int(row["Year"]), int(row["Rape"]), int(row["KA"]), int(row["DD"]), int(row["AoW"]), int(row["AoM"]), int(row["DV"]), int(row["WT"]),
                int(row["Total_Crimes"]), float(row["Population_Lakhs"]), float(row["Crime_Rate"]), float(row["Chargesheeting_Rate"]), float(row["Historical_Trend"]), float(row["Crime_Density"]),
                float(score_cr), float(score_csr), float(score_ht), float(score_cd), float(safety_score), risk
            ))
            
    # Load and process cities data
    city_path = os.path.join("datasets", "city_stats.csv")
    if os.path.exists(city_path) and os.path.exists(coords_path):
        df_city = pd.read_csv(city_path)
        df_city = df_city[df_city['City'].str.upper() != 'TOTAL 34 CITIES']
        
        df_coords = pd.read_csv(coords_path)
        lat_map = {}
        lon_map = {}
        for _, row in df_coords.iterrows():
            dist_clean = str(row['District']).lower().strip()
            lat_map[dist_clean] = row['Latitude']
            lon_map[dist_clean] = row['Longitude']
            
        city_records = []
        for _, row in df_city.iterrows():
            city = row["City"]
            state_raw = CITY_TO_STATE.get(city, "OTHER")
            state = str(state_raw).strip().title()
            pop_lakhs = row["Population_Lakhs"]
            chargesheet_rate = row["Chargesheeting_Rate"]
            
            lookup = CITY_TO_DISTRICT_COORDS.get(city, city).lower().strip()
            lat = lat_map.get(lookup, 22.0)
            lon = lon_map.get(lookup, 78.0)
            
            for year in [2021, 2022, 2023]:
                crimes = row[f"Crime_{year}"]
                crime_rate = crimes / pop_lakhs
                density = crimes
                
                city_records.append({
                    "City": city,
                    "State": state,
                    "Year": int(year),
                    "Total_Crimes": int(crimes),
                    "Population_Lakhs": pop_lakhs,
                    "Crime_Rate": crime_rate,
                    "Chargesheeting_Rate": chargesheet_rate,
                    "Crime_Density": density,
                    "Latitude": lat,
                    "Longitude": lon
                })
                
        df_city_processed = pd.DataFrame(city_records)
        df_city_processed = df_city_processed.sort_values(by=["City", "Year"])
        
        final_city_records = []
        for city_name, group in df_city_processed.groupby("City"):
            prev_rate = None
            for _, row in group.iterrows():
                crime_rate = row["Crime_Rate"]
                if prev_rate is None:
                    trend = 0.0
                else:
                    trend = crime_rate - prev_rate
                prev_rate = crime_rate
                
                row_dict = row.to_dict()
                row_dict["Historical_Trend"] = trend
                final_city_records.append(row_dict)
                
        df_city_processed = pd.DataFrame(final_city_records)
        
        cr_min, cr_max = df_city_processed["Crime_Rate"].min(), df_city_processed["Crime_Rate"].max()
        csr_min, csr_max = df_city_processed["Chargesheeting_Rate"].min(), df_city_processed["Chargesheeting_Rate"].max()
        trend_min, trend_max = df_city_processed["Historical_Trend"].min(), df_city_processed["Historical_Trend"].max()
        cd_min, cd_max = df_city_processed["Crime_Density"].min(), df_city_processed["Crime_Density"].max()
        
        for idx, row in df_city_processed.iterrows():
            score_cr = norm_val(row["Crime_Rate"], cr_min, cr_max, reverse=True)
            score_csr = norm_val(row["Chargesheeting_Rate"], csr_min, csr_max, reverse=False)
            score_ht = norm_val(row["Historical_Trend"], trend_min, trend_max, reverse=True)
            score_cd = norm_val(row["Crime_Density"], cd_min, cd_max, reverse=True)
            
            safety_score = 0.40 * score_cr + 0.25 * score_csr + 0.20 * score_ht + 0.15 * score_cd
            
            if safety_score >= 80:
                risk = "Low Risk"
            elif safety_score >= 55:
                risk = "Medium Risk"
            else:
                risk = "High Risk"
                
            cursor.execute("""
                INSERT INTO cities (City, State, Year, Total_Crimes, Population_Lakhs, Crime_Rate, Chargesheeting_Rate,
                                   Historical_Trend, Crime_Density, Score_CR, Score_CSR, Score_HT, Score_CD,
                                   Safety_Score, Risk_Category, Latitude, Longitude)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row["City"], row["State"], int(row["Year"]), int(row["Total_Crimes"]), float(row["Population_Lakhs"]),
                float(row["Crime_Rate"]), float(row["Chargesheeting_Rate"]), float(row["Historical_Trend"]), float(row["Crime_Density"]),
                float(score_cr), float(score_csr), float(score_ht), float(score_cd), float(safety_score), risk,
                float(row["Latitude"]), float(row["Longitude"])
            ))
            
    conn.commit()
    conn.close()

def round_coordinates(coords, precision=4):
    """Helper to round float lists recursively for GeoJSON geometry optimization."""
    if isinstance(coords, list):
        return [round_coordinates(c, precision) for c in coords]
    elif isinstance(coords, float) or isinstance(coords, int):
        return round(float(coords), precision)
    return coords

@st.cache_data
def load_crime_data():
    """Loads and caches consolidated city-level crime data from SQLite."""
    init_sqlite_db()
    conn = sqlite3.connect("safeher.db")
    df = pd.read_sql_query("""
        SELECT City as District, State, Year, CAST((Population_Lakhs * 100000) AS INTEGER) as Population,
               Population_Lakhs, Total_Crimes, Crime_Rate, Chargesheeting_Rate, Latitude, Longitude, Safety_Score, Risk_Category,
               Score_CR, Score_CSR, Score_HT, Score_CD
        FROM cities
    """, conn)
    conn.close()
    return df

@st.cache_data
def load_historical_state_data():
    """Loads and caches historical state-wise crime data from SQLite."""
    init_sqlite_db()
    conn = sqlite3.connect("safeher.db")
    df = pd.read_sql_query("""
        SELECT State, Year, Rape, KA as [K&A], DD, AoW, AoM, DV, WT, Total_Crimes, Safety_Score, Population_Lakhs,
               Crime_Rate, Chargesheeting_Rate, Historical_Trend, Crime_Density,
               Score_CR, Score_CSR, Score_HT, Score_CD, Risk_Category
        FROM states
        WHERE Year <= 2019
    """, conn)
    conn.close()
    df["State_Clean"] = df["State"].str.upper().str.strip()
    return df

@st.cache_data
def load_geojson_data():
    """Loads, caches, and simplifies the local state-level GeoJSON file."""
    # Try simplified version first
    geojson_path = os.path.join("datasets", "geojson", "india_states_simplified.geojson")
    if not os.path.exists(geojson_path):
        geojson_path = os.path.join("datasets", "geojson", "india_states.geojson")
        
    if os.path.exists(geojson_path):
        with open(geojson_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Only round coordinates if loading the original heavy file
            if "simplified" not in geojson_path:
                for feature in data.get("features", []):
                    geometry = feature.get("geometry", {})
                    if geometry:
                        geometry["coordinates"] = round_coordinates(geometry.get("coordinates", []))
            return data
    return {"type": "FeatureCollection", "features": []}

@st.cache_data
def load_district_geojson():
    """Loads, caches, and simplifies the local district-level GeoJSON file."""
    # Try simplified version first
    geojson_path = os.path.join("datasets", "geojson", "india_district_simplified.geojson")
    if not os.path.exists(geojson_path):
        geojson_path = os.path.join("datasets", "geojson", "india_district.geojson")
        
    if os.path.exists(geojson_path):
        with open(geojson_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Only round coordinates if loading the original heavy file
            if "simplified" not in geojson_path:
                for feature in data.get("features", []):
                    geometry = feature.get("geometry", {})
                    if geometry:
                        geometry["coordinates"] = round_coordinates(geometry.get("coordinates", []))
            return data
    return {"type": "FeatureCollection", "features": []}

@st.cache_resource
def load_classifier_model():
    """Loads classifier."""
    model_path = os.path.join("models", "classifier.joblib")
    if os.path.exists(model_path):
        return joblib.load(model_path)
    return None

@st.cache_resource
def load_kmeans_model():
    """Loads K-Means."""
    model_path = os.path.join("models", "kmeans.joblib")
    if os.path.exists(model_path):
        return joblib.load(model_path)
    return None
