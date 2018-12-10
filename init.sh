#!/bin/sh

git submodule update --init --recursive 
echo "Updated submodules."
cp pre-commit .git/hooks/pre-commit

