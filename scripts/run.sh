#!/bin/bash

rm -rf reqs preds
python3 group_requests.py
export YAGNA_APPKEY=$(yagna app-key list --json | jq -r .values[0][1])
for f in "reqs/*.json"
do
  echo "Requesting predicting for $f"
  filename = $(basename -- "$f")
  extension = "${filename##*.}"
  model = "${filename%.*}"
  node requestor/requestor.js --model=$model
done
echo "Results are saved in ./out"
python3 write_preds_to_db.py
echo "Done!"