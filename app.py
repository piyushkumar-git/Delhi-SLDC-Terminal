import streamlit as st
import pandas as pd
import numpy as np
import joblib
import requests

# -----------------------------
# PAGE CONFIGURATION
# -----------------------------
st.set_page_config(
    page_title="Delhi Power AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS strictly for layout padding and the Live badge (No color overrides)
st.markdown("""
    <style>
    /* Fix top padding to prevent the ticker from being hidden */
    .block-container { padding-top: 2.5rem !important; padding-bottom: 1rem !important; }
    
    /* Sidebar Compacting */
    section[data-testid="stSidebar"] .stMarkdown h3 {
        font-size: 0.9rem !important;
        margin-bottom: 8px !important;
        padding-top: 10px !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    section[data-testid="stSidebar"] .stSlider { 
        margin-bottom: -10px !important; 
    }
    section[data-testid="stSidebar"] .stButton {
        margin-top: 6px !important;
        margin-bottom: 6px !important;
    }
    section[data-testid="stSidebar"] .stButton > button { 
        margin-top: 0px !important; 
    }
    
    /* Typography sizing (keeps native colors) */
    [data-testid="stMetricValue"] { font-size: 2.1rem !important; font-weight: 700; }
    [data-testid="stMetricLabel"] { font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; font-size: 0.75rem !important; }
    
    /* Live Badge */
    .live-badge { background-color: #EF4444; color: white; padding: 2px 10px; border-radius: 4px; font-size: 0.70rem; font-weight: 700; letter-spacing: 1px; animation: pulse 2s infinite; vertical-align: middle; margin-left: 10px; }
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
    
    /* Hardware-style ticker utilizing native translucent backgrounds */
    .top-ticker { font-family: 'SF Mono', 'Courier New', monospace; font-size: 0.85rem; padding: 10px 15px; margin-bottom: 1.5rem; display: flex; justify-content: space-between; border-radius: 6px; border: 1px solid rgba(128, 128, 128, 0.2); background-color: rgba(128, 128, 128, 0.05); }
    </style>
""", unsafe_allow_html=True)

# -----------------------------
# SESSION STATE (For Scenarios)
# -----------------------------
if 'solar_val' not in st.session_state: st.session_state.solar_val = 300
if 'bess_val' not in st.session_state: st.session_state.bess_val = 200
if 'ev_val' not in st.session_state: st.session_state.ev_val = 400
if 'heat_val' not in st.session_state: st.session_state.heat_val = False

def set_scenario(solar, bess, ev, heat):
    st.session_state.solar_val = solar
    st.session_state.bess_val = bess
    st.session_state.ev_val = ev
    st.session_state.heat_val = heat

# -----------------------------
# DATA PIPELINE & MATH
# -----------------------------
def calculate_heat_index(temp_c, humidity):
    temp_f = (temp_c * 9/5) + 32
    hi_f = 0.5 * (temp_f + 61.0 + ((temp_f - 68.0) * 1.2) + (humidity * 0.094))
    if hi_f >= 80:
        hi_f = -42.379 + 2.04901523*temp_f + 10.14333127*humidity - 0.22475541*temp_f*humidity - 0.00683783*temp_f**2 - 0.05481717*humidity**2 + 0.00122874*temp_f**2*humidity + 0.00085282*temp_f*humidity**2 - 0.00000199*temp_f**2*humidity**2
    return (hi_f - 32) * 5/9

@st.cache_data(ttl=3600)
def get_live_forecast():
    latitude, longitude = 28.6139, 77.2090
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&hourly=temperature_2m,relative_humidity_2m&timezone=Asia%2FKolkata&forecast_days=2"
    try:
        response = requests.get(url)
        data = response.json()
        df = pd.DataFrame({
            "timestamp": pd.to_datetime(data["hourly"]["time"]),
            "temperature_C": data["hourly"]["temperature_2m"],
            "humidity": data["hourly"]["relative_humidity_2m"]
        })
        df = df[df["timestamp"] >= pd.Timestamp.now()].head(24)
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['is_weekend'] = df['day_of_week'].apply(lambda x: 1 if x >= 5 else 0)
        return df
    except:
        now = pd.Timestamp.now().floor('H')
        df = pd.DataFrame({
            "timestamp": [now + pd.Timedelta(hours=i) for i in range(24)],
            "temperature_C": np.random.uniform(35, 45, 24),
            "humidity": np.random.uniform(30, 60, 24)
        })
        df['hour'], df['day_of_week'] = df['timestamp'].dt.hour, df['timestamp'].dt.dayofweek
        df['is_weekend'] = df['day_of_week'].apply(lambda x: 1 if x >= 5 else 0)
        return df

GRID_CAPACITY = 8500
forecast = get_live_forecast()

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.markdown("### ☀️ Renewables (Day)")
solar_output_mw = st.sidebar.slider("Distributed Solar Injection (MW)", 0, 2000, key="solar_val", step=50, label_visibility="collapsed")

st.sidebar.markdown("### 🔋 Peak Shaving (Evening)")
battery_discharge_mw = st.sidebar.slider("BESS Discharge (MW)", 0, 1500, key="bess_val", step=50, label_visibility="collapsed")

st.sidebar.markdown("### 🚗 EV Fleet Load (Night)")
ev_charging_mw = st.sidebar.slider("Overnight EV Charging (MW)", 0, 2000, key="ev_val", step=50, label_visibility="collapsed")

st.sidebar.markdown("### 🌪️ Stress Testing")
heatwave_mode = st.sidebar.toggle("🔥 +5°C Heatwave Anomaly", key="heat_val")

st.sidebar.markdown("<br>", unsafe_allow_html=True)
st.sidebar.markdown("### 🎬 1-Click Demo Scenarios")
st.sidebar.button("🌱 Scenario A: Normal Spring Day", on_click=set_scenario, args=(400, 200, 200, False), use_container_width=True)
st.sidebar.button("🔥 Scenario B: July Heatwave Crisis", on_click=set_scenario, args=(50, 500, 600, True), use_container_width=True)
st.sidebar.button("⛈️ Scenario C: Monsoon Cloud Shock", on_click=set_scenario, args=(0, 300, 400, False), use_container_width=True)

if heatwave_mode:
    forecast['temperature_C'] += 5.0  

# Calculate Apparent Temps & CDD
forecast['heat_index'] = forecast.apply(lambda row: calculate_heat_index(row['temperature_C'], row['humidity']), axis=1)
forecast['cdd'] = np.maximum(0, forecast['temperature_C'] - 18)
max_hi = forecast['heat_index'].max()
total_cdd = forecast['cdd'].sum()

# -----------------------------
# MODEL INFERENCE
# -----------------------------
try:
    model = joblib.load("delhi_power_demand_model.pkl")
    features = forecast[['hour', 'day_of_week', 'is_weekend', 'temperature_C', 'humidity']]
    raw_predictions = model.predict(features)
except:
    raw_predictions = forecast["temperature_C"] * 150 + np.random.normal(1000, 200, len(forecast))

forecast["predicted_demand_MW"] = raw_predictions
forecast.loc[(forecast["hour"] >= 7) & (forecast["hour"] <= 17), "predicted_demand_MW"] -= solar_output_mw
forecast.loc[(forecast["hour"] >= 18) & (forecast["hour"] <= 23), "predicted_demand_MW"] -= battery_discharge_mw
forecast.loc[(forecast["hour"] >= 22) | (forecast["hour"] <= 4), "predicted_demand_MW"] += ev_charging_mw
forecast["predicted_demand_MW"] = forecast["predicted_demand_MW"].clip(lower=1500)

# -----------------------------
# TOP TICKER BAR
# -----------------------------
current_time = pd.Timestamp.now(tz='Asia/Kolkata').strftime('%Y-%m-%d %H:%M:%S IST')
grid_freq = np.random.uniform(49.95, 50.05)
st.markdown(f"""
    <div class="top-ticker">
        <span>SYS_TIME: {current_time}</span>
        <span>GRID_FREQ: {grid_freq:.2f} Hz</span>
        <span>MAX_HEAT_INDEX: {max_hi:.1f}°C</span>
        <span>24H_CDD: {total_cdd:.1f}</span>
    </div>
""", unsafe_allow_html=True)

# -----------------------------
# HEADER & EXPORT
# -----------------------------
col_h1, col_h2 = st.columns([4, 1])
with col_h1:
    st.markdown('<h2>⚡ Delhi Power AI <span class="live-badge">LIVE</span></h2>', unsafe_allow_html=True)
    st.caption("AI-Based Electricity Demand Prediction System")
with col_h2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.download_button("📥 Export Report", data=forecast.to_csv(index=False).encode('utf-8'), file_name="delhi_power_forecast.csv", mime="text/csv", use_container_width=True)

if max_hi > 42.0 or heatwave_mode:
    st.error(f"🌡️ **Extreme Weather Alert:** Grid operating under severe apparent heat (Heat Index: {max_hi:.1f}°C). AC cooling loads compounding.")
st.divider()

# -----------------------------
# METRICS
# -----------------------------
peak_row = forecast.loc[forecast["predicted_demand_MW"].idxmax()]
peak_demand = peak_row["predicted_demand_MW"]
max_utilization = (peak_demand / GRID_CAPACITY) * 100
spot_market_exposure = max(0, peak_demand - 7500) * 10000 

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Projected Peak", f"{peak_demand:,.0f} MW", delta=f"{GRID_CAPACITY - peak_demand:,.0f} MW Reserve", delta_color="normal")
c2.metric("Peak Time", f"{peak_row['timestamp'].strftime('%H:%M')}")
c3.metric("Peak Utilization", f"{max_utilization:.1f}%", delta=f"{100 - max_utilization:.1f}% Margin", delta_color="inverse")
c4.metric("Spot Market Exposure", f"₹ {spot_market_exposure:,.0f}" if spot_market_exposure > 0 else "₹ 0")

if max_utilization >= 100:
    c5.metric("System Status", "OVERLOAD")
elif max_utilization >= 90:
    c5.metric("System Status", "WARNING")
else:
    c5.metric("System Status", "NORMAL")

# -----------------------------
# AUTOMATED DISPATCH ADVISORY
# -----------------------------
st.markdown("##### 📋 Automated Dispatch Advisory")
advisory_col1, advisory_col2, advisory_col3 = st.columns(3)
if peak_demand > 7800:
    with advisory_col1: st.error("**1. Spot Market Bidding**\n\nIssue advance buy bids on IEX DAM/RTM market for estimated shortfall before 12:00 PM gate closure.")
    with advisory_col2: st.warning("**2. Demand Response**\n\nTrigger automated peak-shaving incentives for industrial feeders in Okhla & Mayapuri to shed ~180 MW.")
    with advisory_col3: st.info("**3. BESS Readiness**\n\nLock battery discharge schedules to activate 30 minutes prior to projected peak time.")
else:
    with advisory_col1: st.success("**1. Merit Order Dispatch**\n\nBase-load thermal and bilateral PPA contracts sufficient. No spot procurement required.")
    with advisory_col2: st.success("**2. Feeder Integrity**\n\nAll regional lines operating within rated thermal margins.")
    with advisory_col3: st.info("**3. Storage Optimization**\n\nDirect off-peak renewables to BESS charging cycle.")

st.divider()

# -----------------------------
# CHARTS
# -----------------------------
col_chart1, col_chart2 = st.columns([1.3, 1])
with col_chart1:
    st.markdown("##### 📈 Net Load Curve (MW)")
    chart_data = forecast.copy()
    chart_data['Time'] = chart_data['timestamp'].dt.strftime('%H:%M')
    # Removed hardcoded colors so it uses native Streamlit defaults
    st.area_chart(chart_data.set_index("Time")[["predicted_demand_MW"]])

with col_chart2:
    st.markdown("##### 🎯 Historical Accuracy")
    try:
        eval_df = pd.read_csv("delhi_power_processed.csv").tail(24).copy()
        eval_df['Model Prediction'] = model.predict(eval_df[['hour', 'day_of_week', 'is_weekend', 'temperature_C', 'humidity']])
        eval_df = eval_df.rename(columns={'demand_MW': 'Actual Telemetry'})
        eval_df['Time'] = eval_df['timestamp'].astype(str).str.slice(11, 16)
        st.line_chart(eval_df.set_index("Time")[["Actual Telemetry", "Model Prediction"]])
    except:
        st.warning("Telemetry evaluation offline.")

st.divider()

# -----------------------------
# SUBSTATION & FEEDER DRILL-DOWN
# -----------------------------
st.markdown("##### 🔌 Substation & Feeder Drill-Down")
zones = {"South Delhi (BRPL)": 0.28, "North Delhi (TPDDL)": 0.22, "West Delhi (BYPL)": 0.25, "East Delhi (BYPL)": 0.15, "Central Delhi (NDMC)": 0.10}
feeders = {
    "South Delhi (BRPL)": [("66kV Vasant Kunj", 0.35, 3000), ("33kV Okhla Ind.", 0.40, 3200), ("33kV Saket Res.", 0.25, 2500)],
    "North Delhi (TPDDL)": [("66kV Rohini Sec 9", 0.50, 3500), ("33kV Narela Ind.", 0.50, 3600)],
    "West Delhi (BYPL)": [("66kV Janakpuri Grid", 0.55, 3800), ("33kV Punjabi Bagh", 0.45, 3300)],
    "East Delhi (BYPL)": [("66kV Laxmi Nagar", 0.60, 2900), ("33kV Mayur Vihar", 0.40, 2400)],
    "Central Delhi (NDMC)": [("66kV Connaught Place", 0.60, 2200), ("33kV Barakhamba", 0.40, 1800)]
}

selected_zone = st.selectbox("Select Regional DISCOM to inspect feeders:", list(zones.keys()), label_visibility="collapsed")
f_cols = st.columns(len(feeders[selected_zone]))
zone_total = peak_demand * zones[selected_zone]

for idx, (f_name, ratio, rated_mw) in enumerate(feeders[selected_zone]):
    f_load = zone_total * ratio
    loading_pct = (f_load / rated_mw) * 100
    with f_cols[idx]:
        st.markdown(f"**{f_name}**")
        st.write(f"Load: **{f_load:,.0f} MW** / {rated_mw} MW Limit")
        st.progress(min(loading_pct / 100, 1.0))
        if loading_pct > 90:
            st.error("Overload Trip Risk")
        else:
            st.success("Normal Loading")