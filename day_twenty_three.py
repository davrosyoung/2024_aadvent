import os
import sys
import re
from copy import deepcopy
from dataclasses import dataclass


from common import read_lines_from_file, WEST, EAST, NORTH, SOUTH, direction_from_character, Position, \
    STEP_DIRECTIONS_BY_DIRECTION
from grid import Grid

verbose: bool = False
very_verbose: bool = False
DIRECTIONS_PATTERN:  re.Pattern = re.compile(r'^[<^>vV]+$')

def extract_pairs(lines: list[str]) -> list[tuple[str, str]]:
    result: list[tuple[str, str]] = []
    for line in lines:
        if len(line) > 0:
            pair: list[str] = line.split('-')
            result.append((pair[0].strip(), pair[1].strip()))
    return result

def part_one(path: str) -> int:
    result: int = 0

    data_lines: list[str] = read_lines_from_file(path=path)
    pairs: list[tuple[str, str]] = extract_pairs(lines=data_lines)
    connections: dict[str, list[str]] = {}
    nodes: set[str] = set()
    for pear in pairs:
        alpha: str = pear[0]
        beta: str = pear[1]
        nodes.add(alpha)
        nodes.add(beta)
        if alpha not in connections:
            connections[alpha] = []
        connections.get(alpha).append(beta)

        if beta not in connections:
            connections[beta] = []
        connections.get(beta).append(alpha)

    triplets: set[tuple[str, str, str]] = set()

    for node in nodes:
        friends: list[str] = connections.get(node)
        for friend in friends:
            second_friends: list[str] = connections.get(friend)
            for second_friend in second_friends:
                if second_friend == node:
                    continue
                if node in connections.get(second_friend):
                    sorted_names = sorted([node, friend, second_friend])
                    triplets.add((sorted_names[0], sorted_names[1], sorted_names[2]))

    for triple in triplets:
        print(triple)

    filtered_triplets: set[tuple[str, str, str]] = [t for t in triplets if t[0].startswith('t') or t[1].startswith('t') or t[2].startswith('t')]

    print(f'We have {len(filtered_triplets)} filtered triplets')
    for triple in filtered_triplets:
        print(triple)

    result: int = len(filtered_triplets)
    print(f'{result=}')
    return result

def find_friends(node: str, connections: dict[str, list[str]], exclude: list[str]=[], depth: int = 0) -> list[str]:
    result: list[str] = []
    friends: list[str] = connections.get(node)
    exclude_copy: list[str] = deepcopy(exclude)
    exclude_copy.append(node)
    for friend in friends:
        if friend in exclude_copy or friend in result:
            continue
        result.append(friend)
        result.extend(find_friends(node=friend, connections=connections, exclude=exclude_copy, depth=depth+1))
    return result

def part_two(data_lines: list[str]) -> int:
    pairs: list[tuple[str, str]] = extract_pairs(lines=data_lines)
    connections: dict[str, list[str]] = {}
    nodes: set[str] = set()
    for pear in pairs:
        alpha: str = pear[0]
        beta: str = pear[1]
        nodes.add(alpha)
        nodes.add(beta)
        if alpha not in connections:
            connections[alpha] = []
        connections.get(alpha).append(beta)

        if beta not in connections:
            connections[beta] = []
        connections.get(beta).append(alpha)


    max_number_friends: int = None
    largest_friends_group: list[str] = None
    for node in nodes:
        friends: list[str] = connections.get(node)
        # for each directly connected node....
        for friend in friends:
            # find how many of them have friends also directly connected with node...
            second_friends: set[str] = set(connections.get(friend))
            # filter this list to those friends that exist as direct connections to "node"....
            common_friends: set[str] = set([sf for sf in second_friends if sf in friends])

            common_friends.add(node)
            common_friends.add(friend)
            number_common_friends: int = len(common_friends)
            if max_number_friends is None or number_common_friends > max_number_friends:
                max_number_friends = number_common_friends
                largest_friends_group = sorted(common_friends)


    sorted_friends: list[str] = sorted(largest_friends_group)
    print(f'{sorted_friends=}')
    result: str = ','.join(sorted_friends)
    return result

def part_two_take_two(data_lines: list[str]) -> int:
    pairs: list[tuple[str, str]] = extract_pairs(lines=data_lines)
    connections: dict[str, list[str]] = {}
    nodes: set[str] = set()
    for pear in pairs:
        alpha: str = pear[0]
        beta: str = pear[1]
        nodes.add(alpha)
        nodes.add(beta)
        if alpha not in connections:
            connections[alpha] = []
        connections.get(alpha).append(beta)

        if beta not in connections:
            connections[beta] = []
        connections.get(beta).append(alpha)


    networks: list[set[tuple[str, str]]] = []
    networks_by_connection: dict[tuple[str,str],list[set[tuple[str,str]]]] = {}

    groups: list[set[str]] = []
    groups_by_membership: dict[str, list[set[str]]] = {}

    # pass two ... form networks....
    for node in nodes:
        friends: list[str] = connections.get(node)

        for friend in friends:
            # are there any groups that these two nodes already belong to?
            node_groups: list[set[str]] = groups_by_membership.get(node)
            existing_common_groups: list[set[str]] = []
            if node_groups:
                for ng in node_groups:
                    if friend in ng:
                        existing_common_groups.append(ng)

            if len(existing_common_groups) == 0:
                # are there any common friends that either of these two nodes are in a group with already?
                node_friends: set[str] = set(connections.get(node))
                friend_friends: set[str] = set(connections.get(friend))
                common_friends: set[str] = node_friends & friend_friends
                for buddy in common_friends:
                    candidate_groups: list[set[str]] = groups_by_membership.get(buddy)
                    if candidate_groups is None:
                        continue


                    # are both node and friend directly connected to all members in this candidate group?
                    for candidate_group in candidate_groups:
                        # if node is now already in this group .... don't bother....
                        node_in_candidate_group: bool = node in candidate_group
                        friend_in_candidate_group: bool = friend in candidate_group
                        if node_in_candidate_group and friend_in_candidate_group:
                            continue

                        friends_with_all: bool = True
                        for candidate_friend in candidate_group:
                            candidate_friends_with_node: bool = candidate_friend in node_friends or candidate_friend == node
                            candidate_friends_with_friend: bool = candidate_friend in friend_friends or candidate_friend == friend
                            friends_with_all = friends_with_all and (candidate_friends_with_node and candidate_friends_with_friend)
                        if friends_with_all:
                            # huzzah .... we can add both node and friend into this group....
                            if not node_in_candidate_group:
                                candidate_group.add(node)
                                existing_common_groups.append(candidate_group)
                                if node not in groups_by_membership:
                                    groups_by_membership[node] = []
                                groups_by_membership[node].append(candidate_group)
                            if not friend_in_candidate_group:
                                candidate_group.add(friend)
                                if friend not in groups_by_membership:
                                    groups_by_membership[friend] = []
                                groups_by_membership[friend].append(candidate_group)
                            existing_common_groups.append(candidate_group)

            # if we are still not part of any existing group .... create a new group containing just our two pairs
            if len(existing_common_groups) == 0:
                new_group:  set[str] = set()
                new_group.add(node)
                new_group.add(friend)
                if node not in groups_by_membership:
                    groups_by_membership[node] = []
                groups_by_membership[node].append(new_group)
                if friend not in groups_by_membership:
                    groups_by_membership[friend] = []
                groups_by_membership[friend].append(new_group)
                groups.append(new_group)


    # pass three .... see if nodes need to be added into groups that they do not already belong to...
    largest_group_size: int = None
    largest_group: set[str] = None
    for group in groups:
        for node in nodes:
            if node in group:
                # ignore groups that we are already members of
                continue
            # check that this node has a direct connection to all members of this group.
            friends: list[str] = connections.get(node)
            friends_with_all: bool = True
            for candidate in group:
                friends_with_all = friends_with_all and (candidate in friends)
            if friends_with_all:
                group.add(node)
                if node not in groups_by_membership:
                    groups_by_membership[node] = []
                groups_by_membership[node].append(group)

        if largest_group_size is None or len(group) > largest_group_size:
            largest_group_size = len(group)
            largest_group = group

    sorted_friends: list[str] = sorted(largest_group)
    print(f'{sorted_friends=}')
    result: str = ','.join(sorted_friends)
    return result

def test():
    data_lines: list[str] = [
        'aa-bb', 'aa-cc', 'aa-dd',
        'bb-cc', 'cc-dd'
    ]
#    result = part_two_take_two(data_lines)


    data_lines: list[str] = [
        'aa-ab','aa-ac','aa-ad','aa-ae','aa-af',
        'ab-ac', 'ab-ad',
        'ac-ad', 'ac-ae',
        'ad-ae',
        'af-ag', 'af-ah', 'af-ai', 'af-aj',
        'ag-ah', 'ag-ai', 'ag-aj',
        'ah-ai', 'ah-aj',
        'ai-aj'
    ]
    result = part_two_take_two(data_lines)
    assert(result == 'af,ag,ah,ai,aj')
    return

def main(argv: list[str]):
    global very_verbose
    global verbose
    very_verbose = False
    verbose = False

    result = part_one(path='day_twenty_three_test_input.txt')
    print(f'part one: {result=} for test data')
    if result != 7:
        raise Exception(f'Test failed, expected 7 but instead got {result}')
    result = part_one(path='day_twenty_three_input.txt')
    print(f'part one: {result=} for actual data')

    data_lines: list[str] = read_lines_from_file(path='day_twenty_three_test_input.txt')
    result = part_two_take_two(data_lines)

    print(f'part two: {result=} for test data')
    if result != 'co,de,ka,ta':
        raise Exception(f'Test failed, expected co,de,ka,ta but instead got {result}')

    data_lines: list[str] = read_lines_from_file(path='day_twenty_three_input.txt')
    result  = part_two_take_two(data_lines)
    print(f'part two: {result=} for actual data')

    return 0



if __name__ == "__main__":
    exit_code: int = 0
    #test()
    exit_code = main(sys.argv)
    sys.exit(exit_code)