#!/usr/bin/python3

from db import DocDatabase

class RAG(object):
  def __init__(self, database = 'neo4j', password = None, doc_dir = None):
    self.db = DocDatabase(password = password, database = database, locally = True)
    if doc_dir is not None:
      self.db.reset()
      self.db.extract_knowledge_graph(doc_dir)
  def query(self, question):
    answer = self.db.query(question)
    return answer

