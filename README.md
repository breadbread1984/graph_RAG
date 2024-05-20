# Introduction

this project is to implement Graph RAG algorithm with langchain

# Usage

## Install prerequisite packages

```shell
python3 -m pip install -r requirements.txt
```

## Fix issues of langchain-experimental

edit line 551 of **<path/to/site-packages>/langchain_experimental/graph_transformers/llm.py** to change the code from

```python
except NotImplementedError:
```

to

```python
except
```

edit line 595 of **<path/to/site-packages>/langchain_experimental/graph_transformers/llm.py** to change the code from

```python
parsed_json = self.json_repair.loads(raw_schema.content)
```

to

```python
parsed_json = self.json_repair.loads(raw_schema)
```

edit line 597 of **<path/to/site-packages>/langchain_experimental/graph_transformers/llm.py** to change the code from

```python
for rel in parsed_json:
    # Nodes need to be deduplicated using a set
    nodes_set.add((rel["head"], rel["head_type"]))
    nodes_set.add((rel["tail"], rel["tail_type"]))
```

to

```python
for rel in parsed_json:
    if type(rel) is not dict: continue
    # Nodes need to be deduplicated using a set 
    nodes_set.add((rel["head"], rel["head_type"]))
    nodes_set.add((rel["tail"], rel["tail_type"]))
```

## Start service

```shell
python3 main.py --password <password> [--doc_dir <path/to/document/directory>]
```

if doc_dir argument is provided the knowledge graph is extracted from the documents

# Other Information

## View neo4j Database
Open browser using URL: http://103.6.49.76:7474/browser/

## some queries you may try

| query|
|------|
|Where is Berkeley university?|
|Which university is found in 1868?|
