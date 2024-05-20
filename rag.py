#!/usr/bin/python3

from db import DocDatabase

class RAG(object):
  def __init__(self, model = 'llama3', password = None, doc_dir = None):
    self.db = DocDatabase(model, password = password)
    if doc_dir is not None:
      self.db.extract_knowledge_graph(doc_dir)
  def query(self, question):
    answer = self.db.query(question)
    return answer

