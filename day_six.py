import sys
import re

ORDER_LINE_INFO_PATTERN = re.compile(r'^\s*(\d+)\s*\|\s*(\d+)\s*$')
PAGES_LINE_INFO_PATTERN = re.compile(r'^\s*(\d+)\s*(,\s*(\d+)\s*)*$')

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

def find_following_page_numbers(page_ordering_map: dict[int, list[int]], page_number: int, result: list[int] = [], depth: int = 0) -> list[int]:
    if page_number not in page_ordering_map:
        return result
    following_pages: list[int] = page_ordering_map.get(page_number)
    for following_page_number in following_pages:
        # don't fall down the circular recursion trap!!
        if following_page_number in result:
            continue
        result.append(following_page_number)
        more_numbers: list[int] = find_following_page_numbers(page_ordering_map=page_ordering_map, page_number=following_page_number, result=result, depth=depth+1)
        for some_page_number in more_numbers:
            if some_page_number not in result and some_page_number not in following_pages:
                result.append(some_page_number)
    return result

def has_obstacle(location: tuple[int, int], map: list[list[int]]) -> bool:
    row: int = location[0]
    column: int = location[1]
    if row < 0 or row > len(map):
        raise Exception(f'{location} is out of bounds')
    row_obstacles: list[int] = map[row]
    obstructed: bool = column in row_obstacles
    return obstructed


def part_one(path: str) -> int:
    result: int = 0
    obstacles: list[list[int]] = []

    west_boundary: int = 0
    north_boundary: int = 0
    east_boundary: int = None


    # sweep one ... gather the ordering information
    with open(path, 'r') as file:
        row_index: int = 0
        for line in file:
            if east_boundary is None:
                east_boundary = len(line) - 1
            else:
                if len(line.strip()) != east_boundary:
                    raise Exception(f'Inconsistency in input data at row {row_index + 1}... expected grid line to be {east_boundary + 1} squares wide but is instead {len(line)}')
            row_obstacles: list[int] = []
            hash_pos: int = line.find('#')
            while(hash_pos >= 0):
                print(f'Found obstacle at row={row_index}, column={hash_pos}')
                row_obstacles.append(hash_pos)
                hash_pos = line.find('#', hash_pos + 1)
            obstacles.append(row_obstacles)
            row_index += 1

    south_boundary: int = row_index - 1

    guard_position: tuple[int, int] = None
    guard_direction: int = None

    # sweep two ... find the guard...
    with open(path, 'r') as file:
        row_index = 0
        for line in file:
            west_guard_pos: int = line.find('<')
            if west_guard_pos >= 0:
                guard_position = (row_index, west_guard_pos)
                guard_direction = WEST
                continue
            north_guard_pos: int = line.find('^')
            if north_guard_pos >= 0:
                guard_position = (row_index, north_guard_pos)
                guard_direction = NORTH
                continue
            east_guard_pos: int = line.find('>')
            if east_guard_pos >= 0:
                guard_position = (row_index, east_guard_pos)
                guard_direction = EAST
                continue
            south_guard_pos: int = line.find('V')
            if south_guard_pos >= 0:
                guard_position = (row_index, south_guard_pos)
                guard_direction = SOUTH
                continue
            row_index += 1

    print(f'Found guard at {guard_position=}, {guard_direction=}')

    # now for the "wandering about" ....
    visited: dict[tuple[int, int], int] = {}
    visited[(guard_position)] = 1
    out_of_bounds: bool = False
    while not out_of_bounds:
        dr = steps[guard_direction][0]
        dc = steps[guard_direction][1]
        next_position: tuple[int, int] = (guard_position[0] + dr, guard_position[1] + dc)
        next_out_of_bounds: bool = next_position[0] < north_boundary or next_position[0] > south_boundary or next_position[1] < west_boundary or next_position[1] > east_boundary
        if not next_out_of_bounds:
            blocked: bool = has_obstacle(next_position, obstacles)
            while(blocked):
                # we need to change direction....
                guard_direction = (guard_direction + 1) % 4
                dr = steps[guard_direction][0]
                dc = steps[guard_direction][1]
                next_position = (guard_position[0] + dr, guard_position[1] + dc)
                blocked = has_obstacle(next_position, obstacles)
        guard_position = next_position
        out_of_bounds: bool = guard_position[0] < north_boundary or guard_position[0] > south_boundary or guard_position[1] < west_boundary or guard_position[1] > east_boundary
        if out_of_bounds:
            continue
        visited[(guard_position)] = 1

    result = len(visited.keys())
    return result



def part_two(path: str) -> int:
    result: int = 0

    # sweep one ... gather the ordering information
    with open(path, 'r') as file:
        for line in file:
            pass
    return result


def main(argv: list[str]):


    result: int = 0
    result = part_one(path='day_six_test_input.txt')
    print(f'part one: {result=} for test data')
    if result != 41:
        raise Exception(f'Test failed, expected 41 but instead got {result}')
    result = part_one(path='day_six_input.txt')
    print(f'part one: {result=} for actual data')

    result = part_two(path='day_six_test_input.txt')
    print(f'part two: {result=} for test data')
    if result != 41:
        raise Exception(f'Test failed, expected 123 but instead got {result}')
    result: int = part_two(path='day_six_input.txt')
    print(f'part two: {result=} for actual data')

    return 0

if __name__ == "__main__":
    exit_code: int = main(sys.argv)
    sys.exit(exit_code)