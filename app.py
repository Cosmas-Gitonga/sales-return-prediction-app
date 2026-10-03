import os
import time
from typing import Any, Dict, Tuple

import requests
import streamlit as st

st.set_page_config(
    page_title="Sales Return Prediction",
    page_icon="↩️",
    layout="wide",
    initial_sidebar_state="expanded",
)

MODEL_NAME = "workspace.default.sales_return_prediction_sklearn"
MODEL_VERSION = "2"
DEFAULT_ENDPOINT = "sales_return_prediction_sklearn"

REGIONS = ["Coast", "Eastern", "North Eastern", "Nairobi", "Western", "Rift Valley", "Central", "Rift-valley"]
CATEGORIES = ["Food Staples", "Beverages", "Household", "Personal Care", "Dairy", "Bakery", "Baby Care", "Stationery"]
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

st.markdown(
    """
    <style>
    :root {
        --navy: #0b1f4d;
        --blue: #2f6fed;
        --soft-blue: #eef5ff;
        --line: #dfe7f3;
        --text: #102046;
        --green: #159447;
        --amber: #c98200;
        --red: #c83e3e;
    }

    .stApp {
        background: linear-gradient(180deg, #f7faff 0%, #ffffff 34%);
        color: var(--text);
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #15417e 0%, #0b2858 58%, #071f47 100%);
    }
    [data-testid="stSidebar"] * { color: #ffffff; }
    [data-testid="stSidebar"] .stRadio label { color: #e8efff !important; }
    [data-testid="stSidebar"] hr { border-color: rgba(255,255,255,.14); }

    #MainMenu, footer { visibility: hidden; }
    header[data-testid="stHeader"] { background: transparent; }

    .block-container {
        max-width: 1500px;
        padding-top: 1.4rem;
        padding-bottom: 2.5rem;
    }

    .brand-title {
        font-size: 1.55rem;
        line-height: 1.1;
        font-weight: 800;
        margin: .4rem 0 1.1rem 0;
        color: white;
    }
    .brand-icon { font-size: 2rem; margin-top: .6rem; }
    .powered {
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid rgba(255,255,255,.16);
        font-size: .84rem;
        color: #d6e2ff !important;
        line-height: 1.45;
    }

    .hero {
        border: 1px solid #e4ebf5;
        background:
            radial-gradient(circle at 88% 0%, rgba(107,132,255,.18), transparent 31%),
            linear-gradient(110deg, #ffffff 0%, #f8fbff 60%, #f1f4ff 100%);
        border-radius: 22px;
        padding: 1.6rem 1.8rem 1.4rem 1.8rem;
        margin-bottom: 1.25rem;
        box-shadow: 0 12px 34px rgba(33, 61, 120, .06);
    }
    .hero h1 {
        font-size: clamp(2rem, 4vw, 3.2rem);
        margin: 0 0 .35rem 0;
        letter-spacing: -1.5px;
        color: #071a4a;
    }
    .hero p { color: #52617f; font-size: 1.03rem; margin: 0; }

    .feature-row {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: .8rem;
        margin-top: 1.2rem;
    }
    .feature-chip {
        background: rgba(255,255,255,.84);
        border: 1px solid #e5ebf7;
        border-radius: 15px;
        padding: .8rem .95rem;
        min-height: 74px;
    }
    .feature-chip b { display: block; color: #123987; margin-bottom: .15rem; }
    .feature-chip span { color: #66738e; font-size: .87rem; }

    [data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(255,255,255,.96);
        border: 1px solid var(--line) !important;
        border-radius: 20px !important;
        box-shadow: 0 10px 28px rgba(27, 52, 104, .055);
    }
    [data-testid="stVerticalBlockBorderWrapper"] > div {
        padding: .5rem .5rem .4rem .5rem;
    }

    /* Exact alignment of numbered bullet with major heading */
    .step-title {
        display: grid;
        grid-template-columns: 48px 1fr;
        column-gap: .8rem;
        align-items: start;
        margin-bottom: 1rem;
    }
    .step-badge {
        width: 46px;
        height: 46px;
        min-width: 46px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        background: linear-gradient(135deg,#2b6de8,#3f7cf4);
        color: white;
        font-weight: 800;
        font-size: 1rem;
        margin-top: 0;
    }
    .step-copy { min-width: 0; }
    .step-title h2 {
        margin: 0;
        font-size: 1.45rem;
        line-height: 46px;
        color: #0b1f4d;
    }
    .step-title p {
        margin: .15rem 0 0 0;
        color: #6b7892;
        font-size: .92rem;
        line-height: 1.45;
    }

    .subhead {
        padding: .75rem .9rem;
        border-radius: 12px;
        background: linear-gradient(90deg,#eaf3ff,#f4f8ff);
        color: #153c8a;
        font-weight: 750;
        margin: .45rem 0 .85rem 0;
        border: 1px solid #e3edfb;
    }

    .calc-box {
        border: 1px solid #dfe7f4;
        background: #f8fbff;
        border-radius: 12px;
        padding: .75rem .85rem;
        margin-top: .15rem;
    }
    .calc-box small { display: block; color: #72809a; margin-bottom: .15rem; }
    .calc-box strong { color: #102b67; font-size: 1.15rem; }

    .result-panel {
        border-radius: 16px;
        padding: 1.35rem;
        border: 1px solid #dfe9e3;
        margin: .65rem 0 .9rem 0;
    }
    .result-panel.low { background: linear-gradient(135deg,#f0fbf4,#f9fffb); }
    .result-panel.medium { background: linear-gradient(135deg,#fff9ea,#fffdf6); border-color:#f2e2b7; }
    .result-panel.high { background: linear-gradient(135deg,#fff2f2,#fff9f9); border-color:#f0d0d0; }

    .result-tag {
        display: inline-block;
        border-radius: 999px;
        padding: .28rem .68rem;
        font-size: .82rem;
        font-weight: 750;
        margin-bottom: .5rem;
    }
    .tag-low { background:#cdf1d9; color:#087632; }
    .tag-medium { background:#ffedbc; color:#9a6200; }
    .tag-high { background:#ffd4d4; color:#a82f2f; }

    .prediction-main { font-size:1.75rem; font-weight:850; color:#081c4d; line-height:1.15; }
    .prediction-sub { color:#5d6b85; margin-top:.35rem; }
    .big-prob { font-size:2.15rem; font-weight:900; color:#0d234f; }

    .prob-grid {
        display:grid;
        grid-template-columns:1fr 1fr;
        gap:.65rem;
        margin-top:.7rem;
    }
    .prob-tile {
        border:1px solid #e0e7f2;
        border-radius:12px;
        padding:.75rem .85rem;
        background:white;
    }
    .prob-tile span { color:#687590; font-size:.84rem; display:block; }
    .prob-tile strong { color:#102759; font-size:1.05rem; }

    .info-note {
        margin-top:.8rem;
        padding:.8rem .9rem;
        border-radius:12px;
        background:#eef5ff;
        border:1px solid #dbe9ff;
        color:#53617b;
        font-size:.86rem;
    }

    .empty-state {
        min-height: 350px;
        border: 1px dashed #d9e3f1;
        background: linear-gradient(180deg,#fbfdff,#f7faff);
        border-radius:16px;
        display:flex;
        flex-direction:column;
        justify-content:center;
        align-items:center;
        text-align:center;
        padding:2rem;
        color:#66738e;
    }
    .empty-icon { font-size:3.2rem; margin-bottom:.5rem; }

    .status-dot {
        display:inline-flex;
        align-items:center;
        gap:.45rem;
        border:1px solid #cfe6d5;
        background:#f1fbf4;
        color:#19753a;
        border-radius:999px;
        padding:.3rem .6rem;
        font-size:.78rem;
        font-weight:700;
    }
    .status-dot::before {
        content:"";
        width:8px;
        height:8px;
        border-radius:50%;
        background:#27ae60;
    }

    .mini-table { width:100%; border-collapse:collapse; font-size:.9rem; }
    .mini-table td { padding:.42rem 0; border-bottom:1px solid #edf1f7; vertical-align:top; }
    .mini-table td:first-child { color:#6a7892; width:46%; }
    .mini-table td:last-child { color:#122957; font-weight:650; }

    @media (max-width: 900px) {
        .feature-row { grid-template-columns:1fr; }
        .prob-grid { grid-template-columns:1fr; }
        .step-title { grid-template-columns:42px 1fr; }
        .step-badge { width:40px; height:40px; min-width:40px; }
        .step-title h2 { line-height:40px; font-size:1.25rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def _secret(name: str, default: str = "") -> str:
    try:
        return str(st.secrets.get(name, default)).strip()
    except Exception:
        return str(os.getenv(name, default)).strip()


def get_connection() -> Tuple[str, str, str]:
    host = _secret("DATABRICKS_HOST")
    token = _secret("DATABRICKS_TOKEN")
    endpoint = _secret("DATABRICKS_ENDPOINT_NAME", DEFAULT_ENDPOINT) or DEFAULT_ENDPOINT
    return host.rstrip("/"), token, endpoint


def query_model(record: Dict[str, Any]) -> Dict[str, Any]:
    host, token, endpoint = get_connection()

    if not host or not token:
        raise RuntimeError(
            "Databricks connection is not configured. Add DATABRICKS_HOST and "
            "DATABRICKS_TOKEN to Streamlit secrets."
        )

    url = f"{host}/serving-endpoints/{endpoint}/invocations"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {"dataframe_records": [record]}

    retryable_status = {429, 502, 503, 504}
    last_error = None

    for attempt in range(2):
        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=(15, 180),
            )

            if response.status_code in retryable_status and attempt == 0:
                time.sleep(3)
                continue

            response.raise_for_status()
            body = response.json()
            predictions = body.get("predictions")

            if not isinstance(predictions, list) or not predictions:
                raise RuntimeError(f"Unexpected endpoint response: {body}")

            result = predictions[0]
            if not isinstance(result, dict):
                raise RuntimeError(f"Unexpected prediction format: {result}")

            return result

        except requests.Timeout as exc:
            last_error = exc
            if attempt == 0:
                time.sleep(2)
                continue

        except requests.HTTPError as exc:
            status = exc.response.status_code if exc.response is not None else None
            if status == 401:
                raise RuntimeError(
                    "Databricks rejected the credentials (HTTP 401). Check DATABRICKS_TOKEN."
                ) from exc
            if status == 403:
                raise RuntimeError(
                    "The Databricks credential is not authorized to query this endpoint (HTTP 403)."
                ) from exc
            detail = exc.response.text[:500] if exc.response is not None else str(exc)
            raise RuntimeError(f"Databricks endpoint returned HTTP {status}: {detail}") from exc

        except requests.RequestException as exc:
            last_error = exc
            break

    raise RuntimeError(
        "The serving endpoint did not respond in time. It may be starting from scale-to-zero; "
        "wait briefly and try again."
    ) from last_error


def risk_band(probability_return: float) -> Tuple[str, str, str]:
    if probability_return < 0.20:
        return "Low Return Risk", "low", "tag-low"
    if probability_return < 0.50:
        return "Moderate Return Risk", "medium", "tag-medium"
    return "High Return Risk", "high", "tag-high"


def init_state() -> None:
    defaults = {
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
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def apply_example(example: Dict[str, Any]) -> None:
    for key, value in example.items():
        st.session_state[key] = value
    st.session_state.pop("prediction_result", None)


init_state()

with st.sidebar:
    st.markdown('<div class="brand-icon">🛒</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-title">Sales Return<br>Prediction</div>', unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        ["Predict Return", "About Model", "User Guide", "Example Cases"],
        label_visibility="collapsed",
    )

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    host, token, endpoint = get_connection()

    if host and token:
        st.markdown('<span class="status-dot">Model connection configured</span>', unsafe_allow_html=True)
    else:
        st.warning("Add Databricks secrets before making live predictions.")

    st.markdown(
        f"""
        <div class="powered">
            Powered by<br>
            <b>Databricks Model Serving</b><br><br>
            Endpoint:<br><code>{endpoint}</code>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_hero() -> None:
    st.markdown(
        """
        <div class="hero">
            <h1>Sales Return Prediction</h1>
            <p>Predict the likelihood of a product being returned using customer, product and order information.</p>
            <div class="feature-row">
                <div class="feature-chip"><b>⚡ AI-Powered</b><span>Machine-learning classification model</span></div>
                <div class="feature-chip"><b>🛡️ Real-time Predictions</b><span>Powered by Databricks Model Serving</span></div>
                <div class="feature-chip"><b>📊 Probability Output</b><span>Return and no-return probabilities</span></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_predict_page() -> None:
    render_hero()

    left, right = st.columns([1.03, 1], gap="medium")

    with left:
        with st.container(border=True):
            st.markdown(
                """
                <div class="step-title">
                    <div class="step-badge">1</div>
                    <div class="step-copy">
                        <h2>Enter Order Details</h2>
                        <p>Provide the product, customer and transaction information below.</p>
                    </div>
                </div>
                <div class="subhead">📦 &nbsp; Product & Order Information</div>
                """,
                unsafe_allow_html=True,
            )

            c1, c2, c3 = st.columns(3)
            with c1:
                quantity = st.number_input("Quantity", min_value=1, max_value=100, step=1, key="quantity")
            with c2:
                unit_price = st.number_input(
                    "Unit Price (KES)", min_value=0.0, max_value=1_000_000.0,
                    step=10.0, format="%.2f", key="unit_price"
                )
            with c3:
                discount_pct = st.number_input(
                    "Discount (%)", min_value=0.0, max_value=100.0,
                    step=1.0, format="%.1f", key="discount_pct"
                )

            total_sales = round(
                float(quantity) * float(unit_price) * (1 - float(discount_pct) / 100.0), 2
            )

            c4, c5 = st.columns([1, 1])
            with c4:
                st.markdown(
                    f'<div class="calc-box"><small>Total Sales (calculated)</small><strong>KES {total_sales:,.2f}</strong></div>',
                    unsafe_allow_html=True,
                )
            with c5:
                rating = st.number_input(
                    "Product Rating (1–5)", min_value=1.0, max_value=5.0,
                    step=0.5, format="%.1f", key="rating"
                )

            st.markdown(
                '<div class="subhead" style="margin-top:1rem">👥 &nbsp; Customer & Order Context</div>',
                unsafe_allow_html=True,
            )

            r1, r2, r3 = st.columns(3)
            with r1:
                region = st.selectbox("Region", REGIONS, key="region")
            with r2:
                category = st.selectbox("Category", CATEGORIES, key="category")
            with r3:
                payment_method = st.selectbox("Payment Method", PAYMENT_METHODS, key="payment_method")

            r4, r5, r6 = st.columns(3)
            with r4:
                channel = st.selectbox("Channel", CHANNELS, key="channel")
            with r5:
                customer_segment = st.selectbox("Customer Segment", CUSTOMER_SEGMENTS, key="customer_segment")
            with r6:
                delivery_status = st.selectbox("Delivery Status", DELIVERY_STATUSES, key="delivery_status")

            b1, b2 = st.columns([1, 1.35])
            with b1:
                if st.button("↻  Reset", use_container_width=True):
                    for key in [
                        "quantity", "unit_price", "discount_pct", "rating", "region", "category",
                        "payment_method", "channel", "customer_segment", "delivery_status", "prediction_result"
                    ]:
                        st.session_state.pop(key, None)
                    st.rerun()

            with b2:
                predict_clicked = st.button("✨  Predict Return", type="primary", use_container_width=True)

            if predict_clicked:
                record = {
                    "quantity": int(quantity),
                    "unit_price": float(unit_price),
                    "discount_pct": float(discount_pct),
                    "total_sales": float(total_sales),
                    "rating": float(rating),
                    "region": str(region),
                    "category": str(category),
                    "payment_method": str(payment_method),
                    "channel": str(channel),
                    "customer_segment": str(customer_segment),
                    "delivery_status": str(delivery_status),
                }
                try:
                    with st.spinner("Querying the Databricks model serving endpoint…"):
                        result = query_model(record)
                    st.session_state["prediction_result"] = {"result": result, "record": record}
                except Exception as exc:
                    st.error(str(exc))

    with right:
        with st.container(border=True):
            st.markdown(
                """
                <div class="step-title">
                    <div class="step-badge">2</div>
                    <div class="step-copy">
                        <h2>Prediction Result</h2>
                        <p>The deployed model estimates the likelihood that this order will be returned.</p>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            stored = st.session_state.get("prediction_result")

            if not stored:
                st.markdown(
                    """
                    <div class="empty-state">
                        <div class="empty-icon">📊</div>
                        <h3 style="color:#183363;margin:.25rem 0">Ready for Prediction</h3>
                        <div>Enter the order details and click <b>Predict Return</b> to see the result here.</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                result = stored["result"]
                prediction = int(result.get("prediction", 0))
                p_return = min(max(float(result.get("probability_return", 0.0)), 0.0), 1.0)
                p_no_return = min(max(float(result.get("probability_no_return", 1.0 - p_return)), 0.0), 1.0)

                band, panel_class, tag_class = risk_band(p_return)
                prediction_text = "Likely to be returned" if prediction == 1 else "Not likely to be returned"
                icon = "⚠️" if prediction == 1 else "✅"

                st.markdown(
                    f"""
                    <div class="result-panel {panel_class}">
                        <span class="result-tag {tag_class}">{band}</span>
                        <div style="display:flex;justify-content:space-between;gap:1rem;align-items:center">
                            <div>
                                <div class="prediction-main">{icon} {prediction_text}</div>
                                <div class="prediction-sub">The model estimates a <b>{p_return * 100:.1f}%</b> probability of return.</div>
                            </div>
                            <div class="big-prob">{p_return * 100:.1f}%</div>
                        </div>
                    </div>
                    <div class="prob-grid">
                        <div class="prob-tile"><span>Probability of Return</span><strong>{p_return * 100:.2f}%</strong></div>
                        <div class="prob-tile"><span>Probability of No Return</span><strong>{p_no_return * 100:.2f}%</strong></div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                st.progress(p_return, text="Return probability")
                st.markdown("#### Prediction Details")
                st.markdown(
                    f"""
                    <table class="mini-table">
                        <tr><td>Predicted class</td><td>{'Returned (1)' if prediction == 1 else 'Not Returned (0)'}</td></tr>
                        <tr><td>Return probability</td><td>{p_return * 100:.2f}%</td></tr>
                        <tr><td>No-return probability</td><td>{p_no_return * 100:.2f}%</td></tr>
                        <tr><td>Registered model</td><td>{MODEL_NAME}</td></tr>
                        <tr><td>Model version</td><td>{MODEL_VERSION}</td></tr>
                        <tr><td>Model family</td><td>Random Forest (scikit-learn)</td></tr>
                        <tr><td>Serving platform</td><td>Databricks Model Serving</td></tr>
                    </table>
                    """,
                    unsafe_allow_html=True,
                )
                st.markdown(
                    """
                    <div class="info-note"><b>💡 Important note</b><br>
                    The probability is the model's estimated likelihood, not a guarantee. Use it as decision support alongside business context.</div>
                    """,
                    unsafe_allow_html=True,
                )


def render_about_page() -> None:
    render_hero()
    st.markdown("## About the model")
    c1, c2, c3 = st.columns(3)
    c1.metric("Model", "Random Forest")
    c2.metric("Registered Version", MODEL_VERSION)
    c3.metric("Inference Inputs", "11")

    st.markdown(
        """
        The production serving model is an **MLflow pyfunc wrapper** around a scikit-learn pipeline.
        It receives the same raw business inputs used in the Databricks notebook, applies preprocessing,
        and returns `prediction`, `probability_no_return`, and `probability_return`.

        The original practical builds the machine-learning workflow in PySpark. A serving-compatible
        scikit-learn model was then deployed because the Free Edition environment exposed a Spark/PySpark
        version mismatch when loading the serialized Spark Random Forest model.
        """
    )

    st.markdown("### Model inputs")
    st.code(
        "quantity\nunit_price\ndiscount_pct\ntotal_sales\nrating\nregion\ncategory\npayment_method\nchannel\ncustomer_segment\ndelivery_status",
        language="text",
    )
    st.markdown("### Serving architecture")
    st.info("Streamlit → HTTPS request → Databricks Model Serving → MLflow pyfunc → sklearn pipeline → prediction + probabilities")


def render_guide_page() -> None:
    render_hero()
    st.markdown("## User Guide")
    st.markdown(
        """
        1. Enter the product quantity, unit price, discount and rating.
        2. `Total Sales` is calculated automatically using the same formula used in the Silver layer.
        3. Select the categorical values that describe the order.
        4. Click **Predict Return**.
        5. Review the predicted class and the probability of return / no return.

        **Interpretation:** A prediction of `1` indicates *returned*; `0` indicates *not returned*.
        The displayed probability is generated by `predict_proba()` from the deployed Random Forest model.
        """
    )
    st.markdown("### Required Streamlit secrets")
    st.code(
        'DATABRICKS_HOST = "https://<your-workspace-host>"\nDATABRICKS_TOKEN = "<your-token>"\nDATABRICKS_ENDPOINT_NAME = "sales_return_prediction_sklearn"',
        language="toml",
    )


def render_examples_page() -> None:
    render_hero()
    st.markdown("## Example Cases")
    st.caption("These examples are based on the sample records used to test the deployed endpoint in the Databricks notebook.")

    cols = st.columns(2)
    for (name, example), col in zip(EXAMPLES.items(), cols):
        with col:
            with st.container(border=True):
                st.markdown(f"### {name}")
                total = round(example["quantity"] * example["unit_price"] * (1 - example["discount_pct"] / 100), 2)
                st.write({**example, "total_sales": total})
                if st.button(f"Use {name}", key=f"example_{name}", use_container_width=True):
                    apply_example(example)
                    st.rerun()

    st.info("To use an example, select it here, then open **Predict Return** in the sidebar.")


if page == "Predict Return":
    render_predict_page()
elif page == "About Model":
    render_about_page()
elif page == "User Guide":
    render_guide_page()
else:
    render_examples_page()
