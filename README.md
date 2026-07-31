# An AI-powered intent detection engine

---


# What It Does

Ingests 25 signals across 5 categories per company

Predicts buying intent probability using XGBoost

Ranks companies into Hot / Warm / Lukewarm / Cold tiers

Returns the top buying signals and missing signals per company

Recommends a specific sales action per tier

Serves everything via a FastAPI REST endpoint

Visualises results on a Streamlit dashboard with a live gauge

---


# Step 2 — Start the API 

bash cd api

pip install -r requirements.txt

uvicorn main:app --reload

Start the dashboard (VS Code)

bash cd frontend

pip install streamlit plotly requests

streamlit run app.py

----

# Author

Danish Zulfiqar

----
