HINTS = {

    "duplicate_handling": {

        1:
        "Check whether your algorithm works "
        "for all valid inputs.",

        2:
        "Pay attention to cases where the "
        "same value appears more than once.",

        3:
        "Think about how previously processed "
        "values are stored and reused.",

        4:
        "The failure occurs when two equal "
        "values can jointly satisfy the target.",

        5:
        "Inspect the logic that searches for "
        "a previously processed value. "
        "The failing input contains a duplicate pair."
    },


    "boundary_condition": {

        1:
        "Check what happens at the smallest "
        "valid input.",

        2:
        "Test the first and last valid "
        "positions carefully.",

        3:
        "Review the condition that decides "
        "whether an element is processed.",

        4:
        "The failing case occurs at a boundary "
        "that your current condition does not handle.",

        5:
        "Trace the first valid element through "
        "your condition and compare it with "
        "the expected behavior."
    }
}


def fallback_hint(
    level,
    failure_type
):

    hints = HINTS.get(
        failure_type,
        HINTS["boundary_condition"]
    )

    return hints.get(
        level,
        hints[1]
    )