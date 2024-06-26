#!/usr/bin/python3

from absl import flags, app
import gradio as gr
from langchain.graphs import Neo4jGraph
from models import Llama3, CodeLlama
from prompts import entity_generation_template

FLAGS = flags.FLAGS

def add_options():
  flags.DEFINE_string('host', default = 'localhost', help = 'host address')
  flags.DEFINE_string('db', default = 'neo4j', help = 'database name')
  flags.DEFINE_string('user', default = 'neo4j', help = 'database name')
  flags.DEFINE_string('password', default = None, help = 'password')
  flags.DEFINE_integer('port', default = 8083, help = 'port number')

def main(unused_argv):
  neo4j = Neo4jGraph(url = 'bolt://%s:7687' % (FLAGS.host), username = FLAGS.user, password = FLAGS.password, database = FLAGS.db)
  results = neo4j.query("match (n) return distinct labels(n)")
  entity_types = [result['labels(n)'][0] for result in results]
  tokenizer, llm = Llama3(False)
  prompt = entity_generation_template(tokenizer, entity_types)
  chain = prompt | llm
  def query(question, history):
    entities = chain.invoke({'question': question})
    print(prompt.format_prompt(question = question).to_string())
    history.append((question, entities))
    entities = eval(entities)
    triplets = list()
    for entity_type, keywords in entities.items():
      if len(keywords) == 0: continue
      for keyword in keywords:
        #cypher_cmd = 'match (a:`%s`)-[r]->(b) where tolower(a.id) contains tolower(\'%s\') return a,r,b' % (entity_type, keyword)
        cypher_cmd = 'match (a)-[r]->(b) where tolower(a.id) contains tolower(\'%s\') return a,r,b' % (keyword)
        matches = neo4j.query(cypher_cmd)
        triplets.extend([(match['a']['id'],match['r'][1],match['b']['id']) for match in matches])
        #cypher_cmd = 'match (b)-[r]->(a:`%s`) where tolower(a.id) contains tolower(\'%s\') return b,r,a' % (entity_type, keyword)
        cypher_cmd = 'match (b)-[r]->(a) where tolower(a.id) contains tolower(\'%s\') return b,r,a' % (keyword)
        matches = neo4j.query(cypher_cmd)
        triplets.extend([(match['b']['id'],match['r'][1],match['a']['id']) for match in matches])
    print('\n\nmatched triplets:', triplets)
    return "", history
  block = gr.Blocks()
  with block as demo:
    with gr.Row(equal_height = True):
      with gr.Column(scale = 15):
        gr.Markdown("<h1><center>获取问题实体</center></h1>")
    with gr.Row():
      with gr.Column(scale = 4):
        chatbot = gr.Chatbot(height = 450, show_copy_button = True)
        msg = gr.Textbox(label = "需要问什么？")
        with gr.Row():
          submit_btn = gr.Button("发送")
          clear_btn = gr.ClearButton(components = [chatbot], value = "清空问题")
      submit_btn.click(query, inputs = [msg, chatbot], outputs = [msg, chatbot])
  gr.close_all()
  demo.launch(server_name = '0.0.0.0', server_port = FLAGS.port)

if __name__ == "__main__":
  add_options()
  app.run(main)


