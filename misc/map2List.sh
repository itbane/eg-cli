#!/bin/bash

declare -A ms

ms=(["P"]=2 ["M"]=8 ["R"]=7 ["H"]=3 ["S"]=7 ["F"]=5 ["L"]=4)


if [ $# -ne 1 ];then
  echo "Parameter 1 benmötigt: Datei mit map-Daten"
fi

cp $1 $1.map
for mt in "${!ms[@]}"; do
  echo "$mt"
  sed -i "s/^.*map_${mt}.*$/${ms[$mt]} - \0/" $1.map
done
sed -i '/tr>$/d' $1.map
sed -i 's/^\(.\).*data-posx="1".*$/[\1,/' $1.map
sed -i 's/^\(.\).*data-posx="119".*$/\1],/' $1.map
sed -i 's/^\(.\).*data-posx="[0-9]\{1,3\}".*$/\1,/' $1.map
tr '\n' ' ' < $1.map > $1.list
sed -i 's/^/[/' $1.list
sed -i 's/, *$/]/' $1.list
