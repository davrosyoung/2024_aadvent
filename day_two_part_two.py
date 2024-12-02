import sys

def is_safe(candidates: list[int], max_unsafe_count: int = 0) -> bool:
    total_count: int = 0
    unsafe_count: int = 0
    increasing: bool = None
    decreasing: bool = None
    result: bool = True
    if len(candidates) < 2:
        return False
    index: int = 0
    while unsafe_count <= max_unsafe_count and index <= len(candidates) - 2:
        a: int = candidates[index]
        b: int = candidates[index + 1]
        d: int = abs(b - a)
        row_safe: bool = False
        # if we don't yet have a rising or falling trend, set it as soon as it becomes apparent...
        if increasing is None and decreasing is None and d > 0:
            increasing = b > a
            decreasing = b < a

        # if we are following a previously established trend and the rate of change is >= 1 and <= 3 we are ok.
        if increasing:
            row_safe = b > a and d <= 3
        elif decreasing:
            row_safe = b < a and d <= 3
        else:
            row_safe = False


        if not row_safe:
            unsafe_count += 1
        index += 1
    result: bool = unsafe_count <= max_unsafe_count
    return result

def main(argv) -> int:
    # just read from standard input.....
    list_alpha: list[int] = []
    list_beta: list[int] = []
    safe_count: int = 0
    total_count: int = 0
    for line in sys.stdin:
        bits: list[str] = line.strip().split()
        row: list[int] = [int(x) for x in bits]
        total_count += 1
        if is_safe(row, max_unsafe_count=0):
            print(row)
            safe_count += 1
        else:
            we_found_one: bool = False
            shortened_row: list[int] = None
            hole_index: int = 0
            while(hole_index < len(row) and not we_found_one):
                shortened_row = row.copy()
                shortened_row.pop(hole_index)
                if is_safe(shortened_row, max_unsafe_count=0):
                    we_found_one = True
                hole_index += 1
            if we_found_one:
                safe_count += 1
                print(f'{row=} OK with a shortened row {shortened_row=}')


    print(f'{safe_count=} of {total_count=}')
    return 0


if __name__ == '__main__':
    exit_code: int = main(sys.argv[1:])
    sys.exit(exit_code)

