import streamlit as st
import pandas as pd
from utils.data_loader import load_crime_data
from utils.ui_components import inject_custom_css

def show_rankings_page():
    inject_custom_css()
    
    st.markdown("## 🏆 Safety Rankings & Leaderboards")
    st.markdown("Explore rankings of the safest and highest-risk states and districts across India, track the most-improved regions, and search the entire database.")
    
    import sqlite3
    conn = sqlite3.connect("safeher.db")
    
    # Get years list via SQL
    years_df = pd.read_sql_query("SELECT DISTINCT Year FROM cities ORDER BY Year DESC", conn)
    years = years_df["Year"].tolist()
    ranking_year = st.selectbox("Select Year for Rankings", years, index=0)
    
    # 1. State Level Aggregations via SQL Group By
    state_rankings = pd.read_sql_query("""
        SELECT State, AVG(Safety_Score) as Safety_Score, (SUM(Total_Crimes) / SUM(Population_Lakhs)) as Crime_Rate
        FROM cities
        WHERE Year = ?
        GROUP BY State
    """, conn, params=(ranking_year,))
    state_rankings["Safety_Score"] = state_rankings["Safety_Score"].round(2)
    state_rankings["Crime_Rate"] = state_rankings["Crime_Rate"].round(2)
    
    # 2. Tabs for different rankings
    tab_states, tab_districts, tab_improved = st.tabs(["🏛️ State Rankings", "🏙️ District Rankings", "📈 Most Improved (2021-2023)"])
    
    with tab_states:
        col_safe_st, col_risk_st = st.columns(2)
        
        with col_safe_st:
            st.markdown(f"#### 🟢 Safest States ({ranking_year})")
            top_safe_st = state_rankings.sort_values(by="Safety_Score", ascending=False).head(10)[["State", "Safety_Score", "Crime_Rate"]]
            top_safe_st.columns = ["State", "Safety Score", "Crime Rate / 100k"]
            st.dataframe(top_safe_st, use_container_width=True, hide_index=True)
            
        with col_risk_st:
            st.markdown(f"#### 🔴 Highest Risk States ({ranking_year})")
            top_risk_st = state_rankings.sort_values(by="Safety_Score", ascending=True).head(10)[["State", "Safety_Score", "Crime_Rate"]]
            top_risk_st.columns = ["State", "Safety Score", "Crime Rate / 100k"]
            st.dataframe(top_risk_st, use_container_width=True, hide_index=True)
            
    with tab_districts:
        col_safe_dt, col_risk_dt = st.columns(2)
        
        # Load sorted districts via SQL
        districts_sorted = pd.read_sql_query("""
            SELECT City as District, State, Safety_Score, Crime_Rate
            FROM cities
            WHERE Year = ?
            ORDER BY Safety_Score DESC
        """, conn, params=(ranking_year,))
        
        with col_safe_dt:
            st.markdown(f"#### 🟢 Safest Districts ({ranking_year})")
            top_safe_dt = districts_sorted.head(10)
            top_safe_dt.columns = ["District", "State", "Safety Score", "Crime Rate"]
            st.dataframe(top_safe_dt, use_container_width=True, hide_index=True)
            
        with col_risk_dt:
            st.markdown(f"#### 🔴 Highest Risk Districts ({ranking_year})")
            top_risk_dt = districts_sorted.iloc[::-1].head(10)
            top_risk_dt.columns = ["District", "State", "Safety Score", "Crime Rate"]
            st.dataframe(top_risk_dt, use_container_width=True, hide_index=True)
            
    with tab_improved:
        st.markdown("#### 🚀 Safety Improvements (2021 vs 2023)")
        st.markdown("This analysis tracks the growth/decline in safety score index points between the base year (2021) and 2023.")
        
        # Perform self-join in SQL to find net improvement
        merged_growth = pd.read_sql_query("""
            SELECT c21.City as District, c21.State, c21.Safety_Score as Score_2021, c23.Safety_Score as Score_2023,
                   (c23.Safety_Score - c21.Safety_Score) as Net_Improvement
            FROM cities c21
            JOIN cities c23 ON c21.City = c23.City AND c21.State = c23.State
            WHERE c21.Year = 2021 AND c23.Year = 2023
        """, conn)
        merged_growth["Net_Improvement"] = merged_growth["Net_Improvement"].round(2)
        
        col_grow1, col_grow2 = st.columns(2)
        with col_grow1:
            st.markdown("##### 📈 Top 5 Most Improved Districts")
            top_improved_df = merged_growth.sort_values(by="Net_Improvement", ascending=False).head(5)[["District", "State", "Score_2021", "Score_2023", "Net_Improvement"]]
            top_improved_df.columns = ["District", "State", "2021 Score", "2023 Score", "Index Gain"]
            st.dataframe(top_improved_df, use_container_width=True, hide_index=True)
            
        with col_grow2:
            st.markdown("##### 📉 Top 5 Most Declined Districts")
            top_declined_df = merged_growth.sort_values(by="Net_Improvement", ascending=True).head(5)[["District", "State", "Score_2021", "Score_2023", "Net_Improvement"]]
            top_declined_df.columns = ["District", "State", "2021 Score", "2023 Score", "Index Decline"]
            st.dataframe(top_declined_df, use_container_width=True, hide_index=True)
            
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    # 3. Searchable Database Grid
    st.markdown("### 🔍 Search & Filter Database Explorer")
    st.markdown("Filter by state name or type in a district name to search coordinates, population, and specific crime rates.")
    
    # Get distinct states list via SQL
    states_list = pd.read_sql_query("SELECT DISTINCT State FROM cities ORDER BY State", conn)["State"].tolist()
    
    # Filters
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        state_filter = st.multiselect("Filter by State", states_list)
    with col_f2:
        search_query = st.text_input("Search District Name")
        
    # Build dynamic SQL query to search database explorer
    query_str = """
        SELECT City as District, State, Safety_Score as [Safety Score], Risk_Category as [Risk Level],
               CAST((Population_Lakhs * 100000) AS INTEGER) as Population, Total_Crimes as [Total Cases],
               Crime_Rate as [Total Crime Rate], Chargesheeting_Rate as [Chargesheeting Rate (%)]
        FROM cities
        WHERE Year = ?
    """
    params = [ranking_year]
    
    if state_filter:
        placeholders = ",".join("?" for _ in state_filter)
        query_str += f" AND State IN ({placeholders})"
        params.extend(state_filter)
        
    if search_query:
        query_str += " AND City LIKE ?"
        params.append(f"%{search_query}%")
        
    explorer_df = pd.read_sql_query(query_str, conn, params=params)
    conn.close()
    
    st.dataframe(explorer_df, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    show_rankings_page()
