# Introduction

this project is to implement graph RAG

# Usage

## Install prerequisite packages

```shell
python3 -m pip install -r requirements.txt
```

## Install nebula graph database

```shell
wget https://oss-cdn.nebula-graph.com.cn/package/3.6.0/nebula-graph-3.6.0.ubuntu2004.amd64.tar.gz
tar -xvzf nebula-graph-3.6.0.ubuntu2004.amd64.tar.gz
mkdir -p ~/opt
mv nebula-graph-3.6.0.ubuntu2004.amd64 ~/opt/nebula-graph-3.6.0
wget https://github.com/vesoft-inc/nebula-console/releases/download/v3.6.0/nebula-console-linux-amd64-v3.6.0
mv nebula-console-linux-amd64-v3.6.0 ~/opt/nebula-graph-3.6.0/bin/nebula-console
```

add the following lines to **~/.bashrc**

```shell
PATH=~/opt/nebula-graph-3.6.0/bin:~/opt/nebula-graph-3.6.0/scripts:$PATH
export PATH
```

execute the following command or reopen another command line session to activate the above environment variables

```shell
source ~/.bashrc
```

execute the following lines to start nebula graph database service

```shell
nebula.service start all
nebula.service status all
```

create space for graph rag

```shell
nebula-console -addr 127.0.0.1 -P 9669 -u root -p nebula
```

within nebula console

```shell
(root@nebula) [(none)]> show hosts
(root@nebula) [(none)]> CREATE SPACE llamaindex(vid_type=FIXED_STRING(256), partition_num=1, replica_factor=1);
(root@nebula) [(none)]> SHOW SPACES;
(root@nebula) [(none)]> USE llamaindex;
(root@nebula) [(none)]> CREATE TAG entity(name string);
(root@nebula) [(none)]> CREATE EDGE relationship(relationship string);
(root@nebula) [(none)]> CREATE TAG INDEX entity_index ON entity(name(256));
```


