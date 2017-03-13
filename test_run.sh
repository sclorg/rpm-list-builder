#!/bin/bash

make setup-uninstall
make setup-install

$HOME/.local/bin/rhscl-builder \
  -D local \
  -s "$HOME/rh/ror50" \
  -C "rh-ror50-test" \
  "$HOME/git/scl-builder/rhscl-rebuild-recipes/ror_test.yml" \
  rh-ror50
