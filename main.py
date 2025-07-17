import os
import sys
import datetime

from puzzle_generator import generate_puzzle
from portia_n_solver import solve_casket
from portia_n_regex_parser import parse_puzzle_from_file
from CNF_converter import solve_puzzle_from_file

TEST_FOLDER = "test"
OUTPUT_FOLDER = "generated"

def solve_all_tests():
    print("\n Solving all test cases in the 'test' folder")
    files = [f for f in os.listdir(TEST_FOLDER) if f.endswith(".txt")]

    if not files:
        print("No test files found.")
        return

    for filename in files:
        input_path = os.path.join(TEST_FOLDER, filename)
        print(f"\n Solving {filename}")
        try:
            solve_puzzle_output(input_path)

        except Exception as e:
            print(f" Error processing {filename}: {e}")

def generate_new_puzzle():
    print(f"\n To Generate a new Portia puzzle")
    n = input("Enter the number of statements per casket (e.g. 2 or 3): ")
    print(f"\n Generating a new Portia-{n}-m puzzle")
    
    try:
        n = int(n)
        os.makedirs(OUTPUT_FOLDER, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        outputfile = os.path.join(OUTPUT_FOLDER, f"portia{n}_{timestamp}.txt")
        generate_puzzle(n, outputfile)
        print(f"Puzzle saved to {outputfile}")
    except Exception as e:
        print(f" Error generating puzzle: {e}")

def solve_custom_file():
    filepath = input("\n Enter the path to your puzzle file: ").strip()
    if not os.path.isfile(filepath):
        print(" Error:File does not exist.")
        return

    try:

        solve_puzzle_output(filepath)

    except Exception as e:
        print(f" Error: Failed to solve puzzle: {e}")


def solve_puzzle_output(filepath):
        parsed_output = filepath.replace(".txt", "_parsed.txt")
        print(f"\n Parsed puzzle saved to {parsed_output}")
        parse_puzzle_from_file(filepath, parsed_output)
        print(f"Solving {filepath} using Logical Deduction")
        ld_solution = solve_casket(parsed_output)
        print(f" The solution of puzzle {filepath} is {ld_solution}")

        print(f"Solving {filepath} using CNF")
        cnf_solution = solve_puzzle_from_file(parsed_output)
        if cnf_solution["status"] == "SAT":
            print(f" The solution of puzzle {filepath} is {cnf_solution['solution']} using {cnf_solution['valuation']} valuation")
        else:
            print("❌ UNSAT")
            print(cnf_solution["message"])



def main():
    while True:
        print (None)
        print("\n=== Portia Puzzle Tool ===")
        print("1. Solve all test cases in /test folder")
        print("2. Generate a new puzzle to solve")
        print("3. Solve a specific puzzle file")
        print("4. Exit")

        choice = input("\nChoose an option (1-4): ").strip()

        if choice == "1":
            solve_all_tests()
        elif choice == "2":
            generate_new_puzzle()
        elif choice == "3":
            solve_custom_file()
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please select 1–4.")

if __name__ == "__main__":
    main()
