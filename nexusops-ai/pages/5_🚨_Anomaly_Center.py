import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


def detect_anomalies_zscore(data: pd.DataFrame, threshold: float = 2.5) -> pd.DataFrame:
    """Detect anomalies using the z‑score method on the first numeric column.

    Args:
        data: Dataset with a date column and at least one numeric column.
        threshold: Z‑score threshold above which a point is considered an anomaly.

    Returns:
        DataFrame with columns date, metric value, z_score and is_anomaly.
    """
    numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
    if not numeric_cols:
        return pd.DataFrame()
    metric_col = numeric_cols[0]
    values = data[metric_col]
    mean = values.mean()
    std = values.std(ddof=0)
    # Avoid division by zero
    if std == 0:
        z_scores = pd.Series([0] * len(values), index=values.index)
    else:
        z_scores = (values - mean) / std
    anomalies = pd.DataFrame({
        "date": data.get("date"),
        metric_col: values,
        "score": z_scores,
        "is_anomaly": np.abs(z_scores) > threshold,
    })
    return anomalies


def detect_anomalies_isolation(data: pd.DataFrame, contamination: float = 0.05) -> pd.DataFrame:
    """Detect anomalies using the Isolation Forest algorithm on the first numeric column.

    Args:
        data: Dataset with a date column and at least one numeric column.
        contamination: Expected proportion of outliers in the data.

    Returns:
        DataFrame with columns date, metric value, score (negative anomaly score) and is_anomaly.
    """
    numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
    if not numeric_cols:
        return pd.DataFrame()
    metric_col = numeric_cols[0]
    values = data[[metric_col]].copy().dropna()
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(values)
    # Build Isolation Forest
    clf = IsolationForest(contamination=min(max(contamination, 0.001), 0.5), random_state=42)
    clf.fit(X_scaled)
    scores = clf.decision_function(X_scaled)
    preds = clf.predict(X_scaled)
    is_anomaly = preds == -1
    anomalies = pd.DataFrame({
        "date": data.get("date").iloc[values.index] if "date" in data.columns else values.index,
        metric_col: values[metric_col].values,
        "score": scores,
        "is_anomaly": is_anomaly,
    }).reset_index(drop=True)
    return anomalies


def render_anomaly_center():
    """Render the anomaly detection page."""
    st.title("🚨 Anomaly Center")
    st.write(
        """
        Identify unusual points in your primary metric using either a z‑score
        threshold or a machine‑learning based Isolation Forest. Adjust the
        parameters below to fine tune how strictly anomalies are flagged.
        """
    )

    dataset = st.session_state.get("dataset")
    if dataset is None:
        st.info("Please upload data via the Data Hub page first.")
        return

    numeric_cols = dataset.select_dtypes(include=['number']).columns.tolist()
    if not numeric_cols:
        st.warning("No numeric columns found in the dataset.")
        return
    metric_col = numeric_cols[0]

    # Select detection method
    method = st.selectbox("Anomaly detection method", options=["Z‑score", "Isolation Forest"])

    # Detect anomalies according to selected method
    if method == "Z‑score":
        threshold = st.slider("Z‑score threshold", min_value=1.5, max_value=4.0, value=2.5, step=0.1)
        anomalies = detect_anomalies_zscore(dataset, threshold)
        score_label = "z_score"
    else:
        contamination = st.slider("Contamination (proportion of expected anomalies)", min_value=0.01, max_value=0.3, value=0.05, step=0.01)
        anomalies = detect_anomalies_isolation(dataset, contamination)
        score_label = "score"

    if anomalies.empty:
        st.warning("Anomaly detection failed. Please check your data.")
        return

    # Plot anomalies on a scatter/line chart
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
    fig.update_layout(title=f"Anomaly Detection ({method})", xaxis_title="Date", yaxis_title=metric_col)
    st.plotly_chart(fig, use_container_width=True)

    # Show anomaly table
    st.subheader("Anomalies")
    if not anomaly_points.empty:
        table_cols = ["date", metric_col, score_label]
        anomaly_table = anomaly_points[table_cols]
        st.dataframe(anomaly_table.reset_index(drop=True))
    else:
        st.write("No anomalies detected with the current settings.")


def main():  # pragma: no cover - entry point for Streamlit
    render_anomaly_center()


if __name__ == "__main__":
    main()