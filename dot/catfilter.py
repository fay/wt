# -*- coding:utf-8 -*-
from apps.wantown import dao
from apps.wantown.models import Entry                
from lucene import IndexReader, Term, BitSet, PythonFilter, JArray
from django.core.cache import cache
PAGE_SIZE=20
"""
    根据类目过滤搜索结果
"""
class CatFilter(PythonFilter):

    def __init__(self):
        self.query = ''
        self.category_id = ''
        super(CatFilter, self).__init__()
    def bits(self, reader):
        bits = BitSet(reader.maxDoc())
        cat = dao.Category.objects.get(id=self.category_id)
        termDocs = reader.termDocs(Term('summary',cat.what))
        doc_ids = cache.get(self.query.replace(' ','+'))
        if doc_ids:
            for id in doc_ids:
                doc = reader.document(id)
                entry = dao.get_by_link(doc["link"],Entry)
                qec = dao.get_qec_by_qe(self.query, entry.id)
                for i in qec:
                    if i.category.id == self.category_id:
                        bits.set(id)
                        break
            """
            while termDocs.next():
                id = termDocs.doc()
                doc = reader.document(id)
                entry = dao.get_by_link(doc["link"],Entry)
                qec = dao.get_qec_by_qe(self.query, entry.id)
                i +=1
                for i in qec:
                    if i.category.id == self.category_id:
                        bits.set(id)
                        break
            """
        print bits
        return bits

    def __str__():
        return "CatFilter"