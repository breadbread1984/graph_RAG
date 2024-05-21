#!/usr/bin/python3

from db import DocDatabase

class RAG(object):
  def __init__(self, host = 'localhost', port = 7687, database = 'neo4j', username = 'neo4j', password = None, doc_dir = None):
    self.db = DocDatabase(username = username, password = password, host = 'bolt://%s:%d' % (host, port), database = database, locally = False)
    if doc_dir is not None:
      self.db.reset()
      self.db.extract_knowledge_graph(doc_dir)
  def query(self, question):
    answer = self.db.query(question)
    return answer

