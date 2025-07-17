import re

def extract_info(sentence):
    position_pattern = r"(\w+) is (not )?(?:in the|on the) (\w+) case"
    truth_pattern = r"(\w+) (?:on the|in the) (\w+) case are (true|false)"
    
    extracted_info = {}

    # Extract object and position, handling negation
    position_match = re.search(position_pattern, sentence)
    if position_match:
        extracted_info["object"] = position_match.group(1)  # The entity (e.g., "portrait")
        extracted_info["location"] = position_match.group(3)  # The case (e.g., "gold")
        extracted_info["object_not_in_location"] = bool(position_match.group(2))  # True if "not" is present

    # Extract truth value
    truth_match = re.search(truth_pattern, sentence)
    if truth_match:
        extracted_info["object"] = truth_match.group(1)  # The entity (e.g., "statement")
        extracted_info["location"] = truth_match.group(2)  # The case (e.g., "gold")
        extracted_info["statement_truth"] = truth_match.group(3)  # True or False

    return extracted_info

# Test cases
sentences = [
    "The statement on the gold case are false",
    "The portrait is in the silver case",
    "The portrait is not in the gold case"
]

for s in sentences:
    print(extract_info(s))

