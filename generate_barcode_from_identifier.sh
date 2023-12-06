#!/usr/bin/bash

name=$1
echo -n $name | dmtxwrite --symbol-size=8x18 -d 1 -m 1 > "$name-unrot.png"
convert "$name-unrot.png" -rotate 270 "$name.png"
rm "$name-unrot.png"
mv "$name.png" barcode_cache