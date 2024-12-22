import re
from dataclasses import dataclass
from decimal import Decimal
from math import floor
from typing import Pattern

FLOATING_POINT_PATTERN_NO_WHITESPACE: Pattern = re.compile(r'^[-+]?([0-9]*\.[0-9]+|[0-9]+)$')
FLOATING_POINT_PATTERN_WHITESPACE_OK: Pattern = re.compile(r'^\s*[-+]?([0-9]*\.[0-9]+|[0-9]+)\s*$')
HEX_PATTERN_NO_WHITESPACE: Pattern = re.compile(r'^[\da-fA-F]+$')
HEX_PATTERN_WHITESPACE_OK: Pattern = re.compile(r'^\s*[\da-fA-F]+\s*$')
INTEGER_PATTERN_NO_WHITESPACE: Pattern = re.compile(r'^\d+$')
INTEGER_PATTERN_WHITESPACE_OK: Pattern = re.compile(r'^\s*\d+\s*$')
TIME_PATTERN: Pattern = re.compile(r'^([0-2]?\d):([0-5]\d)(:([0-5]\d))?$')
#^\s*(x|c(ol(umn)?)?)\s*=\s*[-+]?([0-9]+(\.[0-9]+)?)$
EXPLICIT_COLUMN_PATTERN = re.compile(r'^\s*(x|c(ol(umn)?)?)\s*=\s*[-+]?([0-9]+(\.[0-9]+)?)\s*$', re.IGNORECASE)
EXPLICIT_ROW_PATTERN = re.compile(r'^\s*(y|r(ow)?)\s*=\s*[-+]?([0-9]+(\.[0-9]+)?)\s*$', re.IGNORECASE)

EAST: int = 0
SOUTH_EAST: int = 1
SOUTH: int = 2
SOUTH_WEST: int = 3
WEST: int = 4
NORTH_WEST: int = 5
NORTH: int = 6
NORTH_EAST: int = 7


@dataclass
class Position:
    row: int
    column: int

    def __init__(self, row: int, column: int):
        if isinstance(row, int):
            self.row = row
        elif isinstance(row, float):
            self.row = int(round(row))
        elif isinstance(row, str):
            self.row = int(row)
        else:
            raise ValueError(f'Expected int for row, but received {type(row)}')
        if isinstance(column, int):
            self.column = column
        elif isinstance(column, float):
            self.column = int(round(column))
        elif isinstance(column, str):
            self.column = int(column)
        else:
            raise ValueError(f'Expected int for column, but received {type(column)}')
        return

    def __str__(self):
        result: str = f'({self.row},{self.column})'
        return result

    def __hash__(self) -> int:
        result: int = int(self.row) << 16
        result += int(self.column)
        return result

    def __eq__(self, other: 'Position'):
        other = Position.as_position(other)
        result: bool = self.row == other.row and self.column == other.column
        return result

    def add(self, other: 'Position') -> 'Position':
        delta_row: int
        delta_column: int
        if isinstance(other, Position):
            delta_row: int = other.row
            delta_column: int = other.column
        elif isinstance(other, tuple) and (isinstance(other[0], int) or isinstance(other[0], float)) and (
                isinstance(other[1], int) or isinstance(other[1], float)):
            delta_row: int = int(other[0])
            delta_column: int = int(other[1])
        else:
            raise Exception(f'Expected Position, but provided position is of type ({type(other)}')

        result: Position = Position(row=self.row + delta_row, column=self.column + delta_column)
        return result

    def subtract(self, other: 'Position') -> 'Position':
        delta_row: int
        delta_column: int
        if isinstance(other, Position):
            delta_row: int = other.row
            delta_column: int = other.column
        elif isinstance(other, tuple) and (isinstance(other[0], int) or isinstance(other[0], float)) and (
                isinstance(other[1], int) or isinstance(other[1], float)):
            delta_row: int = int(other[0])
            delta_column: int = int(other[1])
        else:
            raise Exception(f'Expected Position, but provided position is of type ({type(other)}')

        result: Position = Position(row=self.row - delta_row, column=self.column - delta_column)
        return result

    def adjacent(self, direction: int) -> 'Position':
        return None

    @classmethod
    def as_position(cls, candidate: str | tuple[int, int]) -> 'Position':
        result: Position | None = None
        if isinstance(candidate, str):
            # string formats supported;
            # nnnn,nnnn = row,column
            # x=nnnn,y=nnnn = column, row
            # row=nnnn, column=nnnn = row, column

            # peel off any brackets around the string
            if candidate.strip().startswith('(') and candidate.strip().endswith(')'):
                first_bracket_pos: int = candidate.find('(')
                candidate = candidate[first_bracket_pos + 1:]
                last_bracket_pos: int = candidate.rfind(')')
                candidate = candidate[:last_bracket_pos]

            row: int | None = None
            column: int | None = None
            bits: list[str] = candidate.split(',')
            if len(bits) == 2:
                column_bits = EXPLICIT_COLUMN_PATTERN.match(bits[0])
                row_bits = EXPLICIT_ROW_PATTERN.match(bits[0])
                if row_bits:
                    row = parse_int(row_bits.group(3))
                elif column_bits:
                    column = parse_int(column_bits.group(4))
                else:
                    row = parse_int(candidate=bits[0])

                column_bits = EXPLICIT_COLUMN_PATTERN.match(bits[1])
                row_bits = EXPLICIT_ROW_PATTERN.match(bits[1])
                if row_bits:
                    row = parse_int(row_bits.group(3))
                elif column_bits:
                    column = parse_int(column_bits.group(4))
                else:
                    column = parse_int(candidate=bits[0])

                result = Position(row=row, column=column)
        elif isinstance(candidate, tuple) and len(candidate) == 2 and (
                isinstance(candidate[0], int) or isinstance(candidate[0], float)) and (
                isinstance(candidate[1], int) or isinstance(candidate[1], float)):
            row: int | None = parse_int(candidate[0])
            column: int | None = parse_int(candidate[1])
            result = Position(row=row, column=column)
        elif isinstance(candidate, Position):
            result = Position(row=candidate.row, column=candidate.column)
        else:
            raise Exception(f'Expected string, tuple, or Position, but received {type(candidate)}')
        return result


STEP_DIRECTIONS_BY_DIRECTION: dict[int, Position] = {
    EAST: Position(row=0, column=1),
    SOUTH_EAST: Position(1,1),
    SOUTH: Position(1,0),
    SOUTH_WEST: Position(1,-1),
    WEST: Position(0,-1),
    NORTH_WEST: Position(-1,-1),
    NORTH: Position(-1,0),
    NORTH_EAST: Position(-1,1)
}

def direction_from_character(candidate: str) -> int:
    result: int = None
    if candidate == '<':
        result = WEST
    elif candidate == '>':
        result = EAST
    elif candidate == '^':
        result = NORTH
    elif candidate in ['V', 'v']:
        result = SOUTH
    return result

def read_lines_from_file(path: str) -> list[str]:
    result: list[str] = []
    with open(path, 'r') as file:
        for line in file:
            result.append(line.strip())
    return result

def only_digits(candidate: str, whitespace_ok: bool = False, allow_decimal_point: bool = False) -> bool:
    """Determine if the specified string only contains digits"""

    if isinstance(candidate, int):
        return True
    pattern: Pattern = INTEGER_PATTERN_NO_WHITESPACE
    if allow_decimal_point:
        pattern = FLOATING_POINT_PATTERN_NO_WHITESPACE if not whitespace_ok else FLOATING_POINT_PATTERN_WHITESPACE_OK
    else:
        pattern = INTEGER_PATTERN_NO_WHITESPACE if not whitespace_ok else INTEGER_PATTERN_WHITESPACE_OK
    result: bool = bool(re.match(pattern=pattern, string=candidate))
    return result

def only_hex_digits(candidate: str, whitespace_ok: bool = False) -> bool:
    """Determine if the specified string only contains digits"""
    pattern: Pattern = HEX_PATTERN_NO_WHITESPACE if not whitespace_ok else HEX_PATTERN_WHITESPACE_OK
    result: bool = bool(re.match(pattern=pattern, string=candidate))
    return result


def parse_int(candidate: str|float|int|Decimal) -> int|None:
    result: int|None = None
    if isinstance(candidate, int):
        result = candidate
    elif isinstance(candidate, Decimal):
        result = int(candidate)
    elif candidate == None:
        result = None
    elif isinstance(candidate, float):
        result = floor(candidate)
    else:
        refined: str = str(candidate).strip()
        if len(refined) == 0:
            result = 0
        elif only_digits(candidate=refined):
            result = int(refined)
        elif only_digits(candidate=refined, allow_decimal_point=True):
            result = floor(float(refined))
    return result

def parse_float(candidate: str|float|int) -> float|None:
    result: float|None = None
    if isinstance(candidate, float):
        result = candidate
    elif isinstance(candidate, int):
        result = float(candidate)
    elif isinstance(candidate, Decimal):
        result = float(candidate)
    elif candidate == None:
        result = None
    else:
        refined: str = str(candidate).strip()
        if only_digits(candidate=refined, allow_decimal_point=True):
            result = floor(float(refined))
    return result

def parse_boolean(candidate: str) -> bool:
    if isinstance(candidate, bool):
        return candidate

    if isinstance(candidate, (int, float)):
        return candidate > 0

    t = candidate.strip() if isinstance(candidate, str) else str(candidate).strip()
    if re.match(r'^\d+$', t):
        return int(t) > 0

    result = re.match(r'^[ytj]', t, re.IGNORECASE) is not None
    return result
