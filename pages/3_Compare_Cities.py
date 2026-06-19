import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from utils.data_loader import load_crime_data
from utils.ui_components import render_kpi, get_risk_badge_html, inject_custom_css

def show_compare_page():
    inject_custom_css()
    
    st.markdown("## Side-by-Side City Comparison")
    st.markdown("Select two different cities to perform a comparative analysis of their safety scores, crime rates, and chargesheeting rates.")
    
    df = load_crime_data()
    
    if df.empty:
        st.error("Error: city_stats.csv not found.")
        return
        
    latest_year = int(df["Year"].max())
    states = sorted(df["State"].unique())
    
    # 1. Selection Interface
    col_sel_a, col_sel_b = st.columns(2)
    
    with col_sel_a:
        st.markdown("### City A")
        state_a = st.selectbox("Select State A", states, index=states.index("Maharashtra") if "Maharashtra" in states else 0)
        df_state_a = df[df["State"] == state_a]
        districts_a = sorted(df_state_a["District"].unique())
        district_a = st.selectbox("Select City A", districts_a, index=0)
        
    with col_sel_b:
        st.markdown("### City B")
        state_b = st.selectbox("Select State B", states, index=states.index("Delhi") if "Delhi" in states else 1)
        df_state_b = df[df["State"] == state_b]
        districts_b = sorted(df_state_b["District"].unique())
        district_b = st.selectbox("Select City B", districts_b, index=min(1, len(districts_b)-1))

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    # Filter records using SQL queries directly on safeher.db
    import sqlite3
    conn = sqlite3.connect("safeher.db")
    df_dist_a_all = pd.read_sql_query("""
        SELECT City as District, State, Year, CAST((Population_Lakhs * 100000) AS INTEGER) as Population,
               Total_Crimes, Crime_Rate, Chargesheeting_Rate, Safety_Score, Risk_Category,
               Score_CR, Score_CSR, Score_HT, Score_CD
        FROM cities
        WHERE State = ? AND City = ?
        ORDER BY Year
    """, conn, params=(state_a, district_a))
    
    df_dist_b_all = pd.read_sql_query("""
        SELECT City as District, State, Year, CAST((Population_Lakhs * 100000) AS INTEGER) as Population,
               Total_Crimes, Crime_Rate, Chargesheeting_Rate, Safety_Score, Risk_Category,
               Score_CR, Score_CSR, Score_HT, Score_CD
        FROM cities
        WHERE State = ? AND City = ?
        ORDER BY Year
    """, conn, params=(state_b, district_b))
    conn.close()
    
    if df_dist_a_all.empty or df_dist_b_all.empty:
        st.error("Error retrieving city comparison data.")
        return
        
    rec_a_latest = df_dist_a_all.iloc[-1]
    rec_b_latest = df_dist_b_all.iloc[-1]
    
    # 2. Side-by-Side KPI comparisons
    col_kpi_a, col_space, col_kpi_b = st.columns([10, 1, 10])
    
    with col_kpi_a:
        st.markdown(f"#### {district_a} ({state_a})")
        col_ka1, col_ka2 = st.columns(2)
        with col_ka1:
            render_kpi("Safety Score", f"{rec_a_latest['Safety_Score']:.1f}", f"Year: {latest_year}", "#8B5CF6")
        with col_ka2:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"Risk level: {get_risk_badge_html(rec_a_latest['Risk_Category'])}", unsafe_allow_html=True)
            st.markdown(f"Population: **{rec_a_latest['Population']:,}**")
            st.markdown(f"Crime rate: **{rec_a_latest['Crime_Rate']:.1f}** / lakh")
            
    with col_kpi_b:
        st.markdown(f"#### {district_b} ({state_b})")
        col_kb1, col_kb2 = st.columns(2)
        with col_kb1:
            render_kpi("Safety Score", f"{rec_b_latest['Safety_Score']:.1f}", f"Year: {latest_year}", "#EC4899")
        with col_kb2:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"Risk level: {get_risk_badge_html(rec_b_latest['Risk_Category'])}", unsafe_allow_html=True)
            st.markdown(f"Population: **{rec_b_latest['Population']:,}**")
            st.markdown(f"Crime rate: **{rec_b_latest['Crime_Rate']:.1f}** / lakh")
            
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    # Side-by-side Score Breakdown
    st.markdown("### Safety Score Breakdown Comparison")
    breakdown_comp = pd.DataFrame({
        "City": [district_a, district_a, district_a, district_a, district_b, district_b, district_b, district_b],
        "Component": [
            "Crime Rate (40%)", "Chargesheeting (25%)", "Historical Trend (20%)", "Crime Density (15%)",
            "Crime Rate (40%)", "Chargesheeting (25%)", "Historical Trend (20%)", "Crime Density (15%)"
        ],
        "Weighted Score": [
            0.40 * rec_a_latest["Score_CR"],
            0.25 * rec_a_latest["Score_CSR"],
            0.20 * rec_a_latest["Score_HT"],
            0.15 * rec_a_latest["Score_CD"],
            0.40 * rec_b_latest["Score_CR"],
            0.25 * rec_b_latest["Score_CSR"],
            0.20 * rec_b_latest["Score_HT"],
            0.15 * rec_b_latest["Score_CD"]
        ]
    })
    
    fig_breakdown_comp = px.bar(
        breakdown_comp,
        x="Weighted Score",
        y="Component",
        color="City",
        barmode="group",
        orientation="h",
        color_discrete_map={district_a: "#8B5CF6", district_b: "#EC4899"},
        height=260
    )
    fig_breakdown_comp.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis_title="Weighted Points Contribution (Out of 100)",
        yaxis_title=""
    )
    st.plotly_chart(fig_breakdown_comp, use_container_width=True, config={"displayModeBar": False})
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    # 3. Trend Comparison Chart
    st.markdown("### Safety Evolution (2021 - 2023)")
    
    fig_trend_comp = go.Figure()
    fig_trend_comp.add_trace(go.Scatter(
        x=df_dist_a_all["Year"],
        y=df_dist_a_all["Safety_Score"],
        mode="lines+markers",
        name=f"{district_a}",
        line=dict(color="#8B5CF6", width=3)
    ))
    fig_trend_comp.add_trace(go.Scatter(
        x=df_dist_b_all["Year"],
        y=df_dist_b_all["Safety_Score"],
        mode="lines+markers",
        name=f"{district_b}",
        line=dict(color="#EC4899", width=3)
    ))
    
    fig_trend_comp.update_layout(
        yaxis_range=[20, 100],
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=20, b=20, l=10, r=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_trend_comp, use_container_width=True, config={"displayModeBar": False})
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    # 4. Bar Comparison Charts
    st.markdown("### Metrics Comparison ({})".format(latest_year))
    st.info(" **Category-level radar charts are disabled.** This is because city_stats.csv does not contain category breakdowns (e.g. Rape, Kidnapping counts). Standardized comparative metrics for totals and police efficiency are shown below.")
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.markdown("#### Crime Rate Comparison (Cases per Lakh)")
        fig_rate = go.Figure(data=[
            go.Bar(name=district_a, x=["Crime Rate (2023)"], y=[rec_a_latest["Crime_Rate"]], marker_color='#8B5CF6'),
            go.Bar(name=district_b, x=["Crime Rate (2023)"], y=[rec_b_latest["Crime_Rate"]], marker_color='#EC4899')
        ])
        fig_rate.update_layout(
            barmode='group',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=30, b=20, l=10, r=10)
        )
        st.plotly_chart(fig_rate, use_container_width=True, config={"displayModeBar": False})
        
    with col_chart2:
        st.markdown("#### Chargesheeting Rate Comparison (%)")
        fig_charge = go.Figure(data=[
            go.Bar(name=district_a, x=["Chargesheeting Rate"], y=[rec_a_latest["Chargesheeting_Rate"]], marker_color='#8B5CF6'),
            go.Bar(name=district_b, x=["Chargesheeting Rate"], y=[rec_b_latest["Chargesheeting_Rate"]], marker_color='#EC4899')
        ])
        fig_charge.update_layout(
            barmode='group',
            yaxis_range=[0, 100],
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=30, b=20, l=10, r=10)
        )
        st.plotly_chart(fig_charge, use_container_width=True, config={"displayModeBar": False})

if __name__ == "__main__":
    show_compare_page()
