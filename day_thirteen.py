import os
import sys
import re
from copy import deepcopy
from dataclasses import dataclass
from math import floor, sqrt, atan2

import math

verbose: bool = False
very_verbose: bool = False

PI: float =  3.14159265358979323846

COORDINATE_PATTERN: re.Pattern = re.compile(r'^\s*x([+-]?\d+),\s*y([+-]?\d+)$', re.IGNORECASE)
TARGET_COORDINATE_PATTERN: re.Pattern = re.compile(r'^\s*x=([+-]?\d+),\s*y=([+-]?\d+)$', re.IGNORECASE)

PARSE_STATE_INIT: int = 0
PARSE_STATE_BUTTON_A: int = 1
PARSE_STATE_BUTTON_B: int = 2
PARSE_STATE_TARGET: int = 3
PARSE_STATE_LIMBO: int = 4

class Vector:
    def __init__(self, x: float, y: float):
        self.x: float = x
        self.y: float = y

    def __str__(self) -> str:
        result = f'x={self.x:6.4f},y={self.y:6.4f}'
        return result

    def __repr__(self) -> str:
        result = f'x={self.x:6.4f},y={self.y:6.4f}'
        return result

    def rotate(self, radians: float) -> 'Vector':
        radius: float = sqrt(self.x * self.x + self.y * self.y)
        current_radians: float = self.direction()
        resultant_radians: float = current_radians + radians
        x: float = radius * math.cos(resultant_radians)
        y: float = radius * math.sin(resultant_radians)
        return Vector(x,y)

    def gradient(self) -> float:
        result: float = self.x / self.y if self.y != 0 else (99999999.999 if self.y > 0 else -999999999.99)
        return result

    def direction(self) -> float:
        result: float = atan2(self.y, self.x)
        return result

@dataclass
class Instructions:
    button_a: tuple[int,int]|None = None
    button_b: tuple[int, int]|None = None
    target: tuple[int, int]|None = None

    def alpha_gradient(self) -> float:
        dy: int = self.button_a[1]
        dx: int = self.button_a[0]
        gradient: int = dx / dy if dy != 0 else 999999
        return gradient

    def beta_gradient(self) -> float:
        dy: int = self.button_b[1]
        dx: int = self.button_b[0]
        gradient: int = dx / dy if dy != 0 else 999999
        return gradient

    def solve(self) -> tuple[int, int]:

        if self.target[0] > 1000000 and self.target[1] > 1000000:
            # if both the alpha and beta buttons diverge either side of the nceessary gradient.... no dice!!
            target_gradient: float = self.target[0] / self.target[1]
            if self.alpha_gradient() < target_gradient and self.beta_gradient() < target_gradient:
                return None
            if self.alpha_gradient() > target_gradient and self.beta_gradient() > target_gradient:
                return None

            print(f'ho hum! alpha_gradient={self.alpha_gradient()}, beta_gradient={self.beta_gradient()}')

        # is there any combination of button a and b x deltas that get us to the target x?
        target_x: int = self.target[0]
        button_a_x: int = self.button_a[0]
        button_b_x: int = self.button_b[0]

        # store in this array the number of button "A" pushes that get us to a solution....
        x_solutions: list[tuple[int,int]] = []
        for i,x in enumerate(range(0, target_x + 1, button_a_x)):
            remainder: int = target_x - x
            # how many button "B" pushes are subsequently required?!?
            if remainder == 0 or remainder % button_b_x == 0:
                # nice! it works
                b_pushes: int = int(remainder / button_b_x)
                x_solutions.append((i, b_pushes))

        if len(x_solutions) == 0:
            return None

        #ok .... but does this also work in the Y-axis?!?
        target_y: int = self.target[1]
        button_a_y: int = self.button_a[1]
        button_b_y: int = self.button_b[1]
        solutions: list[tuple[int, int]] = []
        for twin in x_solutions:
            if (button_a_y * twin[0]) + (button_b_y * twin[1]) == target_y:
                solutions.append(twin)

        best_solution: tuple[int,int] = None
        best_price: int = None
        for solution in solutions:
            price: int = (solution[0]) * 3 + solution[1]
            if best_price is None or price < best_price:
                best_price = price
                best_solution = solution

        return best_solution

    def solve_too(self) -> tuple[int,int]|None:
        target: Vector = Vector(x=self.target[0], y=self.target[1])
        alpha: Vector = Vector(self.button_a[0], self.button_a[1])
        beta: Vector = Vector(self.button_b[0], self.button_b[1])

        target_radians: float = target.direction()
        target_angle: float = math.degrees(target_radians)
        rotation: float = 0 - target_radians
        c = target.rotate(radians=rotation)
        a = alpha.rotate(radians=rotation)
        b = beta.rotate(radians=rotation)

        if a.y > 0 and b.y > 0 or a.y < 0 and b.y < 0:
            print(f'NO solutions')
            return None

        if abs(a.x) < 0.0001 and abs(b.x) < 0.0001:
            print(f'both buttons are vertical')
            return None

        a_to_b_ratio: float = abs(a.y / b.y)
        #print(f'For every "b", we need {a_to_b_ratio} "a" buttons.')

        b_portion: float = abs(a_to_b_ratio / (1 + a_to_b_ratio))
        a_portion: float = abs(1.0 - b_portion)

        nbp: float = c.x / (a.x * a_portion + b.x * b_portion)
        nbp_f, nbp_i = math.modf(nbp)
        almost_whole_number: bool = nbp_f < 0.001 or nbp_f > 0.999
        if not almost_whole_number:
            print(f'NO solution')
            return None

        number_button_presses = int(round(nbp))

        # "alpha" makes up a_portion part of the journey....
        number_alpha_buttons: int = int(round(number_button_presses * a_portion))
        number_beta_buttons: int = number_button_presses - number_alpha_buttons
        result: tuple[int,int] = (number_alpha_buttons, number_beta_buttons)
        return result


def extract_instructions(path: str, target_offset: int = 0) -> list[Instructions]:
    if not os.path.exists(path) or not os.path.isfile(path):
        raise Exception(f'Specified path {path} not a file we can read')

    result: list[Instructions] = []
    
    parse_state: int = PARSE_STATE_INIT
    
    with open(path, 'r') as file:
        line_number: int = 0
        for line in file:
            line_number += 1
            text: str = line.strip()
            if parse_state == PARSE_STATE_INIT:
                if text.startswith('Button A:'):
                    parse_state = PARSE_STATE_BUTTON_A
                    instructions = Instructions()
                else:
                    raise Exception(f'Expected "Button A:" but got {text}')
            elif parse_state == PARSE_STATE_BUTTON_A:
                if text.startswith('Button B:'):
                    parse_state = PARSE_STATE_BUTTON_B
                else:
                    raise Exception(f'Expected "Button B:" but got {text}')
            elif parse_state == PARSE_STATE_BUTTON_B:
                if text.startswith('Prize:'):
                    parse_state = PARSE_STATE_TARGET
                else:
                    raise Exception(f'Expected "Target:" but got {text}')
            elif parse_state == PARSE_STATE_TARGET:
                if len(text) == 0:
                    parse_state = PARSE_STATE_LIMBO
                    result.append(instructions)
                else:
                    raise Exception(f'Expected blank line but got [{text}]')
            elif parse_state == PARSE_STATE_LIMBO:
                if text.startswith('Button A:'):
                    parse_state = PARSE_STATE_BUTTON_A
                    instructions = Instructions()
                else:
                    raise Exception(f'Expected EOF, blank text or button A but got {text}')
            else:
                raise Exception(f'Unknown parse state: {parse_state}')

            if parse_state in (PARSE_STATE_BUTTON_A, PARSE_STATE_BUTTON_B):
                colon_pos: int = text.find(':')
                if colon_pos < 0:
                    raise Exception(f'Expected a colon but got {text}')
                rest: str = text[colon_pos + 1:]
                bits = COORDINATE_PATTERN.match(rest)
                if bits is None:
                    raise Exception(f'Expected coordinates but got {text}')
                x_text: str = bits.group(1)
                y_text: str = bits.group(2)
                x: int = int(x_text)
                y: int = int(y_text)
                if parse_state == PARSE_STATE_BUTTON_A:
                    instructions.button_a = (x, y)
                else:
                    instructions.button_b = (x,y)
            elif parse_state == PARSE_STATE_TARGET:
                colon_pos: int = text.find(':')
                if colon_pos < 0:
                    raise Exception(f'Expected a colon but got {text}')
                rest: str = text[colon_pos + 1:]
                bits = TARGET_COORDINATE_PATTERN.match(rest)
                if bits is None:
                    raise Exception(f'Expected target coordinates but got {text}')
                x_text: str = bits.group(1)
                y_text: str = bits.group(2)
                instructions.target = (int(x_text) + target_offset, int(y_text) + target_offset)

    return result


def part_one(path: str) -> int:
    result: int = 0

    instructions: list[Instructions] = extract_instructions(path=path)
    for instruction in instructions:
        solution: tuple[int, int] = instruction.solve()
        if solution is None:
            print(f'No solution found for {instruction}')
            continue
        cost = (solution[0] * 3) + solution[1]
        result += cost
        print(f'{result=}, {cost=}, {solution=}')
    print(f'{result=}')
    return result

def part_two(path: str) -> int:
    result: int = 0

    instructions: list[Instructions] = extract_instructions(path=path, target_offset=10000000000000)
    for instruction in instructions:
        solution: tuple[int, int]|None = instruction.solve_too()
        if solution is None:
            print(f'No solution found for {instruction}')
            continue
        cost = (solution[0] * 3) + solution[1]
        result += cost
        print(f'{result=}, {cost=}, {solution=}')
    print(f'{result=}')
    return result


def main(argv: list[str]):
    global very_verbose
    global verbose
    global OPERATORS
    very_verbose = False
    verbose = False
#    result = part_one(path='day_thirteen_test_input.txt')
#    print(f'part one: {result=} for test data')
#    if result != 480:
#        raise Exception(f'Test failed, expected 1928 but instead got {result}')
#    result = part_one(path='day_thirteen_input.txt')
#    print(f'part one: {result=} for actual data')

    result = part_two(path='day_thirteen_test_input.txt')
    print(f'part two: {result=} for test data')
    if result != 875318608908:
        raise Exception(f'Test failed, expected 875318608908 but instead got {result}')
    result: int = part_two(path='day_thirteen_input.txt')
    print(f'part two: {result=} for actual data')

    return 0

def test():
#    instructions: Instructions = Instructions(button_a=(3,2), button_b=(5,1), target=(20,11))
#    solution: tuple[int, int] = instructions.solve()
#    print(f'{solution=}')
#    assert(solution is not None)
#    assert(solution == (5,1))

    v0 = Vector(x=71,y=71)
    v1 = v0.rotate(math.radians(45))
    print(f'{v0=}, {v1=}')

    target: Vector = Vector(x=8400,y=5400)
    alpha: Vector = Vector(94, 34)
    beta: Vector = Vector(22, 67)

    target_radians: float = target.direction()
    target_angle: float = math.degrees(target_radians)
    rotation: float = 0 - target_radians
    c = target.rotate(radians=rotation)
    a = alpha.rotate(radians=rotation)
    b = beta.rotate(radians=rotation)

    print(f'{c=}')
    print(f'{a=}')
    print(f'{b=}')

    if a.y > 0 and b.y > 0 or a.y < 0 and b.y < 0:
        print(f'NO solutions')
        return

    if a.y == 0 and b.y == 0:
        print(f'both buttons are vertical')
        return
    a_to_b_ratio: float = abs(a.y / b.y)
    print(f'For every "b", we need {a_to_b_ratio} "a" buttons.')

    b_portion: float = abs(a_to_b_ratio / (1 + a_to_b_ratio))
    a_portion: float = abs(1.0 - b_portion)

    number_button_presses: float = c.x / (a.x * a_portion + b.x * b_portion)
    nbp_f, nbp_i = math.modf(number_button_presses)
    almost_whole_number: bool = nbp_f < 0.001 or nbp_f > 0.999
    if not almost_whole_number:
        print(f'NO solution')
        return

    number_button_presses = int(round(number_button_presses))

    # "alpha" makes up a_portion part of the journey....
    number_alpha_buttons: int = int(round(number_button_presses * a_portion))
    number_beta_buttons: int  = number_button_presses - number_alpha_buttons
    assert(80 == number_alpha_buttons)
    assert(40 == number_beta_buttons)
    return

if __name__ == "__main__":
    exit_code: int = 0
#    test()
    exit_code = main(sys.argv)
    sys.exit(exit_code)