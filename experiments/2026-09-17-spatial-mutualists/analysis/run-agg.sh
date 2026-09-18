#!/usr/bin/env bash

DATA_DIR=/mnt/scratch/lalejini/data/2026-gvsu-symbiosis-env-change/2026-09-17-spatial-mutualists/
DUMP_DIR=./dump
FINAL_UPDATE=200000
TS_UNITS=interval
TS_RES=1

python3 aggregate.py \
  --data_dir ${DATA_DIR} \
  --dump_dir ${DUMP_DIR} \
  --summary_update ${FINAL_UPDATE} \
  --time_series_units ${TS_UNITS} \
  --time_series_resolution ${TS_RES}