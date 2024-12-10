import sys
import re
from copy import deepcopy
from math import floor

ORDER_LINE_INFO_PATTERN = re.compile(r'^\s*(\d+)\s*\|\s*(\d+)\s*$')
PAGES_LINE_INFO_PATTERN = re.compile(r'^\s*(\d+)\s*(,\s*(\d+)\s*)*$')

# deliberately number the directions such that by incrementing a direction by one,
# it is equivalent to turning clockwise by ninety degress (turning to the right).
NORTH: int = 0
EAST: int = 1
SOUTH: int = 2
WEST: int = 3

DIRECTION: list[str] = ['NORTH', 'EAST', 'SOUTH', 'WEST']

# use MATRIX notation ... row, then column (dr, dc)
steps: dict[int, tuple[int, int]] = {
    NORTH: (-1, 0),
    EAST: (0, 1),
    SOUTH: (1, 0),
    WEST: (0, -1),
}

verbose: bool = False
very_verbose: bool = False

def render(map: dict[tuple[int, int], int], number_rows: int, number_columns: int):
    for row in range(number_rows):
        line: str = ''
        for column in range(number_columns):
            position: tuple[int, int] = (row, column)
            khar: str = str(map.get(position)) if position in map else '.'
            line += khar
        print(line)
    return

def off_the_reservation(location: tuple[int, int], number_rows: int, number_columns: int) -> bool:
    result: bool = location[0] < 0 or location[0] >= number_rows or location[1] < 0 or location[1] >= number_columns
    return result

def find_nadirs(map: dict[tuple[int, int], int], number_rows: int, number_columns: int) -> list[tuple[int, int]]:
    result = [position for position, height in map.items() if height == 0]
    return result

def next_step(map: dict[tuple[int, int], int], location: tuple[int, int], direction: int, number_rows: int, number_columns: int) -> tuple[int,int]|None:
    dr: int = steps[direction][0]
    dc: int = steps[direction][1]
    candidate: tuple[int, int] = (location[0] + dr, location[1] + dc)
    result = None if off_the_reservation(location=candidate, number_rows=number_rows, number_columns=number_columns) or candidate not in map else candidate
    return result

def read_map(path: str) -> tuple[dict[tuple[int, int], int],tuple[int,int]]:
    result: tuple[dict[tuple[int, int], int],tuple[int,int]]
    map: dict[tuple[int, int], int] = {}
    max_column: int = None

    with open(path, 'r') as file:
        row_index: int = 0
        for line in file:
            for i in range(len(line.strip())):
                khar: str = line[i]
                if khar.isdigit():
                    height: int = int(khar)
                    map[(row_index, i)] = height
                if max_column is None or i > max_column:
                    max_column = i
            row_index += 1
    result = (map, (row_index, max_column + 1))
    return result

def traversable_squares(map: dict[tuple[int, int], int], location: tuple[int, int], number_rows: int, number_columns: int) -> list[tuple[int,int]]:
    direction: int = EAST
    result: list[tuple[int,int]] = []
    while direction <= WEST:
        delta: tuple[int, int] = steps[direction]
        candidate_position: tuple[int, int] = (location[0] + delta[0], location[1] + delta[1])
        if not off_the_reservation(location=candidate_position, number_rows=number_rows, number_columns=number_columns):
            if candidate_position in map and map.get(candidate_position) == map.get(location) + 1:
                result.append(candidate_position)
        direction += 1
    return result

def follow_paths(map:dict[tuple[int, int], int], location:tuple[int, int], number_rows:int, number_columns:int) -> list[list[tuple[int,int]]]:
    result: list[list[tuple[int,int]]] = []

    next_steps: list[tuple[int, int]] = traversable_squares(map=map, location=location, number_rows=number_rows, number_columns=number_columns)
    for next_step in next_steps:
        result.append([next_step])
        if map.get(next_step) < 9:
            # where can we end up from here?
            more_paths: list[list[tuple[int, int]]] = follow_paths(map=map, location=next_step, number_rows=number_rows, number_columns=number_columns)

            result.extend()
    return result



    next_location: tuple[int,int] = starting_point
    next_direction: int = EAST
    while True:
        next_location = next_step(location=next_location, direction=next_direction)
        if off_the_reservation(location=next_location, number_rows=number_rows, number_columns=number_columns):
            break
        if next_location in map:
            result.append(next_location)
        next_direction = (next_direction + 1) % 4
    return result

def follow_path(map:dict[tuple[int, int], int], location:tuple[int, int], instructions:list[int], number_rows:int, number_columns:int) -> tuple[int,int]|None:
    result: tuple[int,int] = None
    index: int = 0
    finito: bool = False
    current_location: tuple[int, int] = location
    height: int = map.get(current_location)
    while not finito:
        direction = instructions[index]
        next_location: tuple[int,int] = next_step(map=map, location=current_location, direction=direction, number_rows=number_rows, number_columns=number_columns)
        if next_location is None:
            finito = True
            continue
        # if this next location is not one unit higher than the last ... abandon the trail...
        next_height: int = map.get(next_location)
        if next_height != height + 1:
            finito = True
            continue
        index += 1
        height = next_height
        current_location = next_location
        if height == 9:
            # we made it to the summit!! what were the chances?!?!
            result = current_location
            finito = True

    return result

def determine_instructions(i:int) -> list[int]:
    result: list[int] = []
    for j in range(9):
        # b is the value that we can divide by in order to extract the direction for this position
        b: int = pow(4, j)
        # c will allow us to extract the operator value for column j
        c: int = floor(i / b)
        direction: int = c % 4
        result.append(direction)
    return result

def perambulate(map:dict[tuple[int,int],int], starting_point:tuple[int,int], number_rows:int, number_columns:int) -> int:
    # sanity checks
    if starting_point not in map:
        raise Exception(f'Expected location {starting_point=} to have a registered altitude (of zero); but it is missing.')
    if map.get(starting_point) != 0:
        raise Exception(f'Expected location {starting_point=} to have height zero, but instead is {map.get(starting_point)}')
    if off_the_reservation(location=starting_point, number_rows=number_rows, number_columns=number_columns):
        raise Exception(f'Expected location {starting_point=} to be within the bounds of the map; but it is not.')

    summits: set[tuple[int, int]] = set()

    # find directions that we can go from here....
    for i in range(pow(4,9)):
        instructions = determine_instructions(i=i)
        destination: tuple[int, int] = follow_path(map, location=starting_point, instructions=instructions, number_rows=number_rows, number_columns=number_columns)
        if destination:
            # doesn't matter if we get to the same summit twice .... this is a set.
            summits.add(destination)

    result = len(summits)
    return result

def perambulate_too(map:dict[tuple[int,int],int], starting_point:tuple[int,int], number_rows:int, number_columns:int) -> int:
    # sanity checks
    if starting_point not in map:
        raise Exception(f'Expected location {starting_point=} to have a registered altitude (of zero); but it is missing.')
    if map.get(starting_point) != 0:
        raise Exception(f'Expected location {starting_point=} to have height zero, but instead is {map.get(starting_point)}')
    if off_the_reservation(location=starting_point, number_rows=number_rows, number_columns=number_columns):
        raise Exception(f'Expected location {starting_point=} to be within the bounds of the map; but it is not.')

    summits: list[tuple[int, int]] = []

    # find directions that we can go from here....
    for i in range(pow(4,9)):
        instructions = determine_instructions(i=i)
        destination: tuple[int, int] = follow_path(map, location=starting_point, instructions=instructions, number_rows=number_rows, number_columns=number_columns)
        if destination:
            # take all paths that lead to a summit, even the same summit
            summits.append(destination)

    result = len(summits)
    return result

def part_one(path: str) -> int:
    result: int = 0
    map_details:tuple[dict[tuple[int,int],int],tuple[int,int]] = read_map(path)

    map: dict[tuple[int, int], int] = map_details[0]
    number_rows: int = map_details[1][0]
    number_columns: int = map_details[1][1]


    # sweep one ... find nadir locations
    nadirs: list[tuple[int,int]] = [point for point, height in map.items() if height == 0]

    for nadir in nadirs:
        number_summits: int = perambulate(map=map, starting_point=nadir, number_rows=number_rows, number_columns=number_columns)
        result += number_summits
    return result



def part_two(path: str) -> int:
    result: int = 0
    map_details:tuple[dict[tuple[int,int],int],tuple[int,int]] = read_map(path)

    map: dict[tuple[int, int], int] = map_details[0]
    number_rows: int = map_details[1][0]
    number_columns: int = map_details[1][1]


    # sweep one ... find nadir locations
    nadirs: list[tuple[int,int]] = [point for point, height in map.items() if height == 0]

    for nadir in nadirs:
        number_summits: int = perambulate_too(map=map, starting_point=nadir, number_rows=number_rows, number_columns=number_columns)
        result += number_summits
    return result



def main(argv: list[str]):
    global very_verbose
    global verbose
    very_verbose = False
    verbose = False
    result: int = 0
#    result = part_one(path='day_ten_test_input.txt')
#    print(f'part one: {result=} for test data')
#    if result != 36:
#        raise Exception(f'Test failed, expected 36 but instead got {result}')
#    result = part_one(path='day_ten_input.txt')
#    print(f'part one: {result=} for actual data')

    result = part_two(path='day_ten_test_input.txt')
    print(f'part two: {result=} for test data')
    if result != 81:
        raise Exception(f'Test failed, expected 81 but instead got {result}')
    result: int = part_two(path='day_ten_input.txt')
    print(f'part two: {result=} for actual data')

    return 0

def test():
    map_details:tuple[dict[tuple[int, int], int],tuple[int,int]]  = read_map('day_ten_test_input.txt')
    topography_matrix = map_details[0]
    number_rows = map_details[1][0]
    number_columns = map_details[1][1]
    print(f'We have {number_rows=}, {number_columns=}')
    render(map=topography_matrix, number_rows=number_rows, number_columns=number_columns)

    summit: tuple[int, int] = follow_path(map=topography_matrix, location=(0,2), instructions=[SOUTH, EAST, SOUTH, WEST, SOUTH, WEST, NORTH, WEST, SOUTH], number_rows=number_rows, number_columns=number_columns)
    assert summit == (3,0)

    result = perambulate(map=topography_matrix, starting_point=(0,2), number_rows=number_rows, number_columns=number_columns)
    assert(result == 5)
    result = perambulate(map=topography_matrix, starting_point=(0,4), number_rows=number_rows, number_columns=number_columns)
    assert(result == 6)

    return

if __name__ == "__main__":
    #test()
    exit_code: int = main(sys.argv)
    sys.exit(exit_code)