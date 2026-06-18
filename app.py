import streamlit as st

from config.constants import DEFAULT_PHONE_RULES, DATE_FORMATS as AVAILABLE_DATE_FORMATS
from services.csv_service import CSVService
from services.validation_service import ValidationService

from ui.metrics import render_metrics
from ui.dashboard import render_preview
from ui.downloads import render_download_buttons

PHONE_RULES = DEFAULT_PHONE_RULES
DATE_FORMATS = AVAILABLE_DATE_FORMATS


def main():
    st.set_page_config(
        page_title="CSV Data Validator",
        page_icon="🧾",
        layout="wide"
    )

    st.title("Data Validator")
    st.write(
        "Upload a CSV file to validate order records for phone, date, payment mode, and payment status."
    )

    with st.sidebar:
        st.header("Upload & settings")

        uploaded_file = st.file_uploader(
            "Choose a CSV file",
            type=["csv"],
            key="csv_file_uploader"
        )

        date_format_key = st.selectbox(
            "Order date format",
            list(DATE_FORMATS.keys()),
            index=0
        )

        show_full_preview = st.checkbox(
            "Show full preview",
            value=False,
            help="Display all rows in the preview tables. Use for smaller files only."
        )

        st.markdown(
            "---\n"
            "This tool validates CSV rows and separates clean records from rows with validation errors."
        )

    if not uploaded_file:
        st.info("Upload a CSV file from the sidebar to start validation.")
        return

    df = CSVService.load_csv(uploaded_file)

    valid_df, invalid_df = ValidationService.validate_dataframe(
        df,
        PHONE_RULES,
        DATE_FORMATS[date_format_key]
    )

    render_metrics(
        len(df),
        len(valid_df),
        len(invalid_df)
    )

    render_preview(
        valid_df,
        invalid_df,
        show_full=show_full_preview
    )

    render_download_buttons(
        valid_df,
        invalid_df
    )


if __name__ == "__main__":
    main()

