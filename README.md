```markdown
# ⚡ Delhi SLDC Predictive Load Management Terminal
**Keeping Delhi’s grid stable and efficient with AI-driven prescriptive analytics.**

![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-Live-FF4B4B?style=for-the-badge&logo=streamlit)
![Scikit-Learn](https://img.shields.io/badge/scikit--learn-Machine%20Learning-F7931E?style=for-the-badge&logo=scikit-learn)
![Open-Meteo](https://img.shields.io/badge/Open--Meteo-Live%20Telemetry-00B2E2?style=for-the-badge)

> **Origin '26 Hackathon** | Track: AI & Machine Learning | Team: **Red_Eyes**

---

## 🚨 The Challenge
Delhi’s power grid faces extreme volatility, with summer peaks regularly exceeding **8,000+ MW** and setting new records. Current State Load Despatch Centre (SLDC) dispatch systems often rely on lagging, manual forecasts. This leads to severe grid instability, frequent overload trip risks on specific 66kV/33kV substations, and exorbitant financial penalties on the spot market.

## 💡 Our Solution
A production-ready **Predictive Load Management Terminal**. Our system transforms environmental telemetry directly into prescriptive grid dispatch action in under 1 second. 

We built a live SCADA-style Streamlit dashboard powered by a highly optimized Random Forest AI that forecasts the 24-hour demand curve based on real-time weather and historical diurnal load patterns.

---

## ✨ Core Features

*   🌍 **Live Open-Meteo Telemetry Ingestion:** Automated streaming of real-time Delhi meteorological forecasts (temp & humidity) with zero API key constraints and built-in cache fallbacks.
*   🧠 **Advanced Feature Engineering:** Calculates critical non-linear Air Conditioning (AC) sensitivity markers, including the **National Weather Service Heat Index** and **Cooling Degree Days (CDD)**.
*   📊 **AI Forecasting Engine:** A high-performance, `joblib`-compressed Random Forest Regressor trained on Delhi historical load dynamics, generating real-time 24H net demand curves.
*   ⚡ **Feeder-Level Stress Testing:** Granular load distribution across 5 regional DISCOM zones (BRPL, TPDDL, BYPL West, BYPL East, NDMC) with 66kV/33kV substation overload trip warnings.
*   🔋 **Multi-DER & BESS Grid Balancing:** Live simulation suite for daytime rooftop solar offset, evening BESS battery discharge, and overnight commercial EV fleet charging.
*   🔥 **1-Click Crisis Scenarios:** Interactive control panel allowing dispatchers to stress-test the model live (e.g., +5°C July Heatwave Anomaly, Monsoon Cloud Shock) to calculate real-time spot-market financial exposure (₹).

---

## 🏗️ Production Tech Stack

*   **Core ML:** Python 3.11, `scikit-learn`, `joblib`
*   **Data Engineering:** `pandas`, `numpy`
*   **Live Telemetry:** Open-Meteo REST API
*   **Frontend UI:** `streamlit` (Custom CSS SCADA Terminal)
*   **Deployment:** Git, GitHub, Streamlit Community Cloud

---

## 🚀 Live Demo
Access the live deployment here: **[Insert Your Streamlit URL Here]**

---

## 💻 Local Installation & Setup

Want to run the terminal locally? Follow these steps:

**1. Clone the repository**
```bash
git clone [https://github.com/your-username/delhi-sldc-terminal.git](https://github.com/your-username/delhi-sldc-terminal.git)
cd delhi-sldc-terminal

```

**2. Install dependencies**

```bash
pip install -r requirements.txt

```

**3. Train & compress the ML model**
*This script optimizes the Random Forest model and compresses it into a tiny `.pkl` file for lightweight deployment.*

```bash
python train_model.py

```

**4. Launch the SCADA Terminal**

```bash
streamlit run app.py

```

*The dashboard will automatically open in your browser at `http://localhost:8501`.*

---

## 👥 The Team (Red_Eyes)

* **Abhik Adhikary** (Data & AI Modeling) — *Data pipeline, cyclical feature extraction, Heat Index modeling, and Random Forest training.*
* **Nagaruthik Muddisetty** (Dashboard & Telemetry) — *Streamlit SCADA terminal UI, live Open-Meteo integration, and capacity alerts.*
* **Piyush Kumar** (Dispatch Logic & Deployment) — *Feeder drill-down, multi-DER balancing (Solar/BESS/EV), dispatch advisory, and cloud deployment.*

```

```