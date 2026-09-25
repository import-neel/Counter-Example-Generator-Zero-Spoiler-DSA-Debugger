import streamlit as st


def show_result(result):

    st.divider()

    st.subheader("Debug Result")

    status = result.get(
        "status",
        "unknown"
    )

    # -------------------------------
    # STATUS
    # -------------------------------

    if status == "accepted":

        st.success("✅ Accepted")

        return

    elif status == "wrong_answer":

        st.error("❌ Wrong Answer")

    elif status == "runtime_error":

        st.error("💥 Runtime Error")

    elif status == "timeout":

        st.error("⏱️ Time Limit Exceeded")

    else:

        st.warning(
            f"Status: {status}"
        )


    # -------------------------------
    # FAILURE TYPE
    # -------------------------------

    st.write(
        "**Failure Type:**",
        result.get(
            "failure_type",
            "Unknown"
        )
    )


    # -------------------------------
    # COUNTEREXAMPLE
    # -------------------------------

    counterexample = result.get(
        "counterexample",
        {}
    )

    st.subheader(
        "Counterexample"
    )


    col1, col2 = st.columns(2)


    with col1:

        st.markdown("### Input")

        st.code(
            counterexample.get(
                "input",
                ""
            )
        )


        st.markdown(
            "### Expected Output"
        )

        st.code(
            counterexample.get(
                "expected_output",
                ""
            )
        )


    with col2:

        st.markdown(
            "### Actual Output"
        )

        st.code(
            counterexample.get(
                "actual_output",
                ""
            )
        )


    # -------------------------------
    # HINT
    # -------------------------------

    hint = result.get("hint")


    if hint:

        st.subheader(
            "💡 Hint"
        )

        st.info(hint)


    # -------------------------------
    # NEXT HINT
    # -------------------------------

    if result.get(
        "next_hint_available",
        False
    ):

        st.caption(
            "A stronger hint is available. "
            "Increase the hint level and run again."
        )