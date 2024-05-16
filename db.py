#!/usr/bin/python3

from os import walk
from os.path import splitext, join
import re
import json
from tqdm import tqdm
from langchain.document_loaders import UnstructuredPDFLoader, UnstructuredFileLoader, UnstructuredMarkdownLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain.graphs import Neo4jGraph
from langchain_experimental.graph_transformers.llm import LLMGraphTransformer
from models import ChatGLM3, Llama2, Llama3
from prompts import extract_triplets_template, cypher_generation_template

class DocDatabase(object):
  def __init__(self, username = 'neo4j', password = None, host = 'bolt://localhost:7687', database = 'neo4j', model = 'llama3', locally = False):
    self.model = model
    self.locally = locally
    self.neo4j = Neo4jGraph(url = host, username = username, password = password, database = database)
    self.update_types()
  def update_types(self):
    results = self.neo4j.query("match (n) return distinct labels(n)")
    self.entity_types = [result['labels(n)'][0] for result in results]
    results = self.neo4j.query("match (a)-[r]-(b) return distinct type(r)")
    self.relation_types = [result['type(r)'] for result in results]
  def get_tokenizer_model(self,):
    if self.model == 'llama2':
      return Llama2(self.locally)
    elif self.model == 'llama3':
      return Llama3(self.locally)
    elif self.model == 'chatglm3':
      return ChatGLM3(self.locally)
    else:
      raise Exception('unknown model!')
  def extract_knowledge_graph(self, doc_dir):
    # extract knowledge graph from documents
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
    tokenizer, llm = self.get_tokenizer_model()
    prompt, _ = extract_triplets_template(tokenizer)
    graph = LLMGraphTransformer(
              llm = llm,
              prompt = prompt
            ).convert_to_graph_documents(split_docs)
    self.neo4j.add_graph_documents(graph)
    # 4) get all labels
    self.update_types()
  def reset(self):
    # delete all entities and relations in neo4j
    self.neo4j.query('match (a)-[r]-(b) delete a,r,b')
    self.update_types()
  def query(self, question):
    tokenizer, llm = self.get_tokenizer_model()
    prompt = cypher_generation_template(tokenizer, self.neo4j, self.entity_types)
    #llm_with_stop = llm.bind({'stop': ['\nCypherResult:']})
    def cypher_parser(message):
      pattern = r"```(.*?)```"
      matches = re.findall(pattern, message, re.DOTALL)
      return matches[0]
    chain = prompt | llm | cypher_parser
    cypher_cmd = chain.invoke({'question': question})
    print(cypher_cmd)
    result = self.neo4j.query(cypher_cmd)
    return result

if __name__ == "__main__":
  db = DocDatabase(model = 'llama3', password = '19841124')
  #db.reset()
  #db.extract_knowledge_graph('docs2')
  res = db.query('what is put into a round-bottomed flask?')
  print(res)
