# app/services/bug_classifier.py

def classify_bug(error_message: str | None, student_output, expected_output) -> str:
    """Classifies the test failure into specific bug categories for the student."""
    if error_message:
        if "IndexError" in error_message:
            return "Off-by-one or Index Boundary Error"
        elif "RecursionError" in error_message:
            return "Infinite Recursion or Missing Base Case"
        elif "TypeError" in error_message or "ValueError" in error_message:
            return "Data Type or Argument Mismatch Error"
        else:
            return f"Runtime Error: {error_message}"
            
    if student_output is None:
        return "Incorrect Initialization or Missing Return Statement"
    elif student_output == []:
        return "Empty Output Returned (Check Search Condition)"
    else:
        return "Logic Mismatch (Wrong Answer for Given Inputs)"