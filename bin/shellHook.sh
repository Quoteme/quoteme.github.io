#!/usr/bin/env bash

export AUTHOR="Luca Leon Happel"
# print the following text in yellow
echo -e "\033[33mWelcome $AUTHOR\033[0m"
echo -e 'Run debug-server with "\033[33mblogServe\033[0m", or update using "\033[33mblogUpdate\033[0m"'
alias blogServe="jekyll serve --watch --live-reload --host"
alias blogUpdate="nix-shell -p bundler -p bundix --run 'bundler update; bundler lock; bundler package --no-install --path vendor; bundix; rm -rf vendor' && exit"


alias blogNewPost="./bin/newPost.sh"
