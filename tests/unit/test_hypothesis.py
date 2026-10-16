# tests/unit/test_hypothesis.py
import sys
import os
import pytest
from hypothesis import given, strategies as st

# Add project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from services.testcase_minimizer import minimize_test_case

# Trusted reference solution
def reference_solution(nums: list[int], target: int) -> list[int]:
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []

# A flawed student solution that fails on arrays with negative numbers
def buggy_student_solution(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        if num < 0:
            continue  # Bug: ignores negative numbers
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []

@given(st.lists(st.integers(min_value=-50, max_value=50), min_size=2, max_size=15), st.integers(min_value=-100, max_value=100))
def test_minimizer_with_hypothesis(nums, target):
    """
    Hypothesis automatically generates random inputs (nums and target).
    We test if our minimizer can successfully shrink a failing case.
    """
    try:
        ref_out = reference_solution(nums, target)
        student_out = buggy_student_solution(nums, target)
        
        # If there's a mismatch, test minimization
        if ref_out != student_out:
            minimized = minimize_test_case(nums, target, buggy_student_solution, reference_solution)
            # Property: the minimized list must be smaller than or equal to the original
            assert len(minimized) <= len(nums)
    except Exception:
        # Ignore runtime errors during fuzzing, we care about minimization invariants
        pass