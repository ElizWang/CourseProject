import sys
import os
sys.path.insert(1, os.path.join('utils', 'frequent_pattern_mining'))

from build_frequent_patterns import FrequentPatternBuilder
from parse_patterns import parse_file_into_patterns, write_patterns_to_file

'''
Utility methods for 
* Eliminating redundancy using one pass microclustering
* Eliminating redundancy using hierarchical microclustering
'''

MINIMAL_TITLE_TERMS_FILENAME = os.path.join('data', 'minimal_title_term_patterns.txt')

def calculate_jaccard_distance(pattern_1, pattern_2):
    '''
    Computes Jaccard distance based on this formula:
        1 - |intersection(pattern 1, pattern 2)| / |union(pattern 1, pattern 2)|

    @param pattern_1: list(int)     A pattern parsed from an output file generated by
        build_frequent_patterns.py
    @param pattern_2: list(int)     A pattern parsed from an output file generated by
        build_frequent_patterns.py
    @return a float representing the Jaccard distance between the two patterns
    '''
    pattern_1_set = set(pattern_1)
    pattern_2_set = set(pattern_2)
    intersection_len = len(pattern_1_set.intersection(pattern_2_set))
    union_len = len(pattern_1_set.union(pattern_2_set))
    return 1 - intersection_len / union_len

def compute_jaccard_distance_matrix(patterns):
    '''
    Computes a triangular matrix of Jaccard distances

    @param patterns: list(list(int))    List of parsed frequent patterns
    @return dict( (int, int), float ), keyed by pattern IDs (aka pattern indices
        (p1_ind, p2_ind) such that p1_ind <= p2_ind) whose values are Jaccard 
        distances
    '''
    jaccard_dists = {}
    num_patterns = len(patterns)
    for i in range(num_patterns):
        for j in range(i, num_patterns):
            jaccard_dists[ (i ,j) ] = calculate_jaccard_distance(patterns[i], patterns[j])
    return jaccard_dists

def get_jaccard_dist(jaccard_dists, id_1, id_2):
    '''
    Get Jaccard distance given two pattern ids (id_1 doesn't have to be leq id_2)

    @param id_1: int       Pattern id 1
    @param id_2: int       Pattern id 2
    @return Jaccard distance between these 2 patterns
    '''
    return jaccard_dists[ (min(id_1, id_2), max(id_1, id_2)) ]

def compute_representative_patterns_from_clusters(patterns, clusters, jaccard_dists):
    '''
    Compute representative patterns given clusters -- one pattern is computed per
    cluster (namely, the pattenr with the minimum average intracluster distance is
    selected)

    @param clusters: dict( int, Collection(int))    Dictionary of cluster-ID (integer)
        to pattern ID mappings -- denotes which patterns belong to which clusters
    @param jaccard_dists: dict( (int, int), float ) Dict keyed by pattern IDs (aka pattern 
        indices (p1_ind, p2_ind) such that p1_ind <= p2_ind) whose values are Jaccard 
        distances
    @return list(list(int)), list of representive patterns, aka P' in the algorithm
    '''
    min_intra_dist_patterns = []

    for cluster_num in clusters:
        cluster_pattern_ids = clusters[cluster_num]
        min_intra_cluster_pattern_id = float("inf")
        min_avg_dist = float("inf")

        for pattern_id in cluster_pattern_ids:
            avg_intra_cluster_dist = sum(get_jaccard_dist(jaccard_dists, pattern_id, cluster_pattern_id)\
                for cluster_pattern_id in cluster_pattern_ids) / len(cluster_pattern_ids)

            if min_avg_dist > avg_intra_cluster_dist:
                min_avg_dist = avg_intra_cluster_dist
                min_intra_cluster_pattern_id = pattern_id

        min_intra_dist_patterns.append(patterns[min_intra_cluster_pattern_id])
    return min_intra_dist_patterns

def find_hierarchical_microclustering_patterns(patterns, dist_thresh = 0.7):
    '''
    Computes a list of non-redundant patterns using the hierarchical microclustering
    algorithm

    @param patterns: list(list(int)):   A list of patterns, where each pattern is 
        a list(int)
    @param dist_thresh: float           Distance threshold, used when deciding whether
        to place a pattern in an existing cluster or create a new cluster for it
    @return list(list(int)), list of representive patterns

    TODO TODO TODO: Not sure if this algorithm is right -- the psuedocode in the paper
    doesn't explain:
    * How we should compute d_st after the first iteration (when we've already merged a
    cluster, so it wouldn't make sense to use the distance between individual patterns again,
    because that will never change). We're computing the distances between clusters instead
    * What d_uv is used for
    * How d is updated (we're treating this as the smallest max inter-cluster distance)
    '''
    clusters = {}
    for ind in range(len(patterns)):
        clusters[ind] = set([ind])

    jaccard_dists = compute_jaccard_distance_matrix(patterns)
    min_dist = min(jaccard_dists[id_pair] for id_pair in jaccard_dists)

    while min_dist < dist_thresh:
        if len(clusters) == 1:
            break

        min_dist = float("inf")
        smaller_cluster_id = None
        larger_cluster_id = None
        
        for cluster_id_i in clusters:
            for cluster_id_j in clusters:
                # We only have to compute the distance when cluster_id_i < cluster_id_j
                # to avoid having to compute the same distance twice
                if cluster_id_i >= cluster_id_j:
                    continue

                max_cluster_dist = 0
                for pattern_i in clusters[cluster_id_i]:
                    for pattern_j in clusters[cluster_id_j]:
                        max_cluster_dist = max(max_cluster_dist, get_jaccard_dist(jaccard_dists, pattern_i, pattern_j))

                if min_dist > max_cluster_dist:
                    min_dist = max_cluster_dist
                    smaller_cluster_id = cluster_id_i
                    larger_cluster_id = cluster_id_j

        clusters[smaller_cluster_id] = clusters[smaller_cluster_id].union(clusters[larger_cluster_id])
        del clusters[larger_cluster_id]

    min_intra_dist_patterns = compute_representative_patterns_from_clusters(patterns, clusters, jaccard_dists)
    print(min_intra_dist_patterns)
    return min_intra_dist_patterns

def find_one_pass_microclustering_patterns(patterns, dist_thresh = 0.9):
    '''
    Computes a list of non-redundant patterns using the one-pass microclustering
    algorithm

    @param patterns: list(list(int)):   A list of patterns, where each pattern is 
        a list(int)
    @param dist_thresh: float           Distance threshold, used when deciding whether
        to place a pattern in an existing cluster or create a new cluster for it
    @return list(list(int)), list of representive patterns
    '''
    jaccard_dists = compute_jaccard_distance_matrix(patterns)

    # Stores pattern IDs rather than pattern lists
    clusters = {}
    curr_cluster_id = 0

    for pattern_id in range(len(patterns)):
        min_dist_cluster_id = float("inf")
        min_dist = float("inf")

        for cluster_num in clusters:
            cluster_pattern_ids = clusters[cluster_num]
            max_pattern_cluster_dist = max(get_jaccard_dist(jaccard_dists, pattern_id, cluster_pattern_id)\
                for cluster_pattern_id in cluster_pattern_ids)

            if min_dist > max_pattern_cluster_dist:
                min_dist = max_pattern_cluster_dist
                min_dist_cluster_id = cluster_num

        if min_dist < dist_thresh:
            clusters[min_dist_cluster_id].append(pattern_id)
        else:
            clusters[curr_cluster_id] = [pattern_id]
            curr_cluster_id += 1
    
    min_intra_dist_patterns = compute_representative_patterns_from_clusters(patterns, clusters, jaccard_dists)
    return min_intra_dist_patterns

if __name__ == "__main__":
    title_patterns = parse_file_into_patterns(FrequentPatternBuilder.TITLE_TERMS_OUTPUT_FILE_PATH)
    minimal_patterns = find_one_pass_microclustering_patterns(title_patterns, 0.5)
    write_patterns_to_file(MINIMAL_TITLE_TERMS_FILENAME, minimal_patterns)