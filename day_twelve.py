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

def off_the_reservation(position: tuple[int, int], extent:tuple[tuple[int,int],tuple[int,int]]|tuple[int,int]) -> bool:
    min_row: int = 0
    max_row: int = None
    min_column: int = 0
    max_column: int = None
    if isinstance(extent, tuple) and isinstance(extent[0], tuple) and isinstance(extent[1], tuple):
        min_row = extent[0][0]
        max_row = extent[1][0]
        min_column = extent[0][1]
        max_column = extent[1][1]
    elif isinstance(extent, tuple) and isinstance(extent[0], int) and isinstance(extent[1], int):
        max_row = extent[0]
        max_column = extent[1]
    result: bool = position[0] < min_row or position[0] >= max_row or position[1] < min_column or position[1] > max_column
    return result

verbose: bool = False
very_verbose: bool = False

@dataclass
class SchreberGarten:
    locations: dict[tuple[int, int], str]
    flavour: str

    def area(self) -> int:
        result: int = len(self.locations.keys())
        return result

    def extent(self) -> tuple[tuple[int, int], tuple[int, int]]:
        min_column: int|None = None
        max_column: int|None = None
        min_row: int|None = None
        max_row: int|None = None
        for location in self.locations:
            if min_row is None or location[0] < min_row:
                min_row = location[0]
            if max_row is None or location[0] > max_row:
                max_row = location[0]
            if min_column is None or location[1] < min_column:
                min_column = location[1]
            if max_column is None or location[1] > max_column:
                max_column = location[1]
        return((min_row, min_column), (max_row, max_column))

    def perimeter(self) -> int:
        # determine extent of our garden...
        result: int = 0
        for location in self.locations:
            for direction in [NORTH, SOUTH, EAST, WEST]:
                delta: tuple[int, int] = step_directions_by_direction.get(direction)
                adjacent_location = (location[0] + delta[0], location[1] + delta[1])
                if adjacent_location not in self.locations:
                    result += 1
        return result

    def edges(self) -> int:
        result: int = 0
        # sort locations left to right, top to bottom...
        sorted_locations: list[tuple[int, int]] = sorted(self.locations.keys(), key=lambda x: x[0] * 1000 + x[1])

        # look up table ... given the direction that an "edge" appears ... which neighbour should we check to see
        #                   if this edge is "shared"?
        neighbour_delta_by_edge_direction: dict[int, tuple[int,int]] = {
            NORTH: step_directions_by_direction.get(WEST),
            SOUTH: step_directions_by_direction.get(WEST),
            EAST:  step_directions_by_direction.get(NORTH),
            WEST:  step_directions_by_direction.get(NORTH)
        }

        for location in sorted_locations:
            # probe for edges in each direction....
            for direction in [NORTH, SOUTH, EAST, WEST]:
                delta: tuple[int, int] = step_directions_by_direction.get(direction)
                adjacent_location = (location[0] + delta[0], location[1] + delta[1])

                if adjacent_location not in self.locations:
                    # we have found an "edge"..... can we "claim" this for this position?

                    # do we have a neighbour in this plot that we've already visited that shares the "same edge"?
                    # for north and south edges; check the neighbour to the west for the presence of the same north or south "edge".
                    # for west and east edges; check the neighbour to the north for the presence of the same west or east "edge".
                    neighbour_delta: tuple[int,int] = neighbour_delta_by_edge_direction.get(direction)
                    neighbour_position: tuple[int, int] = (location[0] + neighbour_delta[0], location[1] + neighbour_delta[1])
                    neighbour_border_position: tuple[int, int] = (neighbour_position[0] + delta[0], neighbour_position[1] + delta[1])

                    if neighbour_position in self.locations and neighbour_border_position not in self.locations:
                        # we've already counted this edge ... so do NOT add it....
                        continue

                    result += 1

        return result

def part_one(path: str) -> int:
    result: int = 0

    # sweep one ... gather the ordering information
    with open(path, 'r') as file:
        input_data: list[str] = []
        for line in file:
            input_data.append(line.strip())

    plots = extract_plots(text=input_data)
    print(f'found {len(plots)} plots')
    for plot in plots:
        result += plot.area() * plot.perimeter()
    return result

def part_two(path: str) -> int:
    result: int = 0

    # sweep one ... gather the ordering information
    with open(path, 'r') as file:
        input_data: list[str] = []
        for line in file:
            input_data.append(line.strip())

    plots = extract_plots(text=input_data)
    print(f'found {len(plots)} plots')
    for plot in plots:
        result += plot.area() * plot.edges()
    return result

def step(position: tuple[int, int], direction: int) -> tuple[int, int]:
    delta: tuple[int, int] = step_directions_by_direction[direction]
    result: tuple[int, int] = (position[0] + delta[0], position[1] + delta[1])
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

def extract_grid(candidate: str|list[str]) -> tuple[dict[tuple[int, int], str],tuple[int,int]]:
    grid: dict[tuple[int, int], str] = {}
    lines: list[str] = candidate if isinstance(candidate, list) else candidate.strip().split('\n')
    max_width: int = None
    row: int = 0
    for line in lines:
        if len(line.strip()) == 0:
            continue
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

def explore(flavour: str, grid: dict[tuple[int, int], str], membership: dict[tuple[int, int], SchreberGarten], position: tuple[int, int], number_rows:int, number_columns: int, breadcrumbs: set[tuple[int, int]] = None, depth: int = 0) -> SchreberGarten|None:
    result: SchreberGarten|None = None

    if breadcrumbs is None:
        breadcrumbs: set[tuple[int, int]] = set()
    breadcrumbs.add(position)
    for direction in [WEST, NORTH, EAST, SOUTH]:
        candidate_position: tuple[int, int] = step(position=position, direction=direction)
        if off_the_reservation(position=candidate_position, extent=(number_rows, number_columns)):
            # don't proceed in this direction if it takes us out of our "universe"
            continue

        if candidate_position in breadcrumbs:
            # if this is a location we've already visited ... then don't proceed here.
            continue

        if grid.get(candidate_position) != flavour:
            # if this adjacent location is not of the same "type" ... ignore it.
            breadcrumbs.add(candidate_position)
            continue

        if candidate_position in membership:
            # hooray ... we found one...
            result = membership.get(candidate_position)
            return result

        # ok ... now explore in this direction...
        # we do NOT want the breadcrumbs we're using to be mutated in the following call...
        #breadcrumbs_copy = deepcopy(breadcrumbs)
        result = explore(flavour=flavour, grid=grid, membership=membership, position=candidate_position, breadcrumbs=breadcrumbs, number_rows=number_rows, number_columns=number_columns, depth=depth+1)
        if result is not None:
            # if there is a garden of the same place next to us .... return that as the garden that we should join...
            break
    return result

def extract_plots(text: str|list[str]) -> list[SchreberGarten]:
    result: list[SchreberGarten] = []
    twin: tuple[dict[tuple[int, int], str],tuple[int,int]] = extract_grid(candidate=text)
    grid: dict[tuple[int, int], str] = twin[0]
    number_rows, number_columns = twin[1]
    membership: dict[tuple[int, int], SchreberGarten] = {}
    visited: set[tuple[int, int]] = set()

    for row_index in range(number_rows):
        print(f'{row_index:03d}: ', end='')
        for column_index in range(number_columns):
            flavour: str = grid.get((row_index, column_index))
            position: tuple[int, int] = (row_index, column_index)
            visited.add(position)

            # is there any neighbour that belongs to a schrebergarten that we should join?
            breadcrumbs_copy = deepcopy(visited)
            existing_schrebergarten: SchreberGarten|None = explore(flavour=flavour, grid=grid, position=position, membership=membership, number_rows=number_rows, number_columns=number_columns)

            if existing_schrebergarten is not None:
                # join this schrebergarten!!
                existing_schrebergarten.locations[position] = flavour
                membership[position] = existing_schrebergarten
                print('.', end='')
            else:
                # create a brand new schrebergarten
                new_schrebergarten: SchreberGarten = SchreberGarten(flavour=flavour, locations={(position): flavour})
                result.append(new_schrebergarten)
                membership[position] = new_schrebergarten
                print(flavour, end='')
        print('')

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
    assert(plots[0].area() == 21)
    assert(plots[0].perimeter() == 36)
    assert(plots[0].edges() == 20)

    assert(plots[1].flavour == 'X')
    assert(plots[1].area() == 1)
    assert(plots[1].perimeter() == 4)
    assert(plots[1].edges() == 4)


    assert(plots[2].flavour == 'X')
    assert(plots[2].area() == 1)
    assert(plots[2].perimeter() == 4)
    assert(plots[2].edges() == 4)


    assert(plots[3].flavour == 'X')
    assert(plots[3].area() == 1)
    assert(plots[3].perimeter() == 4)
    assert(plots[3].edges() == 4)


    assert(plots[4].flavour == 'X')
    assert(plots[4].area() == 1)
    assert(plots[4].perimeter() == 4)
    assert(plots[4].edges() == 4)

    #
    #    AAAAAAAA
    #    ABBBBBBA
    #    ABCCCCBA
    #    ABBBBBBA
    #    AAAAAAAA
    #
    #    ........
    #    .BBBBBB.
    #    .B....B.
    #    .BBBBBB.
    #    ........

    # p(b) = 6 *2 + 3 * 2 + 4 * 2 + 1 * 2 = 12 + 6 + 8 + 2  = 28
    #
    text: str = 'AAAAAAAA\n' + 'ABBBBBBA\n' + 'ABCCCCBA\n' + 'ABBBBBBA\n' + 'AAAAAAAA'
    plots: list[SchreberGarten] = extract_plots(text=text)
    assert(plots is not None)
    assert(len(plots) == 3)
    assert(plots[0].flavour == 'A')
    assert(plots[0].area() == 22)
    assert(plots[0].perimeter() == 44)
    assert(plots[0].edges() ==  8)

    assert(plots[1].flavour == 'B')
    assert(plots[1].area() == 14)
    assert(plots[1].perimeter() == 28)
    assert(plots[1].edges() == 8)

    assert(plots[2].flavour == 'C')
    assert(plots[2].area() == 4)
    assert(plots[2].perimeter() == 10)
    assert(plots[2].edges() == 4)

    #    01234567
    #  0 ABAADDDD
    #  1 AAAADEED
    #  2 ABDDDCCC
    #  3 AABCCCDD
    #  4 ABBBCCDD
    #
    #
    #

    text = 'ABAADDDD\nAAAADEED\nABDDDCCC\nAABCCCDD\nABBBCCDD'
    plots = extract_plots(text=text)
    assert(plots is not None)
    assert(len(plots) == 8)
    assert(plots[0].flavour == 'A')
    assert(plots[0].area() == 11)
    assert(plots[0].perimeter() == 22)

    assert(plots[1].flavour == 'B')
    assert(plots[1].area() == 1)
    assert(plots[1].perimeter() == 4)

    assert(plots[2].flavour == 'D')
    assert(plots[2].area() == 9)
    assert(plots[2].perimeter() == 20)

    assert(plots[3].flavour == 'E')
    assert(plots[3].area() == 2)
    assert(plots[3].perimeter() == 6)

    assert(plots[4].flavour == 'B')
    assert(plots[4].area() == 1)
    assert(plots[4].perimeter() == 4)

    assert(plots[5].flavour == 'C')
    assert(plots[5].area() == 8)
    assert(plots[5].perimeter() == 16)

    assert(plots[6].flavour == 'B')
    assert(plots[6].area() == 4)
    assert(plots[6].perimeter() == 10)

    assert(plots[7].flavour == 'D')
    assert(plots[7].area() == 4)
    assert(plots[7].perimeter() == 8)


    #   AAAADDDD
    #   AAAADEED
    #   AADDDCCC
    #   AABCCCDD
    #   ABBBCCDD


    #   AAAAAADDDD    AAAAAA  DDDD
    #   AAAADDDEED    AAAA DDD EE D
    #   AABCCCCDDD    AA B CCCC DDD
    #   ABBCCCDDDD    A BB CCC DDDD
    #   AAAACCDDDD    AAAA  CC DDDD
    text = 'AAAAAADDDD\n' + 'AAAADDDEED\n' + 'AABCCCCDDD\n' + 'ABBCCCDDDD\n' + 'AAAACCDDDD\n'
    plots = extract_plots(text=text)
    assert(plots is not None)
    assert(len(plots) == 5)
    assert(plots[0].flavour == 'A')
    assert(plots[0].area() == 17)
    assert(plots[0].perimeter() == 28)

    assert(plots[1].flavour == 'D')
    assert(plots[1].area() == 19)
    assert(plots[1].perimeter() == 30)

    assert(plots[2].flavour == 'E')
    assert(plots[2].area() == 2)
    assert(plots[2].perimeter() == 6)

    assert(plots[3].flavour == 'B')
    assert(plots[3].area() == 3)
    assert(plots[3].perimeter() == 8)

    assert(plots[4].flavour == 'C')
    assert(plots[4].area() == 9)
    assert(plots[4].perimeter() == 14)

#
#   AAAAAA
# AAABBA
# AAABBA
# ABBAAA
# ABBAAA
# AAAAAA
#
#
    input_data: list[str] = [
        'AAAAAA',
        'AAABBA',
        'AAABBA',
        'ABBAAA',
        'ABBAAA',
        'AAAAAA'
    ]
    plots = extract_plots(text=input_data)
    assert(len(plots) == 3)
    assert(plots[0].flavour == 'A')
    assert(plots[0].area() == 28)
    assert(plots[0].edges() == 12)
    assert(plots[1].flavour == 'B')
    assert(plots[1].area() == 4)
    assert(plots[1].edges() == 4)
    assert(plots[2].flavour == 'B')
    assert(plots[2].area() == 4)
    assert(plots[2].edges() == 4)
    cost: int = plots[0].area() * plots[0].edges() + plots[1].area() * plots[1].edges() + plots[2].area() * plots[2].edges()
    assert(cost == 368)



def main(argv: list[str]):
    global very_verbose
    global verbose
    global OPERATORS
    very_verbose = False
    verbose = False
    result: int = 0
    result = part_one(path='day_twelve_test_input.txt')
    print(f'part one: {result=} for test data')
    if result != 1930:
        raise Exception(f'Test failed, expected 1930 but instead got {result}')
#    result = part_one(path='day_twelve_input.txt')
#    print(f'part one: {result=} for actual data')
#    if result != 1319878:
#        raise Exception(f'Test failed, expected 55312 but instead got {result}')
    result = part_two(path='day_twelve_test_input.txt')
    if result != 1206:
        raise Exception(f'Test failed, expected 1206 but instead got {result}')
    result = part_two(path='day_twelve_input.txt')
    print(f'part two: {result=} for ACTUAL data.')
    return 0

if __name__ == "__main__":
    test()
    exit_code: int = main(sys.argv)
    sys.exit(exit_code)