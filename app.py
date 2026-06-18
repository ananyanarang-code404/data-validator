import streamlit as st

from config.constants import DEFAULT_PHONE_RULES, DATE_FORMATS
from services.csv_service import CSVService
from services.validation_service import ValidationService

from ui.metrics import render_metrics
from ui.dashboard import render_preview
from ui.downloads import render_download_buttons

PHONE_RULES = DEFAULT_PHONE_RULES
DATE_FORMAT = DATE_FORMATS["YYYY-MM-DD"]


def main():

    uploaded_file = st.file_uploader(
        "Upload CSV",
        type=["csv"]
    )

    if not uploaded_file:
        return

    df = CSVService.load_csv(uploaded_file)

    valid_df, invalid_df = (
        ValidationService.validate_dataframe(
            df,
            PHONE_RULES,
            DATE_FORMAT
        )
    )

    render_metrics(
        len(df),
        len(valid_df),
        len(invalid_df)
    )

    render_preview(
        valid_df,
        invalid_df
    )

    render_download_buttons(
        valid_df,
        invalid_df
    )


if __name__ == "__main__":
    main()