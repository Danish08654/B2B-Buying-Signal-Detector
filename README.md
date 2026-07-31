# B2B Buy detection system

An AI-powered intent detection engine that analyses company signals across different field and engagement to predict which companies are in an active buying.

---

# What It Does

1) Ingests 25 signals across 5 categories per company

2) Predicts buying intent probability using XGBoost

3) Ranks companies into Hot / Warm / Lukewarm / Cold tiers

4) Returns the top buying signals and missing signals per company

5) Recommends a specific sales action per tier

6) Serves everything via a FastAPI REST endpoint

7) Visualises results on a Streamlit dashboard with a live gauge

---

# Tech Stack

Python

Groq API

LangChain

Streamlit

-----


# Use Cases

Business Intelligence

Company Analytics

Self-Service Data Querying

Enterprise Reporting

Data Exploration

---

# Start 

bash cd api

pip install -r requirements.txt

uvicorn main:app --reload

bash cd frontend

pip install streamlit plotly requests

streamlit run app.py

----

# Author

# Danish Zulfiqar |AI Engineer

----
