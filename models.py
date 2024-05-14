#!/usr/bin/python3

from os import environ
from huggingface_hub import login
from transformers import AutoTokenizer
from langchain_community.llms import HuggingFaceEndpoint
from langchain_community.llms.huggingface_pipeline import HuggingFacePipeline

def ChatGLM3(locally = False):
  if locally:
    login('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')
    return HuggingFacePipeline.from_model_id(
      model_id = 'THUDM/chatglm3-6b',
      task = 'text-generation',
      max_length = 8192,
      do_sample = False,
      top_p =  0.8,
      temperature = 0.8,
      trust_remote_code = True
    )
  else:
    environ['HUGGINGFACEHUB_API_TOKEN'] = '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'
    return HuggingFaceEndpoint(
      endpoint_url = 'THUDM/chatglm3-6b',
      task = "text-generation",
      max_length = 8192,
      do_sample = False,
      top_p =  0.8,
      temperature = 0.8,
      trust_remote_code = True
    )

def Llama2(locally = False):
  if locally:
    login('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')
    return HuggingFacePipeline.from_model_id(
      model_id = "meta-llama/Llama-2-7b-chat-hf",
      task = "text-generation",
      max_length = 4096,
      do_sample = False,
      temperature = 0.8,
      top_p = 0.8,
    )
  else:
    environ['HUGGINGFACEHUB_API_TOKEN'] = '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'
    return HuggingFaceEndpoint(
      endpoint_url = "meta-llama/Llama-2-7b-chat-hf",
      task = "text-generation",
      max_length = 4096,
      do_sample = False,
      temperature = 0.8,
      top_p = 0.8,
    )

def Llama3(locally = False):
  login(token = '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')
  tokenizer = AutoTokenizer.from_pretrained('meta-llama/Meta-Llama-3-8B-Instruct')
  if locally:
    return HuggingFacePipeline.from_model_id(
      model_id = "meta-llama/Meta-Llama-3-8B-Instruct",
      task = "text-generation",
      max_length = 4096,
      do_sample = False,
      temperature = 0.6,
      top_p = 0.9,
      model_kwargs = {
        "eos_token_id": [tokenizer.eos_token_id, tokenizer.convert_tokens_to_ids("<|eot_id|>")]
      }
    )
  else:
    environ['HUGGINGFACEHUB_API_TOKEN'] = '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'
    return HuggingFaceEndpoint(
      endpoint_url = "meta-llama/Meta-Llama-3-8B-Instruct",
      task = "text-generation",
      max_length = 4096,
      do_sample = False,
      temperature = 0.6,
      top_p = 0.9,
      model_kwargs = {
        "eos_token_id": [tokenizer.eos_token_id, tokenizer.convert_tokens_to_ids("<|eot_id|>")]
      }
    )

