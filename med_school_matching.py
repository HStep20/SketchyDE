from thefuzz import process, fuzz
import pandas as pd
import re


def normalize_string(input_string):
    banned_words = ["university", "of", "college", "north", "south", "east", "west"]
    normalized_string = input_string.lower()
    for word in banned_words:
        normalized_string = normalized_string.replace(word, "")

    normalized_string = re.sub(r" +", " ", normalized_string)
    normalized_string = re.sub(r"[^ a-zA-Z0-9]", " ", normalized_string)
    normalized_string = normalized_string.strip()
    return normalized_string


def match_med_school(universities_data: pd.DataFrame, enrollment_name:str, state_code:str) -> tuple:
    """Uses TheFuzz library to do a levenstein match on text and the states coded within the school

    Args:
        universities_data (pd.DataFrame): All Uni data from our lookup table
        enrollment_name (str): Name of the school we are matching for in the table
        state_code (str): State abbreviation

    Returns:
        tuple: tuple consisting of (match, match confidence, school id)
    """
    state_universities = universities_data[universities_data["state"] == state_code]
    normalized_uni_name = normalize_string(enrollment_name)
    potential_matches = process.extract(
        normalized_uni_name,
        state_universities["name"],
        limit=5,
        scorer=fuzz.partial_ratio,
    )
    return max(potential_matches, key=lambda x: x[1])


def match_schools(universities_data:pd.DataFrame, enrollment_data:pd.DataFrame) -> pd.DataFrame:
    """Takes in two DFs of Uni data and enrollment data, and creates as 'fuzzy join' on the school name

    Args:
        universities_data (pd.DataFrame): lookup table
        enrollment_data (pd.DataFrame): official attendance numbers of schools across the country

    Returns:
        pd.DataFrame: final 'fuzzy joined' table of uni IDs and school attendance
    """

    universities_data = universities_data.loc[
    universities_data["country"] == "United States of America"
    ]
    enrollment_data = enrollment_data.to_dict("records")
    new_df = []

    for row in enrollment_data:
        enrollment_name = row["Medical School"]
        state_code = row["State"]
        matched_name = match_med_school(universities_data, enrollment_name, state_code)
        new_df.append(
            {
                "original_name": enrollment_name,
                "matched_name": matched_name[0],
                "confidence": matched_name[1],
                "university_id": matched_name[2],
                "student_count": row["All"],
            }
        )
        row_index = universities_data.index[universities_data["name"] == matched_name[0]].to_list()
        universities_data = universities_data.drop(row_index)
    
    df = pd.DataFrame(new_df).sort_values(["confidence"])
    df.to_excel(
        "med_school_scoring.xlsx", index=False
    )
    return df
