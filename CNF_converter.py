import re
import json
from pysat import solvers
from itertools import combinations

def convert_JSON_CNF(parsed_data):
    portia_n = parsed_data["portia"] 
    amount_statements = portia_n * 3
    statement_ids = create_statement_ids(amount_statements)
    n_true = parsed_data["true_statements"]
    CNF_clauses = [["G","S","L"], ["~G","~S"], ["~G","~L"] ,["~S","~L"] ]
    cnf_file =  CNF_clauses

    cnf_file.extend( n_m_true_statements(n_true, statement_ids))

    statement_id = 1
    for casket, data in parsed_data["caskets"].items():
        for statement in data:
            if "contains_portrait" in statement:
                cnf_file += statement_pattern_statement_to_cnf(statement, "n" + str(statement_id))
            elif "mentioned_casket" and "statement_truth" in statement:
                cnf_file += truth_pattern_statement_to_cnf(statement, "n" + str(statement_id), portia_n)
            else :
                cnf_file += other_pattern_to_cnf(statement, "n" + str(statement_id), portia_n , casket)
            statement_id += 1

    return cnf_file


def create_statement_ids(m):
    return [f"n{i+1}" for i in range(m)]


def n_m_true_statements(m, statement_ids):
    n_m_true_statements = []
    n = len(statement_ids)
    if m == 0:
        for all_false in combinations(statement_ids, n):
            n_m_true_statements.append([f"~{v}" for v in all_false])

        return n_m_true_statements

    if n == m:
        for all_false in combinations(statement_ids, n):
            n_m_true_statements.append([f"{v}" for v in all_false])
        
        return n_m_true_statements


    # atleast n are true
    for atleast_vars in combinations(statement_ids, n - m + 1):
        n_m_true_statements.append([f"{v}" for v in atleast_vars])
    # atmost n are true
    for atmost_vars in combinations(statement_ids, m + 1):
        n_m_true_statements.append([f"~{v}" for v in atmost_vars])


    return n_m_true_statements

    


def statement_pattern_statement_to_cnf(statement, statement_id):
    casket = casket_short(statement["mentioned_casket"])
    if statement["contains_portrait"] :
        return [[ casket,f"~{statement_id}"], [f"~{casket}", statement_id]]
    else:
        return [[ casket, statement_id], [f"~{casket}", f"~{statement_id}"]]

    
    
def  truth_pattern_statement_to_cnf (statement, statement_id, portia_n):
    mentioned_casket = statement["mentioned_casket"]
    statement_id_mentioned_casket = statement_id_caskets(mentioned_casket, portia_n)
    if(statement["statement_truth" ] == "true"):
        x = [[ n , "~" + statement_id] for n in statement_id_mentioned_casket]
        temp = statement_id_mentioned_casket
        temp = ["~" + n for n in temp]
        temp.append(statement_id)
        x.append(temp)
        return   x

    else :
        x = [[  "~" + n , "~" + statement_id] for n in statement_id_mentioned_casket]
        temp = statement_id_mentioned_casket
        temp.append(statement_id)
        x.append(temp)
        return  x
    # " /\\\n" + x + " /\\\n" + cnf_string(temp) 

def other_pattern_to_cnf(statement, statement_id, portia_n, casket):
    mentioned_casket = casket
    statement_id_mentioned_casket = statement_id_caskets(mentioned_casket, portia_n)
    statement_id_mentioned_casket.remove(statement_id)

    if(statement["other_statements_truth" ] == "true"):
        x = [[ n , "~" + statement_id] for n in statement_id_mentioned_casket]
        temp = statement_id_mentioned_casket
        temp = ["~" + n for n in temp]
        temp.append(statement_id)
        x.append(temp)
        return x
        # return " /\\\n" + x + " /\\\n" + cnf_string(temp) 

    else :
        x = [[  "~" + n , "~" + statement_id] for n in statement_id_mentioned_casket]
        temp = statement_id_mentioned_casket
        temp.append(statement_id)
        x.append(temp)
        return x
    # " /\\\n" + x + " /\\\n" + cnf_string(temp) 


def statement_id_caskets(casket, portia_n):
    statement_id_caskets = []
    for i in range(1,portia_n + 1):
        if casket == "lead":
            s_id = 2* portia_n +i
            statement_id_caskets.append(f"n{s_id}")
        elif casket == "silver":
            s_id = portia_n +i
            statement_id_caskets.append(f"n{s_id}")
        else:
            statement_id_caskets.append(f"n{i}")
    return statement_id_caskets


def casket_short(name):
    return {"gold": "G", "silver": "S", "lead": "L"}.get(name, name)


def encode_cnf_string_to_int(cnf_clauses):
    """
    Converts string-based CNF clauses (e.g., [['G', '~S']]) to integer-based CNF for PySAT.
    Returns:
        - encoded_cnf: List of integer clauses
        - lit_to_int: Dict mapping literal names to integers
        - int_to_lit: Dict mapping integers to literal names
    """

    base_literals = set()
    for clause in cnf_clauses:
        for literal in clause:
            base_literals.add(literal.strip("~"))


    lit_to_int = {lit: i+1 for i, lit in enumerate(sorted(base_literals))}
    int_to_lit = {v: k for k, v in lit_to_int.items()}


    encoded_cnf = []
    for clause in cnf_clauses:
        encoded_clause = []
        for literal in clause:
            var = lit_to_int[literal.strip("~")]
            encoded_clause.append(-var if literal.startswith("~") else var)
        encoded_cnf.append(encoded_clause)

    return encoded_cnf, lit_to_int, int_to_lit

def decode_model(model, int_to_lit):
    return {int_to_lit[abs(v)]: v > 0 for v in model if abs(v) in int_to_lit}


def create_cnf_string(strings_list):
    result = []
    for inner in strings_list:
        joined = " \\/ ".join(inner)
        line = f"({joined})" 
        result.append(line)
    return " /\\\n".join(result)


def get_solution_casket(data: dict):
    for key, value in data.items():
        if value:
            return key
    return None

def solve_puzzle_from_file(input_filename):
    """Reads a Portia-n-m puzzle from a file, parses it, and writes the output to another file.
    Input : JSON representation of a portia puzzle
    
    output : The answer to the Portia Puzzle as the valuation. 
    """
    try:
        with open(input_filename, "r", encoding="utf-8") as file:
            parsed_data = json.load(file)

        cnf_clauses = convert_JSON_CNF(parsed_data)
        


        encoded_cnf, lit_to_int, int_to_lit = encode_cnf_string_to_int(cnf_clauses)
       

        with solvers.Glucose3(bootstrap_with=encoded_cnf) as solver:
            is_sat = solver.solve()
            model = solver.get_model() if is_sat else None

        

        if is_sat:
            decoded_model = decode_model(model, int_to_lit)
            solution = get_solution_casket(decoded_model) 
            return {"status": "SAT", "solution": solution, "valuation": decoded_model}
        
        return {"status": "UNSAT", "message": "No valid solutio found."}


    except Exception as e:
        print(f"Error: {e}")









