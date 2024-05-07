#!/usr/bin/python3

from db import DocDatabase

class RAG(object):
  def __init__(self, model = 'zephyr', doc_dir = None):
    if doc_dir is not None:
      self.query_engine = DocDatabase(model).load_doc(doc_dir)
    else:
      self.query_engine = DocDatabase(model).load_db()
  def query(self, question):
    response = self.query_engine.query(question)
    return str(response)

if __name__ == "__main__":
  rag = RAG('docs')
  response = rag.query('what is polymer electrolyte?')
  print(response)

