## this specifies how many log files are kept at most. 0 means unlimited.
backupCount = 0

updateLogMaxWaitTime = 10
logFilename = "log/%s_holistserver%s.log"
logNameLength = 18
logFormat = '%(asctime)s %(levelname)-8s %(name)-18s: %(message)s'

showDebugLogs = True

collectNodeIP = "localhost"
collectNodePort = 12137

holistcoreurl = "localhost"
holistcoreport = 1157

core_control_port = 11571

strategyregisterport = 1158

link_node_ip = "localhost"
link_node_port = 8082
link_node_control_port = 60112

dblocation = "localhost"
dbport = 27017
dbname = "holist-gazette"
#dblocation = "ds059957.mongolab.com"
#dbport = 59957

eslocation = "localhost"
esport = "9200"
