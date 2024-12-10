import sys
import re
from copy import deepcopy
from math import floor



verbose: bool = False
very_verbose: bool = False

def render(disk_map: list[tuple[int, int]]) -> str:
    result: str = ''
    for twin in disk_map:
        id: int = twin[0]
        size: int = twin[1]
        if id is not None and id >= 0:
            result += str(id % 10) * size
        else:
            result += '.' * size
    return result

def render_to_list(disk_map: list[tuple[int, int]], empty: int|None= None) -> list[int|None]:
    result: list[int|None] = []
    for twin in disk_map:
        id: int = twin[0]
        size: int = twin[1]
        for i in range(size):
            result.append(id if id >= 0 else empty)
    return result

def extract_disk_map(line:str) -> list[tuple[int, int]]:
    is_file: bool = True
    i: int = 0
    file_id: int = None
    input = line.strip()
    result: list[tuple[int, int]] = []
    while(i < len(line)):
        digit: str = input[i]
        if not digit.isdigit():
            raise Exception(f'Expecting a DIGIT at position {i=}, but rather got {digit}')
        if is_file:
            file_id = 0 if file_id is None else file_id + 1
            result.append((file_id, int(digit)))
        else:
            result.append((-1, int(digit)))
        i += 1
        is_file = not is_file
    return result

def optimise_disk(disk_map: list[tuple[int, int]]) -> list[tuple[int, int]]:
    
    strip: list[int] = render_to_list(disk_map=disk_map, empty=-1)
    first_gap_pos: int = None
    try:
        first_gap_pos = strip.index(-1)
    except ValueError as ve:
        first_gap_pos = -1
    while first_gap_pos >= 0:
        last_id: int = strip[-1]
        if last_id >= 0 and first_gap_pos >= 0:
            strip[first_gap_pos] = last_id
        del strip[-1]
        try:
            first_gap_pos = strip.index(-1)
        except ValueError as ve:
            first_gap_pos = -1
    result = disk_map_from_integer_list(candidate=strip)
    return result


def disk_map_from_render(candidate: str) -> list[tuple[int, int]]:
    result: list[tuple[int,int]] = []
    last_khar: str = None
    khar: str = None
    run_length: int = 0
    for index in range(len(candidate)):
        khar = candidate[index:index+1]
        if khar != last_khar and last_khar is not None:
            # insert a zero-length gap if this is not the first "segment"
            if len(result) > 0:
                result.append((-1, 0))
            result.append((int(last_khar), run_length))
            run_length = 0
        last_khar=khar
        run_length += 1

    if run_length > 0:
        if len(result) > 0:
            result.append((-1, 0))
        result.append((int(last_khar), run_length))

    return result

def disk_map_from_integer_list(candidate: list[int]) -> list[tuple[int, int]]:
    result: list[tuple[int,int]] = []
    last_file_id: int = None
    file_id: int = None
    run_length: int = 0
    for index in range(len(candidate)):
        file_id = candidate[index]
        if file_id != last_file_id and last_file_id is not None:
            # insert a zero-length gap if this is not the first "segment"
            if len(result) > 0:
                result.append((-1, 0))
            result.append((last_file_id, run_length))
            run_length = 0
        last_file_id = file_id
        run_length += 1

    if run_length > 0:
        if len(result) > 0:
            result.append((-1, 0))
        result.append((last_file_id, run_length))

    return result


def optimise_disk_by_file(disk_map: list[tuple[int, int]]) -> list[tuple[int, int]]:
    scratch_map: list[tuple[int, int]] = deepcopy(disk_map)
    file_list: list[tuple[tuple[int, int],int]] = [(t,i) for i,t in enumerate(scratch_map) if t[0] >= 0]
    extract_cursor_index: int = len(file_list) - 1
    insert_cursor_index: int = 0
    result: list[tuple[int, int]] = []
    finito: bool = extract_cursor_index == 0
    insert_segment: tuple[int, int] = scratch_map[insert_cursor_index]
    extract_segment: tuple[int, int] = scratch_map[extract_cursor_index]

    while not finito:
        # find the smallest gap that will accommodate the current file to consider....
        space_needed: int = file_list[extract_cursor_index][0][1]
        file_scratch_index: int = file_list[extract_cursor_index][1]
        contender_index: int = None
        contender_size: int = None
        for i, element in enumerate(scratch_map):
            # skip actual files .... we just want gaps
            if element[0] >= 0:
                continue
            gap_size: int = element[1]
            # don't both if the gap isn't large enough to accommodate the file.
            if gap_size < space_needed:
                # i could have been a contender!!!
                continue
            if contender_size is None or gap_size < contender_size:
                contender_index = i
                contender_size = gap_size

        # did we find a gap?!?
        if contender_index is not None:
            # reduce the size of the existing gap....
            scratch_map[contender_index] = (-1, contender_size - space_needed)
            # insert a spacer of zero...
            scratch_map.insert(contender_index, (-1, 0))
            # now insert the "entire moved file" after the spacer we just inserted....
            file_id: int = file_list[extract_cursor_index][0][0]
            scratch_map.insert(contender_index + 1, (file_id, space_needed))

            # if the gap was to the left of the file, then the location of the file to be extracted will have been incremented by two.
            if contender_index < file_scratch_index:
                file_scratch_index += 2
            # now remove the original file entry from the scratch...
            del scratch_map[file_scratch_index]


        extract_cursor_index -= 1
        finito = extract_cursor_index < 0
        result = scratch_map
    return result

def calculate_checksum(disk_map: list[tuple[int, int]]) -> int:
    block_number: int = 0
    result: int = 0
    for entry in disk_map:
        file_id: int = entry[0]
        length: int = entry[1]
        if file_id < 0:
            block_number += length
            continue
        for i in range(length):
            result += file_id * block_number
            block_number += 1
    return result

def part_one(path: str) -> int:
    result: int = 0

    # sweep one ... gather the ordering information
    with open(path, 'r') as file:
        line_number: int = 1
        for line in file:
            line_number += 1
            disk_map: list[tuple[int, int]] = extract_disk_map(line)
            print(f'BEFORE: {render(disk_map=disk_map)}')
            disk_map = optimise_disk(disk_map=disk_map)
            print(f' AFTER: {render(disk_map=disk_map)}')
            result = calculate_checksum(disk_map=disk_map)
    return result

def part_two(path: str) -> int:
    result: int = 0

    # sweep one ... gather the ordering information
    with open(path, 'r') as file:
        line_number: int = 1
        for line in file:
            line_number += 1
    return result


def main(argv: list[str]):
    global very_verbose
    global verbose
    global OPERATORS
    very_verbose = False
    verbose = False
    result = part_one(path='day_nine_test_input.txt')
    print(f'part one: {result=} for test data')
    if result != 1928:
        raise Exception(f'Test failed, expected 1928 but instead got {result}')
    result = part_one(path='day_nine_input.txt')
    print(f'part one: {result=} for actual data')
#
#    result = part_two(path='day_nine_test_input.txt')
#    print(f'part two: {result=} for test data')
#    if result != 1928:
#        raise Exception(f'Test failed, expected 1928 but instead got {result}')
#    result: int = part_two(path='day_nine_input.txt')
#    print(f'part two: {result=} for actual data')

    return 0

def test():
    input:str = '31415926536'
    disk_map: list[tuple[int, int]] = extract_disk_map(line=input)
    print(render(disk_map=disk_map))
    assert(disk_map is not None)
    assert(len(disk_map) == 11)
    assert(disk_map[0] == (0, 3))
    assert(disk_map[1] == (-1, 1))
    assert(disk_map[2] == (1, 4))
    assert(disk_map[3] == (-1, 1))
    assert(disk_map[4] == (2, 5))
    assert(disk_map[5] == (-1, 9))
    assert(disk_map[6] == (3, 2))
    assert(disk_map[7] == (-1, 6))
    assert(disk_map[8] == (4, 5))
    assert(disk_map[9] == (-1, 3))
    assert(disk_map[10] == (5, 6))


    ## 000.1111.22222.........33......44444...555555

    checksum = calculate_checksum(disk_map=disk_map)
    assert(checksum == 2178)

    print(f' pre optimisation; {render(disk_map=disk_map)}')
    disk_map_p1 = optimise_disk_by_file(disk_map=disk_map)
    print(f'post optimisation; {render(disk_map=disk_map)}')

    ## 000.1111.22222.........33......44444...555555
    ### 0005111152222255554444433
    ### 000 5 1111 5 22222 5555 44444 33
    assert (len(disk_map_p1) == 15)
    assert (disk_map_p1[0] == (0, 3))
    assert (disk_map_p1[1] == (-1, 0))
    assert (disk_map_p1[2] == (5, 1))
    assert (disk_map_p1[3] == (-1, 0))
    assert (disk_map_p1[4] == (1, 4))
    assert (disk_map_p1[5] == (-1, 0))
    assert (disk_map_p1[6] == (5, 1))
    assert (disk_map_p1[7] == (-1, 0))
    assert (disk_map_p1[8] == (2, 5))
    assert (disk_map_p1[9] == (-1, 0))
    assert (disk_map_p1[10] == (5, 4))
    assert (disk_map_p1[11] == (-1, 0))
    assert (disk_map_p1[12] == (4, 5))
    assert (disk_map_p1[13] == (-1, 0))
    assert (disk_map_p1[14] == (3, 2))

    print(f' pre optimisation; {render(disk_map=disk_map)}')
    disk_map_p2 = optimise_disk_by_file(disk_map=disk_map)
    print(f'post optimisation; {render(disk_map=disk_map)}')

    ## 000.1111.22222.........33......44444...555555
    ## 000.1111.22222555555...33......44444...
    ## 000.1111.22222555555...3344444.
    ## 000.1111.22222555555.33..44444.
    assert (len(disk_map_p2) == 12)
    assert (disk_map_p2[0] == (0, 3))
    assert (disk_map_p2[1] == (-1, 1))
    assert (disk_map_p2[2] == (1, 4))
    assert (disk_map_p2[3] == (-1, 1))
    assert (disk_map_p2[4] == (2, 5))
    assert (disk_map_p2[5] == (-1, 0))
    assert (disk_map_p2[6] == (5, 6))
    assert (disk_map_p2[7] == (-1, 1))
    assert (disk_map_p2[8] == (3, 2))
    assert (disk_map_p2[9] == (-1, 2))
    assert (disk_map_p2[10] == (4, 5))
    assert (disk_map_p2[11] == (-1, 1))

    return

if __name__ == "__main__":
    test()
#    exit_code: int = main(sys.argv)
#    sys.exit(exit_code)