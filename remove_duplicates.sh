#!/bin/bash

#https://unix.stackexchange.com/a/383107
fdupes -r -f -o name //share/pictures/ /share/to_be_organized  >/share/homes/john/listtodel

sed -i '/^\s*$/d' listtodel
