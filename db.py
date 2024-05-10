#!/usr/bin/python3

from os import walk
from os.path import splitext, join
import re
from tqdm import tqdm
from langchain.document_loaders import UnstructuredPDFLoader, UnstructuredFileLoader, UnstructuredMarkdownLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain.graphs import Neo4jGraph
from langchain_experimental.graph_transformers.llm import LLMGraphTransformer
from models import ChatGLM3, Llama2, Llama3

class DocDatabase(object):
  def __init__(self, username = 'neo4j', password = None, host = 'bolt://localhost:7687', model = 'llama3', entities = ['reactant', 'catalyst', 'reaction_conditions', 'reaction_devices']):
    self.username = username
    self.password = password
    self.host = host
    self.model = model
    self.entities = entities
  def extract_json(self, message):
    text = message
    pattern = r"```json(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)
    try:
      return matches[0]
    except Exception:
      raise Exception("Failed to parse: {message}")
    self.neo4j = Neo4jGraph(url = host, username = username, password = password)
  def get_model(self,):
    if self.model == 'llama2':
      return Llama2()
    elif self.model == 'llama3':
      return Llama3()
    elif self.model == 'chatglm3':
      return ChatGLM3()
    else:
      raise Exception('unknown model!')
  def load_doc(self, doc_dir):
    print('load pages of documents')
    docs = list()
    for root, dirs, files in tqdm(walk(doc_dir)):
      for f in files:
        stem, ext = splitext(f)
        loader_types = {'.md': UnstructuredMarkdownLoader,
                        '.txt': UnstructuredFileLoader,
                        '.pdf': UnstructuredPDFLoader}
        loader = loader_types[ext](join(root, f), mode = "single", strategy = "fast")
        # load pages of a document to a list
        docs.extend(loader.load())
    # 2) split pages into chunks and save to split_docs
    print('split pages into chunks')
    text_splitter = RecursiveCharacterTextSplitter(chunk_size = 500, chunk_overlap = 150)
    split_docs = text_splitter.split_documents(docs)
    # 3) extract triplets from documents
    print('extract triplets from documents')
    chain = self.get_model() | self.extract_json
    graph = LLMGraphTransformer(
              llm = chain,
              allowed_nodes = self.entities,
            ).convert_to_graph_documents(split_docs)
    self.neo4j.add_graph_documents(graph)
  def query(self, text):
    prompt = ChatPromptTemplate.fromMessage([
      ("system", "You are extracting %s from the text." % ', '.join(self.entities)),
      ("user", "Use the given format to extract information from the following\ninput: {question}")
    ])
    

if __name__ == "__main__":
  db = DocDatabase(model = 'llama3', password = '19841124')
  db.load_doc('docs2')
