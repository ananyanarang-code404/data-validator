# ui/metrics.py

import streamlit as st


def _render_card(column, title, value, bg_color):
    column.markdown(
        f"""
        <div style='
            padding: 18px;
            border-radius: 16px;
            background: {bg_color};
            color: #111111;
            text-align: center;
            box-shadow: 0 6px 18px rgba(0,0,0,0.04);
        '>
            <div style='font-size: 14px; font-weight: 700; margin-bottom: 8px;'>
                {title}
            </div>
            <div style='font-size: 32px; font-weight: 700;'>
                {value}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metrics(total_rows, valid_rows, invalid_rows):
    invalid_pct = 0
    if total_rows:
        invalid_pct = round(invalid_rows / total_rows * 100, 1)

    col1, col2, col3, col4 = st.columns(4)

    _render_card(col1, "Total Rows", total_rows, "#e3f2fd")
    _render_card(col2, "Valid Rows", valid_rows, "#e8f5e9")
    _render_card(col3, "Invalid Rows", invalid_rows, "#ffebee")
    _render_card(col4, "Invalid Rate", f"{invalid_pct}%", "#fff3e0")