#!/bin/bash
set -e

export PATH=/home/[YOU]/.local/bin:$PATH

cd /home/[YOU]/mlg/pool

base="/home/[YOU]/mlg/pool"
rm -rf $base/reqs/* $base/requestor/out
$base/../venv/bin/python3 $base/group_requests.py

if find $base/reqs -name *.json  -maxdepth 0 -empty | grep -q "."; then
    echo "nothing to be done"
    exit 0
fi


export YAGNA_APPKEY=$(yagna app-key list --json | jq -r .values[0][1])
yagna payment init --sender

for f in $base/reqs/*.json
do
  echo "Requesting predicting for $f"
  model=$(basename "$f" .json)
  node $base/requestor/requestor.js --model=$model
done

$base/../venv/bin/python3 $base/write_preds_to_db.py
