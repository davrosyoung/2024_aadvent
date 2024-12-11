import sys
import re
from copy import deepcopy
from math import floor

EQUATION_PATTERN = re.compile(r'^\s*(\d+):(\s*(\d+))+\s*$')
ADD: int = 0
MULTIPLY: int = 1
CONCAT: int = 2
SUBTRACT: int = 3
DIVIDE: int = 4
#OPERATORS:list[int] = [ADD, MULTIPLY, SUBTRACT, DIVIDE]
OPERATORS: list[int]
OPERATOR_MNEMONIC:list[str]=['ADD','MUL','CAT','SUB','DIV']
OPERATOR_SYMBOLS:list[str]=['+','x','||','-','/']


verbose: bool = False
very_verbose: bool = False



def extract_numbers(candidate: str) -> list[int]:
    result: list[int] = [int(b) for b in candidate.split(' ')]
    return result

def extract_numbers_to_dict(candidate: str) -> dict[int, int]:
    result: dict[int, int] = {}
    values: list[int] = [int(b) for b in candidate.split(' ')]
    for value in values:
        if value not in result:
            result[value] = 0
        result[value] += 1
    return result

def blink(stones: list[int]) -> list[int]:
    result: list[int] = []
    for stone in stones:
        if stone == 0:
            result.append(1)
        elif len(str(stone)) % 2 == 0:
            s: str = str(stone)
            l: int = len(s)
            h: int = l>>1
            a: int = int(s[:h])
            b: int = int(s[h:])
            result.append(a)
            result.append(b)
        else:
            result.append(stone * 2024)
    return result

def blink_too(stones: dict[int, int]) -> dict[int, int]:
    result: dict[int,int] = {}
    for v, n in stones.items():
        s: str = str(v)
        l: int = len(s)
        h: int = l>>1
        if v == 0:
            if 1 not in result:
                result[1] = 0
            result[1] += n
        elif v == 1:
            if 2024 not in result:
                result[2024] = 0
            result[2024] += n
        elif v == 2024:
            if 20 not in result:
                result[20] = 0
            result[20] += n
            if 24 not in result:
                result[24] = 0
            result[24] += n
        elif l % 2 == 0:
            a: int = int(s[0:h])
            b: int = int(s[h:])
            if a not in result:
                result[a] = 0
            result[a] += n
            if b not in result:
                result[b] = 0
            result[b] += n
        else:
            r: int = v * 2024
            if r not in result:
                result[r] = 0
            result[r] += n

    return result

def p45(path: str, count: int) -> int:
    result: int = 0

    # sweep one ... gather the ordering information
    with open(path, 'r') as file:
        line_number: int = 1
        for line in file:
            stones: dict[int, int] = extract_numbers_to_dict(candidate=line.strip())
            for i in range(count):
                stones = blink_too(stones=stones)
                result = sum([v for v in stones.values()])
                print(f'{i=}: {result}')
            line_number += 1
    return result


def part_one(path: str) -> int:
    result: int = 0

    # sweep one ... gather the ordering information
    with open(path, 'r') as file:
        line_number: int = 1
        for line in file:
            stones: list[int] = extract_numbers(candidate=line.strip())
            for i in range(25):
                stones = blink(stones=stones)
            result = len(stones)
            line_number += 1
    return result

def part_two(path: str) -> int:
    result: int = 0

    with open(path, 'r') as file:
        line_number: int = 1
        for line in file:
            stones: list[int] = extract_numbers(candidate=line.strip())
            for i in range(75):
                stones = blink(stones=stones)
                print(f'{i=},{len(stones)=}')
            result = len(stones)
            line_number += 1
    return result


def main(argv: list[str]):
    global very_verbose
    global verbose
    global OPERATORS
    very_verbose = False
    verbose = False
    result: int = 0
    result = p45(path='day_eleven_test_input.txt', count=25)
    print(f'part one: {result=} for test data')
    if result != 55312:
        raise Exception(f'Test failed, expected 55312 but instead got {result}')
    result = p45(path='day_eleven_input.txt', count=25)
    print(f'part one: {result=} for actual data')

    result = p45(path='day_eleven_test_input.txt', count=75)
    print(f'part two: {result=} for test data')
#    if result != 11387:
#        raise Exception(f'Test failed, expected 11387 but instead got {result}')
    result: int = p45(path='day_eleven_input.txt', count=75)
    print(f'part two: {result=} for actual data')

    return 0

if __name__ == "__main__":
    exit_code: int = main(sys.argv)
    sys.exit(exit_code)