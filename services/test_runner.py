# app/services/test_runner.py

def run_differential_test(student_func, reference_func, test_inputs: list):
    """
    Compares the student's function output against the reference function output 
    across a list of test cases.
    """
    for index, test_case in enumerate(test_inputs):
        try:
            # Execute both functions with the same test input dictionary
            ref_output = reference_func(**test_case)
            student_output = student_func(**test_case)
            
            # Compare results
            if student_output != ref_output:
                return {
                    "status": "FAILED",
                    "test_case": test_case,
                    "expected": ref_output,
                    "actual": student_output
                }
        except Exception as e:
            return {
                "status": "RUNTIME_ERROR",
                "test_case": test_case,
                "error": str(e)
            }
            
    return {"status": "PASSED"}