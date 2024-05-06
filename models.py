#!/usr/bin/python3

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
    messages_to_prompt=messages_to_prompt,
    completion_to_prompt=completion_to_prompt,
    device_map="auto")
  return llm

