#!/bin/bash

SOAR_URL="http://soar:6000/alert"
SECRET="super-long-secret-random-64chars"

echo "=========================================="
echo " SOAR TEST SCENARIOS"
echo "=========================================="

run_test () {
  TITLE=$1
  PAYLOAD=$2

  echo ""
  echo "▶ $TITLE"
  echo "$PAYLOAD"
  echo "------------------------------------------"

  kubectl run curl-test --rm -i --image=curlimages/curl --restart=Never -- \
    curl -s -X POST ${SOAR_URL} \
      -H "Content-Type: application/json" \
      -d "$PAYLOAD"

  echo ""
}

# 1. Whitelisted IP
run_test "Whitelisted IP" '{
  "secret": "'"$SECRET"'",
  "src_ip": "192.168.1.42",
  "verdict": "DDoS",
  "probability": 0.99
}'

# 2. Low probability
run_test "Low probability DDoS" '{
  "secret": "'"$SECRET"'",
  "src_ip": "9.9.9.9",
  "verdict": "DDoS",
  "probability": 0.40
}'

# 3. Real DDoS
run_test "Real DDoS (BLOCK)" '{
  "secret": "'"$SECRET"'",
  "src_ip": "8.8.8.8",
  "verdict": "DDoS",
  "probability": 0.99
}'

# 4. Benign traffic
run_test "Benign verdict" '{
  "secret": "'"$SECRET"'",
  "src_ip": "7.7.7.7",
  "verdict": "Benign",
  "probability": 0.99
}'

# 5. Invalid secret
run_test "Invalid secret" '{
  "secret": "wrong-secret",
  "src_ip": "6.6.6.6",
  "verdict": "DDoS",
  "probability": 0.99
}'
