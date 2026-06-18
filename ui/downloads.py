# ui/downloads.py

import streamlit as st

from services.csv_service import CSVService


def render_download_buttons(
    valid_df,
    invalid_df
):
    st.subheader("Downloads")

    if not valid_df.empty:
        st.download_button(
            label="Download Clean Data",
            data=CSVService.export_csv(valid_df),
            file_name="cleaned_data.csv",
            mime="text/csv"
        )

    if not invalid_df.empty:
        st.download_button(
            label="Download Error Report",
            data=CSVService.export_csv(invalid_df),
            file_name="error_report.csv",
            mime="text/csv"
        )