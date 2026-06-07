import streamlit as st



def render_overview():
    """Render the overview page with project highlights and instructions."""
    st.title("🏠 Overview")
    st.write(
        """
        **NexusOps AI** is an educational demo that illustrates how you might build
        a professional business intelligence platform with **Streamlit**. It
        includes a data hub for uploading or connecting to datasets, a KPI
        dashboard, a simple forecasting lab, and basic anomaly detection. In a
        production application you could also implement an AI copilot, digital
        twin simulators, optimisation routines and more.

        This overview page summarises the core sections available in this demo:

        - **Data Hub**: Upload your own CSV file or use the built‑in sample
          dataset. Once loaded, you can inspect the first few rows and view
          summary statistics about the data.
        - **KPI Dashboard**: Visualise top‑level metrics such as total sales,
          average monthly sales and recent performance. Simple charts help
          illustrate trends over time.
        - **Forecasting Lab**: Experiment with a rudimentary forecasting model
          based on a linear trend. Select the number of future periods to
          forecast and review the results on an interactive plot.
        - **Anomaly Center**: Compute a z‑score based anomaly detection on your
          metrics and highlight any points that deviate significantly from the
          mean. This simple approach can flag potential issues or outliers.

        Use the navigation links in the sidebar to explore each section. If
        you'd like to extend this project, the repository structure under
        ``src`` is ready for further development.
        """
    )



def main():  # pragma: no cover - entry point for Streamlit
    render_overview()



if __name__ == "__main__":
    main()
