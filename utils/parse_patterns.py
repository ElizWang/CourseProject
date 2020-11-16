def parse_file_into_patterns(pattern_file_name):
    pattern_file = open(pattern_file_name, "r")
    
    patterns = []
    for line in pattern_file:
        sup_ind = line.rfind("#") # Ignore the comment telling us what the support is
        assert sup_ind != -1
        pattern_lst = line[ : sup_ind].split()
        patterns.append([int(item) for item in pattern_lst])

    pattern_file.close()
    return patterns