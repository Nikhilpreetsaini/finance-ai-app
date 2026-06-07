from __future__ import annotations

import datetime
from typing import Optional

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from sklearn.linear_model import LinearRegression


def prepare_time_series(data: pd.DataFrame) -> Optional[pd.DataFrame]:
    """Prepare a time series for simple forecasting by ensuring a date column is
    present and converting it to an ordinal numeric representation.

    Args:
        data (DataFrame): The input dataset with a date column.

    Returns:
        Optional[DataFrame]: DataFrame with 'date' and 'value' columns and a
        numeric 't' column for regression; or None if preparation fails.
    """
    if "date" not in data.columns:
        return None
    # Determine the first numeric column to forecast
    numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
    if not numeric_cols:
        return None
    metric_col = numeric_cols[0]
    df = data[["date", metric_col]].dropna().copy()
    # Convert dates to ordinal (days since 1970‑01‑01) for regression
    df["t"] = df["date"].map(datetime.datetime.toordinal)
    df = df.rename(columns={metric_col: "value"})
    return df


def train_forecast_model(df: pd.DataFrame, horizon: int) -> pd.DataFrame:
    """Train a simple linear regression model and forecast future values.

    Args:
        df (DataFrame): Prepared DataFrame with 'date', 'value', and 't' columns.
        horizon (int): Number of future periods to forecast.

    Returns:
        DataFrame: DataFrame containing historical and forecasted values.
    """
    X = df[["t"]]
    y = df["value"]
    model = LinearRegression()
    model.fit(X, y)

    # Forecast for existing dates
    df["forecast"] = model.predict(X)

    # Forecast for future horizon (assuming same frequency as median difference)
    last_date = df["date"].max()
    # Estimate frequency by median difference in days
    diffs = df["date"].diff().dropna()
    if len(diffs) > 0:
        freq_days = int(diffs.dt.days.median())
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

    return pd.concat([df, future_df], ignore_index=True)


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

    prepared = prepare_time_series(dataset)
    if prepared is None:
        st.warning("Dataset must contain a 'date' column and at least one numeric column.")
        return

    horizon = st.slider("Forecast horizon (number of future periods)", min_value=1, max_value=24, value=6)

    forecast_df = train_forecast_model(prepared, horizon)

    # Plot actual vs forecast
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=forecast_df["date"], y=forecast_df["value"], mode="markers+lines", name="Actual", line=dict(color="#1f77b4")
    ))
    fig.add_trace(go.Scatter(
        x=forecast_df["date"], y=forecast_df["forecast"], mode="lines", name="Forecast", line=dict(color="#d62728", dash="dash")
    ))
    fig.update_layout(title="Actual vs Forecast", xaxis_title="Date", yaxis_title="Metric")
    st.plotly_chart(fig, use_container_width=True)

    # Display forecast table
    st.subheader("Forecast Data")
    st.dataframe(forecast_df.tail(horizon + 5).reset_index(drop=True))


def main():  # pragma: no cover - entry point for Streamlit
    render_forecasting_lab()


if __name__ == "__main__":
    main()
