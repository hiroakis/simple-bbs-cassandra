# Simple BBS

A simple BBS using Apache Cassandra.

# Installation

* Install Apache Cassandra

Install Apache Cassandra on your server.

* Create keyspace and column family

Connect to cassandra command line interface, then create keyspace and create column family.

```

create keyspace bbs;
use bbs;
create column family threads  with comparator=UTF8Type and default_validation_class=UTF8Type and key_validation_class=UTF8Type;
```

* Deploy

Deploy this application.

```
git clone https://github.com/hiroakis/simple-bbs-cassandra.git
cd simple-bbs-cassandra/
pip install -r requirements.txt
```

* Start app.py

Start application. Default port is 8000.

```
python app.py
```

### Demo image

![](demo.png?raw=true)
