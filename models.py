#!/usr/bin/python3

from transformers import AutoTokenizer
from llama_index.llms.huggingface import HuggingFaceLLM

def Zephyr():
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
  llm = HuggingFaceLLM(
    model_name = 'HuggingFaceH4/zephyr-7b-beta',
    tokenizer_name = 'HuggingFaceH4/zephyr-7b-beta',
    generate_kwargs = {"temperature": 0.7, "top_k": 50, "top_p": 0.95},
    messages_to_prompt = messages_to_prompt,
    completion_to_prompt = completion_to_prompt,
    device_map="auto")
  return llm

def LlaMA3():
  tokenizer = AutoTokenizer.from_pretrained('meta-llama/Meta-Llama-3-8B-Instruct', trust_remote_code = True)
  def messages_to_prompt(message):
    messages = [{'role': message.role, 'content': message.content}]
    prompt = tokenizer.apply_chat_template(messages, tokenize = False, add_generation_prompt = True)
    return prompt
  def completion_to_prompt(completion):
    messages = [{'role': 'user', 'content': completion}]
    prompt = tokenizer.apply_chat_template(messages, tokenize = False, add_generation_prompt = True)
    return prompt
  llm = HuggingFaceLLM(
    model_name = 'meta-llama/Meta-Llama-3-8B-Instruct',
    tokenizer_name = 'meta-llama/Meta-Llama-3-8B-Instruct',
    generate_kwargs = {'temperature': 0.6, 'top_p': 0.9, 'do_sample': True},
    messages_to_prompt = messages_to_prompt,
    completion_to_prompt = completion_to_prompt,
    device_map = "auto")
  return llm

def ChatGLM3():
  tokenizer = AutoTokenizer.from_pretrained('THUDM/chatglm3-6b', trust_remote_code = True)
  def messages_to_prompt(message):
    return tokenizer.build_chat_input(message.content, history = list(), role = message.role)
  def completion_to_prompt(completion):
    return tokenizer.build_chat_input(completion, history = list(), role = 'user')
  llm = HuggingFaceLLM(
    model_name = 'THUDM/chatglm3-6b',
    tokenizer_name = 'THUDM/chatglm3-6b',
    generate_kwargs = {'temperature': 0.8, 'top_p': 0.8, 'do_sample': True},
    messages_to_prompt = messages_to_prompt,
    completion_to_prompt = completion_to_prompt,
    device_map = "auto")
  return llm
