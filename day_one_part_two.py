import sys

def insert_into_list(list_alpha: list[int], alpha: int) -> None:
    """Build up an ordered list of integers"""
    # empty list?!? just append to the end of the list
    if len(list_alpha) == 0:
        list_alpha.append(alpha)
        return

    # if alpha is at least as large as the last element; just append to the end
    if alpha >= list_alpha[-1]:
        list_alpha.append(alpha)
        return

    for i, beta in enumerate(list_alpha):
        if alpha >= beta:
            list_alpha.insert(i, alpha)
            return

    list_alpha.append(alpha)

def main(argv) -> int:
    # just read from standard input.....
    list_alpha: list[int] = []
    list_beta: list[int] = []
    beta_hit_count: dict[int, int] = {}
    for line in sys.stdin:
        bits: list[str] = line.strip().split()
        alpha: int = int(bits[0])
        beta: int = int(bits[1])
        list_alpha.append(alpha)
        list_beta.append(beta)
        if beta not in beta_hit_count:
            beta_hit_count[beta] = 0
        beta_hit_count[beta] += 1


    score: int = 0
    for alpha in list_alpha:
        if alpha in beta_hit_count:
            score += beta_hit_count[alpha] * alpha

    print(f'Similarity Score: {score}')
    return 0


if __name__ == '__main__':
    exit_code: int = main(sys.argv[1:])
    sys.exit(exit_code)

