#!/bin/bash

rabbitmqctl await_startup

USER=nklee
PW=1234
VHOST=test

create_user() {
	rabbitmqctl add_vhost $VHOST
	rabbitmqctl add_user $USER $PW
	rabbitmqctl set_user_tags $USER administrator
	rabbitmqctl set_permissions -p $VHOST $USER ".*" ".*" ".*"
}

create_exchanges() {
	curl -i -u $USER:$PW -H "content-type:application/json" \
	-XPUT -d'{"type":"fanout","durable":false}' \
	http://localhost:15672/api/exchanges/$VHOST/janus-exchange
}

create_queues() {
	curl -i -u $USER:$PW -H "content-type:application/json" \
	-XPUT -d'{"auto_delete":false,"durable":false}' \
	http://localhost:15672/api/queues/$VHOST/janus-events
}

create_bind() {
	curl -i -u $USER:$PW -H "content-type:application/json" \
	-XPOST -d'{}' \
	http://localhost:15672/api/bindings/$VHOST/e/janus-exchange/q/janus-events
}

echo "========================================="
echo "create_user"
echo "========================================="
create_user
sleep 3

echo "========================================="
echo "create_exchanges"
echo "========================================="
create_exchanges
sleep 3

echo "========================================="
echo "create_queues"
echo "========================================="
create_queues
sleep 3

echo "========================================="
echo "create_bind"
echo "========================================="
create_bind
