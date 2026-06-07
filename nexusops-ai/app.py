import streamlit as st



def main():
    """
    Main entry point for the NexusOps AI application.

    This file configures the Streamlit app and provides a simple landing page that
    introduces the project. Additional functionality is implemented in the
    individual files within the ``pages`` directory. When deployed on
    Streamlit Community Cloud or run locally via ``streamlit run app.py``, the
    app will automatically detect pages in the ``pages`` folder and display
    navigation links in the sidebar.

    The goal of this project is to provide a professional demonstration of a
    business intelligence platform built with Streamlit. Users can upload
    datasets, view KPIs, perform simple forecasts, detect anomalies and more.
    """
    # Set up the overall app configuration. Using a wide layout makes better use
    # of available screen space when viewing dashboards and charts.
    st.set_page_config(
        page_title="NexusOps AI",
        page_icon="💼",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Render the landing page content. Streamlit automatically adds a sidebar
    # navigation section for files placed in ``pages``. Here we simply display
    # a welcome message and instructions for getting started.
    st.title("NexusOps AI")
    st.subheader("Business Decision Intelligence & Digital Twin Platform")

    st.markdown(
        """
        Welcome to **NexusOps AI**, an AI‑powered business intelligence demo built
        with **Python** and **Streamlit**. This app showcases how you can:

        * Upload and inspect your business data
        * Visualise key performance indicators (KPIs)
        * Forecast future trends using basic time‑series models
        * Detect simple anomalies in your metrics

        Use the sidebar on the left to navigate between pages. If you don't
        have your own data handy, try the sample data included in the
        repository (`data/sample/sales_data.csv`).

        For more information about the full vision of this project, refer to
        the **README** in the repository. This minimal implementation is a
        starting point; you can extend it with advanced models, a chat copilot,
        simulation, optimisation and other features described in the project
        overview.
        """
    )



if __name__ == "__main__":
    main()
