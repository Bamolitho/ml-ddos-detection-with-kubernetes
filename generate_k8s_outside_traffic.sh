#!/usr/bin/bash

kubectl run web-traffic --rm -it \
  --image=busybox \
  --restart=Never -- \
  sh -c "
    wget -qO- https://example.com > /dev/null;
    wget -qO- https://google.com > /dev/null;
    wget -qO- https://api.github.com > /dev/null;
  "

