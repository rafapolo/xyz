#!/usr/bin/env python3
"""Envia os sitemaps do xn--2dk.xyz ao Google Search Console e mostra o estado deles.

Usa o cliente OAuth de ~/.config/gsc/client_secrets.json. Na primeira vez abre o navegador
para você autorizar o escopo do Search Console; o token fica em ~/.config/gsc/token.json
(chmod 600) e as próximas execuções não pedem nada. Nada é impresso além de URLs e estados.

Uso: uv run --with google-auth-oauthlib --with google-api-python-client scripts/gsc_envia.py
"""
import os
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

DIR = Path.home() / ".config/gsc"
TOKEN = DIR / "token.json"
ESCOPO = ["https://www.googleapis.com/auth/webmasters", "https://www.googleapis.com/auth/siteverification"]
SITEMAPS = ["https://xn--2dk.xyz/sitemap.xml", "https://xn--2dk.xyz/sitemap-municipios.xml"]
CANDIDATOS = ["sc-domain:xn--2dk.xyz", "https://xn--2dk.xyz/"]  # sem DNS: scripts/gsc_verifica.py verifica o prefixo por arquivo


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
    gsc = build("searchconsole", "v1", credentials=credenciais(), cache_discovery=False)
    sites = {s["siteUrl"]: s["permissionLevel"] for s in gsc.sites().list().execute().get("siteEntry", [])}
    site = next((c for c in CANDIDATOS if c in sites), None)
    if not site:
        print("O xn--2dk.xyz não está verificado nesta conta do Search Console. Sites da conta:")
        for s, nivel in sites.items():
            print(f"  {s} ({nivel})")
        print("Adicione a propriedade de domínio xn--2dk.xyz em https://search.google.com/search-console e rode de novo.")
        return
    print(f"propriedade: {site} ({sites[site]})")
    for sm in SITEMAPS:
        gsc.sitemaps().submit(siteUrl=site, feedpath=sm).execute()
        print(f"enviado: {sm}")
    for s in gsc.sitemaps().list(siteUrl=site).execute().get("sitemap", []):
        n = sum(int(c.get("submitted", 0)) for c in s.get("contents", []))
        print(f"  {s['path']}: enviado {s.get('lastSubmitted', '-')}, baixado {s.get('lastDownloaded', 'ainda não')}, "
              f"{n} URLs, {'pendente' if s.get('isPending') else 'processado'}, erros {s.get('errors', 0)}")


if __name__ == "__main__":
    main()
