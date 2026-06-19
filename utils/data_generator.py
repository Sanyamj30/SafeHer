import os
import json
import random
import numpy as np
import pandas as pd
import requests

def download_geojson():
    """Downloads India state boundaries GeoJSON if not already cached."""
    geojson_dir = "data"
    os.makedirs(geojson_dir, exist_ok=True)
    geojson_path = os.path.join(geojson_dir, "india_states.geojson")
    
    if not os.path.exists(geojson_path):
        print("Downloading India states GeoJSON...")
        # A reliable public GeoJSON for India states
        url = "https://raw.githubusercontent.com/geohacker/india/master/state/india_state.geojson"
        try:
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                with open(geojson_path, "w", encoding="utf-8") as f:
                    f.write(response.text)
                print("GeoJSON downloaded successfully.")
            else:
                print(f"Failed to download GeoJSON. Status code: {response.status_code}")
                create_dummy_geojson(geojson_path)
        except Exception as e:
            print(f"Error downloading GeoJSON: {e}")
            create_dummy_geojson(geojson_path)
    else:
        print("GeoJSON already exists locally.")

def create_dummy_geojson(path):
    """Creates a basic valid GeoJSON if download fails so app does not crash."""
    print("Creating a fallback empty GeoJSON structure...")
    dummy = {
        "type": "FeatureCollection",
        "features": []
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(dummy, f)

# List of major Indian States & UTs with capital coordinates
STATES_DATA = {
    "Andhra Pradesh": {"lat": 15.9129, "lon": 79.7400, "base_crime": 40.0, "districts": ["Visakhapatnam", "Vijayawada", "Guntur", "Nellore", "Tirupati"]},
    "Arunachal Pradesh": {"lat": 28.2180, "lon": 94.7278, "base_crime": 25.0, "districts": ["Itanagar", "Tawang", "Ziro", "Pasighat", "Bomdila"]},
    "Assam": {"lat": 26.2006, "lon": 92.9376, "base_crime": 55.0, "districts": ["Guwahati", "Dibrugarh", "Silchar", "Jorhat", "Tezpur"]},
    "Bihar": {"lat": 25.0961, "lon": 85.3131, "base_crime": 48.0, "districts": ["Patna", "Gaya", "Muzaffarpur", "Bhagalpur", "Darbhanga"]},
    "Chhattisgarh": {"lat": 21.2787, "lon": 81.8661, "base_crime": 38.0, "districts": ["Raipur", "Bilaspur", "Durg", "Bhilai", "Jagdalpur"]},
    "Goa": {"lat": 15.2993, "lon": 74.1240, "base_crime": 20.0, "districts": ["Panaji", "Margao", "Vasco da Gama", "Mapusa", "Ponda"]},
    "Gujarat": {"lat": 22.2587, "lon": 71.1924, "base_crime": 28.0, "districts": ["Ahmedabad", "Surat", "Vadodara", "Rajkot", "Gandhinagar"]},
    "Haryana": {"lat": 29.0588, "lon": 76.0856, "base_crime": 58.0, "districts": ["Gurugram", "Faridabad", "Panipat", "Ambala", "Rohtak"]},
    "Himachal Pradesh": {"lat": 31.1048, "lon": 77.1734, "base_crime": 22.0, "districts": ["Shimla", "Manali", "Dharamshala", "Solan", "Mandi"]},
    "Jharkhand": {"lat": 23.6102, "lon": 85.2799, "base_crime": 42.0, "districts": ["Ranchi", "Jamshedpur", "Dhanbad", "Bokaro", "Deoghar"]},
    "Karnataka": {"lat": 15.3173, "lon": 75.7139, "base_crime": 32.0, "districts": ["Bengaluru", "Mysuru", "Hubballi", "Mangaluru", "Belagavi"]},
    "Kerala": {"lat": 10.8505, "lon": 76.2711, "base_crime": 24.0, "districts": ["Thiruvananthapuram", "Kochi", "Kozhikode", "Kollam", "Thrissur"]},
    "Madhya Pradesh": {"lat": 22.9734, "lon": 78.6569, "base_crime": 52.0, "districts": ["Bhopal", "Indore", "Gwalior", "Jabalpur", "Ujjain"]},
    "Maharashtra": {"lat": 19.7515, "lon": 75.7139, "base_crime": 36.0, "districts": ["Mumbai", "Pune", "Nagpur", "Thane", "Nashik"]},
    "Manipur": {"lat": 24.6637, "lon": 93.9063, "base_crime": 35.0, "districts": ["Imphal", "Churachandpur", "Thoubal", "Ukhrul", "Senapati"]},
    "Meghalaya": {"lat": 25.4670, "lon": 91.3662, "base_crime": 30.0, "districts": ["Shillong", "Tura", "Jowai", "Nongpoh", "Cherrapunji"]},
    "Mizoram": {"lat": 23.1645, "lon": 92.9376, "base_crime": 18.0, "districts": ["Aizawl", "Lunglei", "Champhai", "Serchhip", "Kolasib"]},
    "Nagaland": {"lat": 26.1584, "lon": 94.5624, "base_crime": 15.0, "districts": ["Kohima", "Dimapur", "Mokokchung", "Wokha", "Tuensang"]},
    "Odisha": {"lat": 20.9517, "lon": 85.0985, "base_crime": 45.0, "districts": ["Bhubaneswar", "Cuttack", "Rourkela", "Sambalpur", "Puri"]},
    "Punjab": {"lat": 31.1471, "lon": 75.3412, "base_crime": 34.0, "districts": ["Ludhiana", "Amritsar", "Jalandhar", "Patiala", "Bathinda"]},
    "Rajasthan": {"lat": 27.0238, "lon": 74.2179, "base_crime": 62.0, "districts": ["Jaipur", "Jodhpur", "Udaipur", "Kota", "Bikaner"]},
    "Sikkim": {"lat": 27.5330, "lon": 88.5122, "base_crime": 16.0, "districts": ["Gangtok", "Namchi", "Gyalshing", "Mangan", "Singtam"]},
    "Tamil Nadu": {"lat": 11.1271, "lon": 78.6569, "base_crime": 28.0, "districts": ["Chennai", "Coimbatore", "Madurai", "Tiruchirappalli", "Salem"]},
    "Telangana": {"lat": 18.1124, "lon": 79.0193, "base_crime": 44.0, "districts": ["Hyderabad", "Warangal", "Nizamabad", "Karimnagar", "Khammam"]},
    "Tripura": {"lat": 23.9408, "lon": 91.9882, "base_crime": 35.0, "districts": ["Agartala", "Dharmanagar", "Udaipur", "Kailasahar", "Belonia"]},
    "Uttar Pradesh": {"lat": 26.8467, "lon": 80.9462, "base_crime": 56.0, "districts": ["Lucknow", "Kanpur", "Ghaziabad", "Agra", "Varanasi", "Meerut", "Prayagraj"]},
    "Uttarakhand": {"lat": 30.0668, "lon": 79.0193, "base_crime": 26.0, "districts": ["Dehradun", "Haridwar", "Haldwani", "Roorkee", "Nainital"]},
    "West Bengal": {"lat": 22.9868, "lon": 87.8550, "base_crime": 50.0, "districts": ["Kolkata", "Howrah", "Darjeeling", "Siliguri", "Asansol"]},
    "Delhi": {"lat": 28.6139, "lon": 77.2090, "base_crime": 65.0, "districts": ["New Delhi", "South Delhi", "North Delhi", "East Delhi", "West Delhi", "Dwarka"]},
    "Jammu & Kashmir": {"lat": 33.7780, "lon": 76.5762, "base_crime": 35.0, "districts": ["Srinagar", "Jammu", "Anantnag", "Baramulla", "Kathua"]},
    "Ladakh": {"lat": 34.1526, "lon": 77.5771, "base_crime": 12.0, "districts": ["Leh", "Kargil"]},
    "Puducherry": {"lat": 11.9416, "lon": 79.8083, "base_crime": 22.0, "districts": ["Puducherry", "Karaikal", "Mahe", "Yanam"]}
}

def generate_crime_dataset():
    """Generates synthetic crime against women dataset from 2015 to 2025."""
    print("Generating synthetic crime data...")
    random.seed(42)
    np.random.seed(42)
    
    records = []
    
    # Yearly trend multipliers (COVID dip in 2020, slight reporting increase in general)
    yearly_multipliers = {
        2015: 0.90,
        2016: 0.95,
        2017: 0.98,
        2018: 1.02,
        2019: 1.06,
        2020: 0.82, # COVID lockdown reduction in public crimes, drop in reporting
        2021: 0.96, # Recovery
        2022: 1.04, # Post-COVID reporting surge
        2023: 1.01, # Stabilizing
        2024: 0.97, # Slow decrease due to awareness campaigns
        2025: 0.92 # More improvement
    }
    
    for year in range(2015, 2026):
        year_mult = yearly_multipliers[year]
        
        for state, state_info in STATES_DATA.items():
            base_state_crime = state_info["base_crime"]
            
            for i, district in enumerate(state_info["districts"]):
                # Add unique coordinates for each district with slight offset from state capital
                angle = (2 * np.pi / len(state_info["districts"])) * i
                dist_lat = state_info["lat"] + 0.3 * np.sin(angle) + random.uniform(-0.08, 0.08)
                dist_lon = state_info["lon"] + 0.3 * np.cos(angle) + random.uniform(-0.08, 0.08)
                
                # Base population
                base_pop = random.randint(600000, 4500000)
                # Grow population by 1.2% per year
                pop = int(base_pop * ((1.012) ** (year - 2015)))
                
                # Generate crime rates (per 100k population)
                # Adding district specific variance
                district_factor = random.uniform(0.7, 1.3)
                base_rate = base_state_crime * year_mult * district_factor
                
                # Crime category rate breakdown
                # Rape: ~12% of total crime against women
                rape_rate = max(0.5, base_rate * 0.12 + random.uniform(-0.5, 0.5))
                # Kidnapping: ~18%
                kidnap_rate = max(1.0, base_rate * 0.18 + random.uniform(-1.0, 1.0))
                # Dowry Deaths: ~2.5%
                dowry_rate = max(0.1, base_rate * 0.025 + random.uniform(-0.2, 0.2))
                # Assault: ~30%
                assault_rate = max(2.0, base_rate * 0.30 + random.uniform(-2.0, 2.0))
                # Insult: ~10%
                insult_rate = max(0.5, base_rate * 0.10 + random.uniform(-1.0, 1.0))
                # Cruelty by Husband: ~27.5%
                cruelty_rate = max(1.5, base_rate * 0.275 + random.uniform(-2.5, 2.5))
                
                # Compute absolute counts based on population
                rape_count = int(round((pop / 100000) * rape_rate))
                kidnap_count = int(round((pop / 100000) * kidnap_rate))
                dowry_count = int(round((pop / 100000) * dowry_rate))
                assault_count = int(round((pop / 100000) * assault_rate))
                insult_count = int(round((pop / 100000) * insult_rate))
                cruelty_count = int(round((pop / 100000) * cruelty_rate))
                
                # Re-calculate exact rates per 100k based on counts (to maintain precision)
                rape_rate_exact = round((rape_count / pop) * 100000, 3)
                kidnap_rate_exact = round((kidnap_count / pop) * 100000, 3)
                dowry_rate_exact = round((dowry_count / pop) * 100000, 3)
                assault_rate_exact = round((assault_count / pop) * 100000, 3)
                insult_rate_exact = round((insult_count / pop) * 100000, 3)
                cruelty_rate_exact = round((cruelty_count / pop) * 100000, 3)
                
                total_crimes = rape_count + kidnap_count + dowry_count + assault_count + insult_count + cruelty_count
                overall_crime_rate = round((total_crimes / pop) * 100000, 3)
                
                # Calculate Safety Score: Weighted Crime Index Subtraction
                # Higher rates = lower safety. Severe crimes have higher weights.
                weighted_crime_index = (
                    rape_rate_exact * 5.0 + 
                    dowry_rate_exact * 8.0 + 
                    kidnap_rate_exact * 4.0 + 
                    assault_rate_exact * 3.0 + 
                    insult_rate_exact * 1.0 + 
                    cruelty_rate_exact * 2.0
                )
                
                # Map index to 0-100 score. A weighted index of 250 yields score of ~30.
                safety_score = 100 - (weighted_crime_index * 0.15)
                # Clip between 20.0 and 99.0
                safety_score = round(float(np.clip(safety_score, 20.0, 99.0)), 2)
                
                # Define Risk Category
                if safety_score >= 80:
                    risk_category = "Low Risk"
                elif safety_score >= 55:
                    risk_category = "Medium Risk"
                else:
                    risk_category = "High Risk"
                
                records.append({
                    "Year": year,
                    "State": state,
                    "District": district,
                    "Population": pop,
                    "Rape": rape_count,
                    "Rape_Rate": rape_rate_exact,
                    "Kidnapping_Abduction": kidnap_count,
                    "Kidnapping_Rate": kidnap_rate_exact,
                    "Dowry_Deaths": dowry_count,
                    "Dowry_Death_Rate": dowry_rate_exact,
                    "Assault_on_Women": assault_count,
                    "Assault_Rate": assault_rate_exact,
                    "Insult_to_Modesty": insult_count,
                    "Insult_Rate": insult_rate_exact,
                    "Cruelty_by_Husband_Relatives": cruelty_count,
                    "Cruelty_Rate": cruelty_rate_exact,
                    "Total_Crimes": total_crimes,
                    "Crime_Rate": overall_crime_rate,
                    "Latitude": round(dist_lat, 4),
                    "Longitude": round(dist_lon, 4),
                    "Safety_Score": safety_score,
                    "Risk_Category": risk_category
                })
                
    df = pd.DataFrame(records)
    csv_path = os.path.join("data", "crime_data.csv")
    df.to_csv(csv_path, index=False)
    print(f"Crime dataset generated successfully at: {csv_path}. Records generated: {len(df)}")

if __name__ == "__main__":
    download_geojson()
    generate_crime_dataset()
