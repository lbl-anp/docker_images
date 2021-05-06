# Based on https://github.com/LINKIT-Group/dockerbuild/blob/master/Makefile
# Used under the MIT license

# Make variables
SHELL := /bin/bash
PROJECT_NAME := lblanp/$(shell basename $(realpath .))
PROJECT_TAG := $(shell git log -1 --pretty=%h)
TAGGED_IMAGE := $(PROJECT_NAME):$(PROJECT_TAG)
LATEST_IMAGE := $(PROJECT_NAME):latest
BUILD_IT := docker build -t $(TAGGED_IMAGE) .
TAG_LATEST := docker tag $(TAGGED_IMAGE) $(LATEST_IMAGE)

# No files to check for these targets
.PHONY: run help build rebuild

run:
	docker run -it --rm $(LATEST_IMAGE)

help:
	@echo ''
	@echo 'Usage: make [OPTION]'
	@echo ''
	@echo 'OPTIONS:'
	@echo '  run      run latest docker image (default)'
	@echo '  build    build docker image and tag as latest'
	@echo '  rebuild  force (--no-cache) build docker image and tag as latest'
	@echo ''

build:
	$(BUILD_IT)
	$(TAG_LATEST)

rebuild:
	$(BUILD_IT) --no-cache
	$(TAG_LATEST)
