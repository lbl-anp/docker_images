# Based on https://github.com/LINKIT-Group/dockerbuild/blob/master/Makefile
# Used under the MIT license

# Make variables
SHELL := /bin/bash
PROJECT_NAME := lblanp/$(shell basename $(realpath .))
GIT_HASH := $(shell git log -1 --pretty=%h)
BUILD_CMD_BASE := docker build -t $(PROJECT_NAME)
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
	@echo '  build_<name>    build docker image and tag as latest'
	@echo '  rebuild_<name>  force (--no-cache) build docker image and tag as latest'
	@echo '  push_<name>     push the image to the default registry (typically dockerhub)'
	@echo ''
	@echo 'NAMES:'
	@echo '  melodic_l4t'
	@echo '  noetic_arm64v8'

build_melodic_l4t:
	$(BUILD_CMD_BASE)_melodic_l4t:latest -f Dockerfile.melodic.l4t .

rebuild_melodic_l4t:
	$(BUILD_CMD_BASE)_melodic_l4t:latest -f Dockerfile.melodic.l4t . --no-cache

push_melodic_l4t:
	docker push $(PROJECT_NAME)_melodic_l4t:latest

build_noetic_arm64v8:
	$(BUILD_CMD_BASE)_noetic_arm64v8:latest -f Dockerfile.noetic.arm64v8 .

rebuild_noetic_arm64v8:
	$(BUILD_CMD_BASE)_noetic_arm64v8:latest -f Dockerfile.noetic.arm64v8 . --no-cache

push_noetic_arm64v8:
	docker push $(PROJECT_NAME)_noetic_arm64v8:latest
