__author__ = 'dowling'
from backend.core.strategy.IStrategy import IStrategy

class NamedEntityStrategy(IStrategy):
    """
    Use Word2Vec phrase detection to detect something like entities.
    """
    def __init__(self):
        pass

    def handleDocument(self, document):
        pass

    def load(self):
        raise Exception("Not implemented!")

    def save(self):
        raise Exception("Not implemented!")
