import sys
import re
from copy import deepcopy

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

def perambulate(map:dict[tuple[int,int],int], starting_point:tuple[int,int], number_rows:int, number_columns:int) -> list[list[tuple[int,int]]]:
    
    return []

def traversable_squares(map: dict[tuple[int, int], int], starting_point: tuple[int, int], number_rows:int, number_columns:int) -> list[tuple[int,int]]:
    direction: int = EAST
    result: list[tuple[int,int]] = []
    while direction <= WEST:
        delta: tuple[int, int] = steps[direction]
        candidate_position: tuple[int, int] = (starting_point[0] + delta[0], starting_point[1] + delta[1])
        if not off_the_reservation(location=candidate_position, number_rows=number_rows, number_columns=number_columns):
            if candidate_position in map and map.get(candidate_position) == map.get(starting_point) + 1:
                result.append(candidate_position)
        direction += 1
    return result

def part_one(path: str) -> int:
    result: int = 0
    map_details:tuple[dict[tuple[int,int],int],tuple[int,int]] = read_map(path)

    map: dict[tuple[int, int], int] = map_details[0]
    number_rows: int = map_details[1][0]
    number_columns: int = map_details[1][1]

    # sweep one ... find nadir locations
    nadirs: list[tuple[int,int]] = [point for point, height in map.items() if height == 0]
    print(f'{nadirs=}')
    return result



def part_two(path: str) -> int:
    result: int = 0

    west_boundary: int = 0
    north_boundary: int = 0
    east_boundary: int = None

    # sweep one ... gather the ordering information
    with open(path, 'r') as file:
        row_index: int = 0
        for line in file:
            row_index += 1
    return result



def main(argv: list[str]):
    global very_verbose
    global verbose
    very_verbose = False
    verbose = False
    result: int = 0
    result = part_one(path='day_ten_test_input.txt')
    print(f'part one: {result=} for test data')
    if result != 36:
        raise Exception(f'Test failed, expected 41 but instead got {result}')
    result = part_one(path='day_ten_input.txt')
    print(f'part one: {result=} for actual data')
#
#    result = part_two(path='day_ten_small_test_input.txt')
#    print(f'part two: {result=} for small test data')

    result = part_two(path='day_ten_davros_input.txt')
    print(f'part two: {result=} for davros test data')

 #   result = part_two(path='day_ten_test_input.txt')
 #   print(f'part two: {result=} for test data')
 #   if result != 6:
 #       raise Exception(f'Test failed, expected 6 but instead got {result}')
 #   result: int = part_two(path='day_ten_input.txt')
 #   print(f'part two: {result=} for actual data')

    return 0

def test():
    map_details:tuple[dict[tuple[int, int], int],tuple[int,int]]  = read_map('day_ten_test_input.txt')
    topography_matrix = map_details[0]
    number_rows = map_details[1][0]
    number_columns = map_details[1][1]
    print(f'We have {number_rows=}, {number_columns=}')
    render(map=topography_matrix, number_rows=number_rows, number_columns=number_columns)

    map_details:tuple[dict[tuple[int, int], int],tuple[int,int]]  = ({(0,5):0, (1,5):1, (2,5):2, (3,5):3, (4,5):4, (4,3):5,(4,2):6,(4,1):7,(4,0):8,(3,0):9,(4,6):5, (4,7):6, (4,8):7, (4,9): 8, (3,9):9}, (5,10))
    nadirs = find_nadirs(map=map_details[0], number_rows=map_details[1][0], number_columns=map_details[1][1])
    for nadir in nadirs:
        paths: list[tuple[int,int]] = perambulate(map=map_details[0], starting_point=nadir, number_rows=number_rows, number_columns=number_columns)
        assert(len(paths) == 10)


    return

if __name__ == "__main__":
    test()
    exit_code: int = main(sys.argv)
    sys.exit(exit_code)