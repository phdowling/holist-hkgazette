from backend.link.strategy.ILinkStrategy import ILinkStrategy

__author__ = 'dowling'
from backend.util.util import *
ln = getModuleLogger(__name__)

from elasticsearch import Elasticsearch
from twisted.web.resource import Resource
from backend.util import config

from backend.util.util import ensureRequestArgs, moduleApiRequest
import json

apiRequest = moduleApiRequest(__name__)
apiPOSTRequest = moduleApiRequest(__name__, post=True)

def silenceElasticsearch():
        import logging
        es_log = logging.getLogger("elasticsearch")
        es_log.setLevel(logging.INFO)


class ElasticearchStrategy(Resource, ILinkStrategy):
    def __init__(self):
        super(ElasticearchStrategy, self).__init__()
        self.elasticsearch = Elasticsearch(["%s:%s" % (config.eslocation, config.esport)])
        self.setupApi()
        silenceElasticsearch()

    def setupApi(self):
        resource = Resource()
        self.putChild("subject_text", resource)
        resource.putChild("_search", SearchText(self))

    def getApiPath(self):
        return "search"

    def searchFullText(self, query):
        results = self.elasticsearch.search(index="%s.%s" % (config.dbname, "new_documents"),
                                            body={
                                                "query":
                                                {
                                                    "multi_match": {
                                                        "query": query,
                                                        "fields": ["subject", "text"],
                                                        "fuzziness": 3
                                                    }
                                                }
                                            }
                                            )
        return results

class SearchText(Resource):
    isLeaf = True
    def __init__(self, strategy):
        self.strategy = strategy

    @apiRequest
    @ensureRequestArgs(["query"])
    def render_GET(self, request):
        query = request.args["query"][0]
        ln.info("Search requested, query=%s" % query)
        return json.dumps(self.strategy.searchFullText(query), indent=4)

    @apiPOSTRequest
    def render_POST(self, request):
        query = request
        return json.dumps(self.strategy.searchFullText(query), indent=4)