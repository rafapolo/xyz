#!/bin/bash
# Extrai o JSON de um município rodando o extrator no beelink.
# uso: ./extract_municipio.sh <id_municipio> <slug>
# ex.: ./extract_municipio.sh 3303401 nova_friburgo
set -euo pipefail
ID="${1:?id_municipio (7 dígitos IBGE)}"
SLUG="${2:?slug do arquivo de saída (ex.: nova_friburgo)}"
DIR="$(cd "$(dirname "$0")" && pwd)"
scp -q "$DIR/extract_municipio.py" beelink:/tmp/extract_municipio.py
ssh beelink "python3 /tmp/extract_municipio.py $ID" > "$DIR/data/$SLUG.json"
echo "ok: data/$SLUG.json"
