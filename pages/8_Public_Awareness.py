import streamlit as st
from utils.ui_components import inject_custom_css

def show_awareness_page():
    inject_custom_css()
    
    st.markdown("## Public Awareness & Safety Resources")
    st.markdown("Access critical emergency contacts, legal rights overview, safety guidelines, and active government initiatives focused on empowering and protecting women.")
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    # 1. Styled Emergency Contacts Section
    st.markdown("### Emergency Helplines (24/7 Toll-Free)")
    
    # Custom HTML styling for emergency contact cards
    helpline_html = """
    <div style="display: flex; gap: 15px; flex-wrap: wrap; margin-bottom: 25px;">
        <div style="flex: 1; min-width: 250px; background: linear-gradient(135deg, #EF4444, #B91C1C); color: white; border-radius: 12px; padding: 20px; box-shadow: 0 4px 15px rgba(239, 68, 68, 0.25); text-align: center;">
            <div style="font-size: 2.5rem; margin-bottom: 10px;"> 112</div>
            <div style="font-size: 1.1rem; font-weight: 700; text-transform: uppercase;">National Emergency Number</div>
            <div style="font-size: 0.85rem; margin-top: 5px; opacity: 0.9;">Unified response for Police, Fire, and Health emergencies.</div>
        </div>
        <div style="flex: 1; min-width: 250px; background: linear-gradient(135deg, #EC4899, #BE185D); color: white; border-radius: 12px; padding: 20px; box-shadow: 0 4px 15px rgba(236, 72, 153, 0.25); text-align: center;">
            <div style="font-size: 2.5rem; margin-bottom: 10px;"> 1091</div>
            <div style="font-size: 1.1rem; font-weight: 700; text-transform: uppercase;">Women Helpline</div>
            <div style="font-size: 0.85rem; margin-top: 5px; opacity: 0.9;">Dedicated helpline for women facing distress or harassment.</div>
        </div>
        <div style="flex: 1; min-width: 250px; background: linear-gradient(135deg, #8B5CF6, #6D28D9); color: white; border-radius: 12px; padding: 20px; box-shadow: 0 4px 15px rgba(139, 92, 246, 0.25); text-align: center;">
            <div style="font-size: 2.5rem; margin-bottom: 10px;"> 181</div>
            <div style="font-size: 1.1rem; font-weight: 700; text-transform: uppercase;">Abuse & Domestic Helpline</div>
            <div style="font-size: 0.85rem; margin-top: 5px; opacity: 0.9;">Support for domestic violence, abuse, and counseling.</div>
        </div>
    </div>
    """
    st.markdown(helpline_html, unsafe_allow_html=True)
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    # 2. Safety Guidelines & Tips Tabs
    st.markdown("### Safety Guidelines")
    
    tab_travel, tab_digital, tab_work = st.tabs([" Travel & Public Spaces", " Cyber & Digital Safety", " Workplace Safety"])
    
    with tab_travel:
        st.markdown("""
        * **Share Location Services:** Always share your live location via trusted contacts (e.g. WhatsApp, Google Maps) when traveling alone or at night.
        * **Utilize Public Transit Apps:** Use government-authorized transport apps and note down vehicle registration details before boarding.
        * **Distress Signal Hotkeys:** Set up the "SOS/Emergency" button shortcut on your smartphone. (Typically pressing the power button 5 times notifies emergency contacts with your location).
        * **Stay in Well-lit Zones:** Avoid poorly lit or isolated pathways. If walking alone, walk facing oncoming traffic so vehicles cannot pull up behind you unnoticed.
        """)
        
    with tab_digital:
        st.markdown("""
        * **Secure Social Media Profiles:** Adjust privacy settings to ensure only trusted friends can view personal contact info, locations, and photos.
        * **Report Cyber Harassment:** Cyberbullying, stalking, or morphing of photos should be reported immediately to the national portal: **[cybercrime.gov.in](https://cybercrime.gov.in)** or local Cyber Police cells.
        * **Two-Factor Authentication (2FA):** Turn on 2FA on WhatsApp, email, and social accounts to prevent identity theft.
        * **Phishing awareness:** Avoid clicking on unsolicited links promising jobs, awards, or gifts which request personal data.
        """)
        
    with tab_work:
        st.markdown("""
        * **Understand POSH Act:** The *Prevention of Sexual Harassment (POSH) Act, 2013* mandates that every organization with 10+ employees must establish an **Internal Complaints Committee (ICC)**.
        * **Log incidents:** If you face discomfort or harassment, keep a log of dates, times, statements, and any supportive digital evidence (emails, chat logs).
        * **She-Box Portal:** You can also file sexual harassment complaints directly to the central ministry using the **SHe-Box** online portal.
        """)
        
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    # 3. Legal Rights & Government Initiatives
    col_rights, col_gov = st.columns(2)
    
    with col_rights:
        st.markdown("### Know Your Legal Rights")
        st.markdown("""
        > **1. Right to Register a Zero FIR**
        > A victim can file an FIR at *any* police station, irrespective of where the crime occurred. The police must register it and later transfer it to the jurisdictional station.
        
        > **2. Right to Free Legal Aid**
        > Under the Legal Services Authorities Act, women are entitled to receive free legal counsel and assistance for court proceedings.
        
        > **3. Right against Sunset Arrest**
        > By law, a woman cannot be arrested after sunset (6 PM) and before sunrise (6 AM), except under exceptional circumstances and only with the written order of a judicial magistrate.
        
        > **4. Right to Confidentiality**
        > Under Section 228A of the IPC, printing or publishing the name or any details that reveal the identity of a victim of sexual crimes is a punishable offense.
        """)
        
    with col_gov:
        st.markdown("### Government Initiatives")
        st.markdown("""
        * **Nirbhaya Fund:** A dedicated multi-crore national fund launched to support government and NGO initiatives focused on improving safety infrastructure, like CCTV installations, police patrol vans, and helplines.
        * **Safe City Project:** Integrated safety programs implemented across major metropolitan cities (like Delhi, Mumbai, Bengaluru, Hyderabad, Kolkata) establishing smart surveillance systems, women police patrol squads (Pink Police), and public lighting systems.
        * **Sakhi One-Stop Centres:** Central government-sponsored centers offering medical aid, police assistance, psycho-social counseling, and legal support under a single roof to women affected by violence.
        """)

if __name__ == "__main__":
    show_awareness_page()
