import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils.data_loader import load_crime_data, load_kmeans_model
from utils.ui_components import render_kpi, inject_custom_css

def show_hotspot_page():
    inject_custom_css()
    
    st.markdown("## 🔍 Hotspot Detection using Unsupervised Learning")
    st.markdown("This section utilizes a **K-Means Clustering** model to segment cities into 3 distinct crime groups: **High-Risk Hotspots**, **Moderate-Risk Regions**, and **Low-Risk Areas**, based on their crime rates and chargesheeting rates.")
    
    df = load_crime_data()
    kmeans_payload = load_kmeans_model()
    
    if df.empty:
        st.error("Error: city_stats.csv not found.")
        return
        
    if not kmeans_payload:
        st.error("Error: K-Means clustering model not loaded. Please run training scripts.")
        return
        
    latest_year = int(df["Year"].max())
    df_latest = df[df["Year"] == latest_year].copy()
    
    # Extract clustering details
    model = kmeans_payload["model"]
    scaler = kmeans_payload["scaler"]
    features = kmeans_payload["features"]
    cluster_mapping = kmeans_payload["cluster_mapping"]
      # Scale features and predict clusters for the latest year data
    X_in = df_latest[features].copy()
    X_scaled = scaler.transform(X_in)
    preds = model.predict(X_scaled)
    
    # Apply standard risk label mapping based on our trained centroids
    mapped_clusters = [cluster_mapping[p] for p in preds]
    
    cluster_labels_map = {
        "Low Risk": "🟢 Low Risk Area",
        "Medium Risk": "🟡 Moderate Risk Area",
        "High Risk": "🔴 High Risk Hotspot"
    }
    df_latest["Cluster_Label"] = [cluster_labels_map[c] for c in mapped_clusters]
    
    # Count sizes
    counts = df_latest["Cluster_Label"].value_counts()
    
    # KPIs for Clusters
    col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
    with col_kpi1:
        render_kpi("Low Risk Districts", f"{counts.get('🟢 Low Risk Area', 0)}", "Favorable safety conditions", "#10B981")
    with col_kpi2:
        render_kpi("Moderate Risk Districts", f"{counts.get('🟡 Moderate Risk Area', 0)}", "Requires routine vigilance", "#F59E0B")
    with col_kpi3:
        render_kpi("High Risk Hotspots", f"{counts.get('🔴 High Risk Hotspot', 0)}", "Requires immediate policing focus", "#EF4444")
        
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    # 1. Interactive Mapbox Hotspot Scatter
    st.markdown("### 🗺️ Geospatial Distribution of K-Means Clusters")
    st.markdown("Each marker represents a city, colored by its unsupervised K-Means risk category. Zoom and hover for details.")
    
    # Mapbox configuration with loading spinner
    with st.spinner("Rendering Hotspot Map..."):
        fig_mapbox = px.scatter_mapbox(
            df_latest,
            lat="Latitude",
            lon="Longitude",
            color="Cluster_Label",
            color_discrete_map={
                "🟢 Low Risk Area": "#10B981", 
                "🟡 Moderate Risk Area": "#F59E0B", 
                "🔴 High Risk Hotspot": "#EF4444"
            },
            hover_name="District",
            hover_data={
                "State": True,
                "Safety_Score": True,
                "Total_Crimes": ":,",
                "Cluster_Label": False,
                "Latitude": False,
                "Longitude": False
            },
            zoom=4,
            height=550
        )
        
        fig_mapbox.update_layout(
            mapbox_style="open-street-map",
            margin={"r":0,"t":0,"l":0,"b":0},
            paper_bgcolor='rgba(0,0,0,0)',
            legend=dict(
                title="K-Means Clusters",
                yanchor="top", y=0.99,
                xanchor="left", x=0.01,
                bgcolor="rgba(255, 255, 255, 0.7)" if st.get_option("theme.base") == "light" else "rgba(0, 0, 0, 0.7)"
            )
        )
        st.plotly_chart(fig_mapbox, use_container_width=True, config={"displayModeBar": False})
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    # 2. 3D Cluster Visualization & Stats
    col_chart, col_stats = st.columns([11, 9])
    
    df_latest["Population_Lakhs"] = df_latest["Population"] / 100000.0
    
    with col_chart:
        st.markdown("### 🧬 3D Dimensional Crime Profile Space")
        st.markdown("A 3D projection mapping Crime Rate, Chargesheeting Rate, and Population. Observe the spatial separation of the risk clusters.")
        
        fig_3d = px.scatter_3d(
            df_latest,
            x="Crime_Rate",
            y="Chargesheeting_Rate",
            z="Population_Lakhs",
            color="Cluster_Label",
            color_discrete_map={
                "🟢 Low Risk Area": "#10B981", 
                "🟡 Moderate Risk Area": "#F59E0B", 
                "🔴 High Risk Hotspot": "#EF4444"
            },
            hover_name="District",
            labels={
                "Crime_Rate": "Crime Rate (per Lakh)",
                "Chargesheeting_Rate": "Chargesheeting Rate (%)",
                "Population_Lakhs": "Population (Lakhs)"
            },
            height=450
        )
        fig_3d.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor='rgba(0,0,0,0)',
            legend=dict(orientation="h", yanchor="bottom", y=0.01, xanchor="left", x=0.01)
        )
        st.plotly_chart(fig_3d, use_container_width=True, config={"displayModeBar": False})
        
    with col_stats:
        st.markdown("### 📊 Cluster Statistical Centroids")
        st.markdown("Average stats, crime rates (per lakh), and safety scores for each K-Means cluster. Centroids define the profiles of the clusters:")
        
        # Calculate cluster means
        cluster_stats = df_latest.groupby("Cluster_Label").agg(
            Size=("District", "count"),
            Avg_Crime_Rate=("Crime_Rate", "mean"),
            Avg_Chargesheeting_Rate=("Chargesheeting_Rate", "mean"),
            Avg_Safety_Score=("Safety_Score", "mean")
        ).round(2)
        
        cluster_stats.columns = ["Cluster Size", "Average Crime Rate", "Average Chargesheeting (%)", "Average Safety Score"]
        
        order = ["🟢 Low Risk Area", "🟡 Moderate Risk Area", "🔴 High Risk Hotspot"]
        cluster_stats = cluster_stats.reindex(order).dropna(how="all")
        
        st.dataframe(cluster_stats, use_container_width=True)
        
        st.markdown("""
        *   **Hotspot Characteristic:** Cities grouped inside the **🔴 High Risk Hotspot** exhibit significantly higher crime rates and lower chargesheeting ratios, suggesting high incident prevalence coupled with lower processing speed.
        *   **Unsupervised Insights:** Unlike the rule-based Safety Score, K-Means groups cities organically based on the statistical distance between their total crime volumes and police productivity.
        """)

if __name__ == "__main__":
    show_hotspot_page()
