import nltk
import unicodedata
import math
import pickle
from statistics import mean
from collections import defaultdict

nltk.download('punkt') 
nltk.download('rslp')

path = 'elo7_recruitment_dataset.csv'

class InvertedIndex:
    """Creates an inverted index object from the given dataset."""
    def __init__(self, data_path, normalization=True, accents=False, stemming=True,
                 remove_stopwords=True, force_reindex=False):
        self.normalization = normalization
        self.accents = accents
        self.stemming = stemming
        self.remove_stopwords = remove_stopwords
        self.dictionary = defaultdict(list)
        self.doc_count = 0
        self.doc_lengths = {}

        if not force_reindex:
            print('Loading index...')
            self.load_index()
        if not bool(self.dictionary): # If index is still empty (force_reindex or failed load)
            print('Building index...')
            with open(path, 'r', encoding='utf-8') as f:
                next(f) # Skip header
                prod_set = set()
                for line in f.readlines():
                    entry = line.rstrip().split(',')
                    product_id = entry[0]
                    if product_id not in prod_set:
                        prod_set.add(product_id)
                        title = entry[5]
                        self.doc_count += 1
                        self.index_product(product_id, title)
        
        self.avg_doc_length = mean(self.doc_lengths.values())
        print('Done!')
                
    def index_product(self, product_id, title):
        """Indexes a single product given its title."""
        tokens = text_processing(title, self.normalization, self.accents, self.stemming, self.remove_stopwords)
        self.doc_lengths[product_id] = len(tokens)

        for token in tokens:                 
            product_list = [product[0] for product in self.dictionary[token]]

            if product_id not in product_list:
                # Store [id, term_frequency]
                self.dictionary[token].append([product_id, 1]) 
            else:
                # Increment term frequency
                lookup_index = product_list.index(product_id)
                self.dictionary[token][lookup_index][1] += 1
                
        
    def load_index(self, path='products.ind'):
        try:
            with open(path, 'rb') as f:
                data = pickle.load(f)
                self.dictionary = data['index']
                self.normalization = data['normalization']
                self.accents = data['accents']
                self.stemming = data['stemming']
                self.remove_stopwords = data['remove_stopwords']
                self.doc_count = data['doc_count']
                self.doc_lengths = data['doc_lengths']
                self.avg_doc_length = data['avg_doc_length']
        except:
            print('Could not load index.')
    
    def save_index(self, path='products.ind'):
        try:
            "Settings file + index"
            save_dict = {'index': self.dictionary,
                         'normalization': self.normalization,
                         'accents': self.accents,
                         'stemming': self.stemming,
                         'remove_stopwords': self.remove_stopwords,
                         'doc_count': self.doc_count,
                         'doc_lengths': self.doc_lengths,
                         'avg_doc_length': self.avg_doc_length}

            with open(path, 'wb') as f:
                pickle.dump(save_dict, f)
        except:
            print('Could not save index.')


class BM25Ranker:
    """Okapi BM25 model inspired by Lucene's implementation.

    Reference: 
    https://www.elastic.co/blog/practical-bm25-part-2-the-bm25-algorithm-and-its-variables
    """

    def __init__(self, parameters={'k1': 1.2, 'b': 0.75}): 
        self.k1 = parameters['k1']
        self.b = parameters['b']

    def score(self, tf, df, doc_count, doc_len, avg_doc_len):
        idf = math.log(1 + ((doc_count - df + 0.5) / (df + 0.5)))
        num = tf * (self.k1 + 1)
        den = tf + (self.k1 * (1 - self.b + (self.b * doc_len / avg_doc_len)))
        return idf * num / den


class Search:
    def __init__(self, inverted_index, ranker):
        self.inverted_index = inverted_index
        self.ranker = ranker

    def rank_documents(self, tokens):
        # Global "constant" values
        doc_count = self.inverted_index.doc_count
        avg_doc_len = self.inverted_index.avg_doc_length
        
        #Scoring
        document_scores = defaultdict(float)
        for term in tokens:
            if self.inverted_index.dictionary[term]:
                term_postings = self.inverted_index.dictionary[term]
                df = len(term_postings)
                for product_id, tf in term_postings:
                    doc_len = self.inverted_index.doc_lengths[product_id]
                    score = self.ranker.score(tf, df, doc_count, doc_len, avg_doc_len)
                    document_scores[product_id] += score
        
        return sorted(list(document_scores.items()), key=lambda x:x[1], reverse=True)

    def process_query(self, query):
        """Processes query with the same settings as inverted index."""
        tokens = text_processing(query, self.inverted_index.normalization, self.inverted_index.accents,
                                 self.inverted_index.stemming, self.inverted_index.remove_stopwords)

        return self.rank_documents(tokens)



# Helper functions                

def text_processing(text, normalization, accents, stemming, 
                    remove_stopwords):
    """Performs common text preprocessing operations."""
    tokens = nltk.word_tokenize(text, language='portuguese')
    
    # Handling hyphenization
    for token in tokens:
        hyphen_split = token.split('-')
        for new_token in hyphen_split:
            if new_token not in tokens:
                tokens.append(new_token)

    if normalization:
            tokens = [token.lower() for token in tokens if token.isalpha()]
    if remove_stopwords:
        stopwords = set(nltk.corpus.stopwords.words('portuguese'))
        tokens = [token.lower() for token in tokens if token not in (stopwords)]
    if not accents:
        tokens = remove_accents(tokens)
    if stemming:
        stemmer = nltk.stem.RSLPStemmer()
        tokens = [stemmer.stem(token) for token in tokens]
    return tokens

def remove_accents(text):
    """Removes Portuguese accents from input text.

    Example accents: êóàãç
    """
    if type(text) == list:
        return [unicodedata.normalize('NFKD', token).encode('ascii', 'ignore').decode('utf-8') for token in text]
    else:
        return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')