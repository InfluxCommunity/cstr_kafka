`hello_world_example` contains the simplest kafka example for two apps running simultaneously and waiting on each respective topic for a new value before altering it and producing a new value. 

`kafka_logic_for_cstr` contains all the logic required to run the full example. 

`cstr_model.py` and `pid_controller.py` contain the full examples with kafka. 

`without_kafka` contians the correct logic for the calculation of values without Kafka, where `without_kafka/cstr_reactor.py` is the basis for `cstr_model.py` and  `without_kafka/pid_control.py` is the basis for `pid_controller`
`data_doublet_steps.txt` contains the correct values that I'm aiming for with `pid_controller`and `cstr_model.py`. It contains t,u,T,Ca,op columns. 


Useful commands: 
To create env, activate and deactivate:
```
pipenv install
pipenv shell
exit
```

To delete topics:
```
docker exec -it ba8784871b18 /bin/sh

/opt/kafka/bin/kafka-topics.sh --delete --topic cstr --bootstrap-server localhost:9092

/opt/kafka/bin/kafka-topics.sh --delete --topic pid_control --bootstrap-server localhost:9092
```

To create topics:
```
/opt/kafka/bin/kafka-topics.sh --create --topic cstr --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1

/opt/kafka/bin/kafka-topics.sh --create --topic pid_control --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
```

To run apps:
```
faust -A pid_controller worker -l info

faust -A cstr_model  worker -l info
```