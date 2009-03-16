# -*- coding: utf-8 -*-
from lucene import IndexReader, initVM, CLASSPATH, TermPositionVector, Term
import os
initVM(CLASSPATH)
STORE_DIR = os.path.dirname(__file__) + '/../index'

def loadterms():
    ireader = IndexReader.open(STORE_DIR)
    tpv = TermPositionVector.cast_(ireader.getTermFreqVector(0, 'title'))
    a = ireader.terms()
    rownames = []
    # 列名为term的中英文表示
    colnames = []
    # term-freq矩阵
    data = []
    ireader.document(- 1)
    i = 0
    while a.next():
        term = a.term()
        if term.field() == 'summary':
            colnames.append(term.text())
            if term.text() == '':
                print 'ok'
                break
            i = i+1
            if i == 1000:
                break
            docs = ireader.termDocs(term)
            vector = []
            lastdoc = 0
            while docs.next():
                # 填补那些不包含当前term的document的词频为0
                if lastdoc < docs.doc():
                    id = docs.doc()
                    for j in range(id - lastdoc):
                        vector.append(0)
                vector.append(docs.freq())
            data.append(vector)
    ireader.close()
    return colnames, data

if __name__ == '__main__':
    loadterms()
