import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap, MarkerCluster
from streamlit_folium import folium_static
from utils.data_loader import load_crime_data
from utils.ui_components import inject_custom_css

def show_heatmaps_page():
    inject_custom_css()
    
    st.markdown("## Geo-Spatial Safety Heatmaps")
    st.markdown("Visualize spatial risk profiles across India. Switch between layers to examine crime density, local safety index drops, or specific regional risk levels.")
    
    # Load data using SQL directly on safeher.db
    import sqlite3
    conn = sqlite3.connect("safeher.db")
    df_latest = pd.read_sql_query("""
        SELECT City as District, State, Year, CAST((Population_Lakhs * 100000) AS INTEGER) as Population,
               Total_Crimes, Crime_Rate, Chargesheeting_Rate, Latitude, Longitude, Safety_Score, Risk_Category
        FROM cities
        WHERE Year = (SELECT MAX(Year) FROM cities)
    """, conn)
    conn.close()
    
    if df_latest.empty:
        st.error("Error: Crime dataset not found in safeher.db.")
        return
        
    latest_year = int(df_latest["Year"].iloc[0])
    
    # 1. Map Layer Selector
    map_type = st.radio(
        "Select Visual Layer",
        [
            " Crime Density Heatmap (Weighted by Incident Counts)",
            " Safety Index Hotspots (Weighted by Unsafety Score)",
            " Regional Risk Concentration Clusters (Pins & Marker Clusters)"
        ],
        horizontal=True
    )
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    # Initialize Folium Map centered on India inside a rendering spinner
    with st.spinner("Rendering Folium Map and Layer Overlay..."):
        m = folium.Map(location=[22.0, 78.0], zoom_start=5, control_scale=True)
        
        if "Crime Density" in map_type:
            st.markdown("#### Crime Density Heatmap")
            st.markdown("This map shows the concentration of total crimes recorded against women. High-intensity red areas indicate a large volume of incidents.")
            
            # Prepare data: [lat, lon, weight]
            heat_data = df_latest[["Latitude", "Longitude", "Total_Crimes"]].dropna().values.tolist()
            
            # Add heatmap layer
            HeatMap(
                heat_data, 
                radius=15, 
                blur=10, 
                max_zoom=10
            ).add_to(m)
            
        elif "Safety Index" in map_type:
            st.markdown("#### Safety Index Hotspots (Unsafety Heatmap)")
            st.markdown("This heatmap highlights regions where the Safety Score drops (higher heat indicates *lower* safety). Weight is calculated as `100 - Safety_Score`.")
            
            # We want lower safety scores to appear as HIGHER density
            # Weight = 100 - Safety_Score
            df_latest["Unsafety_Weight"] = 100 - df_latest["Safety_Score"]
            heat_data = df_latest[["Latitude", "Longitude", "Unsafety_Weight"]].dropna().values.tolist()
            
            # Add heatmap layer with custom color scale
            HeatMap(
                heat_data, 
                radius=16, 
                blur=12, 
                max_zoom=10,
                gradient={0.2: 'blue', 0.4: 'lime', 0.6: 'orange', 1: 'red'}
            ).add_to(m)
            
        else:
            st.markdown("#### Regional Risk Concentration Clusters")
            st.markdown("Pins represent individual districts, clustered by region. Blue bubbles show aggregated district counts; click to expand. Individual pins are colored by risk category.")
            
            marker_cluster = MarkerCluster(
                options={'spiderfyOnMaxZoom': True, 'showCoverageOnHover': False}
            ).add_to(m)
            
            # Render marker pins
            for _, row in df_latest.iterrows():
                score = row["Safety_Score"]
                risk = row["Risk_Category"]
                
                # Map safety score to pin color
                if score >= 80:
                    color = "green"
                elif score >= 55:
                    color = "orange"
                else:
                    color = "red"
                    
                popup_html = f"""
                <div style="font-family: 'Outfit', sans-serif; font-size: 12px; width: 220px;">
                    <h5 style="margin: 0 0 5px 0; color: #4B5563;">{row['District']}</h5>
                    <p style="margin: 2px 0;">State: <b>{row['State']}</b></p>
                    <p style="margin: 2px 0;">Safety Score: <b style="color:{color};">{score:.1f}/100</b></p>
                    <p style="margin: 2px 0;">Risk Level: <b>{risk}</b></p>
                    <p style="margin: 2px 0;">Total Crimes: <b>{row['Total_Crimes']:,} cases</b></p>
                </div>
                """
                
                folium.Marker(
                    location=[row["Latitude"], row["Longitude"]],
                    popup=folium.Popup(popup_html, max_width=250),
                    icon=folium.Icon(color=color, icon="info-sign")
                ).add_to(marker_cluster)
                
        # Render map statically inside Streamlit
        folium_static(m, width=1100, height=600)
        
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    st.markdown("""
    > [!NOTE]
    > **Geospatial Insights**: High-density zones on the crime count heatmap frequently map to high-population metropolitan districts (such as Mumbai, Bengaluru, and Delhi). The Safety Score Heatmap normalizes this by population size, highlighting regions with high per-capita risk, which offers a much more accurate spatial perspective for administrative intervention.
    """)

if __name__ == "__main__":
    show_heatmaps_page()
