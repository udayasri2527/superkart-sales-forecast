import os
import requests
import pandas as pd
import streamlit as st

# Backend reached through the Docker network by its container name
BACKEND_URL = os.getenv("BACKEND_URL", "http://superkart-backend:7860")

st.set_page_config(page_title="SuperKart Sales Forecast", page_icon="🛒", layout="centered")
st.title("🛒 SuperKart Sales Forecasting")
st.write("Predict the total sales revenue of a product in a SuperKart store.")

online_tab, batch_tab = st.tabs(["Online prediction", "Batch prediction"])

with online_tab:
    st.subheader("Product details")
    col1, col2 = st.columns(2)
    with col1:
        product_weight = st.number_input("Product weight", min_value=0.0, max_value=50.0, value=12.66, step=0.01)
        product_mrp = st.number_input("Product MRP", min_value=0.0, max_value=500.0, value=117.08, step=0.01)
        product_allocated_area = st.number_input("Allocated display area (ratio)", min_value=0.0, max_value=1.0,
                                                 value=0.027, step=0.001, format="%.3f")
    with col2:
        product_sugar_content = st.selectbox("Sugar content", ["Low Sugar", "Regular", "No Sugar"])
        product_id_char = st.selectbox("Product group (Product Id prefix)", ["FD", "DR", "NC"],
                                       help="FD = Food, DR = Drinks, NC = Non-consumables")
        product_type_category = st.selectbox("Product type category", ["Perishables", "Non Perishables"])

    st.subheader("Store details")
    col3, col4 = st.columns(2)
    with col3:
        store_size = st.selectbox("Store size", ["Small", "Medium", "High"])
        store_location_city_type = st.selectbox("City type", ["Tier 1", "Tier 2", "Tier 3"])
    with col4:
        store_type = st.selectbox("Store type", ["Supermarket Type1", "Supermarket Type2",
                                                 "Departmental Store", "Food Mart"])
        store_age_years = st.number_input("Store age (years)", min_value=0, max_value=100, value=16, step=1)

    if st.button("Predict sales", type="primary"):
        payload = {
            "Product_Weight": product_weight,
            "Product_Sugar_Content": product_sugar_content,
            "Product_Allocated_Area": product_allocated_area,
            "Product_MRP": product_mrp,
            "Store_Size": store_size,
            "Store_Location_City_Type": store_location_city_type,
            "Store_Type": store_type,
            "Product_Id_char": product_id_char,
            "Store_Age_Years": store_age_years,
            "Product_Type_Category": product_type_category,
        }
        try:
            response = requests.post(f"{BACKEND_URL}/v1/predict", json=payload, timeout=30)
            if response.status_code == 200:
                st.success(f"Predicted product-store sales: **{response.json()['Predicted Sales']:,.2f}**")
            else:
                st.error(f"API error {response.status_code}: {response.text}")
        except requests.exceptions.RequestException as e:
            st.error(f"Could not reach the backend at {BACKEND_URL}: {e}")

with batch_tab:
    st.subheader("Upload a CSV for batch prediction")
    st.caption("Required columns: Product_Weight, Product_Sugar_Content, Product_Allocated_Area, Product_MRP, "
               "Store_Size, Store_Location_City_Type, Store_Type, Product_Id_char, Store_Age_Years, "
               "Product_Type_Category")
    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])
    if uploaded_file is not None and st.button("Predict batch", type="primary"):
        try:
            response = requests.post(f"{BACKEND_URL}/v1/predictbatch",
                                     files={"file": uploaded_file.getvalue()}, timeout=120)
            if response.status_code == 200:
                uploaded_file.seek(0)
                result = pd.read_csv(uploaded_file)
                result["Predicted_Sales"] = [response.json()[str(i)] for i in range(len(result))]
                st.dataframe(result)
                st.metric("Total predicted sales", f"{result['Predicted_Sales'].sum():,.2f}")
                st.download_button("Download predictions", result.to_csv(index=False),
                                   file_name="superkart_predictions.csv", mime="text/csv")
            else:
                st.error(f"API error {response.status_code}: {response.text}")
        except requests.exceptions.RequestException as e:
            st.error(f"Could not reach the backend at {BACKEND_URL}: {e}")
