import sys

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

def extract_letter(grid: list[str], row: int, column: int) -> str:
    result: str = ''
    if row >= 0 and row < len(grid) and column >= 0 and column < len(grid[row]):
        result = grid[row][column]
    return result


def part_one(path: str) -> int:
    result: int = 0
    with open(path, 'r') as file:
        lines: list[str] = file.readlines()

    for row in range(len(lines)):
        for column in range(len(lines[row])):
            # for each cardinal direction ....
            for direction in range(NORTH_EAST + 1):
                step_column, step_row = step_directions_by_direction[direction]
                r: int = row
                c: int = column
                candidate: str = ''

                for i in range(4):
                    letter = extract_letter(grid=lines, row=r, column=c)
                    r += step_row
                    c += step_column
                    candidate += letter

                # only search in the one direction; we're eventually going to match words going backwards
                # from the opposite direction.
                if candidate.lower() == 'xmas':
                   result += 1

    return result

def part_two(path: str) -> int:
    result: int = 0
    with open(path, 'r') as file:
        lines: list[str] = file.readlines()

    for row in range(len(lines)):
        for column in range(len(lines[row])):
            candidate_alpha: str = ''
            candidate_alpha += extract_letter(grid=lines, row=row - 1, column=column - 1)
            candidate_alpha += extract_letter(grid=lines, row=row, column=column)
            candidate_alpha += extract_letter(grid=lines, row=row + 1, column=column + 1)

            candidate_beta: str = ''
            candidate_beta += extract_letter(grid=lines, row=row + 1, column=column - 1)
            candidate_beta += extract_letter(grid=lines, row=row, column=column)
            candidate_beta += extract_letter(grid=lines, row=row - 1, column=column + 1)

            if (candidate_alpha.lower() == 'mas' or candidate_alpha.lower() == 'sam') and (candidate_beta.lower() == 'mas' or candidate_beta.lower() == 'sam'):
                result += 1

    return result


def main(argv: list[str]):
    result: int = part_one(path='day_four_test_input.txt')
    print(f'part one: {result=} for test data')
    if result != 18:
        raise Exception('Test failed')
    result = part_one(path='day_four_actual_input.txt')
    print(f'part one: {result=} for actual data')

    result = part_two(path='day_four_test_input.txt')
    print(f'part two: {result=} for test data')
    if result != 9:
        raise Exception('Test failed')
    result: int = part_two(path='day_four_actual_input.txt')
    print(f'part two: {result=} for actual data')

    return 0

if __name__ == "__main__":
    exit_code: int = main(sys.argv)
    sys.exit(exit_code)