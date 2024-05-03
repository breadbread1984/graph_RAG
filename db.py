#!/usr/bin/python3

from langchain.graphs import Neo4jGraph
from langchain.vectorstores.neo4j_vector import Neo4jVector
from langchain.embedding.huggingface import HuggingFaceEmbedding

class DocDatabase(object):
  def __init__(self, username = 'neo4j', password = None, host = 'localhost'):
    self.username = username
    self.password = password
    self.host = host
    self.entity_types = {
      'polymer electrolyte': "A polymer matrix capable of ion conduction, for example 'polyethylene oxide', 'polyvinyl alcohol', 'polymethyl methacrylate', 'polycaprolactone', 'polychitosan', 'polyvinyl pyrrolidone', 'polyvinyl chloride', 'polyvinylidene fluoride', 'polyimide'",
      'material invention': "material invention item, for example 'polymer', 'plasticizer', 'electrolyte'",
      ''
    }
    self.relation_types = {
    }
    self.entity_relationship_match = {
    }
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
    # 3) encode strings to feature vectors
    print('encode strings to feature vectors')
    # NOTE: alternative model "distilbert/distilbert-base-uncased"
    
