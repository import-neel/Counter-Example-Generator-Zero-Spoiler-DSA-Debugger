# app/problems/arrays/two_sum.py

PROBLEM_METADATA = {
    "id": "array_001",
    "title": "Two Sum",
    "difficulty": "Easy",
    "category": "Arrays",
    "description": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.",
    "constraints": "2 <= nums.length <= 10^4, -10^9 <= nums[i] <= 10^9",
}

# The trusted reference solution (guaranteed correct)
def reference_solution(nums: list[int], target: int) -> list[int]:
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []

# Input generator for testing
import random
def generate_random_input():
    size = random.randint(2, 20)
    nums = [random.randint(-50, 50) for _ in range(size)]
    if len(nums) >= 2:
        a, b = random.sample(range(size), 2)
        target = nums[a] + nums[b]
    else:
        target = 0
    return {"nums": nums, "target": target}