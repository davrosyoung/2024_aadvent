import sys
from dataclasses import dataclass
from typing import Set

from common import EXPLICIT_COLUMN_PATTERN, EXPLICIT_ROW_PATTERN, parse_int, EAST, Position, \
    STEP_DIRECTIONS_BY_DIRECTION


@dataclass
class Grid:
    extent: Position
    karte: dict[Position, str]|None = None

    def __init__(self, extent: Position) -> None:
        self.extent = extent
        self.karte = {}
        for row_index in range(self.extent.row):
            for column_index in range(self.extent.column):
                cursor = Position(row=row_index, column=column_index)
                self.karte[cursor] = '.'

    def __str__(self) -> str:
        result: str = ''
        for row_index in range(self.extent.row):
            for column_index in range(self.extent.column):
                result += self.karte.get(Position(row=row_index, column=column_index), None)
            result += '\n'
        return result

    @classmethod
    def from_lines(cls, lines: list[str]) -> 'Grid':
        column_count: int = None
        # check that all lines are the same length....
        for line in lines:
            if column_count is None:
                column_count = len(line)
            else:
                if len(line) != column_count:
                    raise Exception(f'Expected all lines to be the same length, but received {len(line)} for line {line}')

        result = Grid(extent=Position(row=len(lines), column=column_count))
        for row_index in range(len(lines)):
            row: str = lines[row_index]
            for column_index in range(len(row)):
                position: Position = Position(row=row_index, column=column_index)
                value: str = row[column_index:column_index+1]
                result.set_value(position=position, value=value)

        return result


    def is_valid_position(self, position: tuple[int, int]|Position) -> bool:
        p: Position = Position.as_position(candidate=position)
        row: int = p.row
        column: int = p.column
        result: bool = 0 <= row < self.extent.row and 0 <= column < self.extent.column
        return result

    def get_value(self, position: Position|tuple[int,int]) -> str:
        p: Position = Position.as_position(candidate=position)
        result: str =  self.karte.get(p, None)
        return result

    def get_adjacent_value(self, position: Position|tuple[int,int], direction: int) -> str:
        if isinstance(position, tuple) and (isinstance(position[0], int) or isinstance(position[0], float)) and (isinstance(position[1], int) or isinstance(position[1], float)):
            row: int = int(position[0])
            column: int = int(position[1])
            position = Position(row=row, column=column)
        adjacent_position: Position = position.add(STEP_DIRECTIONS_BY_DIRECTION[direction])
        result: str =  self.karte.get(adjacent_position, None)
        return result

    def set_value(self, position: Position, value: str):
        self.karte[position] = value
        return

    def is_obstacle(self, position: Position) -> bool:
        result: bool
        result: bool = self.get_value(position) == '#'
        return result

    def is_clear(self, position: Position) -> bool:
        result: bool
        result: bool = self.get_value(position) in ('.', ' ')
        return result

    def number_rows(self) -> int:
        result: int = self.extent[0]
        return result

    def number_columns(self) -> int:
        result: int = self.extent[1]
        return result

    def get_extent(self) -> Position:
        result = self.extent
        return result

    def find_value(self, value: str) -> list[Position]:
        result: list[Position] = []
        for position in self.karte.keys():
            if self.karte.get(position) == value:
                result.append(position)
        return result

    def render_row(self, row: int) -> str:
        result: str = ''
        for column_index in range(self.extent.column):
            khar: str = self.get_value(position=(row, column_index)) or '.'
            result += khar
        return result

class BreadCrumbs:
    trail: dict[Position, Set[int]] = {}

    def add(self, position: Position|tuple[int, int], direction: int) -> None:
        if position not in self.trail:
            self.trail[position] = set(direction)
        else:
            self.trail[position].add(direction)

    def already_travelled(self, position: Position, direction: int|None = None) -> bool:
        result: bool = False
        if position not in self.trail:
            return result
        if direction is None:
            result = len(self.trail.get(position)) > 0
        else:
            result = direction in self.trail.get(position)
        return result

    def append(self, other: 'BreadCrumbs') -> 'BreadCrumbs':
        result: BreadCrumbs = BreadCrumbs()
        for position in self.trail.keys():
            for direction in self.trail.get(position):
                result.add(position, direction)
        for position in other.trail.keys():
            for direction in other.trail.get(position):
                result.add(position, direction)
        return result

def test():
    sample_grid: list[str] = ['']
    
    # ###############
    # #...#...#.....#
    # #.#.#.#.#.###.#
    # #S#...#.#.#...#
    # #######.#.#.###
    # #######.#.#...#
    # #######.#.###.#
    # ###..E#...#...#
    # ###.#######.###
    # #...###...#...#
    # #.#####.#.###.#
    # #.#...#.#.#...#
    # #.#.#.#.#.#.###
    # #...#...#...###
    # ###############
    #
    sample_data: list[str] = [
    '###############',
    '#...#...#.....#',
    '#.#.#.#.#.###.#',
    '#S#...#.#.#...#',
    '#######.#.#.###',
    '#######.#.#...#',
    '#######.#.###.#',
    '###..E#...#...#',
    '###.#######.###',
    '#...###...#...#',
    '#.#####.#.###.#',
    '#.#...#.#.#...#',
    '#.#.#.#.#.#.###',
    '#...#...#...###',
    '###############']

    assert(Position.as_position((0.0, 0.0)) == Position(0, 0))
    assert(Position.as_position(('0.0,0.0')) == Position(0, 0))
    assert(Position.as_position(('x=0.0,y=0.0')) == Position(0, 0))
    assert(Position.as_position((0 ,0)) == Position(0, 0))
    assert(Position.as_position(('x=3.0,y=4.0')) == Position(4, 3))
    assert(Position.as_position((' ( x=3.0 , y=4.0 ) ')) == Position(4, 3))
    assert(Position.as_position((4 ,3)) == Position(4, 3))
    assert(Position.as_position((4 ,3.0001)) == Position(4, 3))

    grid: Grid = Grid.from_lines(lines=sample_data)
    assert(grid.get_extent() == (15, 15))
    assert(grid.get_value(position=(3, 1)) == 'S')
    assert(grid.get_value(position=(7, 5)) == 'E')
    assert(grid.is_obstacle(position=(2,2)))
    assert(grid.is_clear(position=(2,1)))
    assert(grid.is_valid_position(position=(0, 0)))
    assert(grid.is_valid_position(position=(-1, 0)) == False)
    assert(grid.is_valid_position(position=(0, -10)) == False)
    assert(grid.is_valid_position(position=(14, 14)))
    assert(grid.is_valid_position(position=(15, 14)) == False)
    assert(grid.is_valid_position(position=(14, 15)) == False)


def main(argv: list[str]):
    test()
    return

if __name__ == '__main__':
    main(sys.argv)