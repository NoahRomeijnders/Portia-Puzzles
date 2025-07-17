import re
import random
from collections import defaultdict
from copy import deepcopy
from portia_n_regex_parser import parse_puzzle_from_file
from portia_n_solver import solve_casket
import CNF_converter
from portia_n_solver import find_correct_casket
from portia_n_regex_parser import parse_puzzle



# all valid statements 
# Keys:
#   text  – the statement
#   refers_to  – the casket this statement references. None if reference is this
#   type  – the type of statement used to group statements


statement_objects = [
    {"text": "The portrait is in this casket", "refers_to": None, "type": "portrait"},
    {"text": "The portrait is in the gold casket", "refers_to": "gold", "type": "portrait"},
    {"text": "The portrait is in the silver casket", "refers_to": "silver", "type": "portrait"},
    {"text": "The portrait is in the lead casket", "refers_to": "lead", "type": "portrait"},
    {"text": "The portrait is not in this casket", "refers_to": None, "type": "portrait"},
    {"text": "The portrait is not in the gold casket", "refers_to": "gold", "type": "portrait"},
    {"text": "The portrait is not in the silver casket", "refers_to": "silver", "type": "portrait"},
    {"text": "The portrait is not in the lead casket", "refers_to": "lead", "type": "portrait"},

    {"text": "The statements on the gold casket are true", "refers_to": "gold", "type": "truth"},
    {"text": "The statements on the silver casket are true", "refers_to": "silver", "type": "truth"},
    {"text": "The statements on the lead casket are true", "refers_to": "lead", "type": "truth"},
    {"text": "The statements on the gold casket are false", "refers_to": "gold", "type": "truth"},
    {"text": "The statements on the silver casket are false", "refers_to": "silver", "type": "truth"},
    {"text": "The statements on the lead casket are false", "refers_to": "lead", "type": "truth"},

    {"text": "The other statements on this casket are true", "refers_to": None, "type": "other"},
    {"text": "The other statements on this casket are false", "refers_to": None, "type": "other"},
]


def create_statements(n):

    caskets = ["gold", "silver", "lead"]

    available_statements = [
        s for s in statement_objects
        if not (n == 1 and s["type"] == "other")
    ]

    allowed = {}
    for casket in caskets:
        allowed[casket] = [
            s for s in deepcopy(available_statements)
            if not (s["type"] == "truth" and s["refers_to"] == casket)  # remove self-truths
        ]
    selected = {c: [] for c in caskets}
    dependencies = {c: set() for c in caskets}

    def would_create_cycle(start, end):
        """Detect if adding start → end would form a cycle."""
        visited = set()

        def dfs(node):
            if node == start:
                return True
            visited.add(node)
            for neighbor in dependencies[node]:
                if neighbor not in visited and dfs(neighbor):
                    return True
            return False

        return dfs(end)

    for casket in caskets:
        count = 0
        while count < n:
            # Filter out truth statements that would cause indirect cycles
            valid_choices = []
            for stmt in allowed[casket]:
                if stmt["type"] == "truth" and stmt["refers_to"]:
                    target = stmt["refers_to"]
                    if would_create_cycle(casket, target):
                        continue
                valid_choices.append(stmt)

            if not valid_choices:
                raise ValueError(f"No valid statements left for {casket} due to cycle prevention.")

            stmt = random.choice(valid_choices)
            allowed[casket].remove(stmt)
            selected[casket].append(stmt["text"])

            # If it's a truth statement referencing another casket, update graph
            if stmt["type"] == "truth" and stmt["refers_to"]:
                dependencies[casket].add(stmt["refers_to"])

            count += 1

    return  selected["gold"] + selected["silver"] + selected["lead"]

    
        


def generate_puzzle(n, outputfile):

    MAX_ATTEMPTS = 50
    max_statements = 3 * n

    for attempt in range(1, MAX_ATTEMPTS + 1):
        print(f"Attempt {attempt}: Generating candidate puzzle...")

        # Step 1: Generate random statements
        try:
            statements_list = create_statements(n)
        except Exception as e:
            print(f"Failed to create statements: {e}")
            continue

        # Step 2: Format into candidate puzzle structure
        candidate_data = {
            "portia": n,
            "true_statements": 0,  # to be filled in
            "caskets": {
                "gold": statements_list[0:n],
                "silver": statements_list[n:2*n],
                "lead": statements_list[2*n:]
            }
        }

        # Step 3: Try all possible true counts
        for true_count in range(max_statements + 1):
            candidate_data["true_statements"] = true_count
            # Convert text into full Portia puzzle string
            puzzle_text = f"Portia {n}, There are {true_count} true statements\n" + "\n".join(statements_list)

            # Parse into structured format
            parsed_data = parse_puzzle(puzzle_text)

            # Evaluate using solver
            valid_caskets = find_correct_casket(parsed_data)

            if len(valid_caskets) == 1:
                # Found a unique solution!
                print(f"Success on attempt {attempt}: Unique solution with {true_count} true statement(s)")
                with open(outputfile, 'w', encoding='utf-8') as f:
                    f.write(f"Portia {n}, There are {true_count} true statements\n")
                    for casket in ["gold", "silver", "lead"]:
                        for line in candidate_data["caskets"][casket]:
                            f.write(f"{line}\n")
                return  # Done!

    # Step 4: If no valid puzzle was found
    raise ValueError(f"Failed to generate a uniquely solvable puzzle after {MAX_ATTEMPTS} attempts.")
   


