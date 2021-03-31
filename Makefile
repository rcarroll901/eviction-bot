NAME := bots
SHELL := /bin/bash
VERSION := $(shell cat VERSION)
COMMIT_SHA := $(shell git rev-parse HEAD)
CHROMEDRIVERPATH := $$PWD/chromedriver

.PHONY: build deploy test-scrape clean

clean:
	rm -rf package
	rm -rf dist
	rm -rf temp
	rm -rf tf/dist

/dist/dependencies-layer.zip:
	mkdir -p dist
	mkdir -p package/bin

	# # Fetch lambda chrome
	bin/get_lambda_chrome.sh

	# # Fetch chromedriver
	bin/get_chromedriver.sh

	# # Package dependencies
	pip3 install --target package -r requirements.txt

	# Add dependencies to layer .zip
	cd package && zip -r9 ../dist/dependencies-layer.zip . && cd ..

	# Clean up
	#rm -rf package

/dist/eviction-bot-lambda.zip:
	mkdir -p dist
	zip -g dist/eviction-bot-lambda.zip *.py google_secret.json

build: /dist/dependencies-layer.zip /dist/eviction-bot-lambda.zip
	echo "Built app..."
	cp -r dist tf/
	echo "Moved into tf directory."

deploy:
	cd tf && terraform apply && cd ..

test-scrape:
	python3 runner.py