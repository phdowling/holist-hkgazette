class IStrategy(object):
    def handleDocument(self, document):
        raise Exception("Not implemented!")

    def load(self):
        raise Exception("Not implemented!")

    def save(self):
        raise Exception("Not implemented!")
