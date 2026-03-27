.PHONY: lint render

lint:
	helm lint ../../charts/ml-proxy

render:
	helm template ml-proxy ../../charts/ml-proxy -f ../../clusters/dev/values.yaml
