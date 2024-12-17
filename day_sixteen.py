import os
import sys
import re
from math import floor

import math
from time import sleep

verbose: bool = False
very_verbose: bool = False

PI: float =  3.14159265358979323846

ROBOT_PATTERN: re.Pattern = re.compile(r'^p=([+\-]?\d+),([+\-]?\d+)\s+v=([+\-]?\d+),([+\-]?\d+)\s*$', re.IGNORECASE)


class Vector:
    def __init__(self, x: float, y: float):
        self.x: float = x
        self.y: float = y

    def __str__(self):
        result = f'x={self.x:6.4f},y={self.y:6.4f}'
        return result

    def multiply(self, m: int) -> 'Vector':
        result: Vector = Vector(x=self.x * m, y=self.y * m)
        return result

    def add(self, other: 'Vector') -> 'Vector':
        result = Vector(x=self.x + other.x, y=self.y + other.y)
        return result

    def rotate(self, degrees: float) -> 'Vector':
        radians: float = degrees * (PI / 180)
        x: float = self.x * math.cos(radians) - self.y * math.sin(radians)
        y: float = self.x * math.sin(radians) + self.y * math.cos(radians)
        return Vector(x,y)

    def gradient(self) -> float:
        return self.x / self.y if self.y != 0 else 99999999.999

class IntegerVector:
    def __init__(self, x: int, y: int):
        self.x: int = x
        self.y: int = y

    def __str__(self):
        result = f'x={self.x:d},y={self.y:d}'
        return result

    def multiply(self, m: int) -> 'IntegerVector':
        result: IntegerVector = IntegerVector(x=self.x * m, y=self.y * m)
        return result

    def add(self, other: 'IntegerVector') -> 'IntegerVector':
        result = IntegerVector(x=self.x + other.x, y=self.y + other.y)
        return result

    def gradient(self) -> float:
        return float(self.x / self.y) if self.y != 0 else 99999999.999

class Robot:
    def __init__(self, position: IntegerVector, velocity: IntegerVector, grid_width: int, grid_height: int):
        self.original_position: IntegerVector = position
        self.original_velocity: IntegerVector = velocity
        self.position: IntegerVector = position
        self.velocity: IntegerVector = velocity
        self.grid_width: int = grid_width
        self.grid_height: int = grid_height
        self.elapsed_iterations: int = 0

    def __str__(self):
        result = f'p={self.position},v={self.velocity}'
        return result

    def move(self, iterations: int) -> IntegerVector:
        self.elapsed_iterations += iterations
        self.position = self.position.add(self.velocity.multiply(iterations))
        self.position.x = ((self.position.x % self.grid_width) + self.grid_width) % self.grid_width
        self.position.y = ((self.position.y % self.grid_height) + self.grid_height) % self.grid_height
        return self.position


def future_locations(robots: list[Robot], width: int, height: int, iterations: int) -> list[Vector]:
    pass

def quadrant_from_location(location: IntegerVector, width: int, height: int) -> int|None:
    centre_x: int = floor(width / 2)
    centre_y: int = floor(height / 2)
    result: int|None
    if location.x == centre_x or location.y == centre_y:
        result = None
    elif location.x < centre_x and location.y < centre_y:
        result = 0
    elif location.x >= centre_x and location.y < centre_y:
        result = 1
    elif location.x < centre_x and location.y > centre_y:
        result = 2
    elif location.x > centre_x and location.y > centre_y:
        result = 3
    return result

def quadrants_from_locations(locations: list[IntegerVector], width: int, height: int) -> dict[int, int]:
    result: dict[int, int] = {0: 0, 1: 0, 2: 0, 3: 0}
    for location in locations:
        quadrant: int| None = quadrant_from_location(location=location, width=width, height=height)
        result[quadrant] += 1
    return result

def extract_robots(path: str, grid_width: int, grid_height: int) -> list[Robot]:
    if not os.path.exists(path) or not os.path.isfile(path):
        raise Exception(f'Specified path {path} not a file we can read')

    result: list[Robot] = []
    
    with open(path, 'r') as file:
        line_number: int = 0
        for line in file:
            line_number += 1
            text: str = line.strip()
            bits = ROBOT_PATTERN.match(text)
            if bits is None:
                continue
            position=IntegerVector(x=int(bits[1]), y=int(bits[2]))
            velocity=IntegerVector(x=int(bits[3]), y=int(bits[4]))
            robot = Robot(position=position, velocity=velocity, grid_width=grid_width, grid_height=grid_height)
            result.append(robot)

    return result

def j_factor(grid: dict[[int, int], int], width: int, height: int) -> float:
    multi__neighbour_count: int = 0
    diagonal_neighbour_count: int = 0
    void_count: int = 0
    void_visited: dict[tuple[int, int], int] = {}
    count_by_neighbour_count: dict[int, int] = {}

    for y in range(height):
        for x in range(width):
            if (x,y) not in grid:
                if (x,y) not in void_visited:
                    # if this is a vacant pixel, are its neighbours also vacant? if so, add to the "void count
                    all_empty: bool = True
                    void_addresses: list[tuple[int, int]] = []
                    for y0 in range(max(0, y-4), min(height, y+4)):
                        if not all_empty:
                            continue
                        for x0 in range(max(0, x-4), min(width, x+4)):
                            if (x0, y0) in grid:
                                all_empty = False
                                break
                            void_addresses.append((x0, y0))
                    if all_empty:
                        void_count += 1
                        # ensure we do not "over count" voids
                        for address in void_addresses:
                            if address not in void_visited:
                                void_visited[address] = 0
                            void_visited[address] += 1
            else:
                neighbour_count: int = 0
                for x0 in range(x-1, x+2):
                    for y0 in range(y-1, y+2):
                        if (x0, y0) in grid:
                            neighbour_count += 1
                        if (x0 == x - 1 or x0 == x + 1) and (y0 == y -1 or y0 == y + 1):
                            diagonal_neighbour_count += 1
                if neighbour_count not in count_by_neighbour_count:
                    count_by_neighbour_count[neighbour_count]  = 0
                count_by_neighbour_count[neighbour_count] += 1

    total: int = sum(count_by_neighbour_count.values())
    connectivity_count: int = 0
    for neighbour_count in count_by_neighbour_count:
        connectivity_count += neighbour_count * count_by_neighbour_count[neighbour_count]
    result = float(connectivity_count) / float(total)
    return result


def extract_grid_from_robots(robots: list[Robot], width: int, height: int) -> dict[tuple[int, int], int]:
    result: dict[tuple[int, int], int] = {}
    for robot in robots:
        if robot.position.x < 0 or robot.position.x >= width or robot.position.y < 0 or robot.position.y >= height:
            continue
        if (robot.position.x, robot.position.y) not in result:
            result[(robot.position.x, robot.position.y)] = 0
        result[(robot.position.x, robot.position.y)] += 1
    return result

def render(robots: list[Robot], width: int, height: int, output_filename: str, min_rating: float = 0.0, iteration: int = None) -> float:
    result: str = ''
    occupied: list[dict[int,int]] = []
    grid: dict[tuple[int,int], int] = extract_grid_from_robots(robots=robots, width=width, height=height)

    rating: float = j_factor(grid=grid, width=width, height=height)

    if iteration is not None:
        print(f'--------------------------<{iteration=:06d}, {rating=:06.4f}>-----------------------')
    else:
        print(f'--------------------------<{rating=:04.4f}>-----------------------')

    if rating >= min_rating:

        for y in range(height):
            occupied.append({})

        for robot in robots:
            row: dict[int, int] = occupied[robot.position.y]
            if robot.position.x not in row:
                row[robot.position.x] = 0
            row[robot.position.x] += 1

        for y in range(height):
            line: str = '.' * width
            for x,n in occupied[y].items():
                line = line[:x] + str(n % 10) + line[x+1:]
                grid[(x,y)] = n
            print(line)

    return

def part_one(path: str, grid_width: int, grid_height: int) -> int:
    result: int = 1

    robots: list[Robot] = extract_robots(path=path, grid_height=grid_height, grid_width=grid_width)
    quadrant_count: dict[int, int] = {0:0, 1:0, 2:0, 3:0}
    for robot in robots:
        robot.move(iterations=100)
        quadrant: int = quadrant_from_location(robot.position, width=grid_width, height=grid_height)
        if quadrant is None:
            continue
        quadrant_count[quadrant] += 1

    for quadrant, count in quadrant_count.items():
        print(f'{quadrant=}, {count=}')
        result *= count
    print(f'{result=}')
    return result


def part_two(path: str, grid_width:int, grid_height: int) -> int:
    result: int = 0
    print(f'{result=}')
    robots: list[Robot] = extract_robots(path=path, grid_height=grid_height, grid_width=grid_width)

    print('----------------------------< INITIAL >-------------------------')
    render(robots, width=grid_width, height=grid_height, iteration = 0, output_filename='zero.png')

    for robot in robots:
        robot.move(7569)
    render(robots, width=grid_width, height=grid_height, output_filename=None, iteration=7528, min_rating=2.0)

#    for iteration in range(-128,655536):
#        sleep(2)
#        for robot in robots:
#            robot.move(iterations=1)
#        render(robots, width=grid_width, height=grid_height, output_filename=f'day_14_{iteration:06d}.png', iteration=iteration, min_rating=2.0)
    return result


def main(argv: list[str]):
    global very_verbose
    global verbose
    global OPERATORS
    very_verbose = False
    verbose = False
    result = part_one(path='day_fourteen_test_input.txt', grid_width=11, grid_height=7)
    print(f'part one: {result=} for test data')
    if result != 12:
        raise Exception(f'Test failed, expected 12 but instead got {result}')
    result = part_one(path='day_fourteen_input.txt', grid_width=101, grid_height=103)
    print(f'part one: {result=} for actual data')

    part_two(path='day_fourteen_input.txt', grid_width=101, grid_height=103)

    return 0

def test():
    ### ###############
    ### #.......#....E#
    ### #.#.###.#.###.#
    ### #.....#.#...#.#
    ### #.###.#####.#.#
    ### #.#.#.......#.#
    ### #.#.#####.###.#
    ### #...........#.#
    ### ###.#.#####.#.#
    ### #...#.....#.#.#
    ### #.#.#.###.#.#.#
    ### #.....#...#.#.#
    ### #.###.#.#.#.#.#
    ### #S..#.....#...#
    ### ###############
    ###
    hewey: Robot = Robot(position=IntegerVector(1, 2), velocity=IntegerVector(1, -2), grid_width=11, grid_height=7)
    dewey: Robot = Robot(position=IntegerVector(5, 6), velocity=IntegerVector(-1, -1), grid_width=11, grid_height=7)
    louis: Robot = Robot(position=IntegerVector(8, 2), velocity=IntegerVector(2, 1), grid_width=11, grid_height=7)

    # check positions after three iterations....
    hewey_new_position: IntegerVector = hewey.move(3)
    dewey_new_position: IntegerVector = dewey.move(3)
    louis_new_position: IntegerVector = louis.move(3)

    assert(hewey_new_position.x == 4)
    assert(hewey_new_position.y == 3)

    assert(dewey_new_position.x == 2)
    assert(dewey_new_position.y == 3)

    assert(louis_new_position.x == 3)
    assert(louis_new_position.y == 5)

    grid: dict[[int, int], int] = {}
    grid[(1,6)] = 1
    grid[(2,6)] = 1
    grid[(2,5)] = 1
    grid[(3,5)] = 1
    grid[(3,4)] = 1
    grid[(4,4)] = 1
    grid[(4,3)] = 1
    print(f'jfactor={j_factor(grid, width=11, height=7)}')

    return

if __name__ == "__main__":
    exit_code: int = 0
    #test()
    exit_code = main(sys.argv)
    sys.exit(exit_code)