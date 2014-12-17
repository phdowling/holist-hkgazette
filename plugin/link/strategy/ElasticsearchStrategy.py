from backend.link.strategy import ILinkStrategy

__author__ = 'dowling'
from backend.util.util import *
ln = getModuleLogger(__name__)

from elasticsearch import Elasticsearch
from twisted.web.resource import Resource
from backend.util import config

from backend.util.util import ensureRequestArgs, moduleApiRequest
import json

apiRequest = moduleApiRequest(__name__)

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
        self.putChild("subject_text", SearchText(self))

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
                                                        "fuzziness": "AUTO"
                                                    }
                                                }
                                            }
                                            )
        return results


class SearchText(Resource):
    def __init__(self, strategy):
        self.strategy = strategy

    @apiRequest
    @ensureRequestArgs(["query"])
    def render_GET(self, request):
        ln.info("Search requested, query=%s" % request.args["query"])
        return json.dumps(self.strategy.searchFullText(request.args["query"]), indent=4)