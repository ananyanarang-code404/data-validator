# ui/metrics.py

import streamlit as st


def render_metrics(total_rows, valid_rows, invalid_rows):
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Total Rows",
            total_rows
        )

    with col2:
        st.metric(
            "Valid Rows",
            valid_rows
        )

    with col3:
        st.metric(
            "Invalid Rows",
            invalid_rows
        )