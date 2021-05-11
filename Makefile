NAME := bots
SHELL := /bin/bash
VERSION := $(shell cat VERSION)
COMMIT_SHA := $(shell git rev-parse HEAD)
CHROMEDRIVERPATH := $$PWD/chromedriver

.PHONY: build deploy test-scrape clean test-lambda

clean:
	rm -rf package
	rm -rf .venv
	rm -rf dist
	rm -rf temp
	rm -rf tf/dist

/dist/dependencies-layer.zip:
	mkdir -p dist
	mkdir -p package
	mkdir -p package/bin

	# # Fetch lambda chrome
	bin/get_lambda_chrome.sh

	# # Fetch chromedriver
	bin/get_chromedriver.sh

	# # Package dependencies
	mkdir -p .venv
	pipenv sync
	cp -a .venv/lib/python3.7/site-packages/. package/

	# copy over python helper files
	cp -R evict_tools/. package/evict_tools

	# Add dependencies to layer .zip
	cd package && zip -r9 ../dist/dependencies-layer.zip . && cd ..

/dist/eviction-bot-lambda.zip:
	mkdir -p dist
	zip -g dist/eviction-bot-lambda.zip *.py

build: /dist/dependencies-layer.zip /dist/eviction-bot-lambda.zip
	echo "Built app..."
	cp -r dist tf/
	echo "Moved into tf directory."

deploy:
	cd tf && terraform apply && cd ..

test-scrape:
	python3 runner.py

test-lambda:
	python3 evict_tools/message.py