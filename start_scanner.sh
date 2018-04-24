#!/bin/sh

# Phase 1: Run the crawler
scrapy crawl scrapeTarget

# Phase 2 & 3: Generate and Inject the Payloads 
declare -a categories=("SQL Injection" "Server Side Code Injection" "Directory Traversal" "Cross Site Request Forgery" "Open Redirect" "Shell Command Injection")

for category in "${categories[@]}"
do
	python payloadInjection.py "$category"
done

# Phase 4: Generate the Exploits
python generateExploits.py
