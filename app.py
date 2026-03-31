import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="SRCS Race Hub",
    page_icon="🏁",
    layout="wide"
)

LOGO = Path("assets/SRCS.png")

# Sidebar branding
with st.sidebar:
    if LOGO.exists():
        st.image(str(LOGO), use_container_width=True)

pages = {
    "HOME": [
        st.Page("pages/Home.py", title="Home", icon="🏠"),
    ],

    "RACE HUB": [
        st.Page("pages/0_Overview.py", title="Overview", icon="📊"),
        st.Page("pages/2_Results_Center.py", title="Results Center", icon="🏁"),
        st.Page("pages/3_Lap_Time_Lab.py", title="Lap Time Lab", icon="⏱️"),
        st.Page("pages/4_Position_Tracker.py", title="Position Tracker", icon="📍"),
    ],

    "PERFORMANCE": [
        st.Page("pages/5_Driver_Analyzer.py", title="Driver Analyzer", icon="👤"),
        st.Page("pages/10_Driver_Pace_Ranking.py", title="Driver Pace Ranking", icon="⚡"),
        st.Page("pages/11_Team_Pace_Ranking.py", title="Team Pace Ranking", icon="🏁"),
        st.Page("pages/6_Team_Battle.py", title="Team Battle", icon="⚔️"),
        st.Page("pages/2_Race_Analysis.py", title="Race Analysis", icon="⏱️"),
        st.sidebar.page_link("pages/5_Strategy_Analyzer.py", label="Strategy Analyzer", icon="🧠"),
    ],

    "STEWARDING": [
        st.Page("pages/7_Incident_Center.py", title="Incident Center", icon="⚠️"),
    ],

    "SEASON": [
        st.Page("pages/1_Championship_Dashboard.py", title="Championship Dashboard", icon="👤"), 
        st.Page("pages/8_Awards.py", title="Awards", icon="🏆"),
        st.Page("pages/9_Season_Impact.py", title="Season Impact", icon="📈"),
        st.Page("pages/12_Circuit_Guide.py", title="Circuit Guide", icon="🛣️"),
        st.Page("pages/5_Race_Archive.py", title="Race Archive", icon="📚"),
    ],
}

pg = st.navigation(pages)
pg.run()
