#!/bin/bash

args=( $@ )
set --
exec "${args[@]}"
