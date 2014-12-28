import logging
from Queue import Queue, Empty
import datetime

from twisted.internet.threads import deferToThread
from backend.util import config
from backend.core.model.Document import Document
from pymongo import MongoClient

import json

loggers = []
## Central queue for log statements. Needed for sync under windows.
logQueue = Queue()


keepLogging = False
logFrame = None

def getDatabaseConnection():
    client = MongoClient(config.dblocation, config.dbport)
    return client

def convertToDocument(bson):
    document = Document()
    document.__dict__ = bson
    #for strategyName in document.vectors:
    #    document.vectors[strategyName] = numpy.array(document.vectors[strategyName])
    return document

## Used as decorator to log a functions return value, using the appropriate logger. 
def logReturnValue(function):
    def loggedFunction(*args):
        moduleName = function.__module__
        funcName = function.__name__
        moduleLogger = getModuleLogger(moduleName)
        ret = function(*args)
        moduleLogger.debug("%s returned %s...", funcName, str(ret))
        return ret
    return loggedFunction

## Starts the logging thread.
def startLogging(name):
    global keepLogging
    if not keepLogging:
        keepLogging = True
        deferToThread(__refreshLog, name)

## Schedules the logging thread to stop.
def stopLogging():
    global keepLogging
    keepLogging = False

## This is a custom log handler assigned to all loggers, which writes log messages to a synchronized queue.
class QueueLogHandler(logging.Handler):
    def emit(self, record):
        global logQueue
        s = self.format(record) #+ '\n'
        #print s
        logQueue.put_nowait(s)


## Utilitiy function used to assign logger objects to modules. 
# This also assigns a custom handler to each logger, so that logs go into both our window as well as to disk.
# Note: Logger name is cut off to fixed length so that log messages align when a monospace font is used.
def getModuleLogger(namespace):
    ln = logging.getLogger(namespace[-config.logNameLength:])
    if not len(ln.handlers):
        filehandler = QueueLogHandler()
        filehandler.setFormatter(logging.Formatter(config.logFormat))
        ln.addHandler(filehandler)

    loggers.append(ln)
    return ln

ln = getModuleLogger(__name__)


def __refreshLog(name):
    global keepLogging
    #get log entry (blocking)
    todaysdate = datetime.date.today()
    logfile = open(config.logFilename % (name, todaysdate), "a")
    while keepLogging:
        #check if we need to start a new file
        if datetime.date.today() != todaysdate:
            logfile.close()
            todaysdate = datetime.date.today()
            logfile = open(config.logFilename % (name, todaysdate), "a")

        logentry = None
        try:
            logentry = logQueue.get(True, 3)
        except Empty:
            pass
        if logentry:
            #print logentry
            ## Write to file
            logfile.write(logentry+"\n")
    try:
        logfile.close()
    except:
        pass


def moduleApiRequest(moduleName, post=False):
    """
    create a decorator that adds basic logging, enables remote access for a resource, and sets the content-type to json
    """
    ln_ = getModuleLogger(moduleName)
    def apiRequest_(render_func):
        """
        decorator that adds basic logging, enables remote access for a resource, and sets the content-type to json
        """
        def wrapped_render(self, request):
            ln_.debug("Got request from %s for %s, args=%s" % (request.getClientIP(), request.uri, request.args))
            request.setHeader("content-type", "application/json")
            request.setHeader('Access-Control-Allow-Origin', '*')
            if post:
                request.setHeader('Access-Control-Allow-Methods', 'POST')
            else:
                request.setHeader('Access-Control-Allow-Methods', 'GET')
            return render_func(self, request)
        return wrapped_render
    return apiRequest_

# retrieve the value at a path in the dict, where the path to follow is specified by keys.
dict_get = lambda d, keys: reduce(lambda d, key: d[key], keys, d)


def ensureRequestArgs(*arg_names):
    """
    return a dectorator for twisted request handlers that ensures args are present
    """
    def ensureArgsDecorator(render):
        def wrapped_render(self, request):
            if request.method == "GET":
                args = request.args
            if request.method == "POST":
                try:
                    args = json.loads(request.content.read())
                except ValueError:
                    request.setResponseCode(400)
                    ln.error("Couldn't parse request content as json.")
                    return "Couldn't parse request content as json."

            parsed_args = []
            for arg_name in arg_names:
                try:
                    arg = dict_get(args, arg_name.split("."))
                    parsed_args.append(arg)
                except (KeyError, TypeError):
                    request.setResponseCode(400)
                    ln.error("Couldn't parse request arg %s." % arg_name)
                    return "Couldn't parse request arg %s." % arg_name
                try:
                    assert len(parsed_args) == len(arg_names)
                except AssertionError:
                    request.setResponseCode(400)
                    return "Could not parse all the required args (need %s)" % (arg_names,)
                return render(self, *parsed_args)
        return wrapped_render
    return ensureArgsDecorator