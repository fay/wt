class Context(object):
    def __init__(self):
        self.tokens = None
        self.terms = None
        self.docs = None
        
class Token(object):
    def __init__(self):
        self.text = None
        self.freq = None
        self.doc_freq = None
        self.start = None
        self.offset = None

class Term(object):
    def __init__(self):
        self.token = None
        self.tfidf = None
        self.field = None
        self.doc = None
        self.doc_index = None
        self.global_index = None