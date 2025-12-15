#!/usr/bin/bash

eval $(minikube docker-env)

kubectl delete -k k8s/overlays/dev --ignore-not-found
kubectl delete -k k8s/base --ignore-not-found
kubectl delete deployment,daemonset,svc,configmap,secret \
  -l app=dashboard --ignore-not-found

kubectl delete deployment,daemonset,svc,configmap,secret \
  -l app=soar --ignore-not-found

kubectl delete deployment,daemonset,svc,configmap,secret \
  -l app=mysql --ignore-not-found

kubectl delete daemonset orchestrator --ignore-not-found

eval $(minikube docker-env)
docker rmi -f \
  ml-ddos-dashboard:latest \
  ml-ddos-soar:latest \
  ml-ddos-orchestrator:latest

docker rmi -f mysql:8.0
kubectl delete pvc --all
kubectl delete pv --all
kubectl delete pod --all --force --grace-period=0

minikube delete
#minikube start

#eval $(minikube docker-env)
