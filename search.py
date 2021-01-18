import nltk
import unicodedata
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
        print('Building index...')
        # Text processing settings
        self.normalization = normalization
        self.accents = accents
        self.stemming = stemming
        self.remove_stopwords = remove_stopwords
        self.dictionary = defaultdict(list)
        
        # Indexing
        with open(path, 'r', encoding='utf-8') as f:
            next(f) # Skip header
            for line in f.readlines():
                entry = line.rstrip().split(',')
                product_id = entry[0]
                title = entry[5]
                self.index_product(product_id, title)
                
        print('Done!')
                
    def index_product(self, product_id, title):
        tokens = nltk.word_tokenize(title, language='portuguese')
        if self.normalization:
            tokens = [token.lower() for token in tokens if token.isalpha()]
        if self.remove_stopwords:
            stopwords = set(nltk.corpus.stopwords.words('portuguese'))
            tokens = [token.lower() for token in tokens if token not in (stopwords)]
        if not self.accents:
            tokens = remove_accents(tokens)
        if self.stemming:
            stemmer = nltk.stem.RSLPStemmer()
            tokens = [stemmer.stem(token) for token in tokens]

        for token in tokens:                 
            product_list = [product[0] for product in self.dictionary[token]]

            if product_id not in product_list:
                # Store [id, term_frequency]
                self.dictionary[token].append([product_id, 1]) 
            else:
                # Increment term frequency
                lookup_index = product_list.index(product_id)
                self.dictionary[token][lookup_index][1] += 1
                
        
    def load_index(self, path):
        pass
    
    def save_index(self, path):
        pass
                
# Helper functions                
                
def remove_accents(text):
    """
    Removes Portuguese accents from input text.
    Example accents: êóàãç
    """
    if type(text) == list:
        return [unicodedata.normalize('NFKD', token).encode('ascii', 'ignore').decode('utf-8') for token in text]
    else:
        return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')