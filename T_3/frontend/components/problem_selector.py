import streamlit as st


PROBLEMS = [
    {
        "id": "two_sum_001",
        "title": "Two Sum",
        "difficulty": "Easy",
        "category": "Arrays"
    },
    {
        "id": "binary_search_001",
        "title": "Binary Search",
        "difficulty": "Easy",
        "category": "Searching"
    },
    {
        "id": "sorting_001",
        "title": "Sorting",
        "difficulty": "Easy",
        "category": "Sorting"
    },
    {
        "id": "stack_001",
        "title": "Stack",
        "difficulty": "Easy",
        "category": "Stack"
    }
]


def problem_selector():

    labels = []

    for problem in PROBLEMS:

        label = (
            f'{problem["title"]} - '
            f'{problem["difficulty"]} '
            f'({problem["category"]})'
        )

        labels.append(label)

    selected = st.selectbox(
        "Select a DSA Problem",
        labels
    )

    index = labels.index(selected)

    return PROBLEMS[index]