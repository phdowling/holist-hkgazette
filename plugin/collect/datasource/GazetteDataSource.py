__author__ = 'dowling'
from backend.util import util
from backend.collect.datasource.IDataSource import IDataSource
from backend.core.model.Document import Document
from backend.util import config


DEBUG = False
if DEBUG:
    import logging
    logging.basicConfig()
    ln = logging.getLogger("test_gazette")
    ln.setLevel(logging.DEBUG)
else:
    ln = util.getModuleLogger(__name__)

import csv

GAZETTE_DATA_ROOT_PATH = "/var/data/hongkong/gazette/"
GAZETTE_METADATA_FILE = GAZETTE_DATA_ROOT_PATH + "all.gazette.csv"
RAW_TEXTS_PATH = GAZETTE_DATA_ROOT_PATH + "text/"

PERSISTENCE_FILE = "persist/gazette_retrieved.txt"

class GazetteDataSource(IDataSource):
    def __init__(self):
        self.load()
        self.updating = False

    def _assemble_document(self, document_dict):
        if document_dict["link"] in self.retrieved:
            return None

        # filter out missing fields
        for field in document_dict.keys():
            if document_dict[field] == "":
                del document_dict[field]
        try:
            filenames = [RAW_TEXTS_PATH + fname[:-4] + ".txt" for fname in document_dict["filename"].split("|")]
        except KeyError:
            #ln.warn("Metadata entry has no filename! Other fields are: %s" % document_dict)
            return None

        texts = []
        for filename in filenames:
            try:
                with open(filename, "r") as textfile:
                    texts.append(textfile.read())
            except IOError:
                ln.warn("File %s could not be opened! Not processing this document." % filename)
                return None

        document_dict["text"] = "\n".join(texts)
        document = Document()
        document.__dict__ = document_dict
        return document

    def updateAndGetDocuments(self):
        self.updating = True
        ln.debug("retrieving gazette data..")
        metadata_file = open(GAZETTE_METADATA_FILE, "r")
        reader = csv.reader(metadata_file)
        fieldnames = reader.next()

        documents = []
        num_lines = 0
        for line in reader:
            num_lines += 1
            if num_lines % 1000 == 0:
                ln.debug("Handled %s metadata entries so far, parsed %s documents." % (num_lines, len(documents)))

            document_dict = dict(zip(fieldnames, line))

            document = self._assemble_document(document_dict)
            if document is not None:
                documents.append(document)
                self.retrieved.add(document.link)

        ln.debug("Read %s metadata entries, was able to fully parse %s documents." % (num_lines, len(documents)))
        metadata_file.close()

        self.save()
        self.updating = False
        return documents

    @staticmethod
    def getUniqueIdField():
        return "link"

    def load(self):
        self.retrieved = set()
        try:
            retrieved_file = open(PERSISTENCE_FILE, "r")
            for line in retrieved_file:
                self.retrieved.add(line.strip())
        except IOError:
            ln.warn("Couldn't read gazette persistence file! Might be adding duplicates.")

    def save(self):
        ln.debug("Writing persistence file.")
        with open(PERSISTENCE_FILE, "w") as outfile:
            for link in self.retrieved:
                outfile.write(link + "\n")