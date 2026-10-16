# app/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import sys

# Ensure project root is in path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from services.test_runner import run_differential_test
from services.testcase_minimizer import minimize_test_case
from services.bug_classifier import classify_bug

app = FastAPI(title="DSA Counterexample Debugger API", version="1.0")

# Request model from the frontend
class DebugRequest(BaseModel):
    problem_id: str
    student_code_snippet: str

# Trusted reference solution for Two Sum
def reference_solution(nums: list[int], target: int) -> list[int]:
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []

@app.post("/api/debug")
def debug_submission(payload: DebugRequest):
    """
    Receives student submission, runs differential testing, 
    minimizes counterexamples, and classifies the bug.
    """
    test_cases = [
        {"nums": [2, 7, 11, 15], "target": 9},
        {"nums": [3, 2, 4], "target": 6},
        {"nums": [3, 3], "target": 6}
    ]
    
    # Simulating a student implementation that returns an empty output
    def student_func(nums, target):
        return []
        
    # 1. Run differential test
    test_result = run_differential_test(student_func, reference_solution, test_cases)
    
    response_data = {
        "status": test_result["status"],
        "bug_classification": None,
        "minimized_counterexample": None
    }
    
    if test_result["status"] == "FAILED":
        failing_input = test_result["test_case"]["nums"]
        target = test_result["test_case"]["target"]
        minimized = minimize_test_case(failing_input, target, student_func, reference_solution)
        bug_type = classify_bug(None, test_result["actual"], test_result["expected"])
        
        response_data["bug_classification"] = bug_type
        response_data["minimized_counterexample"] = {"nums": minimized, "target": target}
        
    return response_data