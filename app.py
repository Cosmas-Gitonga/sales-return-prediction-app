import os
import time
from typing import Any, Dict, Tuple

import requests
import streamlit as st

# -----------------------------------------------------------------------------
# App configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Sales Return Prediction",
    page_icon="↩️",
    layout="wide",
    initial_sidebar_state="expanded",
)

MODEL_NAME = "workspace.default.sales_return_prediction_sklearn"
MODEL_VERSION = "2"
DEFAULT_ENDPOINT = "sales_return_prediction_sklearn"

REGIONS = [
    "Coast",
    "Eastern",
    "North Eastern",
    "Nairobi",
    "Western",
    "Rift Valley",
    "Central",
    "Rift-valley",
]
CATEGORIES = [
    "Food Staples",
    "Beverages",
    "Household",
    "Personal Care",
    "Dairy",
    "Bakery",
    "Baby Care",
    "Stationery",
]
PAYMENT_METHODS = ["Airtel Money", "Cash", "Bank Transfer", "M-pesa", "Card"]
CHANNELS = ["Call Centre", "Online", "In-store", "Mobile App"]
CUSTOMER_SEGMENTS = ["Loyalty Member", "Student", "Wholesale", "Retail", "Corporate"]
DELIVERY_STATUSES = ["Delivered", "Pending", "Cancelled", "Returned"]

EXAMPLES = {
    "Eastern wholesale order": {
        "quantity": 4,
        "unit_price": 179.26,
        "discount_pct": 0.0,
        "rating": 3.0,
        "region": "Eastern",
        "category": "Food Staples",
        "payment_method": "Airtel Money",
        "channel": "Online",
        "customer_segment": "Wholesale",
        "delivery_status": "Delivered",
    },
    "Nairobi student order": {
        "quantity": 1,
        "unit_price": 207.0,
        "discount_pct": 0.0,
        "rating": 5.0,
        "region": "Nairobi",
        "category": "Beverages",
        "payment_method": "Airtel Money",
        "channel": "Mobile App",
        "customer_segment": "Student",
        "delivery_status": "Delivered",
    },
}

# -----------------------------------------------------------------------------
# Styling
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    :root {
        --navy: #0b1f4d;
        --blue: #2f6fed;
        --blue-2: #4b7ff3;
        --soft-blue: #eef5ff;
        --line: #dfe7f3;
        --text: #102046;
        --muted: #62708b;
        --green: #159447;
        --soft-green: #effaf3;
        --amber: #c98200;
        --soft-amber: #fff8e9;
        --red: #c83e3e;
        --soft-red: #fff2f2;
    }

    .stApp {
