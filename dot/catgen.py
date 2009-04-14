# -*- coding:utf-8 -*-
from apps.wantown import dao



def catgenerate():
    all_qec  = dao.QueryEntryCategory.objects.all()
    keyword_cat ={}
    for qec in all_qec:
        query = qec.query
        cat = qec.category
        if not keyword_cat.has_key(query.keyword + '+++--' + cat.what):
            keyword_cat[query.keyword + '+++--' + cat.what] = None
        else:
            continue
        qcs = dao.QueryEntryCategory.objects.filter(query=query,category=cat)
        weight = 0
        for i in qcs:
            weight += i.weight
        dao.save_qc_with_weight(query.keyword, weight, cat.what)
        