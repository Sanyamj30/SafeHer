import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils.data_loader import load_historical_state_data, load_crime_data, load_classifier_model
from utils.ui_components import render_kpi, render_risk_badge, inject_custom_css, get_score_color

def show_district_page():
    inject_custom_css()
    
    st.markdown("## Safety Profile & Trend Analysis")
    st.markdown("Analyze safety scores, historical crime volumes, and risk levels at either the State or City level using the master datasets.")
    
    # 1. Level of Analysis Selector
    analysis_level = st.radio("Select Analysis Level", ["State Level", "City Level"], horizontal=True)
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    if analysis_level == "State Level":
        df = load_historical_state_data()
        classifier_data = load_classifier_model()
        
        if df.empty:
            st.error("Error: state_master.csv not found.")
            return
            
        states = sorted(df["State"].unique())
        selected_state = st.selectbox("Select State", states, index=0)
        
        df_dist = df[df["State"] == selected_state].sort_values("Year")
        latest_record = df_dist.iloc[-1]
        first_record = df_dist.iloc[0]
        
        # 2. Main Stats Grid
        col_card1, col_card2, col_card3 = st.columns(3)
        with col_card1:
            score = latest_record["Safety_Score"]
            score_color = get_score_color(score)
            render_kpi("Safety Score", f"{score:.1f} / 100", f"Category: {latest_record['Risk_Category']} ({latest_record['Year']})", score_color)
        with col_card2:
            pop_lakhs = latest_record["Population_Lakhs"]
            render_kpi("Population (Est.)", f"{int(pop_lakhs * 100000):,}", "Derived from census baseline", "#3B82F6")
        with col_card3:
            render_kpi("Total Incidents", f"{latest_record['Total_Crimes']:,} Cases", f"Crime rate: {latest_record['Crime_Rate']:.1f} per lakh", "#EF4444")
            
        # Composite Score Breakdown
        st.markdown("#### Safety Score Component Breakdown")
        breakdown_df = pd.DataFrame({
            "Component": ["Crime Rate (40%)", "Chargesheeting (25%)", "Historical Trend (20%)", "Crime Density (15%)"],
            "Weighted Score": [
                0.40 * latest_record["Score_CR"],
                0.25 * latest_record["Score_CSR"],
                0.20 * latest_record["Score_HT"],
                0.15 * latest_record["Score_CD"]
            ]
        })
        fig_breakdown = px.bar(
            breakdown_df,
            x="Weighted Score",
            y="Component",
            orientation="h",
            color="Component",
            color_discrete_sequence=px.colors.qualitative.Pastel,
            height=180
        )
        fig_breakdown.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis_title="Weighted Points (Out of 100)",
            yaxis_title="",
            showlegend=False
        )
        st.plotly_chart(fig_breakdown, use_container_width=True, config={"displayModeBar": False})
            
        # 3. ML Risk Classification Section
        st.markdown("### Machine Learning Predictive Insights")
        if classifier_data:
            # Model selection
            model_choice = st.selectbox("Select ML Model", ["Random Forest Classifier", "Logistic Regression Classifier"])
            
            if model_choice == "Random Forest Classifier":
                model = classifier_data["rf_model"]
            else:
                model = classifier_data["lr_model"]
                
            features = classifier_data["features"]
            
            # Prepare population-normalized input features
            pop_lakhs = latest_record["Population_Lakhs"]
            input_rates = {
                "Rape_Rate": latest_record["Rape"] / pop_lakhs,
                "KA_Rate": latest_record["K&A"] / pop_lakhs,
                "DD_Rate": latest_record["DD"] / pop_lakhs,
                "AoW_Rate": latest_record["AoW"] / pop_lakhs,
                "AoM_Rate": latest_record["AoM"] / pop_lakhs,
                "DV_Rate": latest_record["DV"] / pop_lakhs,
                "WT_Rate": latest_record["WT"] / pop_lakhs,
                "Crime_Rate_Per_Lakh": latest_record["Total_Crimes"] / pop_lakhs
            }
            
            X_raw = np.array([input_rates[feat] for feat in features]).reshape(1, -1)
            
            # Apply standard scaling
            scaler = classifier_data["scaler"]
            X_scaled = scaler.transform(X_raw)
            
            # Predict
            predicted_risk = model.predict(X_scaled)[0]
            probabilities = model.predict_proba(X_scaled)[0]
            classes = model.classes_
            
            pred_index = list(classes).index(predicted_risk)
            confidence = probabilities[pred_index] * 100
            
            col_ml1, col_ml2 = st.columns([1, 2])
            with col_ml1:
                st.markdown("**Model Classification Output**")
                render_risk_badge(predicted_risk)
                st.markdown(f"Confidence: **{confidence:.1f}%**")
                
            with col_ml2:
                st.markdown("**Prediction Probabilities**")
                prob_df = pd.DataFrame({
                    "Risk Category": classes,
                    "Probability (%)": (probabilities * 100).round(1)
                })
                fig_prob = px.bar(
                    prob_df, 
                    x="Probability (%)", 
                    y="Risk Category", 
                    orientation="h",
                    color="Risk Category",
                    color_discrete_map={"Low Risk": "#10B981", "Medium Risk": "#F59E0B", "High Risk": "#EF4444"},
                    height=180
                )
                fig_prob.update_layout(margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_prob, use_container_width=True, config={"displayModeBar": False})
                
            # Local Contributing Factors Explanation
            st.markdown("#### Top Contributing Factors (Local Prediction Explanation)")
            if model_choice == "Random Forest Classifier":
                # For RF, use global feature importances as a contribution reference
                importances = classifier_data["rf_importances"]
                sorted_imp = sorted(importances.items(), key=lambda x: x[1], reverse=True)
                explain_df = pd.DataFrame(sorted_imp, columns=["Feature", "Contribution Weight"])
                title_suffix = "Global Feature Importances"
            else:
                # For LR, show local feature contributions: scaled_value * coefficient_for_class
                coeffs = classifier_data["lr_coefficients"].get(predicted_risk, {})
                local_contribs = {}
                for idx, feat in enumerate(features):
                    local_contribs[feat] = X_scaled[0][idx] * coeffs.get(feat, 0.0)
                sorted_contribs = sorted(local_contribs.items(), key=lambda x: abs(x[1]), reverse=True)
                explain_df = pd.DataFrame(sorted_contribs, columns=["Feature", "Contribution Weight"])
                title_suffix = f"Local Feature Contribution Weights ({predicted_risk})"
                
            fig_explain = px.bar(
                explain_df,
                x="Contribution Weight",
                y="Feature",
                orientation="h",
                color="Contribution Weight",
                color_continuous_scale="RdBu",
                height=240
            )
            fig_explain.update_layout(
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                title=f"{model_choice} - {title_suffix}"
            )
            st.plotly_chart(fig_explain, use_container_width=True, config={"displayModeBar": False})
            
            # Model Explanation section
            with st.expander(" Model Explanation & Methodology Details"):
                st.markdown("""
                * **Population Normalization:** Instead of training on raw incident counts (which artificially labels highly populated states as "High Risk"), the model scales crimes to rates per lakh population (e.g. `Rape_Rate = Rape / Population_Lakhs`).
                * **Scaler Payload:** Input features are standardized using the original training dataset mean/std bounds.
                * **Random Forest Classifier:** Classifies risk by aggregating decisions from a collection of decision trees.
                * **Logistic Regression Classifier:** Determines risk probability using a linear equation, showing feature contributions directly. Positive weights push the model toward predicting that risk class, while negative weights oppose it.
                """)
        else:
            st.info("ML Classifier model not loaded.")
            
        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        
        # 4. Visualizations: Trend & Crime Breakdown
        col_vis1, col_vis2 = st.columns(2)
        with col_vis1:
            st.markdown(f"#### Historical Safety Index (2001 - 2021)")
            fig_trend = px.line(
                df_dist, 
                x="Year", 
                y="Safety_Score",
                markers=True,
                labels={"Safety_Score": "Safety Score"},
                color_discrete_sequence=["#8B5CF6"]
            )
            fig_trend.update_layout(
                yaxis_range=[20, 100], 
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(t=20, b=20, l=10, r=10)
            )
            st.plotly_chart(fig_trend, use_container_width=True, config={"displayModeBar": False})
            
        with col_vis2:
            st.markdown(f"#### Crime Category Distribution ({latest_record['Year']})")
            categories = ["Rape", "K&A", "DD", "AoW", "AoM", "DV", "WT"]
            values = [latest_record[c] for c in categories]
            
            breakdown_df = pd.DataFrame({
                "Crime Category": ["Rape", "Kidnapping & Abduction", "Dowry Deaths", "Assault on Women", "Insult to Modesty", "Domestic Violence", "Women Trafficking"],
                "Count": values
            })
            
            fig_pie = px.pie(
                breakdown_df,
                values="Count",
                names="Crime Category",
                color_discrete_sequence=px.colors.sequential.RdBu,
                hole=0.4
            )
            fig_pie.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(t=20, b=20, l=10, r=10)
            )
            st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})
            
        # 5. Automated Insights Section
        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        st.markdown("### Automated Criminological Insights")
        
        score_change = score - first_record["Safety_Score"]
        trend_direction = "improved" if score_change > 0 else "declined"
        abs_change = abs(score_change)
        
        crime_counts = {c: latest_record[c] for c in categories}
        dominant_crime_key = max(crime_counts, key=crime_counts.get)
        dominant_crime_map = {
            "Rape": "Rape", "K&A": "Kidnapping & Abduction", "DD": "Dowry Deaths",
            "AoW": "Assault on Women", "AoM": "Insult to Modesty", "DV": "Domestic Violence", "WT": "Women Trafficking"
        }
        dominant_crime = dominant_crime_map.get(dominant_crime_key, dominant_crime_key)
        
        total_crimes_val = latest_record["Total_Crimes"]
        dominant_percentage = (crime_counts[dominant_crime_key] / total_crimes_val * 100) if total_crimes_val > 0 else 0
        
        insight_text = f"""
        - **Safety Score Evolution:** The safety score of **{selected_state}** stands at **{score:.1f}/100** in **{latest_record['Year']}**, representing a **{trend_direction}** of **{abs_change:.1f}** points since 2001 (where it was **{first_record['Safety_Score']:.1f}/100**).
        - **Primary Crime Driver:** The highest recorded crime type in the state is **{dominant_crime}**, comprising **{dominant_percentage:.1f}%** of all crimes reported against women.
        - **Criminological Context:** In larger states like `{selected_state}`, reporting rates for crimes against women often reflect awareness levels, support hotlines, and judicial efficiency. A high volume does not always imply a lack of safety, but can indicate a higher rate of administrative reporting.
        """
        st.info(insight_text)
        
    else: # City Level
        df = load_crime_data()
        
        if df.empty:
            st.error("Error: city_stats.csv not found.")
            return
            
        cities = sorted(df["District"].unique())
        selected_city = st.selectbox("Select City", cities, index=0)
        
        df_dist = df[df["District"] == selected_city].sort_values("Year")
        latest_record = df_dist.iloc[-1]
        first_record = df_dist.iloc[0]
        
        # 2. Main Stats Grid
        col_card1, col_card2, col_card3 = st.columns(3)
        with col_card1:
            score = latest_record["Safety_Score"]
            score_color = get_score_color(score)
            render_kpi("Safety Score", f"{score:.1f} / 100", f"Category: {latest_record['Risk_Category']} ({latest_record['Year']})", score_color)
        with col_card2:
            render_kpi("Population", f"{latest_record['Population']:,}", f"Metropolitan Scale", "#3B82F6")
        with col_card3:
            render_kpi("Total Incidents", f"{latest_record['Total_Crimes']:,} Cases", f"Crime rate: {latest_record['Crime_Rate']:.1f} per lakh", "#EF4444")
            
        # Composite Score Breakdown for City
        st.markdown("#### Safety Score Component Breakdown")
        breakdown_df = pd.DataFrame({
            "Component": ["Crime Rate (40%)", "Chargesheeting (25%)", "Historical Trend (20%)", "Crime Density (15%)"],
            "Weighted Score": [
                0.40 * latest_record["Score_CR"],
                0.25 * latest_record["Score_CSR"],
                0.20 * latest_record["Score_HT"],
                0.15 * latest_record["Score_CD"]
            ]
        })
        fig_breakdown = px.bar(
            breakdown_df,
            x="Weighted Score",
            y="Component",
            orientation="h",
            color="Component",
            color_discrete_sequence=px.colors.qualitative.Pastel,
            height=180
        )
        fig_breakdown.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis_title="Weighted Points (Out of 100)",
            yaxis_title="",
            showlegend=False
        )
        st.plotly_chart(fig_breakdown, use_container_width=True, config={"displayModeBar": False})
            
        # 3. Disabled Features info box
        st.markdown("### Predictive Analytics & Breakdown")
        st.info(" **Crime Category Breakdown and ML Predictive Insights are disabled for cities.** This is because `city_stats.csv` only contains total crime counts, and lacks head-wise categories like Rape, Kidnapping, or Domestic Violence. State-level analysis remains fully supported.")
        
        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        
        # 4. Trend Viz
        st.markdown(f"#### Historical Safety Index (2021 - 2023)")
        fig_trend = px.line(
            df_dist, 
            x="Year", 
            y="Safety_Score",
            markers=True,
            labels={"Safety_Score": "Safety Score"},
            color_discrete_sequence=["#3B82F6"]
        )
        fig_trend.update_layout(
            yaxis_range=[20, 100], 
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=20, b=20, l=10, r=10)
        )
        st.plotly_chart(fig_trend, use_container_width=True, config={"displayModeBar": False})
        
        # 5. Automated Insights Section
        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        st.markdown("### Automated Criminological Insights")
        
        score_change = score - first_record["Safety_Score"]
        trend_direction = "improved" if score_change > 0 else "declined"
        abs_change = abs(score_change)
        
        insight_text = f"""
        - **Safety Score Evolution:** The safety score of **{selected_city}** stands at **{score:.1f}/100** in **{latest_record['Year']}**, representing a **{trend_direction}** of **{abs_change:.1f}** points since 2021 (where it was **{first_record['Safety_Score']:.1f}/100**).
        - **Police Action Metric:** The chargesheeting rate for crimes against women in **{selected_city}** is **{latest_record['Chargesheeting_Rate']:.1f}%**.
        """
        st.info(insight_text)

if __name__ == "__main__":
    show_district_page()
