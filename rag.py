#!/usr/bin/python3

from db import DocDatabase

class RAG(object):
  def __init__(self, doc_dir = None):
    if doc_dir is not None:
      self.query_engine = DocDatabase().load_doc(doc_dir)
    else:
      self.query_engine = DocDatabase().load_doc()
  def query(self, question):
    response = self.query_engine.query(question)
    return response

if __name__ == "__main__":
  rag = RAG('docs')
  response = rag.query('what is polymer electrolyte?')
  print(response)
