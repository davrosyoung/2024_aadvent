import sys
import re

ORDER_LINE_INFO_PATTERN = re.compile(r'^\s*(\d+)\s*\|\s*(\d+)\s*$')
PAGES_LINE_INFO_PATTERN = re.compile(r'^\s*(\d+)\s*(,\s*(\d+)\s*)*$')

def find_following_page_numbers(page_ordering_map: dict[int, list[int]], page_number: int, result: list[int] = [], depth: int = 0) -> list[int]:
    if page_number not in page_ordering_map:
        return result
    following_pages: list[int] = page_ordering_map.get(page_number)
    for following_page_number in following_pages:
        # don't fall down the circular recursion trap!!
        if following_page_number in result:
            continue
        result.append(following_page_number)
        more_numbers: list[int] = find_following_page_numbers(page_ordering_map=page_ordering_map, page_number=following_page_number, result=result, depth=depth+1)
        for some_page_number in more_numbers:
            if some_page_number not in result and some_page_number not in following_pages:
                result.append(some_page_number)
    return result

def part_one(path: str) -> int:
    result: int = 0
    following_pages_by_preceding_page: dict[int, list[int]] = {}
    preceding_pages_by_following_page: dict[int, list[int]] = {}
    first_page: int = None

    # sweep one ... gather the ordering information
    with open(path, 'r') as file:
        for line in file:
            bits = ORDER_LINE_INFO_PATTERN.match(line)
            if bits is None:
                continue
            alpha: int = int(bits[1])
            beta: int = int(bits[2])
            if alpha not in following_pages_by_preceding_page:
                following_pages_by_preceding_page[alpha] = []

            # add page beta to the list of pages that page alpha comes BEFORE
            # (unless page alpha already listed as coming BEFORE page beta).
            if beta in preceding_pages_by_following_page and alpha in preceding_pages_by_following_page[beta]:
                raise Exception(f'WHAT!?! {alpha=} ALREADY listed as coming before {beta=}')

            # if the following page (beta) is not already listed in list of pages for alpha, then add it to the list.
            if beta not in following_pages_by_preceding_page[alpha]:
                following_pages_by_preceding_page[alpha].append(beta)

            # add page alpha to the list of pages that page beta comes AFTER
            # (unless page beta already listed as coming BEFORE page alpha)
            if beta in following_pages_by_preceding_page and alpha in following_pages_by_preceding_page[beta]:
                raise Exception(f'WHAT!?! {beta=} ALREADY listed as coming after {alpha=}')

            if beta not in preceding_pages_by_following_page:
                preceding_pages_by_following_page[beta] = []
            if alpha not in preceding_pages_by_following_page[beta]:
                preceding_pages_by_following_page[beta].append(alpha)


    # sweep two .... process the page lists.
    result: int = 0
    with open(path, 'r') as file:
        for line in file:
            bits = PAGES_LINE_INFO_PATTERN.match(line)
            if bits is None:
                continue
            page_numbers: list[int] = [int(p) for p in line.split(',')]
            filtered_page_numbers: list[int] = [fp for fp in page_numbers if fp in following_pages_by_preceding_page]
            all_in_order: bool = True
            idx: int = 0
            while idx < len(filtered_page_numbers) - 1 and all_in_order:
                alpha: int = page_numbers[idx]
                beta: int = page_numbers[idx + 1]
                pages_following_alpha: list[int] = []
                pages_following_alpha = find_following_page_numbers(page_ordering_map=following_pages_by_preceding_page, page_number=alpha, result=pages_following_alpha)
                pages_following_beta: list[int] = []
                pages_following_beta = find_following_page_numbers(page_ordering_map=following_pages_by_preceding_page, page_number=beta, result=pages_following_beta)
                if beta not in pages_following_alpha or alpha in pages_following_beta:
                    all_in_order = False
                idx += 1
            if not all_in_order:
                continue
            if len(page_numbers) % 2 == 1:
                middleth_index: int = int(len(page_numbers) / 2)
                result += page_numbers[middleth_index]

    return result



def part_two(path: str) -> int:
    result: int = 0
    with open(path, 'r') as file:
        lines: list[str] = file.readlines()


    return result

def osho():
    page_order: dict[int, list[int]] = {
        75: [29, 53, 47, 61, 13],
        29: [13],
        53: [29, 13],
        47: [53, 29, 13, 61],
        61: [53, 13, 29]
    }

    following_pages = find_following_page_numbers(page_ordering_map=page_order, page_number=61)
    print(following_pages)

def main(argv: list[str]):


    result: int = 0
    result = part_one(path='day_five_test_input.txt')
    print(f'part one: {result=} for test data')
    if result != 143:
        raise Exception(f'Test failed, expected 143 but instead got {result}')
    result = part_one(path='day_five_input.txt')
    print(f'part one: {result=} for actual data')

    result = part_two(path='day_five_test_input.txt')
    print(f'part two: {result=} for test data')
    if result != 0:
        raise Exception(f'Test failed, expected 9 but instead got {result}')
    result: int = part_two(path='day_five_input.txt')
    print(f'part two: {result=} for actual data')

    return 0

if __name__ == "__main__":
    exit_code: int = main(sys.argv)
    sys.exit(exit_code)