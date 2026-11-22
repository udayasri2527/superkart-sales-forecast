import joblib
import pandas as pd
from flask import Flask, request, jsonify

# Initialize the Flask application
superkart_api = Flask("SuperKart Sales Forecaster")

# Load the serialized pipeline (preprocessing + model) once at start-up
model = joblib.load("superkart_model.joblib")

# Features expected by the model, in training order
FEATURES = [
    "Product_Weight", "Product_Sugar_Content", "Product_Allocated_Area", "Product_MRP",
    "Store_Size", "Store_Location_City_Type", "Store_Type", "Product_Id_char",
    "Store_Age_Years", "Product_Type_Category",
]
NUMERIC = ["Product_Weight", "Product_Allocated_Area", "Product_MRP", "Store_Age_Years"]


def prepare(df):
    """Validate columns and cast numeric features."""
    missing = [c for c in FEATURES if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required feature(s): {missing}")
    df = df[FEATURES].copy()
    df[NUMERIC] = df[NUMERIC].astype(float)
    return df


@superkart_api.get("/")
def home():
    """Health check"""
    return "Welcome to the SuperKart Sales Forecasting API!"


@superkart_api.post("/v1/predict")
def predict_sales():
    """Online inference for a single record sent as JSON."""
    try:
        record = request.get_json()
        input_df = prepare(pd.DataFrame([record]))
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    prediction = float(model.predict(input_df)[0])
    return jsonify({"Predicted Sales": round(prediction, 2)})


@superkart_api.post("/v1/predictbatch")
def predict_sales_batch():
    """Batch inference for a CSV file uploaded under the key 'file'."""
    if "file" not in request.files:
        return jsonify({"error": "Upload a CSV file under the key 'file'"}), 400
    try:
        input_df = prepare(pd.read_csv(request.files["file"]))
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    predictions = [round(float(p), 2) for p in model.predict(input_df)]
    # key = row index, value = predicted sales
    return jsonify(dict(zip(input_df.index.astype(str).tolist(), predictions)))


if __name__ == "__main__":
    superkart_api.run(host="0.0.0.0", port=7860, debug=False)
