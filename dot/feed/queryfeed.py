from django.contrib.syndication.feeds import Feed
from dot import dao
class QueryInfo(object):
    def __init__(self):
        self.query = ''
class QueryFeed(Feed):
    def get_object(self, bits):
        query = bits[0]
        return query
    def title(self, obj):
        return "Search results for %s" % obj
    def link(self, obj):
        return "http://127.0.0.1:8000"
    def description(self, obj):
        return "Search results for %s" % obj
    def item_pubdate(self, item):
        return item.when
    def item_guid(self,item):
        return item.author
    def items(self,obj):
        results = dao.query(obj, 1,category_what=None,data_size=10000,nobuildcategory=True)[0]
        return results

