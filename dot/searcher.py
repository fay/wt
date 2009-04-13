# -*- coding: utf-8 -*-
import os
#from dot.categorycomparator import CategoryComparatorSource
from dot.catfilter import CatFilter
from lucene import \
        QueryParser,CJKAnalyzer, IndexSearcher, StandardAnalyzer, CLASSPATH,\
        initVM, Hit, MultiFieldQueryParser, BooleanClause,BooleanQuery,Sort,SortField
STORE_DIR = os.path.dirname(__file__) + '/index'
initVM(CLASSPATH)

class Searcher(object):
    def __init__(self):
        self.searcher = IndexSearcher(STORE_DIR)
        self.analyzer = CJKAnalyzer()
        self.catfilter = CatFilter()
        
    def __del__(self):
        self.searcher.close()
        
    def search(self, query,category_id=None):
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
        
        #camp = CategoryComparatorSource(query)
        #sortfield = SortField("link", camp)
        #sort = Sort(sortfield)
        if category_id:
            self.catfilter.query = query
            self.catfilter.category_id = category_id
            print query,category_id,type(category_id)
            hits = self.searcher.search(boolQuery,self.catfilter)
        else:
            hits = self.searcher.search(boolQuery)
        return hits
    def search_by_field(self,query,field='summary'):
        parser = QueryParser(field,self.analyzer)
        parser.setDefaultOperator(QueryParser.AND_OPERATOR)
        q = parser.parse(query)
        return self.searcher.search(q)
    
def test():
    searcher = Searcher()
    print 'hi'
    hits = searcher.search('java',5026)
    print "%s total matching documents." % hits.length()
    for hit in hits:
            doc = Hit.cast_(hit).getDocument()
            print 'title:', doc.get("author"), 'name:', doc.get("link")
            print Hit.cast_(hit).getScore()
if __name__ == '__main__':
    test()