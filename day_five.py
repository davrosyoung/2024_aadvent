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
    listed_pages: list[int] = []

    # sweep one ... gather the ordering information
    with open(path, 'r') as file:
        for line in file:
            bits = ORDER_LINE_INFO_PATTERN.match(line)
            if bits is None:
                continue
            alpha: int = int(bits[1])
            beta: int = int(bits[2])
            listed_pages.append(alpha)
            listed_pages.append(beta)
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

    # create a list of pages in order...
    # there should be ONE page which is in the keys of following_pages_by_preceding_page map, whilst not
    # in the keys of preceding_pages_by_following_page map.
    preceding_pages: list[int] = following_pages_by_preceding_page.keys()
    pages_out_front: list[int] = []
    for candidate_page in preceding_pages:
        if candidate_page not in preceding_pages_by_following_page:
            pages_out_front.append(candidate_page)

    print(f'{pages_out_front=}')
    if len(pages_out_front) != 1:
        raise Exception(f'THere must be only ONE page which comes first, but instead we got {pages_out_front=}')


    # sweep two .... process the page lists.
    result: int = 0
    with open(path, 'r') as file:
        for line in file:
            bits = PAGES_LINE_INFO_PATTERN.match(line)
            if bits is None:
                continue
            page_numbers: list[int] = [int(p) for p in line.split(',')]
            filtered_page_numbers: list[int] = [fp for fp in page_numbers if fp in listed_pages]
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
            print(f'{page_numbers=}')
            middleth_index: int = int(len(page_numbers) / 2)
            median: int = page_numbers[middleth_index] if len(page_numbers) % 2 == 1 else int((page_numbers[middleth_index - 1] + page_numbers[middleth_index]) / 2)
            result += median

    return result

def part_one_try_too(path: str) -> int:
    result: int = 0
    following_pages_by_preceding_page: dict[int, list[int]] = {}
    preceding_pages_by_following_page: dict[int, list[int]] = {}
    first_page: int = None
    listed_pages: list[int] = []

    # sweep one ... gather the ordering information
    with open(path, 'r') as file:
        for line in file:
            bits = ORDER_LINE_INFO_PATTERN.match(line)
            if bits is None:
                continue
            alpha: int = int(bits[1])
            beta: int = int(bits[2])
            listed_pages.append(alpha)
            listed_pages.append(beta)
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
            filtered_page_numbers: list[int] = [fp for fp in page_numbers if fp in listed_pages]
            all_in_order: bool = True
            idx: int = 0
            while idx < len(filtered_page_numbers) - 1 and all_in_order:
                alpha: int = page_numbers[idx]
                beta: int = page_numbers[idx + 1]

                # ignore pages not listed in ordering instructions...
                if alpha not in listed_pages or beta not in listed_pages:
                    continue

                if alpha not in following_pages_by_preceding_page:
                    all_in_order = False
                    continue

                if beta not in following_pages_by_preceding_page[alpha]:
                    all_in_order = False
                    continue

                idx += 1
            if not all_in_order:
                continue
            print(f'{page_numbers=}')
            middleth_index: int = int(len(page_numbers) / 2)
            median: int = page_numbers[middleth_index] if len(page_numbers) % 2 == 1 else int((page_numbers[middleth_index - 1] + page_numbers[middleth_index]) / 2)
            result += median

    return result


def part_two(path: str) -> int:
    result: int = 0
    following_pages_by_preceding_page: dict[int, list[int]] = {}
    preceding_pages_by_following_page: dict[int, list[int]] = {}
    first_page: int = None
    listed_pages: list[int] = []

    # sweep one ... gather the ordering information
    with open(path, 'r') as file:
        for line in file:
            bits = ORDER_LINE_INFO_PATTERN.match(line)
            if bits is None:
                continue
            alpha: int = int(bits[1])
            beta: int = int(bits[2])
            listed_pages.append(alpha)
            listed_pages.append(beta)
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
            filtered_page_numbers: list[int] = [fp for fp in page_numbers if fp in listed_pages]
            all_in_order: bool = True
            idx: int = 0
            while idx < len(filtered_page_numbers) - 1 and all_in_order:
                alpha: int = page_numbers[idx]
                beta: int = page_numbers[idx + 1]

                # ignore pages not listed in ordering instructions...
                if alpha not in listed_pages or beta not in listed_pages:
                    continue

                if alpha not in following_pages_by_preceding_page:
                    all_in_order = False
                    continue

                if beta not in following_pages_by_preceding_page[alpha]:
                    all_in_order = False
                    continue

                idx += 1


            if all_in_order:
                continue

            # ok.... we need to put these pages in order....
            my_page_numbers: list[int] = page_numbers.copy()
            swap_iteration: int = 0
            while not all_in_order:
                swap_count: int = 0
                mangled_page_numbers: list[int] = my_page_numbers.copy()
                for idx in range(len(my_page_numbers) - 1):
                    alpha: int = my_page_numbers[idx]
                    beta: int = my_page_numbers[idx + 1]

                    # ignore pages not listed in ordering instructions...
                    if alpha not in listed_pages or beta not in listed_pages:
                        continue

                    # if the pages are in the correct order ... leave them alone....
                    if alpha in following_pages_by_preceding_page and beta in following_pages_by_preceding_page[alpha]:
                        continue

                    # ok... swapsy time...
                    my_page_numbers[idx] = beta
                    my_page_numbers[idx + 1] = alpha
                    swap_count += 1
                    idx += 1

                #my_page_numbers = mangled_page_numbers.copy()
                # now are they in order?
                all_in_order: bool = True
                idx: int = 0
                while idx < len(my_page_numbers) - 1 and all_in_order:
                    alpha: int = my_page_numbers[idx]
                    beta: int = my_page_numbers[idx + 1]

                    # ignore pages not listed in ordering instructions...
                    if alpha not in listed_pages or beta not in listed_pages:
                        continue

                    if alpha not in following_pages_by_preceding_page:
                        all_in_order = False
                        continue

                    if beta not in following_pages_by_preceding_page[alpha]:
                        all_in_order = False
                        continue

                    idx += 1

                #print(f'{swap_iteration=}, {swap_count=}, {all_in_order=}')
                swap_iteration += 1

            #print(f'{my_page_numbers=}')
            middleth_index: int = int(len(my_page_numbers) / 2)
            median: int = my_page_numbers[middleth_index] if len(my_page_numbers) % 2 == 1 else int(
                (my_page_numbers[middleth_index - 1] + my_page_numbers[middleth_index]) / 2)
            result += median

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
    result = part_one_try_too(path='day_five_davros.txt')
    print(f'part one: {result=} for davros data')
    if result != 24:
        raise Exception(f'Test failed, expected 24 but instead got {result}')
    result = part_one_try_too(path='day_five_test_input.txt')
    print(f'part one: {result=} for test data')
    if result != 143:
        raise Exception(f'Test failed, expected 143 but instead got {result}')
    result = part_one_try_too(path='day_five_input.txt')
    print(f'part one: {result=} for actual data')

    result = part_two(path='day_five_test_input.txt')
    print(f'part two: {result=} for test data')
    if result != 123:
        raise Exception(f'Test failed, expected 123 but instead got {result}')
    result: int = part_two(path='day_five_input.txt')
    print(f'part two: {result=} for actual data')

    return 0

if __name__ == "__main__":
    exit_code: int = main(sys.argv)
    sys.exit(exit_code)