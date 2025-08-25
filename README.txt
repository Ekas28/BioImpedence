
Files generated:
- simulated_impedance_data.csv : /mnt/data/hydration_project/simulated_impedance_data.csv
- tbw_ridge_model.joblib : /mnt/data/hydration_project/tbw_ridge_model.joblib
- app_fastapi.py : FastAPI inference app (place in same folder as joblib)
- dashboard_streamlit.py : Streamlit demo (uses simulated_impedance_data.csv)

How to run (locally):
1) Install Python 3.10+ and create a virtualenv.
   python -m venv venv
   source venv/bin/activate   (Windows: venv\Scripts\activate)

2) Install dependencies:
   pip install pandas scikit-learn joblib fastapi uvicorn streamlit

3) To run FastAPI (in folder with tbw_ridge_model.joblib and app_fastapi.py):
   uvicorn app_fastapi:app --reload --port 8000

   Example POST:
   curl -X POST "http://127.0.0.1:8000/infer" -H "Content-Type: application/json" -d '{"height_cm":170,"weight_kg":70,"age_years":30,"sex":"F","impedance_ohm":520,"phase_deg":-12}'

4) To run Streamlit dashboard (in folder with simulated_impedance_data.csv and dashboard_streamlit.py):
   streamlit run dashboard_streamlit.py

Notes:
- The dataset is simulated for demo and presentation only.
- Model is a simple Ridge regression fit on simulated data; for real use calibrate with clinical reference.
- I saved files under /mnt/data/hydration_project
