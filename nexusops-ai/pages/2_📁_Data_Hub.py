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

    # Display dataset if available
    dataset = st.session_state.get("dataset")
    if dataset is not None:
        st.subheader("Preview of Loaded Data")
        st.dataframe(dataset.head())
        st.write("Rows:", len(dataset))
        st.write("Columns:", list(dataset.columns))


def main():  # pragma: no cover - entry point for Streamlit
    render_data_hub()


if __name__ == "__main__":
    main()
