import streamlit as st

from frontend.components.problem_selector import (
    problem_selector
)

from frontend.components.code_editor import (
    code_editor
)

from frontend.components.result_view import (
    show_result
)

from frontend.services.backend_client import (
    debug_submission
)


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(

    page_title=
        "Zero-Spoiler DSA Debugger",

    page_icon=
        "🐛",

    layout=
        "wide"
)


# ==========================================
# HEADER
# ==========================================

st.title(
    "🐛 Zero-Spoiler DSA Debugger"
)

st.caption(
    "Find why your DSA code fails "
    "without immediately revealing the solution."
)


# ==========================================
# PROBLEM SELECTION
# ==========================================

problem = problem_selector()


# ==========================================
# CODE EDITOR
# ==========================================

code = code_editor()


# ==========================================
# HINT LEVEL
# ==========================================

hint_level = st.slider(

    "Hint Level",

    min_value=1,

    max_value=5,

    value=1
)


# ==========================================
# DEBUG BUTTON
# ==========================================

if st.button(
    "🔍 Debug Code",
    type="primary"
):

    if not code.strip():

        st.warning(
            "Please enter your code first."
        )

    else:

        with st.spinner(
            "Running debugger..."
        ):

            result = debug_submission(

                problem_id=
                    problem["id"],

                language=
                    "python",

                code=
                    code,

                hint_level=
                    hint_level
            )


        # Display result

        show_result(result)