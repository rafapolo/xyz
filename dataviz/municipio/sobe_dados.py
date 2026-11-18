#!/usr/bin/env python3
"""Sobe data/ (um JSON por município + municipios.json + cobertura.json) para o bucket
público `xyz-municipio` do Hetzner Object Storage (hel1). O painel lê direto de lá:
https://xyz-municipio.hel1.your-objectstorage.com/<código IBGE>.json

Cada objeto vai comprimido (gzip, mtime=0, então o mesmo JSON dá o mesmo arquivo e o
MD5 é estável) com `Content-Encoding: gzip`, `Content-Type: application/json` e leitura
pública. O CORS do bucket libera só o domínio do site (ver --cors). Só sobe o que mudou:
compara o MD5 do gzip com o ETag do objeto (upload simples, então ETag = MD5).

Credenciais: variáveis de ambiente ou `.env` na raiz do repo (fora do git):
S3_ENDPOINT, S3_REGION, S3_BUCKET, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY. Nunca são impressas.

Uso: python3 dataviz/municipio/sobe_dados.py [--seco] [--apaga] [--cors] [--cria] [pasta]
  --seco   só lista o que mudaria
  --apaga  remove do bucket o que não existe mais na pasta
  --cors   reaplica a política de CORS
  --cria   cria o bucket (leitura pública por objeto) se ele não existir
"""
import gzip
import hashlib
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import boto3
from botocore.config import Config

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
ORIGENS_CORS = ["https://xn--2dk.xyz", "https://www.xn--2dk.xyz", "http://localhost:8000", "http://127.0.0.1:8000"]


def carrega_env():
    env = RAIZ / ".env"
    if env.exists():
        for linha in env.read_text().splitlines():
            linha = linha.strip()
            if linha and not linha.startswith("#") and "=" in linha:
                k, v = linha.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    faltam = [k for k in ("S3_ENDPOINT", "S3_BUCKET", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY") if not os.environ.get(k)]
    if faltam:
        sys.exit("sobe_dados: faltam no ambiente ou em .env: " + ", ".join(faltam))


def comprime(caminho):
    return gzip.compress(caminho.read_bytes(), compresslevel=9, mtime=0)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    seco, apaga = "--seco" in sys.argv, "--apaga" in sys.argv
    carrega_env()
    pasta = Path(args[0]) if args else AQUI / "data"
    bucket = os.environ["S3_BUCKET"]
    s3 = boto3.client("s3", endpoint_url=os.environ["S3_ENDPOINT"], region_name=os.environ.get("S3_REGION", "hel1"),
                      aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"], aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
                      config=Config(max_pool_connections=32, retries={"max_attempts": 5, "mode": "standard"}))
    if "--cria" in sys.argv and bucket not in [b["Name"] for b in s3.list_buckets()["Buckets"]]:
        s3.create_bucket(Bucket=bucket)
        print(f"bucket {bucket} criado")
    if "--cors" in sys.argv or "--cria" in sys.argv:
        s3.put_bucket_cors(Bucket=bucket, CORSConfiguration={"CORSRules": [{
            "AllowedOrigins": ORIGENS_CORS, "AllowedMethods": ["GET", "HEAD"], "AllowedHeaders": ["*"],
            "ExposeHeaders": ["Content-Length", "Content-Encoding", "ETag"], "MaxAgeSeconds": 86400}]})
        print("CORS aplicado:", ", ".join(ORIGENS_CORS))

    remoto = {}
    for pg in s3.get_paginator("list_objects_v2").paginate(Bucket=bucket):
        for o in pg.get("Contents", []):
            remoto[o["Key"]] = o["ETag"].strip('"')
    local = {p.name: p for p in sorted(pasta.glob("*.json")) if not p.name.startswith("_")}

    def trabalha(item):
        chave, caminho = item
        corpo = comprime(caminho)
        if remoto.get(chave) == hashlib.md5(corpo).hexdigest():
            return chave, 0, 0
        if not seco:
            s3.put_object(Bucket=bucket, Key=chave, Body=corpo, ACL="public-read", ContentType="application/json",
                          ContentEncoding="gzip", CacheControl="public, max-age=3600")
        return chave, 1, len(corpo)

    subiu = tam = 0
    with ThreadPoolExecutor(16) as ex:
        for i, (chave, mudou, n) in enumerate(ex.map(trabalha, local.items()), 1):
            subiu += mudou
            tam += n
            if i % 500 == 0:
                print(f"  {i}/{len(local)} conferidos, {subiu} {'a subir' if seco else 'subidos'}", flush=True)
    sobra = sorted(set(remoto) - set(local))
    if apaga and not seco:
        for k in sobra:
            s3.delete_object(Bucket=bucket, Key=k)
    print(f"{len(local)} arquivos em {pasta}; {subiu} {'mudariam' if seco else 'subidos'} ({tam / 1e6:.1f} MB gzip); "
          f"{len(sobra)} objetos no bucket sem arquivo local{' (apagados)' if apaga and not seco else ''}")
    print(f"bucket {bucket}: https://{bucket}.hel1.your-objectstorage.com/")


if __name__ == "__main__":
    main()
