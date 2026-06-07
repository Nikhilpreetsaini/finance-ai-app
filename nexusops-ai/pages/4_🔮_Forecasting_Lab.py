from __future__ import annotations

import datetime
from typing import Optional, List, Dict, Tuple

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.ensemble import RandomForestRegressor
try:
    from xgboost import XGBRegressor  # type: ignore [import-not-found]
except Exception:
    # Fall back if xgboost is not available
    XGBRegressor = None  # type: ignore


def prepare_time_series(data: pd.DataFrame, metric_col: str) -> Optional[pd.DataFrame]:
    """Prepare a time series for forecasting by ensuring a date column is
    present and converting it to an ordinal numeric representation for the
    selected metric column.

    Args:
        data: The input dataset with a date column.
        metric_col: Name of the numeric column to forecast.

    Returns:
        DataFrame with 'date', 'value' and numeric 't' columns; or None if
        preparation fails.
    """
    if "date" not in data.columns:
        return None
    if metric_col not in data.columns:
        return None
    df = data[["date", metric_col]].dropna().copy()
    # Convert dates to ordinal (days since 1970‑01‑01) for regression
    df["t"] = df["date"].map(lambda d: d.toordinal() if isinstance(d, datetime.date) else pd.to_datetime(d).toordinal())
    df = df.rename(columns={metric_col: "value"})
    return df


def train_forecast_model(df: pd.DataFrame, horizon: int, model_name: str) -> Tuple[pd.DataFrame, object]:
    """Train a forecasting model and forecast future values.

    Args:
        df: Prepared DataFrame with 'date', 'value', and 't' columns.
        horizon: Number of future periods to forecast.
        model_name: Name of the model ('Linear Regression', 'Random Forest', 'XGBoost').

    Returns:
        A tuple of the resulting DataFrame containing historical and forecasted values
        and the trained model object.
    """
    X = df[["t"]]
    y = df["value"]
    # Select model based on name
    if model_name == "Random Forest":
        model = RandomForestRegressor(n_estimators=200, random_state=42)
    elif model_name == "XGBoost" and XGBRegressor is not None:
        model = XGBRegressor(
            n_estimators=200,
            max_depth=3,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
        )
    else:
        model = LinearRegression()
        model_name = "Linear Regression"
    model.fit(X, y)

    # Forecast for existing dates
    df = df.copy()
    df["forecast"] = model.predict(X)

    # Determine frequency of dates by median difference in days
    last_date = df["date"].max()
    diffs = df["date"].diff().dropna()
    if len(diffs) > 0:
        freq_days = int(diffs.dt.days.median())
        if freq_days <= 0:
            freq_days = 1
    else:
        freq_days = 30  # fallback to 1 month
    future_dates = [last_date + datetime.timedelta(days=freq_days * (i + 1)) for i in range(horizon)]
    future_t = [d.toordinal() for d in future_dates]
    future_values = model.predict(np.array(future_t).reshape(-1, 1))
    future_df = pd.DataFrame({
        "date": future_dates,
        "value": np.nan,
        "t": future_t,
        "forecast": future_values,
    })
    result_df = pd.concat([df, future_df], ignore_index=True)
    return result_df, model


def evaluate_models(df: pd.DataFrame, train_ratio: float = 0.8) -> List[Dict[str, float]]:
    """Evaluate multiple forecasting models on a hold‑out set.

    Splits the prepared dataset into a training and test set using the
    specified ratio. Trains each model and computes MAE and RMSE on the
    test set.

    Args:
        df: Prepared DataFrame with 't' and 'value' columns.
        train_ratio: Fraction of data to use for training.

    Returns:
        A list of dictionaries containing model name and evaluation metrics.
    """
    # Sort by time to ensure chronological order
    df_sorted = df.sort_values("t").reset_index(drop=True)
    n = len(df_sorted)
    if n < 4:
        return []
    split_idx = max(int(n * train_ratio), 1)
    train_df = df_sorted.iloc[:split_idx]
    test_df = df_sorted.iloc[split_idx:]
    X_train = train_df[["t"]]
    y_train = train_df["value"]
    X_test = test_df[["t"]]
    y_test = test_df["value"]

    results = []
    model_names = ["Linear Regression", "Random Forest"]
    if XGBRegressor is not None:
        model_names.append("XGBoost")
    for name in model_names:
        # Train model
        _, model = train_forecast_model(train_df, 0, name)  # horizon=0 for training only
        # Predict on test set
        preds = model.predict(X_test)
        mae = mean_absolute_error(y_test, preds)
        rmse = mean_squared_error(y_test, preds, squared=False)
        results.append({
            "Model": name,
            "MAE": round(float(mae), 2),
            "RMSE": round(float(rmse), 2),
        })
    return results


def render_forecasting_lab():
    """Render the forecasting lab page."""
    st.title("🔮 Forecasting Lab")
    st.write(
        """
        This page provides a simple linear‑trend forecasting example using
        **scikit‑learn**'s ``LinearRegression``. The model fits your metric as a
        function of time (in days). You can adjust the forecast horizon to
        generate predictions into the future. For more robust forecasting,
        consider implementing ARIMA, Prophet or machine learning models.
        """
    )

    dataset = st.session_state.get("dataset")
    if dataset is None:
        st.info("Please upload data via the Data Hub page first.")
        return

    numeric_cols = dataset.select_dtypes(include=['number']).columns.tolist()
    if not numeric_cols or "date" not in dataset.columns:
        st.warning("Dataset must contain a 'date' column and at least one numeric column.")
        return

    # Let user select the metric column to forecast
    metric_col = st.selectbox("Select metric column to forecast", options=numeric_cols)

    prepared = prepare_time_series(dataset, metric_col)
    if prepared is None or prepared.empty:
        st.warning("Unable to prepare time series from the selected column.")
        return

    # Evaluate models on hold‑out set
    with st.expander("Model comparison (MAE/RMSE)"):
        eval_results = evaluate_models(prepared)
        if eval_results:
            eval_df = pd.DataFrame(eval_results)
            st.dataframe(eval_df)
        else:
            st.write("Not enough data for model evaluation.")

    # Select model for forecasting
    model_options: List[str] = ["Linear Regression", "Random Forest"]
    if XGBRegressor is not None:
        model_options.append("XGBoost")
    model_name = st.selectbox("Select forecast model", options=model_options)

    horizon = st.slider("Forecast horizon (number of future periods)", min_value=1, max_value=24, value=6)

    # Train selected model and forecast
    forecast_df, _ = train_forecast_model(prepared, horizon, model_name)

    # Plot actual vs forecast
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=forecast_df["date"], y=forecast_df["value"], mode="markers+lines", name="Actual",
        line=dict(color="#1f77b4")
    ))
    fig.add_trace(go.Scatter(
        x=forecast_df["date"], y=forecast_df["forecast"], mode="lines", name=f"Forecast ({model_name})",
        line=dict(color="#d62728", dash="dash")
    ))
    fig.update_layout(title=f"Actual vs Forecast ({model_name})", xaxis_title="Date", yaxis_title=metric_col)
    st.plotly_chart(fig, use_container_width=True)

    # Display forecast table
    st.subheader("Forecast Data")
    st.dataframe(forecast_df.tail(horizon + 5).reset_index(drop=True))


def main():  # pragma: no cover - entry point for Streamlit
    render_forecasting_lab()


if __name__ == "__main__":
    main()