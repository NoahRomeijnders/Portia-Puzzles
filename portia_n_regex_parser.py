import re
import json
from collections import defaultdict, deque


def parse_puzzle(text):
    """
    Parses all Portia-n-m puzzles with valid statements

    input : text = plain text representation of Portia-n-m puzzle

    output: JSON representation of Portia-n-m puzzle
    
    """
    # Split input into lines
    lines = text.strip().split("\n")

    # Extract "Portia n" and number of true statements
    portia_match = re.match(r"Portia (\d+), There are (\d+) true statements", lines[0])
    
    
    if not portia_match:
        raise ValueError("Invalid Portia header format")

    portia_number = int(portia_match.group(1))
    true_statements_count = int(portia_match.group(2))

    # Define expected casket names
    expected_caskets = ["gold", "silver", "lead"]

    # Prepare extracted data
    extracted_data = {
        "portia": portia_number,
        "true_statements": true_statements_count,
        "caskets": {casket: [] for casket in expected_caskets}  # Store statements per casket
    }

    # Regex pattern to extract statements (they can reference any casket)
    statement_pattern = re.compile(r"The portrait is (not )?in (?:the (\w+)|this) casket")
    truth_pattern = re.compile(r"The statement(?:s)? on the (\w+) casket (?:is|are) (true|false)")
    other_pattern = re.compile(r"The other statement(?:s)? on this casket (?:is|are) (true|false)")

    for i, sentence in enumerate(lines[1:]):
        # Determine which casket this statement belongs to
        if i < portia_number:
            casket_name = "gold"
        elif i < 2 * portia_number:
            casket_name = "silver"
        else:
            casket_name = "lead"



        match = statement_pattern.match(sentence)
        if match:
            
            statement_data = {
                "contains_portrait": not(bool(match.group(1))),  # False if not is present
                "mentioned_casket": match.group(2) if match.group(2) else casket_name# The casket being referenced (e.g., "gold")
            }
        
        truth_match =  truth_pattern.match(sentence)
        if truth_match:
            
            if casket_name ==  truth_match.group(1):
                 raise ValueError(f"Statement on {casket_name} cannot reference {truth_match.group(1)}")
            statement_data = {
                "mentioned_casket" : truth_match.group(1),  # The case (e.g., "gold")
                "statement_truth" : truth_match.group(2)  # True or False
            }
        
        other_match =  other_pattern.match(sentence)
        if other_match:
            
            statement_data = {
                "other_statements_truth" : other_match.group(1)  # True or False
            }

        
        extracted_data["caskets"][casket_name].append(statement_data)
            
    # Validation: Ensure exactly 3 caskets
    if set(extracted_data["caskets"].keys()) != set(expected_caskets):
        raise ValueError(f"Invalid caskets! Expected {expected_caskets}, but found {set(extracted_data['caskets'].keys())}")

    # Validation: Ensure each casket has exactly `n` statements
    for casket, statements in extracted_data["caskets"].items():
        if len(statements) != portia_number:
            raise ValueError(f"Casket '{casket}' has {len(statements)} statements, but Portia {portia_number} requires {portia_number}.")

    # Validation: Ensure 0 <= true statements <= 3n
    max_statements = 3 * portia_number
    if not (0 <= true_statements_count <= max_statements):
        raise ValueError(f"Invalid number of true statements! Expected between 0 and {max_statements}, but found {true_statements_count}.")
    


    return extracted_data




def has_cycle(graph):
    """
    Cycle detection using DFS

    input : graph = tree graph 

    output: boolean, True if and only if the graph has a cycle
    
    """
    visited = set()
    path = set()

    def visit(node):
        if node in path:
            return True
        if node in visited:
            return False
        path.add(node)
        for neighbor in graph[node]:
            if visit(neighbor):
                return True
        path.remove(node)
        visited.add(node)
        return False

    return any(visit(node) for node in graph)


def parse_puzzle_from_file(input_filename, output_filename):
    """Reads a Portia-n-m puzzle from a file, parses it, and writes the output to another file.
    Input : File containing a valid Portia-n-m puzzle
    
    output : File containing the JSON repressentation of this puzzle
    """
    try:
        with open(input_filename, "r", encoding="utf-8") as file:
            puzzle_text = file.read()

        parsed_data = parse_puzzle(puzzle_text)

        with open(output_filename, "w", encoding="utf-8") as out_file:
            json.dump(parsed_data, out_file, indent=4)



    except Exception as e:
        print(f"Error: {e}")
    




