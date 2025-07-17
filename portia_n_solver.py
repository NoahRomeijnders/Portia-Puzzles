import json

def evaluate_statement(assumed_casket, statement, parsed_data, current_casket):
    """
    evaluates a single statement

    input : assumed_casket = casket {gold, silver,lead} that contains portrait
            statement = statement to evaluate
            parsed_data = full statement list
            current_casket = casket this statement is located on

    output: boolean True if and only if statement evaluates to true
    
    """
    
    if "contains_portrait" in statement:
        return eval_statement_pattern(statement, assumed_casket)
    elif "mentioned_casket" and "statement_truth" in statement:
        return eval_truth_pattern(statement, assumed_casket, parsed_data)
    else:
        return eval_other_pattern(statement, assumed_casket, parsed_data , current_casket)


def check_statements(assumed_casket, parsed_data):
    """
    count how many 

    input : assumed_casket = casket {gold, silver,lead} that contains portrait
            parsed_data = full statement list
            
    output: int number of statements that evaluate to true
    
    """
    true_count = 0  # Count how many statements are true

    for casket, data in parsed_data["caskets"].items():
        for statement in data:
            if(evaluate_statement(assumed_casket, statement, parsed_data, casket)):
                true_count += 1 

    # print(f" The {assumed_casket} casket has {true_count} true statements")    
    return true_count



def eval_statement_pattern(statement, assumed_casket):
    """
    evaluates a statement pattern statement

    input : assumed_casket = casket {gold, silver,lead} that contains portrait
            statement = statement to evaluate

    output: boolean True if and only if statement evaluates to true
    
    """
    return (statement["mentioned_casket"] == assumed_casket) == statement["contains_portrait"]

def eval_truth_pattern(statement, assumed_casket, parsed_data):
    """
    evaluates a eval pattern statement

    input : assumed_casket = casket {gold, silver,lead} that contains portrait
            statement = statement to evaluate
            parsed_data = full statement list

    output: boolean True if and only if statement evaluates to true
    
    """
    mentioned_casket = statement["mentioned_casket"]
    statements_to_check = parsed_data["caskets"][mentioned_casket]

    if statement["statement_truth"] == "true":
        for mentioned_statement in statements_to_check:
            if not evaluate_statement(assumed_casket, mentioned_statement, parsed_data, mentioned_casket):
                return False
    else:
        for mentioned_statement in statements_to_check:
            if evaluate_statement(assumed_casket, mentioned_statement, parsed_data, mentioned_casket):
                return False

    return True

def eval_other_pattern(statement, assumed_casket, parsed_data, current_casket):
    """
    evaluates a other pattern statement

    input : assumed_casket = casket {gold, silver,lead} that contains portrait
            statement = statement to evaluate
            parsed_data = full statement list
            current_casket = casket this statement is located on

    output: boolean True if and only if statement evaluates to true
    
    """
    statements_to_check = parsed_data["caskets"][current_casket]

    if statement["other_statements_truth"] == "true":
        for other_statement in statements_to_check:
            if "other_statements_truth" not in other_statement:
                if not evaluate_statement(assumed_casket, other_statement, parsed_data, current_casket):
                    return False
    else:
        for other_statement in statements_to_check:
            if "other_statements_truth" not in other_statement:
                if evaluate_statement(assumed_casket, other_statement, parsed_data, current_casket):
                    return False

    return True

def find_correct_casket(parsed_data):
    """
    find the casket(s) who match that have n true statements when assumed

    input : parsed_data = full statement list
        
    output: list of caskets that have n true statements when assumed
    
    """
    
    valid_caskets = []
    n_true = parsed_data["true_statements"]

    for casket in parsed_data["caskets"].keys():
        true_count = check_statements(casket, parsed_data)
        # If this assumption results in the correct number of true statements, it's a valid answer
        if true_count == n_true:
            valid_caskets.append(casket)

    return valid_caskets

def solve_casket(puzzle_file):
    """
    solves the portia puzzle for file

    input : puzzle_file = file containing JSON format of Portia puzzle
        
    output: list of caskets that have n true statements when assumed
    
    """
    # Load parsed puzzle data from file
    with open(puzzle_file, "r", encoding="utf-8") as file:
        parsed_data = json.load(file)

    # Find the correct casket
    correct_caskets = find_correct_casket(parsed_data)

    # Print the result
    if correct_caskets:
        return correct_caskets
    else:
        print("No valid casket found!")


