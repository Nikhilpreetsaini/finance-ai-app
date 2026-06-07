import io
from typing import Optional

import pandas as pd
import streamlit as st


def load_sample_data() -> pd.DataFrame:
    """Load the sample sales dataset packaged with the repository.

    Returns:
        DataFrame: A pandas DataFrame containing the sample data.
    """
    sample_path = "data/sample/sales_data.csv"
    return pd.read_csv(sample_path, parse_dates=["date"])


def upload_data() -> Optional[pd.DataFrame]:
    """Handle file upload and return a DataFrame if successful.

    Returns:
        Optional[DataFrame]: A pandas DataFrame of the uploaded data or None
        if no file was uploaded.
    """
    uploaded_file = st.file_uploader(
        "Upload a CSV file containing your business data",
        type=["csv"],
        help="Drag and drop or browse to select a CSV file. The file should have a date column and at least one numeric metric column.",
    )
    if uploaded_file is not None:
        try:
            data = pd.read_csv(io.StringIO(uploaded_file.getvalue().decode("utf-8")))
            # Try to parse dates automatically on a column named 'date'
            if "date" in data.columns:
                data["date"] = pd.to_datetime(data["date"])
            return data
        except Exception as e:
            st.error(f"Error reading uploaded file: {e}")
    return None


def render_data_hub():
    """Render the Data Hub page where users can upload or select data."""
    st.title("📁 Data Hub")
    st.write(
        """
        The Data Hub allows you to upload a CSV file or work with the built‑in
        sample dataset. Uploaded data is stored in the Streamlit session so
        that other pages (dashboard, forecasting, anomaly detection) can reuse
        it. To get the most out of this app, your data should have a **date**
        column and at least one **numeric** column (e.g. sales, revenue,
        expenses).
        """
    )

    # Initialise session state storage for the dataset
    if "dataset" not in st.session_state:
        st.session_state.dataset = None

    # File upload
    data = upload_data()
    if data is not None:
        st.session_state.dataset = data
        st.success("File uploaded successfully!")

    # Sample data button
    if st.button("Use sample sales data"):
        st.session_state.dataset = load_sample_data()
        st.success("Sample data loaded.")

    # Display dataset and quality report if available
    dataset = st.session_state.get("dataset")
    if dataset is not None:
        st.subheader("Preview of Loaded Data")
        st.dataframe(dataset.head())
        st.write("Rows:", len(dataset))
        st.write("Columns:", list(dataset.columns))

        # Compute data quality metrics
        def _data_quality_report(df: pd.DataFrame) -> pd.DataFrame:
            """Create a simple data quality report for the loaded dataframe.

            The report includes completeness (non‑null ratio), uniqueness
            (distinct values ratio) and type information for each column.

            Args:
                df: Loaded DataFrame.

            Returns:
                A DataFrame summarising data quality metrics per column.
            """
            report_rows = []
            n_rows = len(df)
            for col in df.columns:
                col_data = df[col]
                missing = col_data.isna().sum()
                completeness = 1.0 - (missing / n_rows) if n_rows else 0.0
                unique = col_data.nunique(dropna=True)
                uniqueness = unique / n_rows if n_rows else 0.0
                dtype = str(col_data.dtype)
                report_rows.append({
                    "Column": col,
                    "Type": dtype,
                    "Missing": missing,
                    "Completeness (%)": round(completeness * 100, 2),
                    "Distinct": unique,
                    "Uniqueness (%)": round(uniqueness * 100, 2),
                })
            return pd.DataFrame(report_rows)

        dq_report = _data_quality_report(dataset)
        # Compute an overall data quality score as weighted mean of completeness and uniqueness
        completeness_score = dq_report["Completeness (%)"].mean() if not dq_report.empty else 0.0
        uniqueness_score = dq_report["Uniqueness (%)"].mean() if not dq_report.empty else 0.0
        # Weight completeness higher than uniqueness
        overall_dq = (0.7 * completeness_score + 0.3 * uniqueness_score) / 100.0

        st.subheader("Data Quality Report")
        st.dataframe(dq_report)
        st.write(f"**Overall Data Quality Score:** {overall_dq:.2f} (0–1 scale)")


def main():  # pragma: no cover - entry point for Streamlit
    render_data_hub()


if __name__ == "__main__":
    main()