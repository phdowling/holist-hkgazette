from backend.util import util
from backend.link.LinkController import LinkController
from plugin.link.strategies.ElasticsearchStrategy import ElasticearchStrategy

__author__ = ['raoulfriedrich', 'dowling']




#from core.util import config
 #import logging
 #logging.basicConfig(format=config.logFormat,level=logging.DEBUG if config.showDebugLogs else logging.INFO)
 #ln = util.getModuleLogger(__name__)
strategies = [ElasticearchStrategy()]

util.startLogging("link")
control = LinkController(strategies)