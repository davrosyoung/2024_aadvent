import sys
import re
from math import gcd
from typing import Callable

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

def off_the_reservation(columns_by_row: list[int], position: tuple[int, int]) -> bool:
    row: int = int(position[0])
    column: int = int(position[1])
    result: bool = row < 0 or row >= len(columns_by_row) or column < 0 or column >= columns_by_row[row]
    return result

def is_occupied(map: list[list[int]], position: tuple[int, int]) -> bool:
    result: bool = position[1] in map[position[0]]
    return result

def antinodes(alpha: tuple[int, int], beta: tuple[int, int], columns_by_row: list[int]) -> list[tuple[int, int]]:
    """Given two locations, obtain the two locations which sit in the same line of sight but equidistant from the two locations provided.

    Very simply put, the difference in rows and the difference in columns between the two points provided is
    projected in either direction. This should work no matter which orientation alpha and beta are in respect
    to one another...
    """
    row_delta: int = beta[0] - alpha[0]
    column_delta: int = beta[1] - alpha[1]
    antinode_alpha: tuple[int, int] = (alpha[0] - row_delta, alpha[1] - column_delta)
    antinode_beta: tuple[int, int] = (beta[0] + row_delta, beta[1] + column_delta)
    result: tuple[tuple[int, int], tuple[int, int]] = (antinode_alpha, antinode_beta)
    return result

#callable[[tuple[int, int], tuple[int, int], columns_by_row:list[int]],list[tuple[int, int]]:
def resonant_antinodes(alpha: tuple[int, int], beta: tuple[int, int], columns_by_row:list[int]) -> list[tuple[int, int]]:
    """Given two locations, obtain all locations exactly in-line with these two locations.

    Here is the thing, let's say the distance between them is four and six units (vertically or horizontally),
    then we are going to have to reduce this to 2 and 3 units ... otherwise we are going to skip locations which
    are actually "in-line".... so we need to determine the greatest common factor and divide them both by that value...
    """
    result: list[tuple[int, int]] = []
    row_delta: int = beta[0] - alpha[0]
    column_delta: int = beta[1] - alpha[1]

    # special case Z: a & b are the same location... return NOTHING
    if row_delta == 0 and column_delta == 0:
        return result

    # special case A: a & b are vertically in-line... just return a horizontal row of nodes....
    if row_delta == 0:
        for column in range(0, columns_by_row[alpha[0]]):
            result.append((alpha[0], column))
        return result

    # special case B: a & b are vertically in-line... just return a vertical column of nodes....
    if column_delta == 0:
        for row in range(0, len(columns_by_row)):
            result.append((row, alpha[1]))
        return result

    # rather than get into linear algebra .... see if there is a greatest common factor/demoninator between
    # the delta-row and delta-column so that we ensure we are not missing out "in-between" locations...
    common_factor: int = gcd(row_delta, column_delta)
    row_small_delta: int = int(row_delta / common_factor)
    column_small_delta: int = int(column_delta / common_factor)

    # now send out a beam from "alpha" backwards......
    cursor: tuple[int, int] = alpha
    out_of_bounds: bool = off_the_reservation(columns_by_row=columns_by_row, position=cursor)
    while not out_of_bounds:
        cursor = (cursor[0] - row_small_delta, cursor[1] - column_small_delta)
        out_of_bounds = off_the_reservation(columns_by_row=columns_by_row, position=cursor)
        if not out_of_bounds:
            result.append(cursor)

    # now send a beam from "alpha" forwards (it'll intersect beta, but that is ok)...
    cursor = alpha
    out_of_bounds: bool = off_the_reservation(columns_by_row=columns_by_row, position=cursor)
    while not out_of_bounds:
        if not out_of_bounds:
            result.append(cursor)
        cursor = (cursor[0] + row_small_delta, cursor[1] + column_small_delta)
        out_of_bounds = off_the_reservation(columns_by_row=columns_by_row, position=cursor)
    return result

def part_one(path: str, antinode_calculator: Callable[[tuple[int, int], tuple[int, int], list[int]],list[tuple[int, int]]]) -> int:
    result: int = 0
    row: int = 0
    antinode_map:list[list[int]] = []
    antennae_map:dict[str,list[tuple[int, int]]] = {}
    columns_by_row: list[int] = []

    # sweep one ... gather the ordering information
    with open(path, 'r') as file:
        for line in file:
            antinode_map.append([])
            columns_by_row.append(len(line.strip()))
            for column, khar in enumerate(line.strip()):
                if khar == '.':
                    continue
                if khar.isalnum():
                    if khar in antennae_map:
                        antennae_map[khar].append((row, column))
                    else:
                        antennae_map[khar] = [(row, column)]
            row += 1

    # for each type of antenna at a time...
    for flavour in antennae_map.keys():
        positions: list[tuple[int, int]] = antennae_map.get(flavour)
        for i in range(0, len(positions)):
            for j in range(i + 1, len(positions)):
                an = antinode_calculator(positions[i], positions[j], columns_by_row)
                for node in an:
                    if off_the_reservation(columns_by_row=columns_by_row, position=node):
                        continue
                    if is_occupied(map=antinode_map, position=node):
                        continue
                    # we have an unoccupied square to place an antinode .... record it!!
                    row: int = node[0]
                    column: int = node[1]
                    antinode_map[row].append(column)
                    result += 1

    return result

def part_two(path: str) -> int:
    result: int = 0
    row: int = 0
    antinode_map:list[list[int]] = []
    antennae_map:dict[str,list[tuple[int, int]]] = {}
    columns_by_row: list[int] = []

    # sweep one ... gather the ordering information
    with open(path, 'r') as file:
        for line in file:
            antinode_map.append([])
            columns_by_row.append(len(line.strip()))
            for column, khar in enumerate(line.strip()):
                if khar == '.':
                    continue
                if khar.isalnum():
                    if khar in antennae_map:
                        antennae_map[khar].append((row, column))
                    else:
                        antennae_map[khar] = [(row, column)]
            row += 1

    # for each type of antenna at a time...
    for flavour in antennae_map.keys():
        positions: list[tuple[int, int]] = antennae_map.get(flavour)
        for i in range(0, len(positions)):
            for j in range(i + 1, len(positions)):
                an = resonant_antinodes(alpha=positions[i], beta=positions[j], columns_by_row=columns_by_row)
                for node in an:
                    if off_the_reservation(columns_by_row=columns_by_row, position=node):
                        continue
                    if is_occupied(map=antinode_map, position=node):
                        continue
                    # we have an unoccupied square to place an antinode .... record it!!
                    row: int = node[0]
                    column: int = node[1]
                    antinode_map[row].append(column)
                    result += 1
    return result


def main(argv: list[str]):
    global very_verbose
    global verbose
    very_verbose = False
    verbose = False
    result: int = 0

    result = part_one(path='day_eight_test_input.txt', antinode_calculator=antinodes)
    print(f'part one: {result=} for test data')
    if result != 14:
        raise Exception(f'Test failed, expected 14 but instead got {result}')
    result = part_one(path='day_eight_input.txt', antinode_calculator=antinodes)
    print(f'part one: {result=} for actual data')

    result = part_one(path='day_eight_test_input.txt', antinode_calculator=resonant_antinodes)
    print(f'part two: {result=} for test data')
    if result != 34:
        raise Exception(f'Test failed, expected 34 but instead got {result}')
    result: int = part_one(path='day_eight_input.txt', antinode_calculator=resonant_antinodes)
    print(f'part two: {result=} for actual data')

    return 0

def tests():
    p = antinodes(alpha=(5,3), beta=(5, 5))
    # expect results to be at 5,1 and 5,7
    assert(p[0]==(5,1))
    assert(p[1]==(5,7))

    p = antinodes(alpha=(5,5), beta=(5, 3))
    # expect results to be at 5,7 and 5,1
    assert(p[0]==(5,7))
    assert(p[1]==(5,1))

    p = antinodes(alpha=(1,0), beta=(2,3))
    # expect results to be at 0,-2 and 3,6
    assert(p[0]==(0,-3))
    assert(p[1]==(3,6))

    # test columunar result
    p=resonant_antinodes(alpha=(6,5),beta=(8,5),columns_by_row=[10,10,10,10,10,10,10,10,10,10])
    assert(len(p) == 10)
    for r,q in enumerate(p):
        assert(q[0]==r)
        assert(q[1]==5)

    # test horz result
    p=resonant_antinodes(alpha=(6,4),beta=(6,8),columns_by_row=[10,10,10,10,10,10,10,10,10,10])
    assert(len(p) == 10)
    for c,q in enumerate(p):
        assert(q[0]==6)
        assert(q[1]==c)

    # test diagonal result with gaps
    p = resonant_antinodes(alpha=(7, 7), beta=(5, 3), columns_by_row=[10, 10, 10, 10, 10, 10, 10, 10, 10, 10])
    assert(len(p) == 5)
    assert((4,1) in p)
    assert((5,3) in p)
    assert((6,5) in p)
    assert((7,7) in p)
    assert((8,9) in p)


    # test special case ... 45 degrees
    p = resonant_antinodes(alpha=(6, 2), beta=(1, 7), columns_by_row=[10, 10, 10, 10, 10, 10, 10, 10, 10, 10])
    assert(len(p) == 9)
    assert((8,0) in p)
    assert((7,1) in p)
    assert((6,2) in p)
    assert((5,3) in p)
    assert((4,4) in p)
    assert((3,5) in p)
    assert((2,6) in p)
    assert((1,7) in p)
    assert((0,8) in p)

if __name__ == "__main__":
    #tests()
    exit_code: int = main(sys.argv)
    sys.exit(exit_code)