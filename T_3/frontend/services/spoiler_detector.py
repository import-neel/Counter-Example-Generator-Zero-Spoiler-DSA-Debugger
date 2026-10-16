import re


FORBIDDEN_PHRASES = [

    "here is the corrected code",

    "here's the corrected code",

    "complete solution",

    "full solution",

    "replace your code with",

    "use this code instead",

    "corrected implementation"
]


def contains_spoiler(text):

    lowered = text.lower()


    for phrase in FORBIDDEN_PHRASES:

        if phrase in lowered:

            return True


    # Detect fenced code blocks

    if len(
        re.findall(
            r"```",
            text
        )
    ) >= 2:

        return True


    return False


def safe_response(
    text,
    fallback
):

    if not text:

        return fallback


    if contains_spoiler(text):

        return fallback


    return text