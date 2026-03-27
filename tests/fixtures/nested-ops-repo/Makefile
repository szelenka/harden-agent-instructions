.PHONY: verify

verify:
	$(MAKE) -C services/ml-proxy lint
	$(MAKE) -C services/ml-proxy render
	$(MAKE) -C services/wordcloud diff
