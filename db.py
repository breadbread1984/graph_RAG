#!/usr/bin/python3

from os import walk
from os.path import splitext, join
import re
import json
from tqdm import tqdm
from langchain_community.document_loaders import UnstructuredPDFLoader, UnstructuredFileLoader, UnstructuredMarkdownLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain.graphs import Neo4jGraph
from langchain_experimental.graph_transformers.llm import LLMGraphTransformer
from models import ChatGLM3, Llama2, Llama3, CodeLlama
from prompts import extract_triplets_template, cypher_generation_template

class DocDatabase(object):
  def __init__(self, username = 'neo4j', password = None, host = 'bolt://localhost:7687', database = 'neo4j', locally = False):
    self.locally = locally
    self.neo4j = Neo4jGraph(url = host, username = username, password = password, database = database)
    self.update_types()

  def update_types(self):
    results = self.neo4j.query("match (n) return distinct labels(n)")
    self.entity_types = [result['labels(n)'][0] for result in results]
    results = self.neo4j.query("match (a)-[r]-(b) return distinct type(r)")
    self.relation_types = [result['type(r)'] for result in results]

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
    text_splitter = RecursiveCharacterTextSplitter(chunk_size = 200, chunk_overlap = 50)
    split_docs = text_splitter.split_documents(docs)
    # 3) extract triplets from documents
    print('extract triplets from documents')
    tokenizer, llm = Llama3(self.locally)
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
    tokenizer, llm = CodeLlama(self.locally)
    prompt = cypher_generation_template(tokenizer, self.neo4j, self.entity_types)
    chain = prompt | llm
    cypher_cmd = chain.invoke({'question': question})
    print('original cypher: ', cypher_cmd)
    # replace property pattern with contains clause
    pattern = r"(\(([^:]*):([^:]*)\s*\{([^:]*):([^:]*)\}\))"
    matches = re.findall(pattern, cypher_cmd)
    constraints = list()
    for match in matches:
      cypher_cmd = cypher_cmd.replace(match[0], "(%s:%s)" % (match[1],match[2]))
      constraints.append((match[1],match[3],match[4]))
    where_clause = ""
    for idx, (obj,prop,value) in enumerate(constraints):
      where_clause += " tolower(%s.%s) contains tolower(%s)" % (obj, prop, value)
      if idx != len(constraints) - 1: where_clause += " and"
      else: where_clause += " "
    pattern = r"(where|WHERE)"
    match = re.search(pattern, cypher_cmd)
    if match:
      # if there exists where clause, add extra condition right after where
      cypher_cmd = cypher_cmd[:match.end()] + where_clause + cypher_cmd[match.end():]
    else:
      # if there is not where clause, add extra condition before return
      pattern = r"(return|RETURN)"
      match = re.search(pattern, cypher_cmd)
      cypher_cmd = cypher_cmd[:match.start()] + " WHERE" + where_clause + cypher_cmd[match.start():]
    print('rewritten cypher: ', cypher_cmd)
    data = self.neo4j.query(cypher_cmd)
    return data

