#!/bin/bash
echo "Testing Kafka consumer - reading messages from order topic..."
echo "Press Ctrl+C to stop consuming messages"
echo "----------------------------------------"

# 주문 처리 그룹
winpty docker exec -it kafka1 kafka-console-consumer \
  --bootstrap-server kafka1:29092 \
  --topic order \
  --group order-processing-group

echo ""
echo "Consumer test completed!"