import sys
import re

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

def turn_right(direction: int) -> int:
    """"Just so that our code reads nicely"""
    result: int = (direction + 1) % 4
    return result

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

def find_guard(candidate: str) -> tuple[int, int]|None:
    """Return the column and direction of the guard if found upon the provided line"""
    result: tuple[int, int]|None = None
    # dummy loop to "continue"/break out of...
    for i in range(1):
        pos: int = candidate.find('<')
        if pos >= 0:
            result = (pos, WEST)
            continue
        pos = candidate.find('^')
        if pos >= 0:
            result = (pos, NORTH)
            continue
        pos = candidate.find('>')
        if pos >= 0:
            result = (pos, EAST)
            continue
        pos = candidate.find('V')
        if pos >= 0:
            result = (pos, SOUTH)
            continue
    return result


def next_step(location: tuple[int, int], direction: int) -> tuple[int, int]:
    dr: int = steps[direction][0]
    dc: int = steps[direction][1]
    result: tuple[int, int] = (location[0] + dr, location[1] + dc)
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
    guard_position: tuple[int, int] = None
    guard_direction: int = None

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

            twin: tuple[int,int]|None = find_guard(line)
            if twin is not None:
                guard_position = (row_index, twin[0])
                guard_direction = twin[1]

            row_index += 1


    south_boundary: int = row_index - 1


    # sweep two ... find the guard...
    with open(path, 'r') as file:
        row_index = 0
        for line in file:
            row_index += 1

    print(f'Found guard at {guard_position=}, {guard_direction=}')

    # now for the "wandering about" ....
    visited: dict[tuple[int, int], int] = {}
    visited[(guard_position)] = 1
    out_of_bounds: bool = False
    while not out_of_bounds:
        next_position: tuple[int, int] = next_step(guard_position, guard_direction)
        next_out_of_bounds: bool = next_position[0] < north_boundary or next_position[0] > south_boundary or next_position[1] < west_boundary or next_position[1] > east_boundary
        if not next_out_of_bounds:
            blocked: bool = has_obstacle(next_position, obstacles)
            while(blocked):
                # we need to change direction....
                guard_direction = turn_right(guard_direction)
                next_position = next_step(guard_position, guard_direction)
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
    obstacles: list[list[int]] = []
    guard_position: tuple[int, int] = None
    guard_direction: int = None

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
                    raise Exception(
                        f'Inconsistency in input data at row {row_index + 1}... expected grid line to be {east_boundary + 1} squares wide but is instead {len(line)}')
            row_obstacles: list[int] = []
            hash_pos: int = line.find('#')
            while (hash_pos >= 0):
                print(f'Found obstacle at row={row_index}, column={hash_pos}')
                row_obstacles.append(hash_pos)
                hash_pos = line.find('#', hash_pos + 1)
            obstacles.append(row_obstacles)

            twin: tuple[int,int]|None = find_guard(line)
            if twin is not None:
                guard_position = (row_index, twin[0])
                guard_direction = twin[1]

            row_index += 1

    south_boundary: int = row_index - 1

    print(f'Found guard at {guard_position=}, {guard_direction=}')

    # now for the "wandering about" ....
    visited: dict[tuple[int, int], set[int]] = {}
    visited[(guard_position)] = {guard_direction}
    out_of_bounds: bool = False
    while not out_of_bounds:
        next_position: tuple[int, int] = next_step(guard_position, guard_direction)
        next_out_of_bounds: bool = next_position[0] < north_boundary or next_position[0] > south_boundary or next_position[1] < west_boundary or next_position[1] > east_boundary
        if not next_out_of_bounds:
            blocked: bool = has_obstacle(next_position, obstacles)
            while (blocked):
                # we need to change direction....
                guard_direction = turn_right(guard_direction)
                next_position = next_step(guard_position, guard_direction)
                blocked = has_obstacle(next_position, obstacles)
        guard_position = next_position
        out_of_bounds: bool = guard_position[0] < north_boundary or guard_position[0] > south_boundary or guard_position[1] < west_boundary or guard_position[1] > east_boundary
        if out_of_bounds:
            continue
        if guard_position in visited:
            previous_visits: set[int] = visited[guard_position]
            # if we have previously walked upon this square, but in a direction 90 degrees clockwise to our
            # current direction, then adding an obstacle within the next square upon the path that we are
            # travelling would cause the guard to enter a loop
            would_loop_direction: int = turn_right(guard_direction)
            if would_loop_direction in previous_visits:
                # ok .... let's increment our counter!!
                result += 1


            # now add our visit in our current direction upon this square...
            previous_visits.add(guard_direction)
        else:
            visited[(guard_position)] = {guard_direction}

        # if adding an obstacle in the next position would cause our guard to reach a previously reached
        # square in the same direction as previously traversed .... that is also a great location to place an obstacle
        # ... mind you ... we are gioing to have to trace that possilbity until we wander off the reservations.
        # diverted_location: int = turn_right(guard_direction)


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
    if result != 6:
        raise Exception(f'Test failed, expected 123 but instead got {result}')
    result: int = part_two(path='day_six_input.txt')
    print(f'part two: {result=} for actual data')

    return 0

if __name__ == "__main__":
    exit_code: int = main(sys.argv)
    sys.exit(exit_code)