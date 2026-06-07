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

    # Let user select which numeric column to analyze
    numeric_cols = dataset.select_dtypes(include=['number']).columns.tolist()
    if not numeric_cols:
        st.warning("No numeric columns found in the dataset.")
        return
    metric_col = st.selectbox("Select metric column", options=numeric_cols)

    # Date range filter if date column exists
    df_filtered = dataset.copy()
    if "date" in dataset.columns:
        min_date, max_date = dataset["date"].min(), dataset["date"].max()
        date_range = st.date_input(
            "Date range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        )
        # Ensure tuple length is 2
        if isinstance(date_range, tuple) and len(date_range) == 2:
            start_date, end_date = date_range
            df_filtered = dataset[(dataset["date"] >= pd.to_datetime(start_date)) & (dataset["date"] <= pd.to_datetime(end_date))]

    # Compute KPIs on the filtered data
    kpis = compute_kpis(df_filtered[["date", metric_col]] if "date" in df_filtered.columns else df_filtered[[metric_col]])
    # Display metric cards
    cols = st.columns(len(kpis))
    for i, (label, value) in enumerate(kpis.items()):
        cols[i].metric(label, f"{value:,.2f}")

    # Plot time series of the selected numeric column
    if "date" in df_filtered.columns:
        fig = px.line(df_filtered.sort_values("date"), x="date", y=metric_col, title=f"{metric_col} Over Time")
        fig.update_layout(xaxis_title="Date", yaxis_title=metric_col)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.line_chart(df_filtered[metric_col], use_container_width=True)


def main():  # pragma: no cover - entry point for Streamlit
    render_dashboard()


if __name__ == "__main__":
    main()