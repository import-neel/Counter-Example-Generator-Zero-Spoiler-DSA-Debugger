# app/services/testcase_minimizer.py

def minimize_test_case(failing_input: list[int], target: int, student_func, reference_func) -> list[int]:
    """
    Simplifies a large failing list by systematically removing elements 
    while ensuring the student's code still produces a mismatch.
    """
    current_nums = list(failing_input)
    
    # Try removing elements one by one to find a smaller failing input
    i = 0
    while i < len(current_nums):
        reduced_nums = current_nums[:i] + current_nums[i+1:]
        
        # Keep length at least 2 for Two Sum constraints
        if len(reduced_nums) < 2:
            i += 1
            continue
            
        try:
            student_out = student_func(reduced_nums, target)
            ref_out = reference_func(reduced_nums, target)
            
            # If it still produces a mismatch, keep the reduced version
            if student_out != ref_out:
                current_nums = reduced_nums
            else:
                i += 1
        except Exception:
            # If it errors out on reduced input, skip removing this element
            i += 1
            
    return current_nums