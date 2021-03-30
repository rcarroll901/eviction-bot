#!/bin/bash

# This script will download a lambda-compatible binary of headless-chromium built from the stable channel of chromium

mkdir temp && cd temp
npm init -y
npm i @serverless-chrome/lambda@v1.0.0-37
cp 'node_modules/@serverless-chrome/lambda/dist/headless-chromium' ../package/bin/headless-chromium
cd .. && rm -rf temp/
