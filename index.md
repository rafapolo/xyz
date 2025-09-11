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
![][image23]

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

<div style="border: 2px solid #e1e5e9; border-radius: 8px; padding: 15px; margin: 20px 0; background-color: #f8f9fa;">

```mermaid
---
config:
 sankey:
  showValues: false
  width: 1200
  height: 600
---
sankey
    Sit_Urbano,Cond_sem_declaracao,1168
    Sit_Suburbano,Cond_sem_declaracao,26
    Sit_Rural,Cond_sem_declaracao,775
    Sit_Urbano,Cond_Proprio_ja_pago,6602220
    Sit_Suburbano,Cond_Proprio_ja_pago,345236
    Sit_Rural,Cond_Proprio_ja_pago,6514120
    Sit_Urbano,Cond_Proprio_em_aquisicao,1021044
    Sit_Suburbano,Cond_Proprio_em_aquisicao,33202
    Sit_Rural,Cond_Proprio_em_aquisicao,111461
    Sit_Urbano,Cond_Alugado,3575026
    Sit_Suburbano,Cond_Alugado,109313
    Sit_Rural,Cond_Alugado,300507
    Sit_Nao_classificado,Cond_Alugado,2
    Sit_Urbano,Cond_Cedido,906408
    Sit_Suburbano,Cond_Cedido,40742
    Sit_Rural,Cond_Cedido,920018
    Sit_Urbano,Cond_Outra_condicao,139868
    Sit_Suburbano,Cond_Outra_condicao,13135
    Sit_Rural,Cond_Outra_condicao,2859867
    Sit_Urbano,Cond_Nao_classificado,16
    Cond_sem_declaracao,Tipo_Rustico,1434
    Cond_sem_declaracao,Tipo_Duravel,535
    Cond_Proprio_ja_pago,Tipo_Rustico,9912955
    Cond_Proprio_ja_pago,Tipo_Duravel,3548621
    Cond_Proprio_em_aquisicao,Tipo_Rustico,1032172
    Cond_Proprio_em_aquisicao,Tipo_Duravel,133535
    Cond_Alugado,Tipo_Rustico,3465003
    Cond_Alugado,Tipo_Duravel,519845
    Cond_Cedido,Tipo_Rustico,1235874
    Cond_Cedido,Tipo_Duravel,631294
    Cond_Outra_condicao,Tipo_Rustico,1659069
    Cond_Outra_condicao,Tipo_Duravel,1353801
    Cond_Nao_classificado,Tipo_Rustico,16
```

</div>
---

**Censo Habitacional de 1980**
> *Início da grande urbanização: emergência da vida em apartamentos e mudança de assentamentos rurais para urbanos*

<div style="border: 2px solid #e1e5e9; border-radius: 8px; padding: 15px; margin: 20px 0; background-color: #f8f9fa;">

```mermaid
---
config:
 sankey:
  showValues: false
  width: 1200
  height: 600
---
sankey
    Aglomerado_rural,Alugado,19572
    Aglomerado_rural,Cedido_por_empregador,13165
    Aglomerado_rural,Cedido_por_particular,8836
    Aglomerado_rural,ignorado,437
    Aglomerado_rural,Outra_condicao,3330
    Aglomerado_rural,Proprio_em_aquisicao,11155
    Aglomerado_rural,Proprio_ja_pago,124728
    Area_urbana_isolada,Alugado,6098
    Area_urbana_isolada,Cedido_por_empregador,1893
    Area_urbana_isolada,Cedido_por_particular,1910
    Area_urbana_isolada,ignorado,38
    Area_urbana_isolada,Outra_condicao,342
    Area_urbana_isolada,Proprio_em_aquisicao,1212
    Area_urbana_isolada,Proprio_ja_pago,15536
    Cidade_ou_Vila,Alugado,1343492
    Cidade_ou_Vila,Cedido_por_empregador,96021
    Cidade_ou_Vila,Cedido_por_particular,277264
    Cidade_ou_Vila,ignorado,6427
    Cidade_ou_Vila,Outra_condicao,54910
    Cidade_ou_Vila,Proprio_em_aquisicao,344477
    Cidade_ou_Vila,Proprio_ja_pago,2334531
    Zona_rural,Alugado,34671
    Zona_rural,Cedido_por_empregador,429076
    Zona_rural,Cedido_por_particular,170478
    Zona_rural,ignorado,3637
    Zona_rural,Outra_condicao,46914
    Zona_rural,Proprio_em_aquisicao,8230
    Zona_rural,Proprio_ja_pago,1125161
    Alugado,Apartamento,192360
    Alugado,Casa,1211473
    Cedido_por_empregador,Apartamento,15897
    Cedido_por_empregador,Casa,524258
    Cedido_por_particular,Apartamento,15198
    Cedido_por_particular,Casa,443290
    ignorado,Apartamento,1420
    ignorado,Casa,9119
    Outra_condicao,Apartamento,3131
    Outra_condicao,Casa,102365
    Proprio_em_aquisicao,Apartamento,107008
    Proprio_em_aquisicao,Casa,258066
    Proprio_ja_pago,Apartamento,115652
    Proprio_ja_pago,Casa,3484304
```

</div>
---

**Censo Habitacional de 2000**
> *Era do milênio: classificação urbano/rural simplificada mostrando a consolidação da vida urbana e cultura de apartamentos*

<div style="border: 2px solid #e1e5e9; border-radius: 8px; padding: 15px; margin: 20px 0; background-color: #f8f9fa;">

```mermaid
---
config:
 sankey:
  showValues: false
  width: 1200
  height: 600
---
sankey
    Rural,Alugado,67876
    Rural,Cedido_de_outra_forma,334512
    Rural,Cedido_por_empregador,776836
    Rural,ignorado,70761
    Rural,Outra_condicao,68061
    Rural,Proprio_em_aquisicao,78000
    Rural,Proprio_pago,3476050
    Urbano,Alugado,2206025
    Urbano,Cedido_de_outra_forma,855342
    Urbano,Cedido_por_empregador,207996
    Urbano,ignorado,108024
    Urbano,Outra_condicao,170945
    Urbano,Proprio_em_aquisicao,1146742
    Urbano,Proprio_pago,10707242
    Alugado,Apartamento,315423
    Alugado,Casa,1907731
    Alugado,Comodo,50747
    Cedido_de_outra_forma,Apartamento,35972
    Cedido_de_outra_forma,Casa,1124609
    Cedido_de_outra_forma,Comodo,29273
    Cedido_por_empregador,Apartamento,21095
    Cedido_por_empregador,Casa,956863
    Cedido_por_empregador,Comodo,6874
    ignorado,OutroNIU,178785
    Outra_condicao,Apartamento,8251
    Outra_condicao,Casa,222231
    Outra_condicao,Comodo,8524
    Proprio_em_aquisicao,Apartamento,287630
    Proprio_em_aquisicao,Casa,933642
    Proprio_em_aquisicao,Comodo,3470
    Proprio_pago,Apartamento,604698
    Proprio_pago,Casa,13508004
    Proprio_pago,Comodo,70590
```

</div>

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

**ミ ~ 2025**



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
