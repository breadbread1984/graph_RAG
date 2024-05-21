# Introduction

this project is to implement Graph RAG algorithm with langchain

# Usage

## install neo4j

download and install neo4j graph database self-managed community version from [official site](https://neo4j.com/deployment-center/#gdb-tab)
download jar of neosemantics from [official github](https://github.com/neo4j-labs/neosemantics/releases)

install neo4j with the following commands

```shell
mkdir -p ~/opt/neo4j/bin
mkdir -p ~/opt/neo4j/plugins
mkdir -p ~/opt/neo4j/conf
cp <path/to/downloaded/neo4j-desktop/executable> ~/opt/neo4j/bin/neo4j
cp <path/to/downloaded/neosemantics/jar> ~/opt/neo4j/plugins
export PATH=~/opt/neo4j/bin:$PATH
export NEO_HOME=~/opt/neo4j
echo "dbms.unmanaged_extension_classes=n10s.endpoint=/rdf" >> ~/opt/neo4j/conf/neo4j.conf
echo "dbms.default_listen_address=0.0.0.0" >> ~/opt/neo4j/conf/neo4j.conf
```

start the neo4j desktop by executing **neo4j** in console.

install plugins: **APOC**, **Neosemantics(n10s)**

add a new dbms and add a database.

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
