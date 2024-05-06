#!/usr/bin/python3

from os import listdir, walk, environ
from os.path import splitext, join, exists
from tqdm import tqdm
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.text_splitter import SentenceSplitter
from llama_index.core import SimpleDirectoryReader, KnowledgeGraphIndex, StorageContext, ServiceContext, PromptHelper
from llama_index.graph_stores.nebula import NebulaGraphStore
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import KnowledgeGraphRAGRetriever
from models import Zephyr

class DocDatabase(object):
  def __init__(self, model = 'zephyr'):
    environ['NEBULA_USER'] = 'root'
    environ['NEBULA_PASSWORD'] = 'nebula'
    environ['NEBULA_ADDRESS'] = 'localhost:9669'
    graph_store = NebulaGraphStore(space_name = 'llamaindex', edge_types = ['relationship'], rel_prop_names = ['relationship'], tags = ['entity'])
    self.storage_context = StorageContext.from_defaults(graph_store = graph_store)
    if model == 'zephyr':
      self.llm = Zephyr()
    else:
      raise Exception('unknown model!')
    self.service_context = ServiceContext.from_defaults(
      llm = self.llm,
      embed_model = HuggingFaceEmbedding(model_name = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'),
      text_splitter = SentenceSplitter(chunk_size = 1024, chunk_overlap = 20),
      prompt_helper = PromptHelper(
        context_window = 4096,
        num_output = 256,
        chunk_overlap_ratio = 0.1,
        chunk_size_limit = None)
    )
  def load_db(self):
    graph_rag_retriever = KnowledgeGraphRAGRetriever(
      storage_context = self.storage_context,
      service_context = self.service_context,
      llm = self.llm,
      verbose = True)
    query_engine = RetrieverQueryEngine.from_args(graph_rag_retriever, service_context = self.service_context)
    return query_engine
  def load_doc(self, doc_dir, visualize = False):
    print('load pages of documents')
    reader = SimpleDirectoryReader(doc_dir)
    documents = reader.load_data()
    kdb = KnowledgeGraphIndex.from_documents(
      documents,
      max_triples_per_chunk = 10,
      storage_context = self.storage_context,
      service_context = self.service_context,
      space_name = 'llamaindex',
      edge_types = ['relationship'],
      rel_prop_names = ['relationship'],
      tags = ['entity'],
      include_embeddings = True
    )
    query_engine = kdb.as_query_engine(include_text = True, retriever_mode = 'keyword', response_mode = "tree_summarize", embedding = 'hybrid', similarity_top_k = 5)
    if visualize:
      self.visualize(kdb)
    return query_engine
  def visualize(self, kdb, output_html = 'example.html'):
    from pyvis.network import Network
    g = kdb.get_network_graph()
    net = NetWork(notebook = True, cdn_resources = "in_line", directed = True)
    net.from_nx(g)
    net.show(output_html)
