def compute_cosine_similarity(context_vec_1, context_vec_2):
    assert len(context_vec_1) == len(context_vec_2)
    dot_product = 0

    for ind in range(len(context_vec_1)):
        dot_product += context_vec_1[ind] * context_vec_2[ind]
    
    def compute_distance(context_vec):
        dist = 0
        for el in context_vec:
            dist += el ** 2
        return dist ** 0.5
    
    return dot_product / compute_distance(context_vec_1) / compute_distance(context_vec_2)