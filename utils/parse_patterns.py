def parse_file_into_patterns(pattern_file_name):
    '''
    Parse a file generated via build_frequent_patterns.py into a list of patterns
    
    @param pattern_file_name: string    Input file name
        Format assumption: item_id_1 item_id_2 item_id_3 #SUP support
        One pattern/line
    @return list(list(int)), representing all patterns parsed from file where each inner list
        is a pattern of item ids (recall that words are being mapped to integer ids)
    '''
    pattern_file = open(pattern_file_name, "r")
    
    patterns = []
    for line in pattern_file:
        sup_ind = line.rfind("#") # Ignore the comment telling us what the support is
        assert sup_ind != -1
        pattern_lst = line[ : sup_ind].split()
        patterns.append([int(item) for item in pattern_lst])

    pattern_file.close()
    return patterns

def write_patterns_to_file(pattern_file_name, patterns):
    '''
    Write a given list of patterns to a file
    Format: item_id_1 item_id_2 item_id_3
        One pattern/line
    
    @param pattern_file_name: string    Output file name
    @param patterns: list(list(int))    All patterns parsed, where each inner list
        is a pattern of integers
    '''
    pattern_file = open(pattern_file_name, "w")
    for pattern in patterns:
        pattern_file.write("%s\n" % ' ' .join([str(item) for item in pattern]))
    pattern_file.close()