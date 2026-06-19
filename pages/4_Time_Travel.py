import os
import json
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_loader import load_historical_state_data, load_geojson_data
from utils.ui_components import render_kpi, inject_custom_css

def show_time_travel_page():
    inject_custom_css()
    
    st.markdown("## ⏳ Historical Time Travel Safety Analysis")
    st.markdown("Use the slider below to navigate through history (2001 - 2021) and observe the evolution of safety scores, crime volumes, and state-level safety maps.")
    
    import sqlite3
    conn = sqlite3.connect("safeher.db")
    
    # 1. Year limits query
    limits = pd.read_sql_query("SELECT MIN(Year) as min_y, MAX(Year) as max_y FROM states WHERE Year <= 2019", conn).iloc[0]
    min_year = int(limits["min_y"])
    max_year = int(limits["max_y"])
    
    selected_year = st.slider(
        "Navigate Year", 
        min_value=min_year, 
        max_value=max_year, 
        value=max_year, 
        step=1
    )
    
    # SQL query to get national summary over time
    national_summary = pd.read_sql_query("""
        SELECT Year, AVG(Safety_Score) as Safety_Score, SUM(Total_Crimes) as Total_Crimes,
               SUM(Population_Lakhs) as Population_Lakhs
        FROM states
        WHERE Year <= 2019
        GROUP BY Year
        ORDER BY Year
    """, conn)
    
    selected_national = national_summary[national_summary["Year"] == selected_year].iloc[0]
    
    # KPIs for the selected year
    col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
    with col_kpi1:
        render_kpi(f"National Safety Index ({selected_year})", f"{selected_national['Safety_Score']:.1f} / 100", "Weighted safety indicator", "#8B5CF6")
    with col_kpi2:
        render_kpi(f"Total Incidents ({selected_year})", f"{selected_national['Total_Crimes']:,} Cases", "Annual crime against women count", "#EF4444")
    with col_kpi3:
        # Crime rate per lakh
        crime_rate = (selected_national['Total_Crimes'] / selected_national['Population_Lakhs'])
        render_kpi(f"National Crime Rate ({selected_year})", f"{crime_rate:.1f}", "Incidents per 100,000 women", "#3B82F6")
        
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    # 2. Main Visualizations: Map and Timeline
    col_map, col_timeline = st.columns([11, 9])
    
    # Prepare Map Data using SQL
    state_summary = pd.read_sql_query("""
        SELECT State, Safety_Score, Total_Crimes, Population_Lakhs, Risk_Category,
               (Total_Crimes / Population_Lakhs) as Crime_Rate
        FROM states
        WHERE Year = ?
    """, conn, params=(selected_year,))
    conn.close()
    
    state_summary["Safety_Score"] = state_summary["Safety_Score"].round(2)
    state_summary["Crime_Rate"] = state_summary["Crime_Rate"].round(2)
    
    map_df = state_summary.copy()
    map_df["State"] = map_df["State"].str.title().str.strip()
    
    with col_map:
        st.markdown(f"#### 🗺️ State Safety Choropleth in {selected_year}")
        
        with st.spinner("Rendering Geospatial Choropleth Map..."):
            geojson = load_geojson_data()
            
            fig_map = px.choropleth(
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
            fig_map.update_geos(
                fitbounds="locations", 
                visible=False,
                projection_type="mercator"
            )
            fig_map.update_layout(
                margin={"r":0,"t":0,"l":0,"b":0},
                height=450,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_map, use_container_width=True, config={"displayModeBar": False})
        
    with col_timeline:
        st.markdown("#### ⏳ Historical Safety Timeline (2001 - 2021)")
        
        fig_timeline = go.Figure()
        # Add trace of safety trend
        fig_timeline.add_trace(go.Scatter(
            x=national_summary["Year"],
            y=national_summary["Safety_Score"],
            mode="lines+markers",
            name="National Index",
            line=dict(color="rgba(139, 92, 246, 0.4)", width=2),
            marker=dict(size=8, color="#a78bfa")
        ))
        
        # Highlight selected year
        selected_row = national_summary[national_summary["Year"] == selected_year]
        fig_timeline.add_trace(go.Scatter(
            x=selected_row["Year"],
            y=selected_row["Safety_Score"],
            mode="markers+text",
            name="Active Year",
            marker=dict(size=14, color="#EF4444", symbol="star"),
            text=[f"{selected_year}"],
            textposition="top center",
            textfont=dict(size=12, color="#EF4444", weight="bold")
        ))
        
        fig_timeline.update_layout(
            yaxis_range=[20, 100],
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=20, b=20, l=10, r=10),
            showlegend=False
        )
        st.plotly_chart(fig_timeline, use_container_width=True, config={"displayModeBar": False})
        
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    # 3. Safety Distribution Analysis
    col_dist, col_analysis = st.columns([1, 1])
    
    with col_dist:
        st.markdown(f"#### 📊 State Score Dispersion ({selected_year})")
        # Draw box plot to show state safety score distribution
        fig_box = px.box(
            state_summary,
            y="Safety_Score",
            points="all",
            labels={"Safety_Score": "Safety Score"},
            color_discrete_sequence=["#8B5CF6"]
        )
        fig_box.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=20, b=20, l=10, r=10)
        )
        st.plotly_chart(fig_box, use_container_width=True, config={"displayModeBar": False})
        
    with col_analysis:
        st.markdown("#### 📝 Safety Evolution Commentary")
        
        # Compare with baseline (2001)
        base_national = national_summary[national_summary["Year"] == 2001].iloc[0]
        diff_base = selected_national["Safety_Score"] - base_national["Safety_Score"]
        
        # Analyze the distribution
        high_risk_states_count = len(state_summary[state_summary["Risk_Category"] == "High Risk"])
        low_risk_states_count = len(state_summary[state_summary["Risk_Category"] == "Low Risk"])
        
        analysis_text = f"""
        *   **Historical Shift:** In **{selected_year}**, the National Safety Index stands at **{selected_national['Safety_Score']:.1f}/100**, compared to the baseline year **2001** index of **{base_national['Safety_Score']:.1f}/100**. This is a net change of **{diff_base:+.2f}** index points over the years.
        *   **Reporting Volume & Capacity:** Over this decadal period, the increase in raw incident counts often correlates with improvements in literacy, gender awareness, police filing protocols (e.g. mandatory registration of FIRs), and the introduction of specialized women's help desks across districts.
        *   **Administrative Risk Profile:** Across India in {selected_year}, **{high_risk_states_count}** states fall under the **High Risk** warning category, while **{low_risk_states_count}** states have achieved **Low Risk (Safe)** status.
        *   **Policy Implications:** Criminological research suggests that long-term safety improvements depend heavily on institutional reforms, chargesheeting swiftness, and structural deterrents rather than policing volume alone.
        """
        st.info(analysis_text)

if __name__ == "__main__":
    show_time_travel_page()
