from backend.util import util
from backend.collect.DataCollector import DataCollector
from plugin.collect.datasource import GazetteDataSource

util.startLogging("collect")
collect = DataCollector([GazetteDataSource()])