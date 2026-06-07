import streamlit as st
import pandas as pd
import plotly.express as px


def compute_kpis(data: pd.DataFrame) -> dict:
    """Compute a few example KPIs from the provided dataset.

    Args:
        data (DataFrame): The loaded dataset with at least a 'date' column and one numeric metric.

    Returns:
        dict: A dictionary of key performance indicators.
    """
    metrics = {}
    # Identify numeric columns other than the date
    numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
    if not numeric_cols:
        return metrics

    # Use the first numeric column as the primary metric
    metric_col = numeric_cols[0]
    values = data[metric_col]

    metrics["Total"] = values.sum()
    metrics["Average"] = values.mean()
    metrics["Min"] = values.min()
    metrics["Max"] = values.max()

    # Compute last period vs previous period difference if dates exist
    if "date" in data.columns:
        # Sort by date to ensure proper chronological order
        df_sorted = data.sort_values("date")
        last_value = df_sorted[metric_col].iloc[-1]
        prev_value = df_sorted[metric_col].iloc[-2] if len(df_sorted) > 1 else None
        if prev_value is not None:
            diff = last_value - prev_value
            pct_change = (diff / prev_value) * 100 if prev_value != 0 else float('nan')
            metrics["Last Period"] = last_value
            metrics["Change"] = diff
            metrics["% Change"] = pct_change
    return metrics


def render_dashboard():
    """Render the KPI dashboard page."""
    st.title("📊 KPI Dashboard")
    st.write(
        """
        This dashboard displays simple metrics computed from your dataset. The
        current implementation looks at the first numeric column in your data
        and calculates totals, averages and simple period‑over‑period changes.
        Advanced dashboards could include additional KPIs, segmentation,
        filters and drill‑downs.
        """
    )

    dataset = st.session_state.get("dataset")
    if dataset is None:
        st.info("Please upload data via the Data Hub page first.")
        return

    # Compute KPIs
    kpis = compute_kpis(dataset)
    if not kpis:
        st.warning("No numeric columns found in the dataset.")
        return

    # Display metric cards
    cols = st.columns(len(kpis))
    for i, (label, value) in enumerate(kpis.items()):
        cols[i].metric(label, f"{value:,.2f}")

    # Plot time series of the first numeric column
    numeric_cols = dataset.select_dtypes(include=['number']).columns.tolist()
    metric_col = numeric_cols[0]
    if "date" in dataset.columns:
        fig = px.line(dataset.sort_values("date"), x="date", y=metric_col, title=f"{metric_col} Over Time")
        fig.update_layout(xaxis_title="Date", yaxis_title=metric_col)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.line_chart(dataset[metric_col], use_container_width=True)


def main():  # pragma: no cover - entry point for Streamlit
    render_dashboard()


if __name__ == "__main__":
    main()
