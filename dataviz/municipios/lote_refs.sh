#!/bin/sh
# Gera as referências pelo método antigo (um município por vez, via CLI do duckdb).
cd ~/painel_lote && rm -f ref/FIM
for m in 3303401 2514107 1302603 3550308 $(cat ref/extra.txt); do
  python3 extract_municipio.py $m > ref/$m.json 2> ref/$m.err
done
echo fim > ref/FIM
