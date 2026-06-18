import streamlit as st


def render_preview(
    valid_df,
    invalid_df
):
    st.subheader("Clean Records")
    st.dataframe(valid_df.head())

    st.subheader("Invalid Records")
    st.dataframe(invalid_df.head())