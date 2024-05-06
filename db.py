#!/usr/bin/python3

from os import listdir, walk, environ
from os.path import splitext, join, exists
from tqdm import tqdm
from llama_index.llms.huggingface import HuggingFaceLLM
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.text_splitter import SentenceSplitter
from llama_index.core import SimpleDirectoryReader, KnowledgeGraphIndex, StorageContext, ServiceContext, PromptHelper
from llama_index.graph_stores.nebula import NebulaGraphStore
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import KnowledgeGraphRAGRetriever

class DocDatabase(object):
  def __init__(self):
    environ['NEBULA_USER'] = 'root'
    environ['NEBULA_PASSWORD'] = 'nebula'
    environ['NEBULA_ADDRESS'] = 'localhost:9669'
    graph_store = NebulaGraphStore(space_name = 'llamaindex', edge_types = ['relationship'], rel_prop_names = ['relationship'], tags = ['entity'])
    self.storage_context = StorageContext.from_defaults(graph_store = graph_store)
    def messages_to_prompt(message):
      prompt = ''
      for message in messages:
        if message.role == 'system':
          prompt += f"<|system|>\n{message.content}</s>\n"
        elif message.role == 'user':
          prompt += f"<|user|>\n{message.content}</s>\n"
        elif message.role == 'assistant':
          prompt += f"<|assistant|>\n{message.content}</s>\n"
      if not prompt.startswith('<|system|>\n'):
        prompt = "<|system|>\n</s>\n" + prompt
      prompt = prompt + "<|assistant|>\n"
      return prompt
    def completion_to_prompt(completion):
      return f"<|system|>\n</s>\n<|user|>\n{completion}</s>\n<|assistant|>\n"
    self.llm = HuggingFaceLLM(
      model_name = 'HuggingFaceH4/zephyr-7b-beta',
      tokenizer_name = 'HuggingFaceH4/zephyr-7b-beta',
      generate_kwargs = {"temperature": 0.7, "top_k": 50, "top_p": 0.95},
      messages_to_prompt=messages_to_prompt,
      completion_to_prompt=completion_to_prompt,
      device_map="auto")
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
    return graph_rag_retriever, query_engine
  def load_doc(self, doc_dir):
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
    return kdb, query_engine
  @staticmethod
  def visualize(kdb, output_html = 'example.html'):
    from pyvis.network import Network
    g = kdb.get_network_graph()
    net = NetWork(notebook = True, cdn_resources = "in_line", directed = True)
    net.from_nx(g)
    net.show(output_html)
