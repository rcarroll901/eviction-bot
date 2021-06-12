NAME := bots
SHELL := /bin/bash
VERSION := $(shell cat VERSION)
COMMIT_SHA := $(shell git rev-parse HEAD)
CHROMEDRIVERPATH := $$PWD/chromedriver

.PHONY: build deploy test-scrape clean test-lambda test-flow

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

	# # Package dependencies
	mkdir -p .venv
	pipenv sync
	cp -a .venv/lib/python3.9/site-packages/* package/


	# Add dependencies to layer .zip
	cd package && zip -r9 ../dist/dependencies-layer.zip . && cd ..

/dist/eviction-bot-lambda.zip:
	mkdir -p dist
	zip -g dist/eviction-bot-lambda.zip *.py evict_tools/*

build: /dist/dependencies-layer.zip /dist/eviction-bot-lambda.zip
	echo "Built app..."
	cp -r dist tf/
	echo "Moved into tf directory."

deploy:
	cd tf && terraform apply && cd ..

test-flow:
	python3 runner.py

test-scrape:
	python3 evict_tools/scrape.py

test-lambda:
	python3 evict_tools/message.py

test-persist:
	python3 evict_tools/persist.py