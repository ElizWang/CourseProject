import mutual_information_manager

'''
Encapsulates all papers (aka data.csv) and provides utility methods
'''
class TransactionsManager:

    '''
    Represents a single paper
    '''
    class Paper:
        def __init__(self, authors, title):
            '''
            @param
                authors: Collection(int)    Collection of author ids
                title: list(int)            Ordered list of title word ids

            IMPORTANT: Both collections must store integers (to correctly compute the
            support of a certain pattern)
            '''
            self.authors = authors
            self.title = title

    def __init__(self, papers_file_name, authors_mapping_filename, \
                title_terms_mapping_filename):
        '''
        Parses and stores the author-id mapping, the title terms-id mapping, and
        a list of all papers

        @param
            papers_file_name: string                data.csv file path
            authors_mapping_filename: string        file path to author-id mapping file
            title_terms_mapping_filename: string    file path to title term-id mapping file
        '''
        papers_file = open(papers_file_name, "r", encoding='utf-8')

        self.__authors_id_mapping = {}
        self.__id_authors_mapping = {}
        TransactionsManager.__parse_mapping(authors_mapping_filename, \
            self.__authors_id_mapping, self.__id_authors_mapping)

        self.__title_terms_id_mapping = {}
        self.__id_title_terms_mapping = {}
        TransactionsManager.__parse_mapping(title_terms_mapping_filename, \
            self.__title_terms_id_mapping, self.__id_title_terms_mapping)

        self.__papers = []

        for line in papers_file:
            # Note: Titles are guaranteed to not have commas
            line_as_lst = line.split(',')
            authors = line_as_lst[ : -1]
            author_ids = set()

            for author in authors:
                author_ids.add(self.__authors_id_mapping[author])

            title = line_as_lst[-1]
            term_ids = []
            for title_term in title.split():
                term_ids.append(self.__title_terms_id_mapping[title_term])
            self.__papers.append(TransactionsManager.Paper(author_ids, term_ids))

        papers_file.close()

    def compute_title_context_models(self, patterns):
        '''
        Computes context models for each paper's title terms against title patterns
        @param
            patterns: list(list(int))         List of all frequent title patterns
        @return
            context_models: list(list(float)) List of all context models, one per paper
        '''
        context_models = []

        num_transactions = self.get_number_of_transactions()
        for paper_id in range(num_transactions):
            paper_context_model = []

            for pattern in patterns:
                paper_titles = self.get_paper_title_terms(paper_id)
                mutual_info = \
                    mutual_information_manager.MutualInformationManager.compute_mutual_information_for_pattern_pair(self, \
                        mutual_information_manager.MutualInformationManager.PatternType.TITLE_TITLE, \
                             pattern, paper_titles)
                paper_context_model.append(mutual_info)

            context_models.append(paper_context_model)
        return context_models

    def compute_author_context_models(self, patterns):
        '''
        Computes context models for each paper's authors against author patterns
        @param
            patterns: list(list(int))         List of all frequent author patterns
        @return
            context_models: list(list(float)) List of all context models, one per paper
        '''
        context_models = []

        num_transactions = self.get_number_of_transactions()
        for paper_id in range(num_transactions):
            paper_context_model = []

            for pattern in patterns:
                paper_authors = self.get_paper_authors(paper_id)
                mutual_info = \
                    mutual_information_manager.MutualInformationManager.compute_mutual_information_for_pattern_pair(self, \
                        mutual_information_manager.MutualInformationManager.PatternType.AUTHOR_AUTHOR, \
                             pattern, paper_authors)
                paper_context_model.append(mutual_info)

            context_models.append(paper_context_model)
        return context_models

    def find_title_pattern_transactions_ids(self, title_pattern):
        '''
        Find transactions that have title pattern as a subset

        @param:
            title_pattern: list(int)     Ordered list of title ids
        '''
        # https://stackoverflow.com/questions/24017363/how-to-test-if-one-string-is-a-subsequence-of-another
        def is_subseq(x, y):
            it = iter(y)
            return all(any(c == ch for c in it) for ch in x)

        title_transactions = set()
        for ind, paper in enumerate(self.__papers):
            # Title patterns are sequential so we need to ensure that the order is there
            # Check that the title is a subsequence of paper.title
            if is_subseq(title_pattern, paper.title):
                title_transactions.add(ind)
        return title_transactions

    def find_author_pattern_transactions_ids(self, author_pattern):
        '''
        Find transactions that have author pattern as a subset

        @param:
            author_pattern: Collection(int)     Collection of author ids
        '''
        author_transactions = set()
        for ind, paper in enumerate(self.__papers):
            if author_pattern.issubset(paper.authors):
                author_transactions.add(ind)
        return author_transactions

    def get_author_name(self, author_id):
        return self.__id_authors_mapping[author_id]

    def get_title_term(self, title_id):
        return self.__id_title_terms_mapping[title_id]

    def get_paper_authors(self, paper_id):
        return self.__papers[paper_id].authors

    def get_paper_title_terms(self, paper_id):
        return self.__papers[paper_id].title

    def get_number_of_transactions(self):
        '''
        Returns the number of papers, aka the number of transactions
        '''
        return len(self.__papers)

    @staticmethod
    def __parse_mapping(mapping_filename, word_id_mapping, id_word_mapping):
        '''
        Parses a mapping from a file into a dictionary

        @param
            mapping_filename: string                Filename containing id-word mapping
            word_id_mapping: dict(string, int)      Mapping dict from word to id to be populated
            word_id_mapping: dict(string, int)      Mapping dict from id to word to be populated
        '''
        mapping_file = open(mapping_filename, "r", encoding='utf-8')

        for line in mapping_file:
            id_word_lst = line.strip().split()
            assert len(id_word_lst) == 2
            assert id_word_lst[1] not in word_id_mapping

            word_id = int(id_word_lst[0])
            word = id_word_lst[1]
            word_id_mapping[word] = word_id
            id_word_mapping[word_id] = word
        mapping_file.close()

if __name__ == "__main__":
    transactions = TransactionsManager("data/data.csv", "data/author_id_mappings.txt", "data/title_term_id_mappings.txt")
