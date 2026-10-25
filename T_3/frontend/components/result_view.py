
import streamlit as st


def show_result(result):
    st.divider()
    st.subheader("Debug Result")

    status = str(result.get("status", "unknown")).lower()

    # Handle analysis results, if supplied by the test engine.
    if status in ("accepted", "wrong_answer"):
        if status == "accepted":
            st.success("Accepted")
            return

        st.error("Wrong Answer")

        st.write(
            "**Failure Type:**",
            result.get("failure_type", "Wrong Answer")
        )

        counterexample = result.get("counterexample") or {}

        st.subheader("Counterexample")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Input**")
            st.code(str(counterexample.get("input", "Not available")))

            st.markdown("**Expected Output**")
            st.code(str(counterexample.get("expected_output", "Not available")))

        with col2:
            st.markdown("**Actual Output**")
            st.code(str(counterexample.get("actual_output", "Not available")))

        hint = result.get("hint")
        if hint:
            st.subheader("Hint")
            st.info(hint)

        if result.get("next_hint_available", False):
            st.caption(
                "A stronger hint is available. Increase the hint level "
                "and run the debugger again."
            )

        return

    # Handle the execution response returned by the current FastAPI backend.
    if status == "success":
        st.success("Execution completed successfully")
        st.info(
            "This confirms the program ran, not that its algorithm is correct. "
            "A reference test is needed to detect wrong answers."
        )
    elif status == "timeout":
        st.error("Time Limit Exceeded")
    elif status == "syntax_error":
        st.error("Syntax Error")
    elif status == "runtime_error":
        st.error("Runtime Error")
    else:
        st.warning(f"Execution status: {status}")

    st.write(
        "**Failure / Error Details:**",
        result.get("error_message") or "No additional error message"
    )

    stdout = result.get("stdout", "")
    stderr = result.get("stderr", "")

    st.markdown("### Program Output (stdout)")
    st.code(stdout if stdout else "(No output)")

    if stderr:
        st.markdown("### Error Output (stderr)")
        st.code(stderr)

    if result.get("exit_code") is not None:
        st.caption(f"Exit code: {result['exit_code']}")

    if result.get("execution_time") is not None:
        st.caption(f"Execution time: {result['execution_time']:.4f} seconds")
