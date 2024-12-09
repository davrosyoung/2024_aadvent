import sys
import re
from copy import deepcopy
from math import floor



verbose: bool = False
very_verbose: bool = False

def render(disk_map: list[tuple[int, int]]) -> str:
    result: str = ''
    for twin in disk_map:
        id: int = twin[0]
        size: int = twin[1]
        if id >= 0:
            result += str(id) * size
        else:
            result += '.' * size
    return result

def extract_disk_map(line:str) -> list[tuple[int, int]]:
    is_file: bool = True
    i: int = 0
    file_id: int = None
    input = line.strip()
    result: list[tuple[int, int]] = []
    while(i < len(line)):
        digit: str = input[i]
        if not digit.isdigit():
            raise Exception(f'Expecting a DIGIT at position {i=}, but rather got {digit}')
        if is_file:
            file_id = 0 if file_id is None else file_id + 1
            result.append((file_id, int(digit)))
        else:
            result.append((-1, int(digit)))
        i += 1
        is_file = not is_file
    return result

def optimise_disk(disk_map: list[tuple[int, int]]) -> list[tuple[int, int]]:
    return None

def calculate_checksum(disk_map: list[tuple[int, int]]) -> int:
    block_number: int = 0
    result: int = 0
    for entry in disk_map:
        file_id: int = entry[0]
        length: int = entry[1]
        if file_id < 0:
            block_number += length
            continue
        for i in range(length):
            result += file_id * block_number
            block_number += 1
    return result

def part_one(path: str) -> int:
    result: int = 0

    # sweep one ... gather the ordering information
    with open(path, 'r') as file:
        line_number: int = 1
        for line in file:
            line_number += 1
            disk_map: list[tuple[int, int]] = extract_disk_map(line)
            disk_map = optimise_disk(disk_map=disk_map)
            result = calculate_checksum(disk_map=disk_map)
    return result

def part_two(path: str) -> int:
    result: int = 0

    # sweep one ... gather the ordering information
    with open(path, 'r') as file:
        line_number: int = 1
        for line in file:
            line_number += 1
    return result


def main(argv: list[str]):
    global very_verbose
    global verbose
    global OPERATORS
    very_verbose = False
    verbose = False
    result = part_one(path='day_nine_test_input.txt')
    print(f'part one: {result=} for test data')
    if result != 1928:
        raise Exception(f'Test failed, expected 1928 but instead got {result}')
#    result = part_one(path='day_nine_input.txt')
#    print(f'part one: {result=} for actual data')
#
#    result = part_two(path='day_nine_test_input.txt')
#    print(f'part two: {result=} for test data')
#    if result != 1928:
#        raise Exception(f'Test failed, expected 1928 but instead got {result}')
#    result: int = part_two(path='day_nine_input.txt')
#    print(f'part two: {result=} for actual data')

    return 0

def test():
    input:str = '31415926536'
    disk_map: list[tuple[int, int]] = extract_disk_map(line=input)
    print(render(disk_map=disk_map))
    assert(disk_map is not None)
    assert(len(disk_map) == 11)
    assert(disk_map[0] == (0, 3))
    assert(disk_map[1] == (-1, 1))
    assert(disk_map[2] == (1, 4))
    assert(disk_map[3] == (-1, 1))
    assert(disk_map[4] == (2, 5))
    assert(disk_map[5] == (-1, 9))
    assert(disk_map[6] == (3, 2))
    assert(disk_map[7] == (-1, 6))
    assert(disk_map[8] == (4, 5))
    assert(disk_map[9] == (-1, 3))
    assert(disk_map[10] == (5, 6))


    ## 000.1111.22222.........33......44444...555555

    checksum = calculate_checksum(disk_map=disk_map)
    assert(checksum == 2178)

    return

if __name__ == "__main__":
    test()
    exit_code: int = main(sys.argv)
    sys.exit(exit_code)