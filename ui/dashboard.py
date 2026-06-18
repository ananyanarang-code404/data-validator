import streamlit as st


def _highlight_rows(row, is_invalid=False):
    base = "background-color: #0a0a0a;" if not is_invalid else "background-color:#0a0a0a;"
    return [base for _ in row]


def render_preview(
    valid_df,
    invalid_df,
    show_full=False
):
    st.subheader("Preview")

    tabs = st.tabs(["Clean Records", "Invalid Records"])

    with tabs[0]:
        st.success("Clean records pass validation rules.")
        st.write(
            "Showing "
            f"{'all' if show_full else 'top 100'} clean records"
        )
        valid_view = valid_df if show_full else valid_df.head(100)
        styled_valid = (
            valid_view.style.apply(
                _highlight_rows,
                axis=1,
                is_invalid=False
            )
            if not valid_view.empty else valid_view
        )
        st.dataframe(
            styled_valid,
            use_container_width=True
        )

    with tabs[1]:
        st.error("Invalid records contain one or more validation errors.")
        st.write(
            "Showing "
            f"{'all' if show_full else 'top 100'} invalid records"
        )
        invalid_view = invalid_df if show_full else invalid_df.head(100)
        styled_invalid = (
            invalid_view.style.apply(
                _highlight_rows,
                axis=1,
                is_invalid=True
            )
            if not invalid_view.empty else invalid_view
        )
        st.dataframe(
            styled_invalid,
            use_container_width=True
        )
