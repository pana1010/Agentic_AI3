import streamlit as st
from dotenv import load_dotenv
from streamlit_lottie import st_lottie
import requests

# Load environment (GROQ_API_KEY handled in chatbot_core.py)
load_dotenv()

# Import backend
from chatbot_core import (
    recommend_chain,
    analyze_recommendations,
    get_appliance_suggestions,
    get_renewable_options,
    estimate_kwh_savings,
    calculate_co2_savings,
)

# ─── Page Config & Theme ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="Energy Conservation Chatbot",
    page_icon="⚡",
    layout="wide",
)

# Ensure ~/.streamlit/config.toml has your theme:
# [theme]
# primaryColor = "#b9b9cb"
# backgroundColor = "#193447"
# secondaryBackgroundColor = "#536b6b"
# textColor = "#ffffff"

# Custom CSS for contrast
st.markdown("""
    <style>
      body, .stApp { background-color: #193447; color: #ffffff; }
      .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: #2a3b4d; color: #ffffff;
      }
      .stButton>button {
        background-color: #b9b9cb; color: #193447;
        border-radius: 6px; padding: 0.5rem 1rem;
      }
      .stTabs [data-baseweb="tab-list"] { background-color: #536b6b; }
      .stTabs [data-baseweb="tab"] { color: #ddd; }
      .stTabs [aria-selected="true"] {
        background-color: #44475a; color: #ffffff;
      }
    </style>
""", unsafe_allow_html=True)

# ─── Load Lottie Animation ───────────────────────────────────────────────────────
def load_lottie(url: str):
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return None

lottie_energy = load_lottie("https://lottie.host/8e45add1-58b7-4e22-b8db-ec35f51fbb82/Vh8JqESc2g.json")

# ─── Header ─────────────────────────────────────────────────────────────────────
with st.container():
    col1, col2 = st.columns([1, 2])
    if lottie_energy:
        st_lottie(lottie_energy, height=200, key="energy_anim")
    st.markdown("## ⚡ Energy Conservation Chatbot")
    st.markdown(
        "Get personalized advice to save energy, recommend efficient appliances, "
        "and explore renewable options."
    )

# ─── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "💬 Recommendations",
    "🛠 Appliance Suggestions",
    "🌞 Renewable Options",
    "🌍 CO₂ Savings"
])

# ─── Tab 1: Recommendations ─────────────────────────────────────────────────────
with tab1:
    st.subheader("Your Personalized Energy Advice")
    user_type  = st.selectbox("User Type", ["Household", "Business"])
    appliances = st.text_area("Appliances in Use", placeholder="e.g., AC, Refrigerator, Heater...")
    concerns   = st.text_area("Energy Concerns", placeholder="e.g., High bill, eco-friendly...")
    location   = st.text_input("Location (optional)", placeholder="City or region...")

    if st.button("Generate Recommendations"):
        with st.spinner("Generating advice..."):
            recs = recommend_chain.invoke({
                "user_type": user_type,
                "appliances": appliances,
                "concerns": concerns,
                "location": location
            })
        st.success("✅ Here’s your advice:")
        st.markdown(recs)

        with st.expander("📊 Analysis & CO₂ Estimate"):
            analysis = analyze_recommendations(recs)
            st.markdown("**Analysis:**")
            st.write(analysis)

            kwh = estimate_kwh_savings(recs)
            co2 = calculate_co2_savings(kwh)
            st.metric("kWh Saved (monthly)", f"{co2['kWh Saved']} kWh")
            st.metric("CO₂ Saved (kg monthly)", f"{co2['CO₂ Saved (kg)']} kg")
            st.metric("CO₂ Saved (t yearly)", f"{co2['CO₂ Saved (t)'] * 12:.2f} t")

# ─── Tab 2: Appliance Suggestions ───────────────────────────────────────────────
with tab2:
    st.subheader("Optimize Your Appliances")
    app_input = st.text_area("Enter appliances to upgrade", placeholder="e.g., old fridge, bulbs...")
    if st.button("Suggest Alternatives"):
        with st.spinner("Finding efficient models..."):
            suggestions = get_appliance_suggestions(app_input)
        st.success("✅ Suggestions ready")
        st.markdown(suggestions)

# ─── Tab 3: Renewable Options ───────────────────────────────────────────────────
with tab3:
    st.subheader("Renewable Energy Recommendations")
    loc_input = st.text_input("Enter your Location", placeholder="City or region")
    usr_type  = st.selectbox("User Type", ["Household", "Business"], key="renew_tab")
    if st.button("Show Options"):
        with st.spinner("Analyzing renewables..."):
            opts = get_renewable_options(loc_input, usr_type)
        st.success("✅ Here are some options")
        st.markdown(opts)

# ─── Tab 4: CO₂ Savings Meter ───────────────────────────────────────────────────
with tab4:
    st.subheader("CO₂ Savings Calculator")
    kwh_manual = st.number_input("Enter monthly kWh saved", min_value=0.0, step=1.0)
    if st.button("Calculate CO₂ Saved"):
        co2m = calculate_co2_savings(kwh_manual)
        st.metric("CO₂ Saved (kg / month)", f"{co2m['CO₂ Saved (kg)']} kg")
        st.metric("CO₂ Saved (t / year)", f"{(co2m['CO₂ Saved (t)'] * 12):.2f} t")

# ─── Footer ─────────────────────────────────────────────────────────────────────
st.caption("Built with ❤️ for a greener future.")