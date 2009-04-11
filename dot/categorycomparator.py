from math import sqrt
from lucene import Term, IndexReader, \
    PythonSortComparatorSource, PythonScoreDocComparator, Double
from apps.wantown import dao
from apps.wantown.models import Entry
from math import sqrt
from unittest import TestCase

from lucene import \
    WhitespaceAnalyzer, IndexSearcher, Term, TermQuery, RAMDirectory, \
    Document, Field, IndexWriter, Sort, SortField, FieldDoc, Double,CJKAnalyzer,QueryParser,FieldDoc
#
# A SortComparatorSource implementation
#

class CategoryComparatorSource(PythonSortComparatorSource):

    def __init__(self,query):
        super(CategoryComparatorSource, self).__init__()
        self.query = query
        
    def newComparator(self, reader, fieldName):
        #
        # A ScoreDocComparator implementation
        # 
        class CategoryScoreDocLookupComparator(PythonScoreDocComparator):

            def __init__(self, reader, fieldName,query):
                super(CategoryScoreDocLookupComparator, self).__init__()
                self.query = query
                self.reader = reader
            def compare(self, i, j):
                """
                fielddoc = FieldDoc.cast_(i)
                link = self.reader.document(fielddoc.doc).get('link')
                entry = dao.get_by_link(link,Entry)
                count = dao.get_category_count_by_entry(self.query,entry)
                
                fielddoc = FieldDoc.cast_(j)
                link1 = self.reader.document(fielddoc.doc).get('link')
                entry1 = dao.get_by_link(link1,Entry)
                count1 = dao.get_category_count_by_entry(self.query,entry1)
                if count < count1:
                    return -1
                if count > count1:
                    return 1
                """
                return 0

            def sortValue(self, i):
                fielddoc = FieldDoc.cast_(i)
                link = self.reader.document(fielddoc.doc).get('link')
                entry = dao.get_by_link(link,Entry)
                count = dao.get_category_count_by_entry(self.query,entry)
                
                return Double(count)

            def sortType(self):
                return SortField.FLOAT
        comp = CategoryScoreDocLookupComparator(reader, fieldName,self.query)
        a = PythonScoreDocComparator.cast_(comp)
        print dir(a)
        return comp

    def __str__(self):
        return query
    
# ====================================================================
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
# ====================================================================

from math import sqrt
from lucene import SortField, Term, IndexReader, \
    PythonSortComparatorSource, PythonScoreDocComparator, Double

#
# A SortComparatorSource implementation
#

class DistanceComparatorSource(PythonSortComparatorSource):

    def __init__(self, x, y):
        super(DistanceComparatorSource, self).__init__()
        self.x = x
        self.y = y

    def newComparator(self, reader, fieldName):

        #
        # A ScoreDocComparator implementation
        # 
        class DistanceScoreDocLookupComparator(PythonScoreDocComparator):

            def __init__(self, reader, fieldName, x, y):
                super(DistanceScoreDocLookupComparator, self).__init__()
                enumerator = reader.terms(Term(fieldName, ""))
                self.distances = distances = [0.0] * reader.numDocs()


            def compare(self, i, j):
                print 'compare'
                return 0

            def sortValue(self, i):
                import random
                return Double(random.random())

            def sortType(self):
                return SortField.FLOAT

        return DistanceScoreDocLookupComparator(reader, fieldName,
                                                self.x, self.y)

    def __str__(self):

        return "Distance from ("+x+","+y+")"
    
def dumpDocs(self, sort, docs):

        print "Sorted by:", sort

        for scoreDoc in docs.scoreDocs:
            fieldDoc = FieldDoc.cast_(scoreDoc)
            distance = Double.cast_(fieldDoc.fields[0]).doubleValue()
            doc = self.searcher.doc(fieldDoc.doc)
            print "  %(name)s @ (%(location)s) ->" %doc, distance
        
       
def a():
    import os
    from lucene import CJKAnalyzer,Hit
    dire = os.path.dirname(__file__) + '/index'

    analyzer = CJKAnalyzer()
    searcher = IndexSearcher(dire)
    query = QueryParser('summary',analyzer).parse('java')#TermQuery(Term("type", "restaurant"))
    sort = Sort(SortField("locatisdon", CategoryComparatorSource('java')))

    hits = searcher.search(query,sort)
    print len(hits)
    i = 0
    for hit in hits:
            i+=1
            if i== 10:
                break
            doc = Hit.cast_(hit).getDocument()
            print 'title:', doc.get("author"), 'name:', doc.get("link")
            print Hit.cast_(hit).getScore()
    searcher.close()