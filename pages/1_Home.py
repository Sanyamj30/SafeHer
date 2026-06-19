import os
import json
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_loader import load_historical_state_data, load_crime_data, load_geojson_data
from utils.ui_components import render_hero, render_kpi, inject_custom_css

def show_home_page():
    inject_custom_css()
    
    # 1. Hero banner
    render_hero()
    
    # Load data
    df_state = load_historical_state_data()
    df_city = load_crime_data()
    
    # Check if data exists
    if df_state.empty or df_city.empty:
        st.error("Error: Crime datasets not found. Please ensure state_master.csv and city_stats.csv are present.")
        return
        
    latest_state_year = int(df_state["Year"].max())
    df_latest_state = df_state[df_state["Year"] == latest_state_year]
    
    latest_city_year = int(df_city["Year"].max())
    df_latest_city = df_city[df_city["Year"] == latest_city_year]
    
    # Calculate KPIs directly from the data sources
    total_crimes_state_2021 = df_latest_state["Total_Crimes"].sum()
    total_states = df_state["State_Clean"].nunique()
    
    total_crimes_city_2023 = df_latest_city["Total_Crimes"].sum()
    avg_city_safety = df_latest_city["Safety_Score"].mean()
    
    # 2. KPI Cards Grid
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_kpi("State Master Records", f"{len(df_state):,} Rows", f"2001 - {latest_state_year} Timeline", "#8B5CF6")
    with col2:
        render_kpi("State Crime Volume", f"{total_crimes_state_2021:,} Cases", f"All States & UTs ({latest_state_year})", "#EC4899")
    with col3:
        render_kpi("Metro Cities Volume", f"{total_crimes_city_2023:,} Cases", f"34 Metropolitan Cities ({latest_city_year})", "#3B82F6")
    with col4:
        score_color = "#10B981" if avg_city_safety >= 80 else "#F59E0B" if avg_city_safety >= 55 else "#EF4444"
        render_kpi("Metro Safety Index", f"{avg_city_safety:.1f} / 100", f"Average Metro Score ({latest_city_year})", score_color)
        
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    # 3. Interactive Map & Section Overview
    st.markdown(f"### India State-Wise Safety Index ({latest_state_year})")
    st.markdown("This interactive map showcases the safety score across different Indian States calculated directly from `state_master.csv`. *Hover over a state to view metrics.*")
    
    # Lazy load and render map with a loading spinner
    with st.spinner("Rendering Geospatial Choropleth Map..."):
        geojson = load_geojson_data()
        
        # Prepare map data
        state_summary = df_latest_state.groupby("State").agg({
            "Safety_Score": "mean",
            "Total_Crimes": "sum",
            "Population_Lakhs": "sum"
        }).reset_index()
        
        state_summary["Safety_Score"] = state_summary["Safety_Score"].round(2)
        state_summary["Crime_Rate"] = (state_summary["Total_Crimes"] / state_summary["Population_Lakhs"]).round(2)
        
        def get_risk_cat(score):
            if score >= 80: return "Low Risk"
            elif score >= 55: return "Medium Risk"
            else: return "High Risk"
        state_summary["Risk_Category"] = state_summary["Safety_Score"].apply(get_risk_cat)
        
        # Standardize casing to capitalize names for GeoJSON properties.NAME_1 matching
        map_df = state_summary.copy()
        map_df["State"] = map_df["State"].str.title().str.strip()
        
        # Plotly Choropleth Map (using the district geojson NAME_1 properties to match states)
        fig = px.choropleth(
            map_df,
            geojson=geojson,
            locations="State",
            featureidkey="properties.NAME_1",
            color="Safety_Score",
            color_continuous_scale="RdYlGn",
            range_color=[40, 95],
            labels={"Safety_Score": "Safety Score"},
            hover_name="State",
            hover_data={
                "State": False,
                "Safety_Score": ":.2f",
                "Total_Crimes": ":,",
                "Crime_Rate": ":.2f",
                "Risk_Category": True
            }
        )
        
        fig.update_geos(
            fitbounds="locations", 
            visible=False,
            projection_type="mercator"
        )
        
        fig.update_layout(
            margin={"r":0,"t":0,"l":0,"b":0},
            height=600,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            coloraxis_colorbar=dict(
                title="Safety Score",
                thicknessmode="pixels", thickness=15,
                lenmode="pixels", len=300,
                yanchor="middle", y=0.5,
                ticks="outside"
            )
        )
        
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    
    # 4. Top States Summary Columns
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown("#### Top 5 Safest States")
        top_safe = state_summary.sort_values(by="Safety_Score", ascending=False).head(5)[["State", "Safety_Score", "Total_Crimes"]]
        top_safe = top_safe.rename(columns={"Safety_Score": "Safety Score", "Total_Crimes": "Total Incidents"})
        st.dataframe(top_safe, use_container_width=True, hide_index=True)
        
    with col_right:
        st.markdown("#### Top 5 Highest Risk States")
        top_risk = state_summary.sort_values(by="Safety_Score", ascending=True).head(5)[["State", "Safety_Score", "Total_Crimes"]]
        top_risk = top_risk.rename(columns={"Safety_Score": "Safety Score", "Total_Crimes": "Total Incidents"})
        st.dataframe(top_risk, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    show_home_page()
