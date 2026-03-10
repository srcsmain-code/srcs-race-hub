import streamlit as st

st.set_page_config(
    page_title="SRCS Race Hub",
    page_icon="🏁",
    layout="wide"
)

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
        st.Page("pages/6_Team_Battle.py", title="Team Battle", icon="⚔️"),
    ],

    "STEWARDING": [
        st.Page("pages/7_Incident_Center.py", title="Incident Center", icon="⚠️"),
    ],

    "SEASON": [
        st.Page("pages/8_Awards.py", title="Awards", icon="🏆"),
        st.Page("pages/9_Season_Impact.py", title="Season Impact", icon="📈"),
        st.Page("pages/5_Race_Archive.py", title="Race Archive", icon="📚"),
    ],
}

pg = st.navigation(pages)
pg.run()
