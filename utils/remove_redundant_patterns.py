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