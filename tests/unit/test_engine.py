# tests/unit/test_engine.py
import sys
import os
import pytest

# Add project root to Python path so 'app' can be imported reliably
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Trusted reference solution for Two Sum
def reference_solution(nums: list[int], target: int) -> list[int]:
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []

# Import your core backend services
from services.test_runner import run_differential_test
from services.testcase_minimizer import minimize_test_case
from services.bug_classifier import classify_bug

# A buggy student solution that always returns an empty list
def buggy_student_solution(nums, target):
    return []

def test_differential_and_minimization():
    test_cases = [
        {"nums": [2, 7, 11, 15], "target": 9},
        {"nums": [3, 2, 4], "target": 6},
    ]
    
    # 1. Run differential test
    result = run_differential_test(buggy_student_solution, reference_solution, test_cases)
    assert result["status"] == "FAILED"
    
    # 2. Test minimization on a larger failing case
    large_failing_input = [10, 20, 2, 7, 30, 40]
    minimized = minimize_test_case(large_failing_input, 9, buggy_student_solution, reference_solution)
    assert len(minimized) <= len(large_failing_input)
    
    # 3. Classify the bug
    bug_type = classify_bug(None, result["actual"], result["expected"])
    assert "Empty Output Returned" in bug_type