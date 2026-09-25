#!/usr/bin/env bash
# Sequential, polite download of the 30 binary TabArena-v0.1 datasets from OpenML.
# One request at a time, at most two retries per file, no credentials, no query
# parameters. Reads the plan written from the OpenML dataset descriptions:
#   name <TAB> task_id <TAB> data_id <TAB> arff_url <TAB> parquet_url <TAB> md5
# Usage (Git Bash):  bash scripts/download_raw.sh
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PLAN="$ROOT/build/download_plan.tsv"
LOG="$ROOT/build/download_log.tsv"
: > "$LOG"

fetch() {  # url, out
  local url="$1" out="$2" code tries=0
  if [ -s "$out" ]; then echo -e "skip\t-\t$(stat -c %s "$out")\t$url\t$out" >> "$LOG"; return 0; fi
  while [ $tries -le 2 ]; do
    code=$(curl -sS -L --max-time 1800 -o "$out.part" -w "%{http_code}" "$url" 2>>"$LOG.err")
    if [ "$code" = "200" ] && [ -s "$out.part" ]; then
      mv "$out.part" "$out"
      echo -e "ok\t$code\t$(stat -c %s "$out")\t$url\t$out" >> "$LOG"
      return 0
    fi
    rm -f "$out.part"; tries=$((tries+1)); sleep 5
  done
  echo -e "FAIL\t$code\t0\t$url\t$out" >> "$LOG"
  return 1
}

while IFS=$'\t' read -r name tid did arff pq md5; do
  d="$ROOT/raw/$name"; mkdir -p "$d"
  fetch "$arff" "$d/${arff##*/}"; sleep 1
  fetch "$pq"   "$d/${pq##*/}";   sleep 1
done < "$PLAN"
echo "DONE" >> "$LOG"
