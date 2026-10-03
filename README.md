# Sales Return Prediction — Streamlit + Databricks Model Serving

A Streamlit front end for the deployed Databricks model:

- Registered model: `workspace.default.sales_return_prediction_sklearn`
- Serving endpoint: `sales_return_prediction_sklearn`
- Current serving model version in the supplied notebook: `2`
- Output fields: `prediction`, `probability_no_return`, `probability_return`

## Architecture

`Streamlit → Databricks Model Serving REST API → MLflow pyfunc → sklearn pipeline → prediction + probabilities`

The underlying practical was developed in PySpark. A scikit-learn serving model was deployed to bypass the Spark/PySpark artifact compatibility issue encountered in Databricks Free Edition.

## Model inputs

The endpoint expects exactly 11 inputs:

1. `quantity`
2. `unit_price`
3. `discount_pct`
4. `total_sales`
5. `rating`
6. `region`
7. `category`
8. `payment_method`
9. `channel`
10. `customer_segment`
11. `delivery_status`

The app calculates `total_sales` using the notebook's Silver-layer formula:

`quantity × unit_price × (1 - discount_pct / 100)`

## Run locally

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

Create `.streamlit/secrets.toml` locally using `.streamlit/secrets.toml.example` as a template:

```toml
DATABRICKS_HOST = "https://<your-workspace-host>"
DATABRICKS_TOKEN = "<your-token>"
DATABRICKS_ENDPOINT_NAME = "sales_return_prediction_sklearn"
```

Then run:

```bash
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

1. Put this project in a GitHub repository.
2. Do **not** commit `.streamlit/secrets.toml`.
3. Open Streamlit Community Cloud and create a new app from the repository.
4. Set the main file to `app.py`.
5. In the app's **Secrets** settings, add:

```toml
DATABRICKS_HOST = "https://<your-workspace-host>"
DATABRICKS_TOKEN = "<your-token>"
DATABRICKS_ENDPOINT_NAME = "sales_return_prediction_sklearn"
```

6. Deploy.

## Endpoint request shape

```json
{
  "dataframe_records": [
    {
      "quantity": 4,
      "unit_price": 179.26,
      "discount_pct": 0.0,
      "total_sales": 717.04,
      "rating": 3.0,
      "region": "Eastern",
      "category": "Food Staples",
      "payment_method": "Airtel Money",
      "channel": "Online",
      "customer_segment": "Wholesale",
      "delivery_status": "Delivered"
    }
  ]
}
```

Expected response structure:

```json
{
  "predictions": [
    {
      "prediction": 0,
      "probability_no_return": 0.9616889754683525,
      "probability_return": 0.03831102453164713
    }
  ]
}
```

## Security

Never hard-code a real Databricks token in `app.py`, GitHub, or any public repository. Store it only in Streamlit secrets or environment variables.

## Notes

- The endpoint has scale-to-zero enabled, so the first request after inactivity may take longer.
- The probability displayed by the app is the Random Forest model's estimated probability, not a guarantee.
- The app uses categorical choices observed in the cleaned Databricks dataset supplied with the notebook.
