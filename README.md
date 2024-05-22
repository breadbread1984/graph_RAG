# Introduction

this project is to implement Graph RAG algorithm with langchain

# Usage

## install neo4j

download jar of apoc from [official github](https://github.com/neo4j/apoc/releases/tag/5.19.0)

download jar of neosemantics from [official github](https://github.com/neo4j-labs/neosemantics/releases)

install neo4j with the following commands

```shell
wget -O - https://debian.neo4j.com/neotechnology.gpg.key | sudo apt-key add -
echo 'deb https://debian.neo4j.com stable latest' | sudo tee /etc/apt/sources.list.d/neo4j.list
sudo apt update
sudo apt install daemon cypher-shell neo4j
cp <path/to/downloaded/apoc/jar> /var/lib/neo4j/plugins
cp <path/to/downloaded/neosemantics/jar> /var/lib/neo4j/plugins
sudo echo "dbms.directories.plugins=/var/lib/neo4j/plugins" >> /etc/neo4j/neo4j.conf
sudo echo "dbms.security.procedures.unrestricted=algo.*,apoc.*" >> /etc/neo4j/neo4j.conf
sudo echo "dbms.unmanaged_extension_classes=n10s.endpoint=/rdf" >> /etc/neo4j/neo4j.conf
sudo echo "server.default_listen_address=0.0.0.0" >> /etc/neo4j/neo4j.conf
sudo systemctl start neo4j
sudo systemctl status neo4j
```

start the neo4j desktop by executing **neo4j** in console.

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
Open browser using URL: http://localhost:7474

## some queries you may try

| query|
|------|
|what does sodium produce when it reacts with chlorine?|
|what is the application of sodium chloride?|
|what is deoxyribose?|
|what are the nitrogenous bases?|
|what is found in plant cells?|
|why photosynthesis is essential?|
|what is equation of photosynthesis?|
|how the periodic table is organized?|
|why the periodic table is important?|
|what is the purpose of electrolysis?|
|what is Henderson-Hasselbalch equation used for?|
|what is a catalysis process?|
|what is the purpose of Zeigler-Natta?|
|what is enzymes?|
|what is chemical bonding?|
|what is Covalent bonds?|
|what does the strength of a chemical bond depend on?|
