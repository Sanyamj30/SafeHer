import os
import sys
import joblib
import sqlite3
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score

# Make sure we can import from the parent directory when running this file directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_loader import init_sqlite_db

def train_models():
    print("Initializing SQLite database and training ML models...")
    init_sqlite_db()
    
    models_dir = "models"
    os.makedirs(models_dir, exist_ok=True)
    
    # 1. Train Classifiers on state data from safeher.db
    conn = sqlite3.connect("safeher.db")
    df_state = pd.read_sql_query("""
        SELECT State, Year, Rape, KA as [K&A], DD, AoW, AoM, DV, WT, Total_Crimes,
               Population_Lakhs, Safety_Score, Risk_Category
        FROM states
        WHERE Year <= 2019
    """, conn)
    
    # Calculate population-normalized rates (per 100k population)
    # Since Population_Lakhs is in lakhs, we divide counts by Population_Lakhs to get rate per lakh.
    # We will define features:
    df_state["Rape_Rate"] = df_state["Rape"] / df_state["Population_Lakhs"]
    df_state["KA_Rate"] = df_state["K&A"] / df_state["Population_Lakhs"]
    df_state["DD_Rate"] = df_state["DD"] / df_state["Population_Lakhs"]
    df_state["AoW_Rate"] = df_state["AoW"] / df_state["Population_Lakhs"]
    df_state["AoM_Rate"] = df_state["AoM"] / df_state["Population_Lakhs"]
    df_state["DV_Rate"] = df_state["DV"] / df_state["Population_Lakhs"]
    df_state["WT_Rate"] = df_state["WT"] / df_state["Population_Lakhs"]
    df_state["Crime_Rate_Per_Lakh"] = df_state["Total_Crimes"] / df_state["Population_Lakhs"]
    
    features_clf = [
        "Rape_Rate", "KA_Rate", "DD_Rate", "AoW_Rate", 
        "AoM_Rate", "DV_Rate", "WT_Rate", "Crime_Rate_Per_Lakh"
    ]
    
    X_clf = df_state[features_clf]
    y_clf = df_state["Risk_Category"]
    
    # Fit scaler for classification features (vital for Logistic Regression)
    scaler_clf = StandardScaler()
    X_clf_scaled = scaler_clf.fit_transform(X_clf)
    X_clf_scaled_df = pd.DataFrame(X_clf_scaled, columns=features_clf)
    
    X_train, X_test, y_train, y_test = train_test_split(
        X_clf_scaled_df, y_clf, test_size=0.2, random_state=42, stratify=y_clf
    )
    
    # Random Forest Classifier
    rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_model.fit(X_train, y_train)
    rf_acc = accuracy_score(y_test, rf_model.predict(X_test))
    
    # Logistic Regression Classifier
    lr_model = LogisticRegression(max_iter=1000, random_state=42)
    lr_model.fit(X_train, y_train)
    lr_acc = accuracy_score(y_test, lr_model.predict(X_test))
    
    print(f"Random Forest Classifier Accuracy: {rf_acc:.4f}")
    print(f"Logistic Regression Classifier Accuracy: {lr_acc:.4f}")
    
    # Save feature importances and coefficients
    rf_importances = dict(zip(features_clf, rf_model.feature_importances_))
    lr_coefficients = {}
    if len(lr_model.classes_) == 2:
        lr_coefficients[lr_model.classes_[0]] = dict(zip(features_clf, -lr_model.coef_[0]))
        lr_coefficients[lr_model.classes_[1]] = dict(zip(features_clf, lr_model.coef_[0]))
    else:
        for i, class_name in enumerate(lr_model.classes_):
            lr_coefficients[class_name] = dict(zip(features_clf, lr_model.coef_[i]))
        
    classifier_payload = {
        "rf_model": rf_model,
        "lr_model": lr_model,
        "scaler": scaler_clf,
        "features": features_clf,
        "rf_accuracy": rf_acc,
        "lr_accuracy": lr_acc,
        "rf_importances": rf_importances,
        "lr_coefficients": lr_coefficients
    }
    joblib.dump(classifier_payload, os.path.join(models_dir, "classifier.joblib"))
    print("Saved classification models successfully.")
    
    # 2. Train K-Means Clustering on city data from safeher.db
    # We filter for Year = 2023 for clustering
    df_city = pd.read_sql_query("""
        SELECT City, State, Year, Total_Crimes, Population_Lakhs,
               Crime_Rate, Chargesheeting_Rate, Safety_Score, Risk_Category
        FROM cities
        WHERE Year = 2023
    """, conn)
    conn.close()
    
    features_kmeans = ["Crime_Rate", "Chargesheeting_Rate", "Population_Lakhs", "Safety_Score"]
    X_kmeans = df_city[features_kmeans]
    
    scaler_kmeans = StandardScaler()
    X_kmeans_scaled = scaler_kmeans.fit_transform(X_kmeans)
    
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    kmeans.fit(X_kmeans_scaled)
    
    df_city["cluster"] = kmeans.labels_
    
    # Map clusters to risk categories programmatically based on average safety score
    # Highest average safety score -> Low Risk
    # Lowest average safety score -> High Risk
    # The middle one -> Medium Risk
    cluster_means = df_city.groupby("cluster")["Safety_Score"].mean()
    sorted_clusters = cluster_means.sort_values(ascending=False).index.tolist()
    
    cluster_mapping = {
        sorted_clusters[0]: "Low Risk",
        sorted_clusters[1]: "Medium Risk",
        sorted_clusters[2]: "High Risk"
    }
    
    kmeans_payload = {
        "model": kmeans,
        "scaler": scaler_kmeans,
        "features": features_kmeans,
        "cluster_mapping": cluster_mapping
    }
    
    joblib.dump(kmeans_payload, os.path.join(models_dir, "kmeans.joblib"))
    print("Saved K-Means clustering model successfully.")

if __name__ == "__main__":
    train_models()
