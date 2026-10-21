import os

from dotenv import load_dotenv

from frontend.services.hint_generator import (
    fallback_hint
)

from frontend.services.spoiler_detector import (
    safe_response
)


load_dotenv()


def build_prompt(
    problem,
    student_code,
    counterexample,
    failure_type,
    hint_level
):

    prompt = f"""
You are a zero-spoiler DSA debugging tutor.

Problem:
{problem}

Student code:
{student_code}

Failure type:
{failure_type}

Counterexample input:
{counterexample.get("input", "")}

Expected output:
{counterexample.get("expected_output", "")}

Actual output:
{counterexample.get("actual_output", "")}

Hint level:
{hint_level}

Rules:

1. Use only the execution evidence provided.

2. Explain why the observed input exposes
   a weakness.

3. Do NOT provide corrected code.

4. Do NOT provide the complete algorithm.

5. Do NOT reveal the final solution.

6. Give a hint appropriate for the
   requested hint level.

7. Return JSON only.

Required format:

{{
    "hint": "...",
    "next_hint_available": true
}}
"""

    return prompt.strip()


def generate_ai_hint(
    problem,
    student_code,
    counterexample,
    failure_type,
    hint_level
):

    fallback = fallback_hint(
        hint_level,
        failure_type
    )


    api_key = os.getenv(
        "AI_API_KEY"
    )


    # --------------------------------
    # No API key
    # --------------------------------

    if not api_key:

        return {

            "hint":
                fallback,

            "next_hint_available":
                hint_level < 5,

            "source":
                "fallback"
        }


    # --------------------------------
    # AI API will be connected later
    # --------------------------------

    return {

        "hint":
            fallback,

        "next_hint_available":
            hint_level < 5,

        "source":
            "fallback_until_api_connected"
    }