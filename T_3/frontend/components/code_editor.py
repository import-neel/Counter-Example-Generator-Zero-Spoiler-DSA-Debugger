import streamlit as st


DEFAULT_CODE = """def two_sum(arr, target):
    # Write your solution here
    pass
"""


def code_editor():

    code = st.text_area(
        "Your Python Code",
        value=DEFAULT_CODE,
        height=350
    )

    return code
