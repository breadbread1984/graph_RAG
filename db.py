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
from prompts import extract_triplets_template

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
  def extract_json(self, message):
    pattern = r"```json(.*?)```"
    matches = re.findall(pattern, message, re.DOTALL)
    if len(matches) == 0:
      pattern = r"```(.*?)```"
      matches = re.findall(pattern, message, re.DOTALL)
    return "[]" if len(matches) == 0 else matches[0]
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
    prompt, parser = extract_triplets_template(tokenizer)
    chain = llm | self.extract_json
    graph = LLMGraphTransformer(
              llm = chain,
              prompt = prompt
            ).convert_to_graph_documents(split_docs)
    self.neo4j.add_graph_documents(graph)
    # 4) get all labels
    self.update_types()
  def reset(self):
    # delete all entities and relations in neo4j
    self.neo4j.query('match (a)-[r]-(b) delete a,r,b')
    self.update_types()
  def extract_entities(self, text):
    # extract entities of type exists in neo4j
    schemas = [
      ResponseSchema(name = entity_type, description = "key words of type %s" % entity_type)
      for entity_type in self.entity_types
    ]
    parser = StructuredOutputParser.from_response_schemas(schemas)
    prompt = PromptTemplate(
      template = "You are extracting keywords of type among %s from the following text.\n{question}\n{format_instructions}" % (', '.join(self.entity_types),),
      input_variables = ['question'],
      partial_variables = {'format_instructions': parser.get_format_instructions()}
    )
    chain = prompt | self.get_model() | parser
    keywords = chain.invoke({'question': text})
    return keywords
  def query(self, text):
    cypher_prompt = ChatPromptTemplate.from_messages([
      ('system', 'Given an input question, convert it to a Cypher query. No pre-amble.'),
      ('user', 'Based on the Neo4j graph schema below, write a Cypher query that would answer the user\'s question:\n{schema}\nEntities in the question map to the following database values:\n{entities_list}\nQuestion: {question}\nCypher query:')
    ])

if __name__ == "__main__":
  db = DocDatabase(model = 'llama3', password = '19841124')
  db.reset()
  db.extract_knowledge_graph('docs2')
  #db.query('who played in Casino movie?')
