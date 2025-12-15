#!/usr/bin/env bash

echo "======================================"
echo "  K8S OUTSIDE TRAFFIC GENERATOR"
echo "======================================"

kubectl run web-traffic --rm -i \
  --image=curlimages/curl \
  --restart=Never -- \
  sh -c "
    echo '[+] example.com';
    curl -s https://example.com > /dev/null;

    echo '[+] google.com';
    curl -s https://www.google.com > /dev/null;

    echo '[+] github api';
    curl -s https://api.github.com > /dev/null;

    echo '[+] cloudflare';
    curl -s https://www.cloudflare.com > /dev/null;
  "

