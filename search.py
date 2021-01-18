import nltk
import unicodedata
import math
from collections import defaultdict

nltk.download('punkt') 
nltk.download('rslp')

path = 'elo7_recruitment_dataset.csv'

class InvertedIndex:
    """
    Creates an inverted index object from the given dataset.
    """
    def __init__(self, data_path, normalization=True, accents=False, stemming=True,
                 remove_stopwords=True, force_reindex=False):
        self.normalization = normalization
        self.accents = accents
        self.stemming = stemming
        self.remove_stopwords = remove_stopwords
        self.dictionary = defaultdict(list)
        self.doc_count = 0
        
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
        
        print('Done!')
                
    def index_product(self, product_id, title):
        tokens = nltk.word_tokenize(title, language='portuguese')
        tokens = text_processing(tokens, self.normalization, self.accents, self.stemming, self.remove_stopwords)

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
        except:
            print('Could not load index.')
    
    def save_index(self, path='products.ind'):
        try:
            "Settings file + index"
            save_dict = {'index': self.dictionary,
                         'normalization': self.normalization,
                         'accents': self.accents,
                         'stemming': self.stemming,
                         'remove_stopwords': self.remove_stopwords}

            with open(path, 'wb') as f:
                pickle.dump(save_dict, f)
        except:
            print('Could not save index.')


class BM25Ranker:
    def __init__(self, parameters={'k1': 1.2, 'b': 0.75}):
        self.k1 = parameters['k1']
        self.b = parameters['b']

    def rank(self, query):
        pass

class Search:
    def __init__(self, inverted_index, ranker):
        self.inverted_index = inverted_index
        self.ranker = ranker


# Helper functions                

def text_processing(tokens,  normalization, accents, stemming, 
                    remove_stopwords):
    "Performs common text preprocessing operations."    
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
    """
    Removes Portuguese accents from input text.
    Example accents: êóàãç
    """
    if type(text) == list:
        return [unicodedata.normalize('NFKD', token).encode('ascii', 'ignore').decode('utf-8') for token in text]
    else:
        return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')

def idf(df_term, total_doc_count):
    """
    Computes IDF according to Lucene's implementation.
    Reference: 
    https://www.elastic.co/blog/practical-bm25-part-2-the-bm25-algorithm-and-its-variables
    """
    return math.log(1 + ((total_doc_count - df_term + 0.5) / (df_term + 0.5)))