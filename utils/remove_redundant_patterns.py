'''
NOTE: Each pattern is stored as a list of integers (@see parse_patterns.py
for parsing implementation)
'''

def calculate_jaccard_distance(pattern_1, pattern_2):
    pattern_1_set = set(pattern_1)
    pattern_2_set = set(pattern_2)
    intersection_len = len(pattern_1_set.intersection(pattern_2_set))
    union_len = len(pattern_1_set.union(pattern_2_set))
    return 1 - intersection_len / union_len

def find_one_pass_microclustering_patterns(patterns):
    # Patterns are denoted by their index
    # Jaccard dists are keyed via tuples -- (p1_ind, p2_ind) such that 
    # p1_ind < p2_ind
    jaccard_dists = {}
    num_patterns = len(patterns)
    for i in range(num_patterns):
        for j in range(i, num_patterns):
            jaccard_dists[ (i ,j) ] = calculate_jaccard_distance(patterns[i], patterns[j])

from parse_patterns import parse_file_into_patterns
patterns = parse_file_into_patterns("data/toy_title_patterns.txt")
find_one_pass_microclustering_patterns(patterns)