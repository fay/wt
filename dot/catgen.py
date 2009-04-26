# -*- coding:utf-8 -*-
from apps.wantown import dao


"""
    定期对用户查询时生成的类目进行统计，生成用于在前台展示的类目
    展示类目最终的权重由类目与每个对应的entry的相似度权重和用户点击的entry的类目次数
"""
def catgenerate():
    all_qec  = dao.QueryEntryCategory.objects.all()
    keyword_cat = {}
    for qec in all_qec:
        query = qec.query
        cat = qec.category
        if not keyword_cat.has_key(query.keyword + '+++--' + cat.what):
            keyword_cat[query.keyword + '+++--' + cat.what] = None
        else:
            continue
        qcs = dao.QueryEntryCategory.objects.filter(query=query,category=cat)
        weight = 0
        qc = dao.QueryCategory.objects.filter(query=query,category=cat)
        for i in qcs:
            """
                TODO 加入用户点击类目的计数
            """
            weight += i.weight
        count = 0.5
        if qc:
            count = qc[0].count
        weight =  weight * count
        dao.save_qc_with_weight(query.keyword, weight, cat.what)
        