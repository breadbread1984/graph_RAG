#!/usr/bin/python3

from db import DocDatabase

class RAG(object):
  def __init__(self, doc_dir = None):
    kdb = DocDatabase().load_doc(doc_dir)
    self.query_engine = kdb.as_query_engine(include_text = True, retriever_mode = 'keyword', response_mode = "tree_summarize", embedding = 'hybrid', similarity_top_k = 5)
  def query(self, question):
    response = self.query_engine.query(question)
    return response

if __name__ == "__main__":
  rag = RAG('docs')
  response = rag.query('what is polymer electrolyte?')
  print(response)
