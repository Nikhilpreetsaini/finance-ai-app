import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


def detect_anomalies(data: pd.DataFrame, threshold: float = 2.5) -> pd.DataFrame:
    """Detect anomalies in the first numeric column using z‑score method.

    Args:
        data (DataFrame): Dataset with a date column and at least one numeric column.
        threshold (float): Z‑score threshold above which a point is considered an anomaly.

    Returns:
        DataFrame: Original data with an additional 'z_score' and 'is_anomaly' columns.
    """
    numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
    if not numeric_cols:
        return pd.DataFrame()
    metric_col = numeric_cols[0]
    values = data[metric_col]
    mean = values.mean()
    std = values.std(ddof=0)
    z_scores = (values - mean) / std
    anomalies = pd.DataFrame({
        "date": data.get("date"),
        metric_col: values,
        "z_score": z_scores,
        "is_anomaly": np.abs(z_scores) > threshold,
    })
    return anomalies


def render_anomaly_center():
    """Render the anomaly detection page."""
    st.title("🚨 Anomaly Center")
    st.write(
        """
        This page uses a simple **z‑score** method to flag potential anomalies
        in your primary metric. Points with a z‑score above the specified
        threshold (in absolute terms) are highlighted. This is a basic
        approach—more sophisticated techniques like Isolation Forest or
        Prophet residuals could be added for better results.
        """
    )

    dataset = st.session_state.get("dataset")
    if dataset is None:
        st.info("Please upload data via the Data Hub page first.")
        return

    # Detect anomalies
    threshold = st.slider("Z‑score threshold", min_value=1.5, max_value=4.0, value=2.5, step=0.1)
    anomalies = detect_anomalies(dataset, threshold)
    if anomalies.empty:
        st.warning("No numeric columns found in the dataset.")
        return

    # Plot anomalies on a scatter/line chart
    metric_col = dataset.select_dtypes(include=['number']).columns.tolist()[0]
    fig = go.Figure()
    # Plot original data
    fig.add_trace(go.Scatter(
        x=anomalies["date"] if "date" in anomalies.columns else anomalies.index,
        y=anomalies[metric_col],
        mode="lines+markers",
        name="Metric",
        line=dict(color="#1f77b4"),
    ))
    # Highlight anomalies
    anomaly_points = anomalies[anomalies["is_anomaly"]]
    if not anomaly_points.empty:
        fig.add_trace(go.Scatter(
            x=anomaly_points["date"] if "date" in anomalies.columns else anomaly_points.index,
            y=anomaly_points[metric_col],
            mode="markers",
            name="Anomaly",
            marker=dict(color="red", size=10, symbol="x"),
        ))
    fig.update_layout(title="Anomaly Detection", xaxis_title="Date", yaxis_title=metric_col)
    st.plotly_chart(fig, use_container_width=True)

    # Show anomaly table
    st.subheader("Anomalies")
    anomaly_table = anomaly_points[["date", metric_col, "z_score"]] if not anomaly_points.empty else pd.DataFrame(columns=["date", metric_col, "z_score"])
    st.dataframe(anomaly_table.reset_index(drop=True))


def main():  # pragma: no cover - entry point for Streamlit
    render_anomaly_center()


if __name__ == "__main__":
    main()
