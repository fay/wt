# -*- coding:utf-8 -*-
class Context(object):
    def __init__(self):
        self.suffix = None
        self.lcp = None
        self.tokens = []
        self.terms = None
        self.docs = []
        #raw text or term list
        self.text = None
        #text中term list每个term的token type
        self.token_types = None
        self.term_doc_range = []
        self.title_field = []
class Token(object):
    def __init__(self):
        self.text = None
        self.freq = None
        self.doc_freq = None
        self.start = None
        self.offset = None
        # 所在doc中的索引
        self.doc_index = None
        # 所在doc的id
        self.doc = None
        self.global_index = None
        
    def __cmp__(self,other):
        return cmp(self.text,other.text)

class Term(object):
    def __init__(self):
        self.token = None
        self.tfidf = None
        self.field = None
