import os
import sys
import re
from dataclasses import dataclass


from common import read_lines_from_file, WEST, EAST, NORTH, SOUTH, direction_from_character, Position, \
    STEP_DIRECTIONS_BY_DIRECTION
from grid import Grid

verbose: bool = False
very_verbose: bool = False
DIRECTIONS_PATTERN:  re.Pattern = re.compile(r'^[<^>vV]+$')

@dataclass
class State:
    grid: Grid
    position: Position
    directions: list[int]
    direction_index: int = 0

    def finished(self) -> bool:
        result: bool = self.direction_index >= len(self.directions)
        return result

    def box_in_this_direction(self, position: Position, direction: int) -> bool:
        result: bool = False
        if not self.grid.is_valid_position(position=position):
            return result

        delta: Position = STEP_DIRECTIONS_BY_DIRECTION.get(direction)
        next_step: Position = position.add(delta)
        if not self.grid.is_valid_position(position=next_step)
            return result

        at_next_step: str = self.grid.get_value(next_step)
        if at_next_step in ['O','[',']']:
            result = True
        return result

    def boxes_in_this_direction(self, position: Position, direction: int) -> list[Position]:
        result: list[Position] = []

        start_column: int
        end_column: int
        delta: Position = STEP_DIRECTIONS_BY_DIRECTION.get(direction)

        if direction in [EAST, WEST]:
            # horizontal is easy...
            if self.box_in_this_direction(position=position, direction=direction):
                train_length: int = 1
                delta: Position = STEP_DIRECTIONS_BY_DIRECTION.get(direction)
                next_box_pos = position.add(delta)
                at_next_box_pos = self.grid.get_value(position=next_box_pos)
                while at_next_box_pos in ['O', '[', ']']:
                    train_length += 1
                    result.add(Position.as_position(candidate=next_box_pos))
                    next_box_pos = next_box_pos.add(delta)
                    at_next_box_pos = self.grid.get_value(position=next_box_pos)
        else:
            # what are my dimensions?
            position_khar: str = self.grid.get_value(position)
            if position_khar in ['@','O']:
                # just the single character
                start_column = position.column
                end_column = position.column
            elif position_khar == '[':
                start_column = position.column
                end_column = position.column + 1
            elif position_khar == ']':
                start_column = position.column - 1
                end_column = position.column

            boxes_exist: bool = False
            box_positions: list[Position] = []
            for column in range(start_column, end_column + 1):
                candidate: Position = Position(row=position.row, column=column)
                if self.box_in_this_direction(position=candidate, direction=direction):
                    boxes_exist = True
                    bp = Position.as_position(candidate.add(delta))
                    box_positions.append(bp)

            if boxes_exist:
                # we have the boxes in box positions ... question is ... one or two boxes?
                if len(box_positions) == 1:
                    box_khar = self.grid.get_value(position=box_positions[0])
                    if  box_khar in ['[','O']:
                        result.append(box_positions[0])
                        result.extend(self.boxes_in_this_direction(position=box_positions[0], direction=direction))
                    elif box_khar == ']':
                        # if we have the "right hand" pair, then the box position is considered to start to the left of this location
                        box_column: int = box_positions[0].column - 1 if box_positions[0].column > 0 else box_positions[0].column
                        found_box_position: Position = Position(row=box_positions[0].row, column=box_column)
                        result.append(found_box_position)
                        # now find any boxes that this box is up against....
                        result.extend(self.boxes_in_this_direction(position=found_box_position, direction=direction))
                    else:
                        raise Exception(f'UNKNOWN box character {box_khar} at {box_positions[0]}')
                elif len(box_positions) == 2:
                    # multiple columns to check .... might be more than a single box...
                    left_box_position: Position = box_positions[0]
                    at_left_box_position: str = self.grid.get_value(left_box_position)
                    right_box_position: Position = box_positions[1]
                    at_right_box_position: str = self.grid.get_value(right_box_position)
                    if at_left_box_position == '[' and at_right_box_position == ']':
                        # just the one box after all....
                        result.append(left_box_position)
                        result.extend(self.boxes_in_this_direction(position=left_box_position, direction=direction))
                    elif at_left_box_position == ']' and at_right_box_position == '[':
                        alpha_box_position: Position = Position(row=left_box_position.row, column=left_box_position.column - 1)
                        beta_box_position: Position = Position(row=right_box_position.row, column=right_box_position.column)
                        result.append(alpha_box_position)
                        result.append(beta_box_position)
                        for bp in [alpha_box_position, beta_box_position]:
                            result.extend(self.boxes_in_this_direction(position=bp, direction=direction))
                    else:
                        raise Exception(f'Did NOT expect {at_left_box_position=} and {at_right_box_position=}')

                    pass
                else:
                    raise Exception(f'TOO MANY {len(box_positions)}; {box_positions=}')
        return result

    def is_box_blocked(self, position: Position, direction: int) -> bool:
        """Determine if the box at the specified location is blocked directly."""
        result: bool = False
        if not self.grid.is_valid_position(position=position):
            return result
        double_wide: bool = False
        box_column: int = position.column

        khar: str = self.grid.get_value(position=position)
        if khar in ['O','0','o']:
            # single box
            pass
        elif khar == '[':
            double_wide = True
        elif khar == ']':
            double_wide = True
            # this box actually starts one character to the left...
            box_column = position.column - 1
            if box_column < 0:
                raise Exception(f'Did NOT expect to find ] at column zero, row={position.row}')
            box_left: Position = Position.as_position(candidate=(position.row, box_column))
            if self.grid.get_value(position=box_left) != '[':
                raise Exception(f'Rouge ] charactyer at {position=} is NOT accompanied by matching [ at {box_left=}')
        else:
            raise Exception(f'NO box character at {position=}, {khar=}')

        refined_position: Position = Position(row=position.row, column=box_column)
        # when checking east or west ... we only have to test a single target location
        if direction in [EAST, WEST]:
            delta: Position = STEP_DIRECTIONS_BY_DIRECTION.get(direction)
            one_step_beyond: Position = refined_position.add(delta) if direction == WEST else refined_position.add(delta).add(delta)
            target_position: Position = Position(row=position.row, column=box_column + 1 if direction == EAST else box_column - 1)
            if not self.grid.is_valid_position(position=target_position):
                return result
            at_target_position: str = self.grid.get_value(target_position)
            if at_target_position in ['O', '[', ']']:
                result = True
            return result
        one_step_beyond: Position =



            delta: Position = STEP_DIRECTIONS_BY_DIRECTION.get(direction)
            next_step: Position = position.add(delta)
            if not self.grid.is_valid_position(position=next_step):
                return result

            at_next_step: str = self.grid.get_value(next_step)
            if at_next_step in ['O', '[', ']']:
                result = True
            return result



#        delta: Position = STEP_DIRECTIONS_BY_DIRECTION.get(direction)
#        next_step: Position = position.add(delta)
#        at_next_step: str = self.grid.get_value(next_step)
#        while at_next_step in ['O', '[', ']']:
#            if at_next_step in ['O', '[']:
#                result.append(next_step)
#            next_step = next_step.add(delta)
#            at_next_step = self.grid.get_value(next_step)
#        return result

    def follow_direction(self) -> bool:
        result: bool = False
        if self.finished():
            return result
        direction: int = self.directions[self.direction_index]
        self.direction_index += 1

        delta: Position = STEP_DIRECTIONS_BY_DIRECTION.get(direction)
        next_step: Position = self.position.add(delta)
        at_next_step: str = self.grid.get_value(self.position.add(delta))
        if at_next_step == '#':
            return result

        if at_next_step == 'O':
            # we would like to move this if we can...
            train_length: int = 1

            # how many boxes to shift?
            next_box_position: Position = next_step.add(delta)
            at_next_box_position: str = self.grid.get_value(next_box_position)
            while(at_next_box_position == 'O'):
                train_length += 1
                next_box_position = next_box_position.add(delta)
                at_next_box_position = self.grid.get_value(next_box_position)

            # is the "next box position" available or a wall?
            if at_next_box_position in ['.', ' '] and self.grid.is_valid_position(position=next_box_position):
                # move the train .. simply add an O at the end and clear the O at the next step location...
                self.grid.set_value(next_box_position, 'O')
                self.grid.set_value(next_step, '.')
                result = True
            else:
                # boxes cannot be moved ... wall in the way.
                pass
        elif at_next_step in ['[', ']']:
            # how we handle "double-wide" boxes depends a lot upon whether we are moving vertically or horizontally
            if direction in [EAST, WEST]:
                # trivial case is moving left-right
                boxes: list[Position] = self.boxes_in_this_direction(position=self.position, direction=direction)

                # reverse-sort these boxes in the direction of travel..
                boxes = sorted(boxes, lambda box: box.column, reverse=True) if direction == EAST else sorted(boxes, lambda box: box.column)
                for box in boxes:
                    # shuffle each box along in the direction of travel...
                    # "next step" points past the box in the direction that we are moving along .... when travelling right, this is two positions along, not one when dealing with wide boxes.
                    next_step:  Position = box.add(delta)
                    # position that the box is going to leave vacant.....
                    vacating: Position = box.subtract(delta).subtract(delta)
                    at_box: str = self.grid.get_value(box)
                    double_wide: bool = False
                    box_right: Position = box.add(STEP_DIRECTIONS_BY_DIRECTION.get(EAST))
                    at_box_right: str = self.grid.get_value(position=box_right)
                    next_step_right: Position = next_step.add(delta)
                    if at_box == '[' and self.grid.is_valid_position(box_right):
                        # we have to shift a double-wide box ... two characters!!
                        double_wide = True
                        # ok ... this is what we expect for a double-wide box
                        # the spot we are vacating is one grid location away when travelling east ... but two grid locations to rhe right when travelling west...
                        vacating = box.subtract(delta).subtract(delta) if direction == WEST else box.subtract(delta)
                    self.grid.set_value(position=vacating, value='.')
                    self.grid.set_value(position=next_step, value=at_box)
                    if double_wide:
                        self.grid.set_value(next_step_right, value=at_box_right)



#                # simple case is moving horizontally...
#                train_length: int = 1
#                # how many boxes to shift?
#                next_box_position: Position = next_step.add(delta)
#                at_next_box_position: str = self.grid.get_value(next_box_position)
#                while at_next_box_position in ['O','[',']']:
#                    train_length += 1
#                    next_box_position = next_box_position.add(delta)
#                    at_next_box_position = self.grid.get_value(next_box_position)

 #               # is the "next box position" available or a wall?
 #               if at_next_box_position in ['.', ' '] and self.grid.is_valid_position(position=next_box_position):
 #                   # actually move the train in its entirety ... move backwards from the position we are moving into back to where we started from
 #                   cursor: Position = next_box_position
 #                   previous: Position = cursor
 #                   while cursor != next_step:
 #                       cursor = cursor.subtract(delta)
 #                       # everybody's shuffling...
 #                       khar: str = self.grid.get_value(position=cursor)
 #                       self.grid.set_value(position=previous, value=khar)
 #                       previous = Position.as_position(candidate=cursor)  # copy the current position
 #                   self.grid.set_value(next_step, '.')
                    result = True
                else:
                    # boxes cannot be moved ... wall in the way.
                    pass
            else:
                # we are moving vertically ... OUCH ...
                # we have to check any boxes below us which are "stuck"....
                boxes: list[Position] = self.boxes_in_this_direction(position=self.position, direction=direction)
                # are any of these boxes blocked?

                pass
        elif at_next_step in ['.', ' ']:
            result = True
        elif at_next_step == '#':
            # cannot move..
            pass

        if result:
            self.grid.set_value(self.position, '.')
            self.position = next_step
            self.grid.set_value(self.position, '@')
        return result


def extract_grid_and_instructions(lines: str|list[str]) -> tuple[Grid, list[int]]:
    result: tuple[Grid, list[int]]
    input_lines: list[str] = lines if isinstance(lines, list) else lines.split('\n')
    grid_lines: list[str] = []
    instructions: list[int] = []
    found_instructions: bool = False
    for line in input_lines:
        bits = DIRECTIONS_PATTERN.match(line)
        if bits:
            found_instructions = True
            for c in line:
                direction: int = direction_from_character(candidate=c)
                if direction is not None:
                    instructions.append(direction)
        elif not found_instructions:
            if len(line) > 0:
                grid_lines.append(line)

    grid: Grid = Grid.from_lines(lines=grid_lines)
    result: tuple[Grid, list[int]] = (grid, instructions)
    return result

def extract_grid_and_instructions_too(lines: str|list[str]) -> tuple[Grid, list[int]]:
    result: tuple[Grid, list[int]]
    input_lines: list[str] = lines if isinstance(lines, list) else lines.split('\n')
    grid_lines: list[str] = []
    instructions: list[int] = []
    found_instructions: bool = False
    for line in input_lines:
        bits = DIRECTIONS_PATTERN.match(line)
        if bits:
            found_instructions = True
            for c in line:
                direction: int = direction_from_character(candidate=c)
                if direction is not None:
                    instructions.append(direction)
        elif not found_instructions:
            if len(line) > 0:
                # transform the row!!!
                transformed_line: str = ''
                for c in line:
                    if c == '@':
                        transformed_line += '@.'
                    else:
                        transformed_line += f'{c}{c}'
                grid_lines.append(transformed_line)

    grid: Grid = Grid.from_lines(lines=grid_lines)
    result: tuple[Grid, list[int]] = (grid, instructions)
    return result


def part_one(path: str) -> int:
    result: int = 0

    data_lines: list[str] = read_lines_from_file(path=path)
    grid, directions = extract_grid_and_instructions(data_lines)
    robot_positions: list[Position] = grid.find_value(value='@')
    if len(robot_positions) != 1:
        raise Exception(f'Expected one robot position but found {len(robot_positions)}')

    state: State = State(grid=grid, position=robot_positions[0], directions=directions)
    while not state.finished():
        state.follow_direction()

    print(state.grid)

    box_positions: list[Position] = grid.find_value(value='O')
    for bp in box_positions:
        score: int = bp.row * 100 + bp.column
        result += score

    print(f'{result=}')
    return result

def part_two(path: str) -> int:
    result: int = 0
    data_lines: list[str] = read_lines_from_file(path=path)
    grid, directions = extract_grid_and_instructions_too(data_lines)
    robot_positions: list[Position] = grid.find_value(value='@')
    if len(robot_positions) != 1:
        raise Exception(f'Expected one robot position but found {len(robot_positions)}')

    state: State = State(grid=grid, position=robot_positions[0], directions=directions)
    while not state.finished():
        state.follow_direction()

    print(state.grid)

    print(f'{result=}')
    return result


def main(argv: list[str]):
    global very_verbose
    global verbose
    very_verbose = False
    verbose = False

    result = part_one(path='day_fifteen_test_input.txt')
    print(f'part one: {result=} for test data')
    if result != 10092:
        raise Exception(f'Test failed, expected 1928 but instead got {result}')
    result = part_one(path='day_fifteen_input.txt')
    print(f'part one: {result=} for actual data')

    result = part_two(path='day_fifteen_test_input.txt')
    print(f'part two: {result=} for test data')
    if result != 875318608908:
        raise Exception(f'Test failed, expected 875318608908 but instead got {result}')
    result: int = part_two(path='day_fifteen_input.txt')
    print(f'part two: {result=} for actual data')

    return 0


def test():
#    instructions: Instructions = Instructions(button_a=(3,2), button_b=(5,1), target=(20,11))
#    solution: tuple[int, int] = instructions.solve()
#    print(f'{solution=}')
#    assert(solution is not None)
#    assert(solution == (5,1))


#    01234567
# 0: ########
# 1: #..O.O.#
# 2: ##@.O..#
# 3: #...O..#
# 4: #.#.O..#
# 5: #...O..#
# 6: #......#
# 7: ########

#<^^>>>vv<v>>v<

    input_data: str = '########\n#..O.O.#\n##@.O..#\n#...O..#\n#.#.O..#\n#...O..#\n#......#\n########\n\n<^^>>>vv\n<v>>v<\n'
    grid, instructions = extract_grid_and_instructions(lines=input_data)
    assert(grid is not None)
    assert(isinstance(grid, Grid))
    assert(grid.get_extent() == Position(8, 8))
    assert(grid.get_value(position=Position(2,2)) == '@')
    robot_positions = grid.find_value(value='@')
    assert(len(robot_positions) == 1)
    assert(robot_positions[0] == Position(2,2))

    assert(grid.get_value(position=Position(1, 1)) == '.')

    # setup the stage so that we move the two boxed to the right in the top row...
    state = State(grid=grid, position=Position(1,2), directions=[EAST, EAST, EAST, SOUTH, SOUTH])
    assert(state.follow_direction() == True)
    assert(state.follow_direction() == True)
    assert(state.follow_direction() == False)
    assert(state.grid.get_value(position=(1,6)) == 'O')
    assert(state.grid.get_value(position=(1,5)) == 'O')
    assert(state.grid.get_value(position=(1,4)) == '@')
    assert(state.grid.get_value(position=(1,3)) == '.')
    assert(state.position == Position(1,4))

    assert (state.follow_direction() == True)
    assert (state.follow_direction() == False)
    assert (state.grid.get_value(position=(2, 4)) == '@')
    assert (state.grid.get_value(position=(3, 4)) == 'O')
    assert (state.grid.get_value(position=(4, 4)) == 'O')
    assert (state.grid.get_value(position=(5, 4)) == 'O')
    assert (state.grid.get_value(position=(6, 4)) == 'O')

    return

def test_too():
    # test shuffling left
    #    012345678901
    # 0: #..[].[]..@#
    grid: Grid = Grid(extent=Position(row=1, column=12))
    grid.set_value(position=Position(0,0), value='#')
    grid.set_value(position=Position(0,1), value='.')
    grid.set_value(position=Position(0,2), value='.')
    grid.set_value(position=Position(0,3), value='[')
    grid.set_value(position=Position(0,4), value=']')
    grid.set_value(position=Position(0,5), value='.')
    grid.set_value(position=Position(0,6), value='[')
    grid.set_value(position=Position(0,7), value=']')
    grid.set_value(position=Position(0,8), value='.')
    grid.set_value(position=Position(0,9), value='.')
    grid.set_value(position=Position(0,10), value='@')
    grid.set_value(position=Position(0,11), value='#')
    state: State = State(grid=grid, position=Position(row=0, column=10), directions=[WEST, WEST, WEST, WEST, WEST, WEST, WEST])

    # first two moves west are without obstacle ... not much changes
    assert(state.follow_direction() == True)
    assert(state.follow_direction() == True)
    assert(state.position.column == 8)
    assert(grid.get_value(position=Position(0, 0)) == '#')
    assert(grid.get_value(position=Position(0, 1)) == '.')
    assert(grid.get_value(position=Position(0, 2)) == '.')
    assert(grid.get_value(position=Position(0, 3)) == '[')
    assert(grid.get_value(position=Position(0, 4)) == ']')
    assert(grid.get_value(position=Position(0, 5)) == '.')
    assert(grid.get_value(position=Position(0, 6)) == '[')
    assert(grid.get_value(position=Position(0, 7)) == ']')
    assert(grid.get_value(position=Position(0, 8)) == '@')
    assert(grid.get_value(position=Position(0, 9)) == '.')
    assert(grid.get_value(position=Position(0, 10)) == '.')

    # next move west should push the two boxes up against one another.
    assert(state.follow_direction() == True)
    #    012345678901
    # 0: #..[][]@...#
    assert(state.position.column == 7)
    row_as_text: str = state.grid.render_row(row=0)
    assert('#..[][]@...#' == row_as_text)
    # assert(grid.get_value(position=Position(0, 0)) == '#')

    # next move west should shunt the two boxes one pixel west.
    assert(state.follow_direction() == True)
    #    012345678901
    # 0: #.[][]@....#
    assert(state.position.column ==6)
    row_as_text: str = state.grid.render_row(row=0)
    assert('#.[][]@....#' == row_as_text)

    # next move west should shunt the two boxes one pixel west.
    assert(state.follow_direction() == True)
    #    012345678901
    # 0: #[][]@.....#
    assert(state.position.column == 5)
    row_as_text: str = state.grid.render_row(row=0)
    assert('#[][]@.....#' == row_as_text)

    # next move west should have no affect
    assert(state.follow_direction() == False)
    assert(state.finished() == False)
    #    012345678901
    # 0: #[][]@.....#
    assert(state.position.column == 5)
    row_as_text: str = state.grid.render_row(row=0)
    assert('#[][]@.....#' == row_as_text)

    assert(state.follow_direction() == False)
    assert(state.finished() == True)


    #    01234567
    # 0: ########
    # 1: #..@...#
    # 2: ##[]...#
    # 3: #..[]..#
    # 4: #.[][].#
    # 5: #[]..[]#
    # 6: #......#
    # 7: #.....##
    # 8: #......#
    # 9: ########
    grid: Grid = Grid(extent=Position(row=10, column=8))
    # robot
    grid.set_value(position=Position(1, 3), value='@')

    # boxes
    grid.set_value(position=Position(2, 2), value='[')
    grid.set_value(position=Position(2, 3), value=']')
    grid.set_value(position=Position(3, 3), value='[')
    grid.set_value(position=Position(3, 4), value=']')
    grid.set_value(position=Position(4, 1), value='[')
    grid.set_value(position=Position(4, 2), value=']')
    grid.set_value(position=Position(4, 3), value='[')
    grid.set_value(position=Position(4, 4), value=']')
    grid.set_value(position=Position(5, 1), value='[')
    grid.set_value(position=Position(5, 2), value=']')
    grid.set_value(position=Position(5, 5), value='[')
    grid.set_value(position=Position(5, 6), value=']')

    # bottom "fence"
    grid.set_value(position=Position(7, 6), value='#')
    grid.set_value(position=Position(9, 0), value='#')
    grid.set_value(position=Position(9, 1), value='#')
    grid.set_value(position=Position(9, 2), value='#')
    grid.set_value(position=Position(9, 3), value='#')
    grid.set_value(position=Position(9, 4), value='#')
    grid.set_value(position=Position(9, 5), value='#')
    grid.set_value(position=Position(9, 6), value='#')
    grid.set_value(position=Position(9, 7), value='#')

    # push the robot down twice
    state: State = State(grid=grid, position=Position(1, 3), directions=[SOUTH, SOUTH])

    state.follow_direction()
    # check state after first iteration
    # expecting;
    #    01234567
    # 0: ########
    # 1: #......#
    # 2: #..@...#
    # 3: #.[]...#
    # 4: #..[]..#
    # 5: #.[][].#
    # 6: #[]..[]#
    # 7: #.....##
    # 8: #......#
    # 9: ########
    assert(state.grid.get_value(position=Position(1, 3)) == '.')
    assert(state.grid.get_value(position=Position(2, 2)) == '.')
    assert(state.grid.get_value(position=Position(2, 3)) == '@')
    assert(state.grid.get_value(position=Position(3, 2)) == '[')
    assert(state.grid.get_value(position=Position(3, 3)) == ']')
    assert(state.grid.get_value(position=Position(4, 3)) == '[')
    assert(state.grid.get_value(position=Position(4, 4)) == ']')
    assert(state.grid.get_value(position=Position(5, 2)) == '[')
    assert(state.grid.get_value(position=Position(5, 1)) == '.')
    assert(state.grid.get_value(position=Position(5, 3)) == ']')
    assert(state.grid.get_value(position=Position(5, 4)) == '[')
    assert(state.grid.get_value(position=Position(5, 5)) == ']')
    assert(state.grid.get_value(position=Position(5, 6)) == '[')
    assert(state.grid.get_value(position=Position(6, 1)) == ']')
    assert(state.grid.get_value(position=Position(6, 3)) == '.')
    assert(state.grid.get_value(position=Position(6, 4)) == '.')
    assert(state.grid.get_value(position=Position(6, 5)) == '[')
    assert(state.grid.get_value(position=Position(6, 6)) == ']')

    # now send the robot south once more .... should not be able to move any boxes
    state.follow_direction()
    # check state after second iteration
    # expecting;
    #    01234567
    # 0: ########
    # 1: #......#
    # 2: #..@...#
    # 3: #.[]...#
    # 4: #..[]..#
    # 5: #.[][].#
    # 6: #[]..[]#
    # 7: #.....##
    # 8: #......#
    # 9: ########
    assert(state.grid.get_value(position=Position(1, 3)) == '.')
    assert(state.grid.get_value(position=Position(2, 2)) == '.')
    assert(state.grid.get_value(position=Position(2, 3)) == '@')
    assert(state.grid.get_value(position=Position(3, 2)) == '[')
    assert(state.grid.get_value(position=Position(3, 3)) == ']')
    assert(state.grid.get_value(position=Position(4, 3)) == '[')
    assert(state.grid.get_value(position=Position(4, 4)) == ']')
    assert(state.grid.get_value(position=Position(5, 2)) == '[')
    assert(state.grid.get_value(position=Position(5, 1)) == '.')
    assert(state.grid.get_value(position=Position(5, 3)) == ']')
    assert(state.grid.get_value(position=Position(5, 4)) == '[')
    assert(state.grid.get_value(position=Position(5, 5)) == ']')
    assert(state.grid.get_value(position=Position(5, 6)) == '[')
    assert(state.grid.get_value(position=Position(6, 1)) == ']')
    assert(state.grid.get_value(position=Position(6, 3)) == '.')
    assert(state.grid.get_value(position=Position(6, 4)) == '.')
    assert(state.grid.get_value(position=Position(6, 5)) == '[')
    assert(state.grid.get_value(position=Position(6, 6)) == ']')




    return

if __name__ == "__main__":
    exit_code: int = 0
    test_too()
#    exit_code = main(sys.argv)
    sys.exit(exit_code)