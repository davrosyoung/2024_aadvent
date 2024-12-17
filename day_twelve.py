import sys
import re
from copy import deepcopy
from dataclasses import dataclass
from math import floor


EAST: int = 0
SOUTH_EAST: int = 1
SOUTH: int = 2
SOUTH_WEST: int = 3
WEST: int = 4
NORTH_WEST: int = 5
NORTH: int = 6
NORTH_EAST: int = 7

step_directions_by_direction: dict[int, tuple[int,int]] = {
    EAST: (0, 1),
    SOUTH_EAST: (1, 1),
    SOUTH: (1, 0),
    SOUTH_WEST: (1, -1),
    WEST: (0, -1),
    NORTH_WEST: (-1, -1),
    NORTH: (-1, 0),
    NORTH_EAST: (-1, 1)
}

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

@dataclass
class SchreberGarten:
    locations: dict[tuple[int, int], str]
    flavour: str

    def area(self) -> int:
        result: int = -1
        return result

    def perimeter(self) -> int:
        result: int = -1
        return result

def part_one(path: str) -> int:
    result: int = 0

    # sweep one ... gather the ordering information
    with open(path, 'r') as file:
        line_number: int = 1
        for line in file:
            pass
    return result

def part_two(path: str) -> int:
    result: int = 0

    with open(path, 'r') as file:
        line_number: int = 1
        for line in file:
            pass
    return result

def step(position: tuple[int, int], direction: int) -> tuple[int, int]:
    delta: tuple[int, int] = step_directions_by_direction[direction]
    result: tuple[int, int] = (position[0] + delta[0], position[1] + delta[1])
    return result

def off_the_reservation(position: tuple[int, int], extent:tuple[int,int]) -> bool:
    result: bool = position[0] < 0 or position[0] >= extent[0] or position[1] < 0 or position[1] > extent[1]
    return result

def extract_runs(candidate: str) -> list[tuple[int, int, str]]:
    result: list[tuple[int, int, str]] = []
    previous_khar: str|None = None
    run_length: int|None = None
    run_pos: int|None = None
    for i in range(len(candidate)):
        current_khar = candidate[i]
        if previous_khar is None or previous_khar != current_khar:
            if run_length is not None and previous_khar is not None:
                result.append((run_length, run_pos, previous_khar))
            run_pos = i
            run_length = 0
            previous_khar = current_khar
        run_length += 1

    if run_length > 0:
        result.append((run_length, run_pos, previous_khar))
    return result

def extract_grid(candidate: str) -> tuple[dict[tuple[int, int], str],tuple[int,int]]:
    grid: dict[tuple[int, int], str] = {}
    lines: list[str] = candidate.split('\n')
    max_width: int = None
    row: int = 0
    for line in lines:
        runs: list[tuple[int, int, str]] = extract_runs(candidate=line)
        column: int = 0
        for run in runs:
            column = run[1]
            if max_width is None or column + run[0] > max_width:
                max_width = column + run[0]
            for i in range(run[0]):
                grid[(row, column + i)] = run[2]
        row += 1

    result: tuple[dict[tuple[int, int], str], tuple[int, int]] = (grid, (len(lines), max_width))
    return result

def extract_plots(text: str) -> list[SchreberGarten]:
    result: list[SchreberGarten] = []
    twin: tuple[dict[tuple[int, int], str],tuple[int,int]] = extract_grid(candidate=text)
    grid: dict[tuple[int, int], str] = twin[0]
    number_rows, number_columns = twin[1]
    membership: dict[tuple[int, int], SchreberGarten] = {}


    for row_index in range(number_rows):
        for column_index in range(number_columns):
            flavour: str = grid.get((row_index, column_index))
            position: tuple[int, int] = (row_index, column_index)

            # is there any neighbour that belongs to a schrebergarten that we should join?
            existing_schrebergarten: SchreberGarten|None = None
            for direction in (EAST, SOUTH, WEST, NORTH):
                candidate_position: tuple[int, int] = step(position=position, direction=direction)
                if off_the_reservation(position=candidate_position, extent=(number_rows, number_columns)):
                    continue
                # is this location already in a plot? if so, join this position to it.
                neighbour_flavour: str = grid.get(candidate_position)
                if neighbour_flavour  == flavour:
                    plot: SchreberGarten|None = membership.get(candidate_position)
                    if plot is not None:
                        # we found a schrebergarten to join!!
                        existing_schrebergarten = plot
                        break

            if existing_schrebergarten is not None:
                # join this schrebergarten!!
                existing_schrebergarten.locations[position] = flavour
                membership[position] = existing_schrebergarten
            else:
                # create a brand new schrebergarten
                new_schrebergarten: SchreberGarten = SchreberGarten(flavour=flavour, locations={(position): flavour})
                result.append(new_schrebergarten)
                membership[position] = new_schrebergarten

    return result

def test():
    # OOOOO
    # OXOXO
    # OOOOO
    # OXOXO
    # OOOOO
    # expect total perimeter to be 36
    # expect "cost" to be 772
    #                                                         01234567890123456789012
    runs:list[tuple[int, int, str]] = extract_runs(candidate='aaaaabaaaaccccbbaaaad')
    assert(len(runs) == 7)
    assert(runs[0] == (5, 0, 'a'))
    assert(runs[1] == (1, 5, 'b'))
    assert(runs[2] == (4, 6, 'a'))
    assert(runs[3] == (4, 10, 'c'))
    assert(runs[4] == (2, 14, 'b'))
    assert(runs[5] == (4, 16, 'a'))
    assert(runs[6] == (1, 20, 'd'))

    text: str = 'OOOOO\nOXOXO\nOOOOO\nOXOXO\nOOOOO'

    twin: tuple[dict[tuple[int, int], str], tuple[int, int]] = extract_grid(candidate=text)
    grid: dict[tuple[int, int], str] = twin[0]
    rows, columns = twin[1]
    assert(rows == 5)
    assert(columns == 5)
    assert(len(grid) == 25)
    assert(grid.get((0,0)) == 'O')
    assert(grid.get((0,1)) == 'O')
    assert(grid.get((0,2)) == 'O')
    assert(grid.get((0,3)) == 'O')
    assert(grid.get((0,4)) == 'O')

    assert(grid.get((1,0)) == 'O')
    assert(grid.get((1,1)) == 'X')
    assert(grid.get((1,2)) == 'O')
    assert(grid.get((1,3)) == 'X')
    assert(grid.get((1,4)) == 'O')

    assert(grid.get((2,0)) == 'O')
    assert(grid.get((2,1)) == 'O')
    assert(grid.get((2,2)) == 'O')
    assert(grid.get((2,3)) == 'O')
    assert(grid.get((2,4)) == 'O')

    assert(grid.get((3,0)) == 'O')
    assert(grid.get((3,1)) == 'X')
    assert(grid.get((3,2)) == 'O')
    assert(grid.get((3,3)) == 'X')
    assert(grid.get((3,4)) == 'O')

    assert(grid.get((4,0)) == 'O')
    assert(grid.get((4,1)) == 'O')
    assert(grid.get((4,2)) == 'O')
    assert(grid.get((4,3)) == 'O')
    assert(grid.get((4,4)) == 'O')

    plots: list[SchreberGarten] = extract_plots(text=text)
    assert(plots is not None)
    assert(len(plots) == 5)
    assert(plots[0].flavour == 'O')
    assert(plots[0].area() == 36)
    assert(plots[0].perimeter() == 21)

    assert(plots[1].flavour == 'X')
    assert(plots[1].area() == 1)
    assert(plots[1].perimeter() == 4)


    assert(plots[2].flavour == 'X')
    assert(plots[2].area() == 1)
    assert(plots[2].perimeter() == 4)


    assert(plots[3].flavour == 'X')
    assert(plots[3].area() == 1)
    assert(plots[3].perimeter() == 4)


    assert(plots[4].flavour == 'X')
    assert(plots[4].area() == 1)
    assert(plots[4].perimeter() == 4)

    #
    #    AAAAAAAA
    #    ABBBBBBA
    #    ABCCCCBA
    #    ABBBBBBA
    #    AAAAAAAA
    #
    text: str = 'AAAAAAAA\n' + 'ABBBBBBA\n' + 'ABCCCCBA\n' + 'ABBBBBBA\n' + 'AAAAAAAA'
    plots = extract_plots(text=text)
    assert(plots is not None)
    assert(len(plots) == 3)
    assert(plots[0][2] == 'A')
    assert(plots[0][1] == 20)
    assert(plots[1][0] == 'B')
    assert(plots[1][1] == 12)
    assert(plots[2][0] == 'C')
    assert(plots[2][1] == 3)


    #   AAAAADDDDD    AAAA   DDDDD
    #   AAAADDDEED    AAAA DDD EE D
    #   AABCCCCDDD    AA B CCCC DDD
    #   ABBCCCDDDD    A BB CCC DDDD
    #   AAAACCDDDD    AAAA  CC DDDD
    text = 'AAAAADDDDD\n' + 'AAAADDDEED\n' + 'AABCCCCDDD\n' + 'ABBCCCDDDD\n' + 'AAAACCDDDD\n'
    plots = extract_plots(text=text)
    assert(plots is not None)
    assert(len(plots) == 5)
    assert(plots[0] == (17, 26, 'A'))
    assert(plots[1] == (19, 21, 'D'))



def main(argv: list[str]):
    global very_verbose
    global verbose
    global OPERATORS
    very_verbose = False
    verbose = False
    result: int = 0
    result = part_one(path='day_twelve_input.txt')
    print(f'part one: {result=} for test data')
    if result != 55312:
        raise Exception(f'Test failed, expected 55312 but instead got {result}')
    return 0

if __name__ == "__main__":
    test()
    exit_code: int = main(sys.argv)
    sys.exit(exit_code)