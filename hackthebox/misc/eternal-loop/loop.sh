#!/bin/bash

archive=${1:-""}
password=$(unzip -l "$archive" | sed -n 4p | perl -ne 'm/([0-9]+).zip/g && print $1')
while file "$archive" | grep -qia compression; do
  echo "+ $archive"
  archive=$(unzip -P "$password" "$archive" | perl -ne 'm/inflating:\s+(.+zip)/g && print $1')
  password=$(unzip -l "$archive" | sed -n 4p | perl -ne 'm/([0-9]+).zip/g && print $1')
done

