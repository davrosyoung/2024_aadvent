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

def off_the_reservation(location: tuple[int, int], boundaries: tuple[int, int, int, int]) -> bool:
    north_boundary: int  = boundaries[NORTH]
    east_boundary: int  = boundaries[EAST]
    south_boundary: int  = boundaries[SOUTH]
    west_boundary: int  = boundaries[WEST]

    result: bool = location[0] > south_boundary or location[0] < north_boundary or location[1] < west_boundary or location[1] > east_boundary
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

def perambulate(map: list[list[int]], boundaries: tuple[int, int, int, int], location: tuple[int, int], direction: int, breadcrumbs: dict[tuple[int, int], set[int]]|None=None) -> tuple[bool, bool, list[tuple[int, int, int]]]:
    """Follows the specified path until either we wander off the reservation or find ourselves back where we started...."""
    if breadcrumbs is None:
        breadcrumbs = {}

    loop_detected: bool = False
    next_location: tuple[int, int]|None = None
    next_direction: int = direction  # until it gets altered!!
    alternate_history: list[tuple[int, int, int]] = []

    out_of_bounds: bool = False
    while not out_of_bounds:
        next_location = next_step(location=location, direction=direction)
        out_of_bounds: bool = off_the_reservation(location=next_location, boundaries=boundaries)
        if out_of_bounds:
            continue

        # if the next step would encounter an obstacle, then point ourselves in a new direction.
        remaining_turn_count: int = 4
        while has_obstacle(location=next_location, map=map) and remaining_turn_count > 0:
            # turn right instead.....
            next_direction = turn_right(direction)
            next_location = next_step(location=location, direction=next_direction)
            remaining_turn_count -= 1

        # if blocked in all directions; then we're done.
        if remaining_turn_count == 0:
            loop_detected = True
            break

        # are we following our previous footsteps in the same direction?
        if next_location in breadcrumbs:
            prior_directions: set[int] = breadcrumbs.get(next_location)
            if next_direction in prior_directions:
                loop_detected = True
                continue

        location = next_location
        direction = next_direction
        if location not in breadcrumbs:
            breadcrumbs[location] = {direction}
        else:
            breadcrumbs[location].add(direction)
        alternate_history.append((location[0], location[1], direction))

    return out_of_bounds, loop_detected, alternate_history


def road_to_nowhere(map: list[list[int]], location: tuple[int, int], direction: int, breadcrumbs: dict[tuple[int, int], set[int]]|None=None) -> bool:
    """Return true if heading off in the specified direction from the specified
    location ends up with the guard following an endless loop."""
    if breadcrumbs is None:
        breadcrumbs = {}


    if location in breadcrumbs:
        if direction in breadcrumbs[location]:
            return True
        breadcrumbs[location].add(direction)
    else:
        breadcrumbs[location] = set([direction])
    next_location: tuple[int, int] = next_step(location=location, direction=direction)
    if has_obstacle(location=next_location, map=map):
        return leads_nowhere(map=map, location=next_location, direction=turn_right(direction), breadcrumbs=breadcrumbs)
    if next_location in breadcrumbs:
        if direction in breadcrumbs[next_location]:
            return True
        breadcrumbs[next_location].add(direction)
    else:
        breadcrumbs[next_location] = set([direction])
    breadcrumbs: dict[tuple[int, int], set[int]] = {}
    return False


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
                east_boundary = len(line.strip()) - 1
            else:
                if len(line.strip()) != east_boundary + 1:
                    raise Exception(f'Inconsistency in input data at row {row_index + 1}... expected grid line to be {east_boundary + 1} squares wide but is instead {len(line)}')
            row_obstacles: list[int] = []
            hash_pos: int = line.find('#')
            while(hash_pos >= 0):
                #print(f'Found obstacle at row={row_index}, column={hash_pos}')
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
    breadcrumbs: dict[tuple[int, int], int] = {}
    breadcrumbs[(guard_position)] = 1
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
        breadcrumbs[(guard_position)] = 1

    result = len(breadcrumbs.keys())
    return result

def part_two(path: str) -> int:
    result: int = 0
    obstacles: list[list[int]] = []
    guard_position: tuple[int, int] = None
    guard_direction: int = None
    east_boundary: int = None
    south_boundary: int = None
    history: list[tuple[int, int, int]] = []

    # gather the obstacles and guard position in one fell swoop...
    with open(path, 'r') as file:
        row_index: int = 0
        for line in file:
            if east_boundary is None:
                east_boundary = len(line.strip()) - 1
            else:
                if len(line.strip()) != east_boundary + 1:
                    raise Exception(f'Inconsistency in input data at row {row_index + 1}... expected grid line to be {east_boundary + 1} squares wide but is instead {len(line)}')
            row_obstacles: list[int] = []
            hash_pos: int = line.find('#')
            while (hash_pos >= 0):
                #print(f'Found obstacle at row={row_index}, column={hash_pos}')
                row_obstacles.append(hash_pos)
                hash_pos = line.find('#', hash_pos + 1)
            obstacles.append(row_obstacles)

            twin: tuple[int,int]|None = find_guard(line)
            if twin is not None:
                guard_position = (row_index, twin[0])
                guard_direction = twin[1]

            row_index += 1

    south_boundary = row_index - 1
    boundaries: tuple[int, int, int, int] = (0, east_boundary, south_boundary, 0)

    print(f'Found guard at {guard_position=}, {guard_direction=}, {boundaries=}')

    # now for the "wandering about" ....
    next_position: tuple[int, int]|None = None
    next_direction: int = guard_direction # until we change it
    breadcrumbs: dict[tuple[int, int], set[int]] = {}
    breadcrumbs[(guard_position)] = {guard_direction}
    history.append((guard_position[0], guard_position[1], guard_direction))
    out_of_bounds: bool = False
    while not out_of_bounds:
        next_position: tuple[int, int] = next_step(guard_position, next_direction)
        next_out_of_bounds: bool = off_the_reservation(next_position, boundaries)
        # if the next step in the current direction takes us off the edge of the map ... we're done here.
        if next_out_of_bounds:
            out_of_bounds = True
            continue

        blocked: bool = has_obstacle(next_position, obstacles)
        remaining_turn_count: int = 4
        while (blocked) and remaining_turn_count > 0:
            # we need to change direction....
            next_direction = turn_right(next_direction)
            next_position = next_step(guard_position, next_direction)
            blocked = has_obstacle(next_position, obstacles)
            remaining_turn_count -= 1

        if remaining_turn_count == 0:
            raise Exception(f'Did not expect this to occur!! {guard_position=}, {guard_direction=}, {next_position=}, {next_direction=}, {remaining_turn_count=}')

        # before we take the next step ... would adding an obstacle there cause the guard to have to turn and end
        # up pursuing the same path over and over?!?
        map_with_extra_obstacle: list[list[int]] = obstacles.copy()
        map_with_extra_obstacle[next_position[0]].append(next_position[1])         # place obstacle where we're headed.
        copy_of_breadcrumbs: dict[tuple[int, int], set[int]] = breadcrumbs.copy()  # we don't want to mutate the actual path we've taken
        exits_map, would_loop, fake_history = perambulate(map=obstacles, boundaries=boundaries, location=guard_position, direction=guard_direction, breadcrumbs=copy_of_breadcrumbs)
        if would_loop:
            # if following a path with the extra obstacle ends up looping, then record the fact that we found this solution
            result += 1

        # now continue onto the next position
        guard_position = next_position
        guard_direction = next_direction

        # record the fact that we've visited this location in this heading...
        breadcrumbs[(guard_position)] = {guard_direction}
        history.append((guard_position[0], guard_position[1], guard_direction))

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
        raise Exception(f'Test failed, expected 6 but instead got {result}')
    result: int = part_two(path='day_six_input.txt')
    print(f'part two: {result=} for actual data')

    return 0

if __name__ == "__main__":
    exit_code: int = main(sys.argv)
    sys.exit(exit_code)