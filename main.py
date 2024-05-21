#!/usr/bin/python3

from absl import flags, app
from os.path import exists
import gradio as gr
from rag import RAG

FLAGS = flags.FLAGS

def add_options():
  flags.DEFINE_string('doc_dir', default = None, help = 'path to document directory')
  flags.DEFINE_string('host', default = 'localhost', help = 'host address')
  flags.DEFINE_string('db', default = 'neo4j', help = 'database name')
  flags.DEFINE_string('user', default = 'neo4j', help = 'user name')
  flags.DEFINE_string('password', default = None, help = 'password')
  flags.DEFINE_integer('port', default = 8081, help = 'port number')

def main(unused_argv):
  rag = RAG(host = FLAGS.host, database = FLAGS.db, username = FLAGS.user, password = FLAGS.password, doc_dir = FLAGS.doc_dir)
  def query(question, history):
    answer = rag.query(question)
    history.append((question, str(answer)))
    return "", history
  block = gr.Blocks()
  with block as demo:
    with gr.Row(equal_height = True):
      with gr.Column(scale = 15):
        gr.Markdown("<h1><center>graph QA</center></h1>")
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

