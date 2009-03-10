# -*- coding: utf-8 -*-
import lucene,os
from apps.wantown.models import Entry
STORE_DIR = os.path.dirname(__file__) + '/index'
try:
    lucene.initVM(lucene.CLASSPATH)
except Exception ,e:
    print e
class Indexer(object):
    def __init__(self):
        self.store = lucene.FSDirectory.getDirectory(STORE_DIR, True)
        self.analyzer = lucene.StandardAnalyzer()
        self.writer = lucene.IndexWriter(self.store, lucene.CJKAnalyzer(), True)
        print 'optimizing index\n',
        self.index()
        self.writer.optimize()
        self.writer.close()
        print 'done'
    def index(self):
        entries = Entry.objects.all()
        for entry in entries:
            try:
                doc = lucene.Document()
                title_field = lucene.Field("title", entry.title,
                                     lucene.Field.Store.NO,
                                     lucene.Field.Index.TOKENIZED,
                                     lucene.Field.TermVector.WITH_POSITIONS_OFFSETS)
                #标题的权重比内容大
                #title_field.setBoost(1.1)
                doc.add(title_field)
                doc.add(lucene.Field("summary", entry.summary,
                                     lucene.Field.Store.NO,
                                     lucene.Field.Index.TOKENIZED,
                                     lucene.Field.TermVector.WITH_POSITIONS_OFFSETS))
                doc.add(lucene.Field("author", entry.author,
                                     lucene.Field.Store.YES,
                                     lucene.Field.Index.UN_TOKENIZED))      
                doc.add(lucene.Field("link", entry.link,
                                     lucene.Field.Store.YES,
                                     lucene.Field.Index.UN_TOKENIZED))    
                doc.add(lucene.Field("when", entry.when.__str__(),
                                     lucene.Field.Store.YES,
                                     lucene.Field.Index.UN_TOKENIZED))
                doc.add(lucene.Field("category", entry.category.what,
                                     lucene.Field.Store.NO,
                                     lucene.Field.Index.TOKENIZED))
                self.writer.addDocument(doc)
            except Exception,e:
                print 'Failed in index:' ,e
                continue
   
if __name__ == '__main__':
    pass