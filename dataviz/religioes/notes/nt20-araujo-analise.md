# NT 20 (CEM/Fapesp, Victor Araújo) — o que dá pra atualizar com nossos dados

Fonte analisada: [NT20.pdf](https://centrodametropole.fflch.usp.br/sites/centrodametropole.fflch.usp.br/files/cem_na_midia_anexos/NT20.pdf) — "Surgimento, trajetória e expansão das Igrejas Evangélicas no território brasileiro ao longo do último século (1920-2019)", Victor Araújo, CEM-Cepid/Fapesp, 17/05/2023.

## O que ele fez (resumo técnico)

- Fonte: `br_me_cnpj` (Receita Federal, via Brasil.io/DADOSCOPE), filtrado por CNAE **94.91-0-00** ("Atividades de organizações religiosas ou filosóficas") → 152.142 estabelecimentos ativos em 2019.
- Método: dicionário de termos (Tabela 1) + `str_detect` (R/`stringi`) na razão social, classificando em 4 categorias: Missionária, Pentecostal, Neopentecostal, Não determinada. Só evangélicos — não cobre católica, espírita, umbanda/candomblé, etc.
- Unidade de análise: **UF** (agregado), nunca município nem endereço — ele não geolocaliza, só conta por estado/ano.
- Período: 1922–2019 (data de corte da extração).
- Validação: correlaciona a taxa de igrejas/100mil hab. por UF (2010) com % evangélicos do Censo IBGE 2010.

## O que "nossos dados" já têm hoje

1. **`docs/viz-uf`** (`scripts/extrai_estados_cnpj.py`, `scripts/build_br_national.py`): geolocalização **ponto-a-ponto** de todo estabelecimento CNPJ ativo, casado contra o CNEFE (Censo IBGE 2022) por (CEP, logradouro, número) com fallback de interpolação/fuzzy match. Cobertura atual: 26,86M estabelecimentos ativos, 67,5% geolocalizados (18,1M pontos), as 27 UFs (DF zerado por gap de fonte). **Ainda não filtrado por CNAE religioso** — hoje é a base genérica de todos os CNPJs, não isolamos igrejas.
2. **`dataviz/religioes/data.json`**: perfil religioso por **município** (não UF) a partir do Censo IBGE, comparando **2010 vs 2022** (5.565 e 5.570 municípios) — autodeclaração de religião pessoa a pessoa, todas as religiões, não só evangélica.
3. Snapshot CNPJ mensal (`ano*100+mes` mais recente na mirror), então dá pra estender a série dele até o presente, não só 2019.

## Tabelas/figuras do NT20, uma a uma

| # | O que é | Dá pra atualizar/estender? | Como |
|---|---|---|---|
| Tabela 1 (dicionário de termos) | Léxico p/ classificar razão social em 4 categorias evangélicas | **Sim, direto** | Reaplicar o mesmo `str_detect` (ou regex equivalente em SQL/DuckDB) sobre `br_me_cnpj.estabelecimentos` filtrado por CNAE `9491000` — reproduzível 1:1, e dá pra estender o dicionário pra outras religiões usando o Censo como gabarito |
| Fig. 1 — igrejas ativas por denominação (1922-2019) | Série temporal, contagem nacional | **Sim** | Mesma query, sem filtrar UF, agrupando por ano de abertura (`data_inicio_atividade`) — estende até 2026 com o snapshot atual |
| Fig. 2 — novas igrejas por ano (1922-2019) | Aberturas por ano | **Sim** | Idem Fig. 1, mas `COUNT(*) GROUP BY ano_abertura` — cobre o ciclo pós-2019 que ele não viu (pandemia, eleições 2022) |
| Fig. 3 — igrejas/100mil hab. por UF em 2019 | Choropleth por UF | **Sim, e melhor** | Já temos ponto geolocalizado, não precisa de choropleth por UF — dá pra fazer isso como camada de densidade real no mapa que já existe em `docs/viz-uf`, não um agregado estático |
| Fig. 4 — mesma métrica, 6 décadas (1970-2019), painéis A-F | Small multiples por década | **Sim** | Estende pra década de 2020 (painel G); com geolocalização por ponto dá pra animar a expansão têmporo-espacial em vez de 6 mapas estáticos |
| Fig. 5 — Pentecostal vs. outras denominações/100mil (UFs, 2019) | Scatter de correlação | **Sim** | Reproduzível com dado mais recente; com ponto geolocalizado dá pra rodar por **município**, não só por UF — resolução muito maior que o paper original |
| Fig. 6 — correlação com Censo IBGE 2010 | Validação do método | **Sim, e melhor** | Ele só validou contra 2010 porque era o censo disponível em mai/2023. **Nós já temos o Censo 2022** (`dataviz/religioes/data.json`) — dá pra validar contra o censo mais recente, coisa que ele não pôde fazer |
| Apêndice A (Fig. A.1-A.4) — mesma Fig. 4, por denominação | Painéis por década x denominação | **Sim**, mesma extensão da Fig. 4 |
| Apêndice B (Fig. B.1-B.3) — validação por denominação vs Censo 2010 | Scatter de validação | **Sim, e melhor**, mesma vantagem da Fig. 6 (validar contra 2022) |

## O que dá pra fazer que ele não fez (diferencial real, não só "atualização")

1. **Geolocalização de verdade (endereço → lat/lng), não agregado por UF.** Ele nunca teve isso — é o maior salto de resolução possível sobre o trabalho dele.
2. **Todas as religiões, não só evangélica.** O CNAE `9491000` cobre qualquer organização religiosa — católica, espírita, umbanda/candomblé, judaica, etc. também têm CNPJ. O dicionário dele é evangélico-only por escolha, não por limitação da fonte.
3. **Validação cruzada 2010 → 2022** em vez de só 2010 (o Censo 2022 nem existia quando ele escreveu).
4. **Granularidade município**, não só UF — nosso `data.json` já é por município; a base CNPJ×CNEFE também permite agregar em qualquer nível (bairro, até).
5. **Série viva/atualizável mensalmente** (snapshot da Receita Federal), contra o corte fixo dele em 2019.

## Pré-requisito antes de gerar qualquer uma dessas atualizações

`docs/viz-uf/dados/*.bin.gz` hoje é **todo CNPJ ativo, sem filtro de CNAE**. Pra replicar/estender o NT20 precisamos primeiro:
1. Rodar uma variante de `extrai_estados_cnpj.py` filtrando `WHERE cnae_fiscal = '9491000'` (ou código equivalente na mirror local — checar nome exato da coluna).
2. Aplicar o dicionário de classificação (Tabela 1, e estendido pra outras religiões) sobre `razao_social`.
3. Só então cruzar com o Censo 2022 (`data.json`) por município.

Nenhum desses três passos está feito ainda — é o próximo trabalho, não algo que já existe hoje na pipeline.
