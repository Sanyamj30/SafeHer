import streamlit as st

def inject_custom_css():
    """Injects high-end, responsive custom CSS that adapts to light/dark themes."""
    css = """
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    /* Font family overrides (applied to text containers, preserving icons) */
    html, body, [data-testid="stAppViewContainer"], .stMarkdown, p, h1, h2, h3, h4, h5, h6, label {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Gradient headers */
    .main-header {
        font-weight: 700;
        background: linear-gradient(90deg, #6D28D9, #DB2777);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    /* Hero section container */
    .hero-container {
        background: linear-gradient(135deg, rgba(109, 40, 217, 0.15), rgba(219, 39, 119, 0.15));
        border: 1px solid rgba(109, 40, 217, 0.3);
        border-radius: 16px;
        padding: 2.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.05);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
    }
    
    .hero-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--text-color);
        margin-bottom: 1rem;
    }
    
    .hero-subtitle {
        font-size: 1.1rem;
        color: var(--text-color);
        opacity: 0.85;
        line-height: 1.6;
    }
    
    /* Premium KPI Card styling */
    .kpi-card {
        background: var(--secondary-background-color);
        border: 1px solid rgba(128, 128, 128, 0.15);
        border-left: 5px solid #6D28D9;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        margin-bottom: 15px;
    }
    
    .kpi-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 20px rgba(109, 40, 217, 0.15);
        border-color: rgba(109, 40, 217, 0.4);
    }
    
    .kpi-title {
        font-size: 0.85rem;
        font-weight: 600;
        color: var(--text-color);
        opacity: 0.7;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }
    
    .kpi-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--text-color);
        margin-bottom: 5px;
        line-height: 1.1;
    }
    
    .kpi-subtitle {
        font-size: 0.8rem;
        color: var(--text-color);
        opacity: 0.6;
    }
    
    /* Risk levels */
    .badge {
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
        text-align: center;
    }
    
    .badge-low {
        background-color: rgba(16, 185, 129, 0.15);
        color: #10B981;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    
    .badge-medium {
        background-color: rgba(245, 158, 11, 0.15);
        color: #F59E0B;
        border: 1px solid rgba(245, 158, 11, 0.3);
    }
    
    .badge-high {
        background-color: rgba(239, 68, 68, 0.15);
        color: #EF4444;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    
    /* Custom divider */
    .custom-divider {
        height: 2px;
        background: linear-gradient(90deg, #6D28D9, #DB2777, transparent);
        margin: 2rem 0;
        border-radius: 2px;
    }
    
    /* Pulse Animation */
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    .pulse-element {
        animation: pulse 2s infinite ease-in-out;
    }
    """
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

def render_hero():
    """Renders the SafeHer Hero Banner."""
    st.markdown(
        """
        <div class="hero-container">
            <h1 class="hero-title" style="margin:0; font-size:2.6rem; background: linear-gradient(90deg, #8B5CF6, #EC4899); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">SafeHer</h1>
            <p style="font-size: 1.2rem; font-weight: 500; margin-top: 5px; margin-bottom: 15px; color: var(--text-color); opacity: 0.9;">
                Women's Safety Analytics & Predictive Intelligence Platform
            </p>
            <div style="font-size: 0.95rem; line-height: 1.6; color: var(--text-color); opacity: 0.8;">
                SafeHer is an academic data science platform focused on identifying trends, forecasting risk levels, and 
                detecting hot spots of crimes against women across India. Using machine learning (Random Forest Classification, 
                K-Means Clustering) and interactive geospatial visualization tools, the platform translates historical public databases 
                into actionable awareness and resource-allocation insights.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_kpi(title, value, subtitle="", border_color="#6D28D9"):
    """Renders a single premium KPI card."""
    st.markdown(
        f"""
        <div class="kpi-card" style="border-left-color: {border_color};">
            <div class="kpi-title">{title}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def get_risk_badge_html(category):
    """Returns the HTML for a styled risk category badge."""
    cat_lower = category.lower()
    if "low" in cat_lower:
        return f'<span class="badge badge-low">🛡️ {category}</span>'
    elif "medium" in cat_lower or "moderate" in cat_lower:
        return f'<span class="badge badge-medium">⚠️ {category}</span>'
    else:
        return f'<span class="badge badge-high">🚨 {category}</span>'

def render_risk_badge(category):
    """Directly renders a styled risk category badge in Streamlit."""
    st.markdown(get_risk_badge_html(category), unsafe_allow_html=True)

def get_score_color(score):
    """Helper to return safety color based on score."""
    if score >= 80:
        return "#10B981"  # Green
    elif score >= 55:
        return "#F59E0B"  # Yellow
    else:
        return "#EF4444"  # Red
