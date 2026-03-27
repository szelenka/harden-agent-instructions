.PHONY: lint render diff

lint:
	helm lint charts/ml-proxy

render:
	helm template ml-proxy charts/ml-proxy -f environments/dev/values.yaml

diff:
	helmfile -e dev diff
