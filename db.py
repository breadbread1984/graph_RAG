#!/usr/bin/python3

from os import listdir, walk
from os.path import splitext, join, exists
from tqdm import tqdm
from llama_index.core import SimpleDirectoryReader, KnowledgeGraphIndex
from llama_index.core import StorageContext
from llama_index.core.graph_stores import SimpleGraphStore

class DocDatabase(object):
  def __init__(self):
    pass
  @staticmethod
  def load_db(db_dir):
    raise NotImplemented
  @staticmethod
  def load_doc(doc_dir, db_dir):
    print('load pages of documents')
    documents = SimpleDirectoryReader(doc_dir)
    graph_store = SimpleGraphStore()
    storage_context = StorageContext.from_default(graph_store = graph_store)
    self.kdb = KnowledgeGraphIndex.from_documents(documents, max_triples_per_chunk = 2, storage_context = storage_context)
    query_engine = self.kdb.as_query_engine(include_text = False, response_mode = 'tree_summarize')
    return query_engine

