import sys
import re
from copy import deepcopy
from math import floor

EQUATION_PATTERN = re.compile(r'^\s*(\d+):(\s*(\d+))+\s*$')
ADD: int = 0
MULTIPLY: int = 1
SUBTRACT: int = 2
DIVIDE: int = 3
#OPERATORS:list[int] = [ADD, MULTIPLY, SUBTRACT, DIVIDE]
OPERATORS:list[int] = [ADD, MULTIPLY]
OPERATOR_MNEMONIC:list[str]=['ADD','MUL','SUB','DIV']
OPERATOR_SYMBOLS:list[str]=['+','x','-','/']


verbose: bool = False
very_verbose: bool = False

def as_text(operands: list[int], operators: list[int]) -> str:
    result: str = str(operands[0])
    for i, operator in enumerate(operators):
        result += OPERATOR_SYMBOLS[operator]
        result += str(operands[i+1])
    return result

def determine_operators(i:int, operands:list[int]) -> list[int]:
    result: list[int] = []
    # the number of "pairs" of operands is one less than the number of operands
    number_pairs: int = len(operands) - 1
    j: int = number_pairs - 1
    while( j >= 0 ):
        # we now need to extract the operator value for the jth pair.... from i...

        # b is the vaue that we can divide by in order to eliminate those operators to the right of column j
        b: int = pow(len(OPERATORS), j)
        # c will allow us to extract the operator value for column j
        c: int = floor(i / b)
        operator_index: int = c % len(OPERATORS)
        result.append(OPERATORS[operator_index])
        j -= 1
    return result

def calculate(operands:list[int], operators:list[int]) -> int:
    result: int = operands[0]
    for i, operator in enumerate(operators):
        operand_index: int = i + 1
        operand: int = operands[operand_index]
        if operator == ADD:
            result += operand
        elif operator == MULTIPLY:
            result *= operand
        elif operator == SUBTRACT:
            result -= operand
        elif operator == DIVIDE:
            result /= operand
        else:
            raise Exception(f'Unknown operator: {operators[i]}')
    return result

def part_one(path: str) -> int:
    result: int = 0

    # sweep one ... gather the ordering information
    with open(path, 'r') as file:
        line_number: int = 1
        for line in file:
            bits = EQUATION_PATTERN.match(line.strip())
            if bits is None:
                continue
            colon_pos: int = line.find(':')
            part_alpha: str = line[:colon_pos].strip()
            part_beta: str = line[colon_pos+1:].strip()
            expected: int = int(part_alpha)
            operands: list[int] = [int(o) for o in part_beta.split(' ')]
            number_pairs: int = len(operands) - 1
            i: int = 0
            # we now have to try each possibilities
            matched_expected: bool = False
            number_possibilities: int = pow(4, number_pairs)
            while not matched_expected and i < number_possibilities:
                calculated: int = 0
                operators: list[int] = determine_operators(i=i, operands=operands)
                calculated = calculate(operands=operands, operators=operators)
                matched_expected = calculated == expected
                if matched_expected:
                    result += calculated
                    print(f'{i=} Found match: {as_text(operands, operators)} == {calculated} at {line_number=}')
                i += 1
            line_number += 1
    return result

def part_two(path: str) -> int:
    result: int = 0

    # sweep one ... gather the ordering information
    with open(path, 'r') as file:
        row_index: int = 0
        for line in file:
            bits = EQUATION_PATTERN.match(line.strip())
            if bits is None:
                continue





def main(argv: list[str]):
    global very_verbose
    global verbose
    very_verbose = False
    verbose = False
    result: int = 0

    result = part_one(path='day_seven_test_input.txt')
    print(f'part one: {result=} for test data')
    if result != 3749:
        raise Exception(f'Test failed, expected 3749 but instead got {result}')
    result = part_one(path='day_seven_input.txt')
    print(f'part one: {result=} for actual data')
#
    result = part_two(path='day_seven_test_input.txt')
    print(f'part two: {result=} for test data')
    if result != 3749:
        raise Exception(f'Test failed, expected 3749 but instead got {result}')
    result: int = part_two(path='day_seven_input.txt')
    print(f'part two: {result=} for actual data')

    return 0

if __name__ == "__main__":
    exit_code: int = main(sys.argv)
    sys.exit(exit_code)