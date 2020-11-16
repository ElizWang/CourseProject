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

def find_one_pass_microclustering_patterns(patterns, dist_thresh = 0.9):
    # Patterns are denoted by their index
    # Jaccard dists are keyed via tuples -- (p1_ind, p2_ind) such that 
    # p1_ind < p2_ind
    jaccard_dists = {}
    num_patterns = len(patterns)
    for i in range(num_patterns):
        for j in range(i, num_patterns):
            jaccard_dists[ (i ,j) ] = calculate_jaccard_distance(patterns[i], patterns[j])

    def get_jaccard_dist(id_1, id_2):
        return jaccard_dists[ (min(id_1, id_2), max(id_1, id_2)) ]

    # Stores pattern IDs rather than pattern lists
    clusters = {}
    curr_cluster_id = 0

    for pattern_id in range(num_patterns):
        min_dist_cluster_id = float("inf")
        min_dist = float("inf")

        for cluster_num in clusters:
            cluster_pattern_ids = clusters[cluster_num]
            max_pattern_cluster_dist = max(get_jaccard_dist(pattern_id, cluster_pattern_id)\
                for cluster_pattern_id in cluster_pattern_ids)

            if min_dist > max_pattern_cluster_dist:
                min_dist = max_pattern_cluster_dist
                min_dist_cluster_id = cluster_num

        if min_dist < dist_thresh:
            clusters[min_dist_cluster_id].append(pattern_id)
        else:
            clusters[curr_cluster_id] = [pattern_id]
            curr_cluster_id += 1
    
    min_intra_dist_patterns = []

    for cluster_num in clusters:
        cluster_pattern_ids = clusters[cluster_num]
        min_intra_cluster_pattern_id = float("inf")
        min_avg_dist = float("inf")

        for pattern_id in cluster_pattern_ids:
            avg_intra_cluster_dist = sum(get_jaccard_dist(pattern_id, cluster_pattern_id)\
                for cluster_pattern_id in cluster_pattern_ids) / len(cluster_pattern_ids)

            if min_avg_dist > avg_intra_cluster_dist:
                min_avg_dist = avg_intra_cluster_dist
                min_intra_cluster_pattern_id = pattern_id

        min_intra_dist_patterns.append(min_intra_cluster_pattern_id)
    print(min_intra_dist_patterns)

from parse_patterns import parse_file_into_patterns
patterns = parse_file_into_patterns("data/toy_title_patterns.txt")
find_one_pass_microclustering_patterns(patterns)