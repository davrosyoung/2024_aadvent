import re
import sys

#valid_instruction_pattern: re.Pattern = re.compile(r'^(mul|add|del|sub|div)\((\d+),(\d+)\)')
valid_instruction_pattern: re.Pattern = re.compile(r'^(mul)\((\d+),(\d+)\)')

def main(argv) -> int:
    # just read from standard input.....
    content: str = ''
    for line in sys.stdin:
        content += line

    if len(content) < 3:
        print('Invalid input')
        return 1

    # sweep the content looking for dos and donts
    i: int  = 0
    dos: list[int] = []
    donts: list[int] = []
    while(i < len(content) - 5):
        candidate: str = content[i:i+5]
        if candidate == 'don\'t':
            donts.append(i)
            i += 5
            continue
        if candidate[0:2] == 'do':
            dos.append(i)
            i += 2
            continue
        i += 1

    enabled: list[bool] = []
    do_idx: int = 0
    dont_idx: int = 0
    currently_enabled: bool = True
    for i in range(len(content)):
        if len(donts) > dont_idx and i == donts[dont_idx]:
            currently_enabled = False
            dont_idx += 1
        elif len(dos) > do_idx and i == dos[do_idx]:
            currently_enabled = True
            do_idx += 1
        enabled.append(currently_enabled)

    # sweep the content looking for mul strings
    strikes: list[int] = []
    i: int = 0
    while(i < len(content) - 3):
        candidate: str = content[i:i+3]
        if candidate in ['mul']:
            strikes.append(i)
            i += 3
            continue
        i += 1

    operations: list[tuple[str, int, int]] = []

    # now check out the strings where the operators lie....
    for idx, pos in enumerate(strikes):
        # if the input string is not "enabled" at the location of this operation .... do not include it
        if not enabled[pos]:
            continue
        end_pos: int = strikes[idx+1] if idx < len(strikes) - 1 else len(content)
        candidate: str = content[pos:end_pos]
        bits = valid_instruction_pattern.match(candidate)
        if bits is None:
            continue
        operation: str = bits[1]
        operand_alpha: int = int(bits[2])
        operand_beta: int = int(bits[3])
        operations.append((operation, operand_alpha, operand_beta))

    result: int = 0
    for operation, operand_alpha, operand_beta in operations:
        if operation == 'mul':
            print(f'{operand_alpha}+{operand_beta}={operand_alpha+operand_beta}')
            result += operand_alpha * operand_beta
        elif operation == 'add':
            result += operand_alpha + operand_beta
        elif operation == 'sub':
            result += operand_alpha - operand_beta
        elif operation == 'div':
            result += operand_alpha / operand_beta
        else:
            print(f'Unknown operation: {operation}')

    print(f'{result=}')
    return 0


if __name__ == '__main__':
    exit_code: int = main(sys.argv[1:])
    sys.exit(exit_code)

