#!/usr/bin/python3

from langchain.graphs import Neo4jGraph
from langchain.vectorstores.neo4j_vector import Neo4jVector
from langchain.embedding.huggingface import HuggingFaceEmbedding
from langchain_experimental.graph_transformers.llm import LLMGraphTransformer
from models import ChatGLM3, Llama2, Llama3

class DocDatabase(object):
  def __init__(self, username = 'neo4j', password = None, host = 'localhost', model = 'llama3', device = 'cuda'):
    self.username = username
    self.password = password
    self.host = host
    if model == 'llama2':
      self.model = Llama2(device = device)
    elif model == 'llama3':
      self.model = Llama3(device = device)
    elif model == 'chatglm3':
      self.model = ChatGLM3(device = device)
    else:
      raise Exception('unknown model!')
  @staticmethod
  def load_db(db_dir):
    vectordb = Neo4jVector.from_existsing_graph(
      HuggingFaceEmbeddings(model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"),
      url = 'localhost',
      username = self.username,
      password = self.password,
      index_name = 'tasks',
      node_label = 'Task',
      text_node_properties = ['name', 'description', 'status'],
      embedding_node_property = 'embedding',)
    return vectordb
  @staticmethod
  def load_doc(doc_dir, db_dir):
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
    graph = LLMGraphTransformer(llm = self.model).convert_to_graph_documents(docs)
    
