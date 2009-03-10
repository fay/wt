from dot.searcher import Searcher
from apps.wantown.models import Entry
from apps.wantown import dao
from lucene import Hit
from django.core.paginator import Paginator, InvalidPage, EmptyPage
searcher = Searcher()
def query(query, page):
    hits = searcher.search(query)
    query = dao.get_keywords(query)
    results = []
    scores = []
    #last page number
    total = hits.length()
    pages_num = total / 20 + (total % 20 and 1) or 0
    if ((page - 1) * 20) > total :
        page = pages_num
    for i in range(20):
        start = (page - 1) * 20
        if start + i >= total:
            break

        doc = hits.doc(i + start)
        link = doc.get("link")
        entry = dao.get_by_link(link, Entry)
        if entry:
            entry.summary = entry.summary[0:200] + "..."
            results.append(entry)
            scores.append(hits.score(i + (page - 1) * 20))
        
    if 0:
        for hit in hits:
            doc = Hit.cast_(hit).getDocument()
            link = doc.get("link")
            entry = dao.get_by_link(link, Entry)
            if entry:
                entry.summary = entry.summary[0:200] + "..."
                results.append(entry)
                scores.append(Hit.cast_(hit).getScore())
    
    return results, scores, query,total