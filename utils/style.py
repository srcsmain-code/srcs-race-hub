import streamlit as st

def apply_srcs_style():
    st.markdown("""
    <style>
    /* Main app spacing */
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }

    /* Headings */
    h1, h2, h3 {
        letter-spacing: 0.01em;
    }

    h1 {
        color: #FFFFFF;
        font-weight: 800;
    }

    h2, h3 {
        color: #C0C0C0;
        font-weight: 700;
    }

    /* Custom SRCS section labels */
    .srcs-section {
        color: #FFFFFF;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 0.6rem;
        margin-bottom: 0.6rem;
    }

    .srcs-note {
        color: #C0C0C0;
        font-size: 0.95rem;
    }

    /* Metric cards */
    div[data-testid="stMetric"] {
        background: linear-gradient(180deg, rgba(10,42,102,0.38) 0%, rgba(5,10,25,0.55) 100%);
        border: 1px solid rgba(192,192,192,0.18);
        padding: 12px 14px;
        border-radius: 14px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.18);
    }

    /* Dataframes and tables */
    div[data-testid="stDataFrame"] {
        border: 1px solid rgba(192,192,192,0.14);
        border-radius: 14px;
        overflow: hidden;
        box-shadow: 0 4px 10px rgba(0,0,0,0.12);
    }

    /* Charts */
    div[data-testid="stVegaLiteChart"],
    div[data-testid="stPlotlyChart"] {
        border: 1px solid rgba(192,192,192,0.14);
        border-radius: 14px;
        padding: 0.4rem;
        background: rgba(10,42,102,0.16);
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        border-right: 1px solid rgba(192,192,192,0.12);
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #FFFFFF;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 10px;
        border: 1px solid rgba(192,192,192,0.22);
    }

    /* Info/success/warning boxes softer */
    div[data-testid="stAlert"] {
        border-radius: 12px;
    }

    /* Hero panel utility */
    .srcs-hero {
        background: linear-gradient(135deg, #050A19 0%, #0A2A66 55%, #007BFF 100%);
        padding: 1.5rem 1.7rem;
        border-radius: 18px;
        border: 1px solid rgba(192,192,192,0.22);
        margin-bottom: 1rem;
        box-shadow: 0 6px 18px rgba(0,0,0,0.25);
    }

    .srcs-hero-title {
        color: #FFFFFF;
        font-size: 2.1rem;
        font-weight: 800;
        margin-bottom: 0.15rem;
    }

    .srcs-hero-subtitle {
        color: #C0C0C0;
        font-size: 1rem;
        margin-bottom: 0;
    }
    </style>
    """, unsafe_allow_html=True)
