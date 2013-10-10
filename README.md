# Simple BBS

A simple BBS using Apache Cassandra.

### Installation

1. Install Apache Cassandra

Install Apache Cassandra on your server.

2. Create keyspace and column family

Connect to cassandra command line interface, then create keyspace and create column family.

```
create keyspace bbs_ks;
use bbs_ks;
create column family bbs  with comparator=UTF8Type and default_validation_class=UTF8Type and key_validation_class=UTF8Type;
```

2. Deploy

Deploy this application.

```
git clone https://github.com/hiroakis/simple-bbs-using-cassandra.git
cd simple-bbs-using-cassandra/
pip install -r requirements.txt
python app.py
```

