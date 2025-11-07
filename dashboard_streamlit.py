
# import streamlit as st
# import pandas as pd
# import requests
# st.set_page_config(layout="wide")
# st.title("Hydration Monitoring - Demo Dashboard")
# df = pd.read_csv("simulated_impedance_data.csv", parse_dates=['timestamp'])
# sub = st.selectbox("Choose subject", df['subject_id'].unique())
# patient_df = df[df['subject_id']==sub].sort_values('timestamp')
# st.write("Patient info (simulated):")
# st.table(patient_df[['subject_id','height_cm','weight_kg','age_years','sex']].drop_duplicates().iloc[0])
# st.line_chart(patient_df.set_index('timestamp')[['hydration_pct_true','hydration_pct_pred']])
# st.write("Latest measurement:")
# latest = patient_df.sort_values('timestamp').iloc[-1]
# st.json({
#     "timestamp": str(latest['timestamp']),
#     "impedance_ohm": float(latest['impedance_ohm']),
#     "phase_deg": float(latest['phase_deg']),
#     "hydration_pct_pred": float(latest['hydration_pct_pred']),
#     "hydration_pct_true": float(latest['hydration_pct_true'])
# })
# st.write("You can run a local FastAPI inference server (see instructions) and use the /infer endpoint to get predictions for new measurements.")



import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="CKD Hydration Level Detection", layout="wide")

st.title("💧 CKD Hydration Level Detection")

# Left = input, Right = results
col1, col2 = st.columns(2)

with col1:
    st.subheader("Patient Details")
    height = st.number_input("Height (cm)", 140, 200, 165)
    weight = st.number_input("Weight (kg)", 30, 150, 60)
    age = st.number_input("Age (years)", 1, 100, 40)
    sex = st.selectbox("Sex", ["F", "M"])

    st.subheader("Upload Sensor CSV")
    csv_file = st.file_uploader("Upload impedance data file", type=["csv"])

    if csv_file is not None:
        df = pd.read_csv(csv_file)

        # Automatically detect columns
        df.columns = [c.strip() for c in df.columns]
        
        # Convert to numeric
        df['Impedance'] = pd.to_numeric(df['Impedance'], errors='coerce')
        df['Phase'] = pd.to_numeric(df['Phase'], errors='coerce')

        # Drop NaN rows
        df.dropna(subset=['Impedance', 'Phase'], inplace=True)

        # Take average impedance & phase
        avg_impedance = df['Impedance'].mean()
        avg_phase = df['Phase'].mean()

        st.write(f"📊 **Average Impedance:** {avg_impedance:.2f} Ω")
        st.write(f"📊 **Average Phase:** {avg_phase:.2f}°")

        if st.button("Predict Hydration"):
            payload = {
                "height_cm": height,
                "weight_kg": weight,
                "age_years": age,
                "sex": sex,
                "impedance_ohm": avg_impedance,
                "phase_deg": avg_phase
            }
            API_URL = "https://bioimpedence.onrender.com/infer"
            res = requests.post(API_URL, json=payload)

            if res.status_code == 200:
                result = res.json()
                hydration_pct = result['hydration_pct']
                tbw = result['tbw_l']

                with col2:
                    st.subheader("Results")
                    st.metric(label="Hydration Percentage", value=f"{hydration_pct}%")
                    st.metric(label="Total Body Water", value=f"{tbw} L")

                    if hydration_pct < 50:
                        st.error("⚠ Dehydrated")
                    elif hydration_pct <= 65:
                        st.success("✅ Hydration in Normal Range")
                    else:
                        st.warning("💧 Overhydrated")
            else:
                st.error("Error in prediction API call")



