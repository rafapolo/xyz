**ミxplorando Novas Tecnologias Cartográficas**

Hoje, através de uma tela, um indíviduo pode inter-relacionar, interagir, representar e navegar entre milhões de dados. O avanço nas tecnologias ampliou drasticamente nossa capacidade de mapear o território, as redes e os fluxos.

Experimentamos visualizar dados públicos, integrando os Censos do IBGE, o CNEFE e o Cadastro da Receita Federal, envolvendo:

- dados populacionais por perfil religioso, escolaridade, cor, idade...;
- empresas com atividades econômicas, sociedades, organizações religiosas, batalhões, prefeituras, comunidades quilombolas, bancos... a maioria com localização geográfica;
- potencialmente co-relacionados com o TSE, Despesas da Câmara, Frentes, Emendas PIX...

Demonstrando em pulos, a imagem abaixo não é uma foto aérea: é uma representação visual do Rio de Janeiro, onde cada ponto iluminado é um estabelecimento de Pessoa Jurídica;

\=\> [https://ミ.xyz/dataviz/rio/ibge](https://xn--2dk.xyz/dataviz/rio/ibge)

![][image1]![][image2]

**Todas as Igrejas do País**
![][image3]![][image4]![][image5]![][image6]![][image7]

**Mais igrejas que escolas. :/**
![][image8]

**Residenciais em Nova Friburgo com Altura relativa a número de moradores**
![][image9]
\=\> [https://ミ.xyz/dataviz/friba/pop\_3d](https://xn--2dk.xyz/dataviz/friba/pop_3d)

**Distribuição de Confecções (mapeado a partir dos CNPJs ativos)**

**![][image10]**
**![][image11]**

**Visualizando Confecçoes Abertas e Fechadas na Pandemia no pólo de moda intima**

**![][image12]**

**Todas as Residências no Município de Nova Friburgo**
![][image13]

**Número de Entidades Religiosas supera o de Sindicatos no ano 2000**
![][image14]

**Heatmap de registros de novas Empresas em Nova Friburgo**
![][image15]

**Quanto mais amarelo, mais Católico um município. Roxo tende a ser Evangélico.**

![][image16]
![][image17]

**81,5% dos estados brasileiros têm o dobro de estabelecimentos religiosos comparado a unidades de saúde.**![][image18]

**Distribuição de Tipo de Escolas no Rio (primário, secundária…)**
![][image19]

![][image20]

**Que áreas econômicas fecharam depois de outras durante a pandemia?**
![][image22]

**Relação Societária de Empresários Friburguenses com mais empresas**
![][image23]![][image24]

**Mapa de calor de áreas com mais Residências**
![][image25]![][image26]![][image27]![][image28]

**Empresas e Sócios do dono do Jogo do Tigrinho**
\=\> [https://tinyurl.com/pegadas-tigrim](https://tinyurl.com/pegadas-tigrim)

![][image29]

**Visualização das Sociedades e Empresas de um determinado Senador**
**![][image30]**

**Empresas Suíças com sede no Brasil**
\=\> [https://tinyurl.com/swiss-brazilian-network](https://tinyurl.com/swiss-brazilian-network)

**![][image31]**

---

**📈 Dados dos Censos Habitacionais do IBGE: Quatro Décadas de Evolução (1970-2010)**

> *Diagramas de fluxo Sankey abrangentes mostrando os padrões habitacionais brasileiros ao longo de cinco períodos censitários, revelando a transformação da propriedade habitacional, tendências de urbanização e características das moradias durante 40 anos*

**Censo Habitacional de 1970**
> *Padrões habitacionais da era pós-industrialização mostrando o domínio de propriedades rurais próprias e tipos de habitação rústica*

---
```mermaid
---
config:
  sankey:
    showValues: false
    width: 1200
    height: 600
---
sankey-beta
  Sit Urbano,Cond sem declaracao,1168
  Sit Suburbano,Cond sem declaracao,26
  Sit Rural,Cond sem declaracao,775
  Sit Urbano,Cond Proprio ja pago,6602220
  Sit Suburbano,Cond Proprio ja pago,345236
  Sit Rural,Cond Proprio ja pago,6514120
  Sit Urbano,Cond Proprio em aquisicao,1021044
  Sit Suburbano,Cond Proprio em aquisicao,33202
  Sit Rural,Cond Proprio em aquisicao,111461
  Sit Urbano,Cond Alugado,3575026
  Sit Suburbano,Cond Alugado,109313
  Sit Rural,Cond Alugado,300507
  Sit Nao classificado,Cond Alugado,2
  Sit Urbano,Cond Cedido,906408
  Sit Suburbano,Cond Cedido,40742
  Sit Rural,Cond Cedido,920018
  Sit Urbano,Cond Outra condicao,139868
  Sit Suburbano,Cond Outra condicao,13135
  Sit Rural,Cond Outra condicao,2859867
  Sit Urbano,Cond Nao classificado,16
  Cond sem declaracao,Tipo Rustico,1434
  Cond sem declaracao,Tipo Duravel,535
  Cond Proprio ja pago,Tipo Rustico,9912955
  Cond Proprio ja pago,Tipo Duravel,3548621
  Cond Proprio em aquisicao,Tipo Rustico,1032172
  Cond Proprio em aquisicao,Tipo Duravel,133535
  Cond Alugado,Tipo Rustico,3465003
  Cond Alugado,Tipo Duravel,519845
  Cond Cedido,Tipo Rustico,1235874
  Cond Cedido,Tipo Duravel,631294
  Cond Outra condicao,Tipo Rustico,1659069
  Cond Outra condicao,Tipo Duravel,1353801
  Cond Nao classificado,Tipo Rustico,16
```
---

**Censo Habitacional de 1980**
> *Início da grande urbanização: emergência da vida em apartamentos e mudança de assentamentos rurais para urbanos*

---
```mermaid
---
config:
  sankey:
    showValues: false
    width: 1200
    height: 600
---
sankey-beta
  Aglomerado rural,Alugado,19572
  Aglomerado rural,Cedido por empregador,13165
  Aglomerado rural,Cedido por particular,8836
  Aglomerado rural,ignorado,437
  Aglomerado rural,Outra condicao,3330
  Aglomerado rural,Proprio em aquisicao,11155
  Aglomerado rural,Proprio ja pago,124728
  Area urbana isolada,Alugado,6098
  Area urbana isolada,Cedido por empregador,1893
  Area urbana isolada,Cedido por particular,1910
  Area urbana isolada,ignorado,38
  Area urbana isolada,Outra condicao,342
  Area urbana isolada,Proprio em aquisicao,1212
  Area urbana isolada,Proprio ja pago,15536
  Cidade ou Vila,Alugado,1343492
  Cidade ou Vila,Cedido por empregador,96021
  Cidade ou Vila,Cedido por particular,277264
  Cidade ou Vila,ignorado,6427
  Cidade ou Vila,Outra condicao,54910
  Cidade ou Vila,Proprio em aquisicao,344477
  Cidade ou Vila,Proprio ja pago,2334531
  Zona rural,Alugado,34671
  Zona rural,Cedido por empregador,429076
  Zona rural,Cedido por particular,170478
  Zona rural,ignorado,3637
  Zona rural,Outra condicao,46914
  Zona rural,Proprio em aquisicao,8230
  Zona rural,Proprio ja pago,1125161
  Alugado,Apartamento,192360
  Alugado,Casa,1211473
  Cedido por empregador,Apartamento,15897
  Cedido por empregador,Casa,524258
  Cedido por particular,Apartamento,15198
  Cedido por particular,Casa,443290
  ignorado,Apartamento,1420
  ignorado,Casa,9119
  Outra condicao,Apartamento,3131
  Outra condicao,Casa,102365
  Proprio em aquisicao,Apartamento,107008
  Proprio em aquisicao,Casa,258066
  Proprio ja pago,Apartamento,115652
  Proprio ja pago,Casa,3484304
```
---

**Censo Habitacional de 1990**
> *Período de transição democrática: diversificação dos tipos de habitação e expansão de assentamentos urbanos incluindo reconhecimento de habitações indígenas*

---
```mermaid
---
config:
  sankey:
    showValues: false
    width: 1200
    height: 600
---
sankey-beta
  Loc Aglomerado rural de extensao urbana,Sit Alugado,8375
  Loc Aglomerado rural de extensao urbana,Sit Cedido de outra forma,6122
  Loc Aglomerado rural de extensao urbana,Sit Cedido por empregador,6815
  Loc Aglomerado rural de extensao urbana,Sit Nao classificado,580
  Loc Aglomerado rural de extensao urbana,Sit Outra condicao,514
  Loc Aglomerado rural de extensao urbana,Sit Proprio em aquisicao,6156
  Loc Aglomerado rural de extensao urbana,Sit Proprio ja pago,57251
  Loc Aglomerado rural isolado,Sit Alugado,9310
  Loc Aglomerado rural isolado,Sit Cedido de outra forma,5654
  Loc Aglomerado rural isolado,Sit Cedido por empregador,2808
  Loc Aglomerado rural isolado,Sit Nao classificado,585
  Loc Aglomerado rural isolado,Sit Outra condicao,892
  Loc Aglomerado rural isolado,Sit Proprio em aquisicao,19368
  Loc Aglomerado rural isolado,Sit Proprio ja pago,106603
  Loc Area urbana isolada,Sit Alugado,6734
  Loc Area urbana isolada,Sit Cedido de outra forma,5982
  Loc Area urbana isolada,Sit Cedido por empregador,13437
  Loc Area urbana isolada,Sit Nao classificado,937
  Loc Area urbana isolada,Sit Outra condicao,754
  Loc Area urbana isolada,Sit Proprio em aquisicao,7707
  Loc Area urbana isolada,Sit Proprio ja pago,47955
  Loc Cidade ou Vila,Sit Alugado,2089471
  Loc Cidade ou Vila,Sit Cedido de outra forma,759162
  Loc Cidade ou Vila,Sit Cedido por empregador,206631
  Loc Cidade ou Vila,Sit Nao classificado,94259
  Loc Cidade ou Vila,Sit Outra condicao,60118
  Loc Cidade ou Vila,Sit Proprio em aquisicao,887345
  Loc Cidade ou Vila,Sit Proprio ja pago,7795740
  Loc ignorado,Sit Alugado,47031
  Loc ignorado,Sit Cedido de outra forma,370395
  Loc ignorado,Sit Cedido por empregador,934760
  Loc ignorado,Sit Nao classificado,32430
  Loc ignorado,Sit Outra condicao,59016
  Loc ignorado,Sit Proprio em aquisicao,491894
  Loc ignorado,Sit Proprio ja pago,2472469
  Loc Nucleo colonial,Sit Alugado,18613
  Loc Nucleo colonial,Sit Cedido de outra forma,23966
  Loc Nucleo colonial,Sit Cedido por empregador,13288
  Loc Nucleo colonial,Sit Nao classificado,2708
  Loc Nucleo colonial,Sit Outra condicao,2421
  Loc Nucleo colonial,Sit Proprio em aquisicao,34871
  Loc Nucleo colonial,Sit Proprio ja pago,302623
  Loc Povoado,Sit Alugado,3817
  Loc Povoado,Sit Cedido de outra forma,313
  Loc Povoado,Sit Cedido por empregador,16409
  Loc Povoado,Sit Nao classificado,525
  Loc Povoado,Sit Outra condicao,288
  Loc Povoado,Sit Proprio em aquisicao,533
  Loc Povoado,Sit Proprio ja pago,2349
  Loc Zona rural exclusiva,Sit Alugado,368
  Loc Zona rural exclusiva,Sit Cedido de outra forma,328
  Loc Zona rural exclusiva,Sit Cedido por empregador,679
  Loc Zona rural exclusiva,Sit Nao classificado,383
  Loc Zona rural exclusiva,Sit Outra condicao,70
  Loc Zona rural exclusiva,Sit Proprio em aquisicao,369
  Loc Zona rural exclusiva,Sit Proprio ja pago,5529
  Sit Alugado,Tipo Apartamento,66678
  Sit Alugado,Tipo Casa,1772472
  Sit Alugado,Tipo Comodo cortico cabecadeporco etc,41940
  Sit Alugado,Tipo Oca maloca habitacao indigena,247780
  Sit Alugado,Tipo Outro tipo de domicilio,34482
  Sit Alugado,Tipo Unidade em predio nao residencial loja galpao etc,18951
  Sit Alugado,Tipo Unidade improvisada barraco tenda etc,1416
  Sit Cedido de outra forma,Tipo Apartamento,39443
  Sit Cedido de outra forma,Tipo Casa,1069614
  Sit Cedido de outra forma,Tipo Comodo cortico cabecadeporco etc,21893
  Sit Cedido de outra forma,Tipo Oca maloca habitacao indigena,28353
  Sit Cedido de outra forma,Tipo Outro tipo de domicilio,7413
  Sit Cedido de outra forma,Tipo Unidade em predio nao residencial loja galpao etc,4966
  Sit Cedido de outra forma,Tipo Unidade improvisada barraco tenda etc,240
  Sit Cedido por empregador,Tipo Apartamento,15743
  Sit Cedido por empregador,Tipo Casa,1150444
  Sit Cedido por empregador,Tipo Comodo cortico cabecadeporco etc,5137
  Sit Cedido por empregador,Tipo Oca maloca habitacao indigena,20849
  Sit Cedido por empregador,Tipo Outro tipo de domicilio,2264
  Sit Cedido por empregador,Tipo Unidade em predio nao residencial loja galpao etc,368
  Sit Cedido por empregador,Tipo Unidade improvisada barraco tenda etc,22
  Sit Nao classificado,Tipo Nao classificado,132407
  Sit Outra condicao,Tipo Apartamento,9140
  Sit Outra condicao,Tipo Casa,102627
  Sit Outra condicao,Tipo Comodo cortico cabecadeporco etc,7642
  Sit Outra condicao,Tipo Oca maloca habitacao indigena,2449
  Sit Outra condicao,Tipo Outro tipo de domicilio,1336
  Sit Outra condicao,Tipo Unidade em predio nao residencial loja galpao etc,829
  Sit Outra condicao,Tipo Unidade improvisada barraco tenda etc,50
  Sit Proprio em aquisicao,Tipo Apartamento,18875
  Sit Proprio em aquisicao,Tipo Casa,1003340
  Sit Proprio em aquisicao,Tipo Comodo cortico cabecadeporco etc,393779
  Sit Proprio em aquisicao,Tipo Oca maloca habitacao indigena,19784
  Sit Proprio em aquisicao,Tipo Outro tipo de domicilio,2798
  Sit Proprio em aquisicao,Tipo Unidade em predio nao residencial loja galpao etc,6985
  Sit Proprio em aquisicao,Tipo Unidade improvisada barraco tenda etc,2682
  Sit Proprio ja pago,Tipo Apartamento,709720
  Sit Proprio ja pago,Tipo Casa,9229077
  Sit Proprio ja pago,Tipo Comodo cortico cabecadeporco etc,242178
  Sit Proprio ja pago,Tipo Oca maloca habitacao indigena,452334
  Sit Proprio ja pago,Tipo Outro tipo de domicilio,7102
  Sit Proprio ja pago,Tipo Unidade em predio nao residencial loja galpao etc,147814
  Sit Proprio ja pago,Tipo Unidade improvisada barraco tenda etc,2294
```
---

**Censo Habitacional de 2000**
> *Era do milênio: classificação urbano/rural simplificada mostrando a consolidação da vida urbana e cultura de apartamentos*

---
```mermaid
---
config:
  sankey:
    showValues: false
    width: 1200
    height: 600
---
sankey-beta
  Rural,Alugado,67876
  Rural,Cedido de outra forma,334512
  Rural,Cedido por empregador,776836
  Rural,ignorado,70761
  Rural,Outra condicao,68061
  Rural,Proprio em aquisicao,78000
  Rural,Proprio pago,3476050
  Urbano,Alugado,2206025
  Urbano,Cedido de outra forma,855342
  Urbano,Cedido por empregador,207996
  Urbano,ignorado,108024
  Urbano,Outra condicao,170945
  Urbano,Proprio em aquisicao,1146742
  Urbano,Proprio pago,10707242
  Alugado,Apartamento,315423
  Alugado,Casa,1907731
  Alugado,Comodo,50747
  Cedido de outra forma,Apartamento,35972
  Cedido de outra forma,Casa,1124609
  Cedido de outra forma,Comodo,29273
  Cedido por empregador,Apartamento,21095
  Cedido por empregador,Casa,956863
  Cedido por empregador,Comodo,6874
  ignorado,OutroNIU,178785
  Outra condicao,Apartamento,8251
  Outra condicao,Casa,222231
  Outra condicao,Comodo,8524
  Proprio em aquisicao,Apartamento,287630
  Proprio em aquisicao,Casa,933642
  Proprio em aquisicao,Comodo,3470
  Proprio pago,Apartamento,604698
  Proprio pago,Casa,13508004
  Proprio pago,Comodo,70590
```
---

**Censo Habitacional de 2010**
> *Era moderna: introdução de condomínios, redução significativa em habitações alugadas e reconhecimento de diversas situações habitacionais incluindo moradia institucional*

---
```mermaid
---
config:
  sankey:
    showValues: false
    width: 1200
    height: 600
---
sankey-beta
  Rural,Alugado,30676
  Rural,Cedido de outra forma,95891
  Rural,Cedido por empregador,153284
  Rural,ignorado,27598
  Rural,Outra condicao,11729
  Rural,Proprio em aquisicao,20009
  Rural,Proprio quitado,1005936
  Urbano,Alugado,937170
  Urbano,Cedido de outra forma,267596
  Urbano,Cedido por empregador,42101
  Urbano,ignorado,50847
  Urbano,Outra condicao,24180
  Urbano,Proprio em aquisicao,262339
  Urbano,Proprio quitado,3262976
  Alugado,Apartamento,133582
  Alugado,Casa,799893
  Alugado,Casa de vila ou condominio,24121
  Alugado,Habitacao em comodo ou cortico,10250
  Cedido de outra forma,Apartamento,11659
  Cedido de outra forma,Casa,346043
  Cedido de outra forma,Casa de vila ou condominio,3130
  Cedido de outra forma,Habitacao em comodo ou cortico,2568
  Cedido de outra forma,Oca maloca indigena,87
  Cedido por empregador,Apartamento,4203
  Cedido por empregador,Casa,187970
  Cedido por empregador,Casa de vila ou condominio,2566
  Cedido por empregador,Habitacao em comodo ou cortico,644
  Cedido por empregador,Oca maloca indigena,2
  ignorado,Alojamento de trabalhadores,5449
  ignorado,Asilo orfanato ou similar,18186
  ignorado,Dentro de estabelecimento nao residencial,7180
  ignorado,Hotel pensao ou similar,4752
  ignorado,Outro coletivo,3522
  ignorado,Outro vagao trailer gruta etc,1825
  ignorado,Penitenciaria presidio ou casa de detencao,32517
  ignorado,Tenda ou barraca,5014
  Outra condicao,Apartamento,1406
  Outra condicao,Casa,32798
  Outra condicao,Casa de vila ou condominio,538
  Outra condicao,Habitacao em comodo ou cortico,977
  Outra condicao,Oca maloca indigena,190
  Proprio em aquisicao,Apartamento,59811
  Proprio em aquisicao,Casa,214613
  Proprio em aquisicao,Casa de vila ou condominio,7730
  Proprio em aquisicao,Habitacao em comodo ou cortico,190
  Proprio em aquisicao,Oca maloca indigena,4
  Proprio quitado,Apartamento,197869
  Proprio quitado,Casa,4027172
  Proprio quitado,Casa de vila ou condominio,34572
  Proprio quitado,Habitacao em comodo ou cortico,7180
  Proprio quitado,Oca maloca indigena,2119
```
---

**Principais Insights de Quatro Décadas de Evolução Habitacional**

**Principais Tendências Observadas:**
- **Aceleração da Urbanização**: Mudança massiva de habitação rural para urbana (1970-2010)
- **Crescimento da Propriedade**: Aumento em propriedades quitadas vs. aluguéis
- **Diversificação Habitacional**: De classificação rural/urbana básica para categorizações complexas incluindo condomínios
- **Reconhecimento Social**: Inclusão de habitação indígena e categorias de moradia institucional
- **Desenvolvimento Econômico**: Mudança de "quitado" para "em aquisição" refletindo acesso ao crédito

🔗 **[Repositório Fonte: Análise dos Censos Habitacionais IBGE](https://github.com/rafapolo/IBGE13/)**

---

(Drucker, 2011) A cartografia digital permite espacializar saberes complexos — como padrões econômicos, práticas religiosas, ou redes de poder — que antes ficavam dispersos ou ocultos nos dados brutos. Essa espacialização transforma grandes volumes de dados em interfaces cognitivas acessíveis, mobilizando tanto percepção visual quanto análise crítica.

**ミ**

**~2025**



[image1]: images/image1.png
[image2]: images/image2.png
[image3]: images/image3.png
[image4]: images/image4.png
[image5]: images/image5.png
[image6]: images/image6.png
[image7]: images/image7.png
[image8]: images/image8.png
[image9]: images/image9.png
[image10]: images/image10.png
[image11]: images/image11.png
[image12]: images/image12.png
[image13]: images/image13.png
[image14]: images/image14.png
[image15]: images/image15.png
[image16]: images/image16.png
[image17]: images/image17.png
[image18]: images/image18.png
[image19]: images/image19.png
[image20]: images/image20.png
[image21]: images/image21.png
[image22]: images/image22.png
[image23]: images/image23.png
[image24]: images/image24.png
[image25]: images/image25.png
[image26]: images/image26.png
[image27]: images/image27.png
[image28]: images/image28.png
[image29]: images/image29.png
[image30]: images/image30.png
[image31]: images/image31.png
