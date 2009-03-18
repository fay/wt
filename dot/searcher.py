# -*- coding: utf-8 -*-
import os
from lucene import \
        QueryParser,CJKAnalyzer, IndexSearcher, StandardAnalyzer, CLASSPATH, initVM, Hit, MultiFieldQueryParser, BooleanClause,BooleanQuery
STORE_DIR = os.path.dirname(__file__) + '/index'
initVM(CLASSPATH)

class Searcher(object):
    def __init__(self):
        self.searcher = IndexSearcher(STORE_DIR)
        self.analyzer = CJKAnalyzer()
        
        
    def __del__(self):
        self.searcher.close()
        
    def search(self, query):
        SHOULD = BooleanClause.Occur.SHOULD
        #MultiFieldQueryParser.setOperator(QueryParser.DEFAULT_OPERATOR_AND);
        parser1 = QueryParser('summary',self.analyzer)
        parser2 = QueryParser('title',self.analyzer)        
        parser1.setDefaultOperator(QueryParser.AND_OPERATOR)
        parser2.setDefaultOperator(QueryParser.AND_OPERATOR)
        q1 = parser1.parse(query)
        q2 = parser2.parse(query)
        boolQuery = BooleanQuery()
        boolQuery.add(q1,SHOULD)
        boolQuery.add(q2,SHOULD)
        hits = self.searcher.search(boolQuery)
        
        return hits
    def search_by_field(self,query,field='summary'):
        parser = QueryParser(field,self.analyzer)
        parser.setDefaultOperator(QueryParser.AND_OPERATOR)
        q = parser.parse(query)
        return self.searcher.search(q)
if __name__ == '__main__':
    searcher = Searcher()
    print 'hi'
    hits = searcher.search_by_field(u'web','category')
    print "%s total matching documents." % hits.length()
    print hits.length()
    for hit in hits:
            doc = Hit.cast_(hit).getDocument()
            print dir(doc)
            print 'title:', doc.get("author"), 'name:', doc.get("link")
            print Hit.cast_(hit).getScore()
        