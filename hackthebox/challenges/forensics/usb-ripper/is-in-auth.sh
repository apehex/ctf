#!/bin/bash

while read serial; do
  if ! grep -qia "$serial" auth.json; then echo "$serial"; fi
done
