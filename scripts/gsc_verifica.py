#!/usr/bin/env python3
"""Verifica https://xn--2dk.xyz/ no Search Console por arquivo HTML (sem mexer no DNS).

  pega-token  pede ao Google o arquivo de verificação e o grava na raiz do repo (google<...>.html)
  confirma    depois que o arquivo estiver no ar: verifica o site e o adiciona ao Search Console

Escopos: Search Console + Site Verification; o token fica em ~/.config/gsc/token.json (chmod 600).
Uso: uv run --with google-auth-oauthlib --with google-api-python-client scripts/gsc_verifica.py pega-token|confirma
"""
import os
import sys
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

DIR = Path.home() / ".config/gsc"
TOKEN = DIR / "token.json"
ESCOPO = ["https://www.googleapis.com/auth/webmasters", "https://www.googleapis.com/auth/siteverification"]
SITE = "https://xn--2dk.xyz/"
RAIZ = Path(__file__).resolve().parent.parent


def credenciais():
    cred = Credentials.from_authorized_user_file(TOKEN) if TOKEN.exists() else None
    if cred and not set(ESCOPO) <= set(cred.scopes or []):  # token antigo, com menos permissões
        cred = None
    if cred and cred.expired and cred.refresh_token:
        cred.refresh(Request())
    if not cred or not cred.valid:
        cred = InstalledAppFlow.from_client_secrets_file(DIR / "client_secrets.json", ESCOPO).run_local_server(port=0)
    TOKEN.write_text(cred.to_json())
    os.chmod(TOKEN, 0o600)
    return cred


def main():
    passo = sys.argv[1] if len(sys.argv) > 1 else ""
    cred = credenciais()
    sv = build("siteVerification", "v1", credentials=cred, cache_discovery=False)
    alvo = {"site": {"type": "SITE", "identifier": SITE}, "verificationMethod": "FILE"}
    if passo == "pega-token":
        nome = sv.webResource().getToken(body=alvo).execute()["token"]
        (RAIZ / nome).write_text(f"google-site-verification: {nome}")
        print(f"arquivo: {nome}")
    elif passo == "confirma":
        sv.webResource().insert(verificationMethod="FILE", body={"site": alvo["site"]}).execute()
        print(f"verificado: {SITE}")
        build("searchconsole", "v1", credentials=cred, cache_discovery=False).sites().add(siteUrl=SITE).execute()
        print(f"adicionado ao Search Console: {SITE}")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
