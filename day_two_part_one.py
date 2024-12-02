import sys

def is_safe(candidates: list[int]) -> bool:
    safe: bool = True
    if len(candidates) < 2:
        return False
    if candidates[0] == candidates[1]:
        return False
    increasing: bool = candidates[1] > candidates[0]
    index: int = 0
    while safe and index <= len(candidates) - 2:
        a: int = candidates[index]
        b: int = candidates[index + 1]
        d: int = abs(b - a)
        if increasing:
            safe = b > a and d <= 3
        else:
            safe = b < a and d <= 3
        index += 1
    return safe

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
        if is_safe(row):
            print(row)
            safe_count += 1

    print(f'{safe_count=} of {total_count=}')
    return 0


if __name__ == '__main__':
    exit_code: int = main(sys.argv[1:])
    sys.exit(exit_code)

