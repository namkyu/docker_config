#!/bin/bash

echo "Testing Kafka producer - sending messages to order topic..."

# 각 메시지를 개별적으로 전송
echo '{"orderId": "ORD-001", "customerId": "CUST-123", "amount": 99.99, "timestamp": "'$(date -Iseconds)'"}' | \
docker exec -i kafka1 kafka-console-producer --bootstrap-server kafka1:29092 --topic order

echo '{"orderId": "ORD-002", "customerId": "CUST-456", "amount": 149.50, "timestamp": "'$(date -Iseconds)'"}' | \
docker exec -i kafka1 kafka-console-producer --bootstrap-server kafka1:29092 --topic order

echo '{"orderId": "ORD-003", "customerId": "CUST-789", "amount": 75.25, "timestamp": "'$(date -Iseconds)'"}' | \
docker exec -i kafka1 kafka-console-producer --bootstrap-server kafka1:29092 --topic order

echo '{"orderId": "ORD-004", "customerId": "CUST-123", "amount": 200.00, "timestamp": "'$(date -Iseconds)'"}' | \
docker exec -i kafka1 kafka-console-producer --bootstrap-server kafka1:29092 --topic order

echo '{"orderId": "ORD-005", "customerId": "CUST-999", "amount": 50.75, "timestamp": "'$(date -Iseconds)'"}' | \
docker exec -i kafka1 kafka-console-producer --bootstrap-server kafka1:29092 --topic order

echo "Test messages sent to order topic!"