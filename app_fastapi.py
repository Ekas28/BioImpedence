
# from fastapi import FastAPI
# import joblib
# import pydantic
# import numpy as np

# app = FastAPI()
# model = joblib.load("tbw_ridge_model.joblib")

# class Measurement(pydantic.BaseModel):
#     height_cm: float
#     weight_kg: float
#     age_years: int
#     sex: str
#     impedance_ohm: float
#     phase_deg: float

# @app.post("/infer")
# def infer(m: Measurement):
#     H2_div_R = (m.height_cm**2) / m.impedance_ohm
#     sex_M = 1 if m.sex=='M' else 0
#     X = np.array([[H2_div_R, m.weight_kg, m.age_years, sex_M, m.phase_deg]])
#     tbw = float(model.predict(X)[0])
#     hydration_pct = tbw / m.weight_kg * 100
#     return {"tbw_l": round(tbw,2), "hydration_pct": round(hydration_pct,2)}


from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="CKD Hydration Level API")

class HydrationRequest(BaseModel):
    height_cm: float
    weight_kg: float
    age_years: int
    sex: str
    impedance_ohm: float
    phase_deg: float = None

@app.post("/infer")
def infer(data: HydrationRequest):
    # Encode sex
    sex_encoded = 1 if data.sex.upper() == "M" else 0

    # -------------------------
    # Tuned parameters for dry-skin arm measurement
    # -------------------------
    ARM_TO_BODY_FACTOR = 0.18  # reduced so effective resistance is smaller
    WATER_INTAKE_BOOST = 1.05  # +5% boost for recent water intake
    BIAS_TERM = 28.0           # bias increased from 22.5 to 28 for realistic TBW

    # Convert arm impedance to estimated whole-body
    effective_R = data.impedance_ohm * ARM_TO_BODY_FACTOR

    # Prevent divide-by-zero
    if effective_R <= 0:
        return {"error": "Invalid impedance value"}

    # TBW formula (adapted Lukaski-type)
    tbw = (0.372 * (data.height_cm ** 2) / effective_R) \
          + (0.142 * data.weight_kg) \
          + (0.069 * sex_encoded) \
          - (0.0015 * data.age_years) \
          + BIAS_TERM

    # Apply water intake boost
    tbw *= WATER_INTAKE_BOOST

    # Hydration percentage
    hydration_pct = (tbw / data.weight_kg) * 100

    # Clamp to realistic human range
    hydration_pct = max(35, min(hydration_pct, 75))

    # Status classification
    if hydration_pct < 50:
        status = "Dehydrated"
    elif hydration_pct <= 65:
        status = "Normal"
    else:
        status = "Overhydrated"

    return {
        "tbw_l": round(tbw, 2),
        "hydration_pct": round(hydration_pct, 2),
        "status": status,
        "effective_R_used": round(effective_R, 2)
    }




