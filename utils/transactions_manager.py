class TransactionsManager:

    class Paper:
        def __init__(self, authors, title):
            self.authors = authors
            self.title = title

    def __init__(self, papers_file_name, authors_mapping_filename, \
                title_terms_mapping_filename):
        papers_file = open(papers_file_name, "r")
        
        # {Author name, id}
        self.__authors_mapping = {}
        TransactionsManager.__parse_mapping(authors_mapping_filename, self.__authors_mapping)

        # {Title term, id}
        self.__title_terms_mapping = {}
        TransactionsManager.__parse_mapping(title_terms_mapping_filename, self.__title_terms_mapping)

        self.__papers = []

        for line in papers_file:
            # Note: Titles are guaranteed to not have commas
            line_as_lst = line.split(',')
            authors = line_as_lst[ : -1]
            author_ids = set()

            for author in authors:
                author_ids.add(self.__authors_mapping[author])
            
            title = line_as_lst[-1]
            term_ids = []
            for title_term in title.split():
                term_ids.append(self.__title_terms_mapping[title_term])

            self.__papers.append(TransactionsManager.Paper(author_ids, term_ids))

        papers_file.close()
    
    def find_author_pattern_support(self, author_pattern):
        support = 0
        for paper in self.__papers:
            # NOTE: This wasn't working -- if author_pattern.issubset(paper.authors)
            is_subset = True
            for author in paper.authors:
                if author not in author_pattern:
                    is_subset = False
                    break
            if is_subset:
                support += 1
        return support

    def get_number_of_transactions(self):
        return len(self.__papers)

    @staticmethod
    def __parse_mapping(mapping_filename, mapping):
        mapping_file = open(mapping_filename, "r")

        for line in mapping_file:
            id_word_lst = line.strip().split()
            assert len(id_word_lst) == 2
            assert id_word_lst[1] not in mapping
            mapping[id_word_lst[1]] = int(id_word_lst[0])

        mapping_file.close()

if __name__ == "__main__":
    transactions = TransactionsManager("data/data.csv", "data/author_id_mappings.txt", "data/title_term_id_mappings.txt")