# Diagnóstico offline de pressão

O programa usa Python 3 e biblioteca padrão. O classificador é um experimento de bancada com dados sintéticos gerados pelo próprio código. A votação e o disparo continuam no RTL.

```bash
python3 diagnostico/offline.py --gerar amostra.csv
python3 diagnostico/offline.py --csv amostra.csv
python3 diagnostico/offline.py --comparar
```

O gerador cria um arquivo novo. A importação aceita UTF-8, com até 2 MB e cabeçalho exato:

```csv
timestamp_ms,unidade,a_kpa,b_kpa,c_kpa
0,kPa,400,410,405
100,kPa,402,411,406
```

Forneça pelo menos seis linhas de leitura com cadência uniforme. Cada linha representa um instante, com pressão inteira entre 0 e 1000 kPa. Uma célula vazia representa leitura ausente. Valores e formatos inválidos interrompem a importação antes de qualquer classificação. Essa escala serve ao experimento e precisa de recalibração para uma bancada física.

A referência reproduz o critério de discrepância do RTL com os parâmetros padrão, com exclusão por ausência e confirmação em três amostras válidas. A comparação usa uma árvore de até três níveis, treinada em 180 ensaios sintéticos e avaliada em 90 ensaios distintos. A unidade das métricas é uma combinação de janela e canal. Um degrau aplicado aos três canais entra como cenário sem falha individual. Desvio, congelamento e ausência são aplicados a um canal por ensaio.

O comando de importação usa a regra de referência. O comando de comparação relata os resultados da árvore experimental. A próxima etapa para sustentar uma conclusão sobre os sensores é repetir o teste com três transmissores físicos e uma referência independente. Uma reprodução do PRONTO é outra opção para variar os perfis de pressão.

| Método | Alarmes indevidos | Falhas não detectadas | Falhas detectadas |
|---|---:|---:|---:|
| Regra de discrepância | 0 | 64 | 44 |
| Árvore experimental | 2 | 3 | 105 |

Resultados do conjunto sintético de teste. O critério adotado foi reduzir falhas não detectadas sem aumentar alarmes indevidos. A árvore ainda é candidata para uma comparação com medições físicas.

## Ensaio de pressão com PRONTO

Use o Python a partir da raiz do repositório. O conversor lê uma coluna de pressão dos CSVs pré-processados do PRONTO. Cada linha vira uma amostra com três canais derivados da mesma medição. O tempo relativo de 1 s por linha representa o recorte para reprodução. A opção de bancada injeta um desvio de +200 kPa em B na segunda metade.

No PowerShell, com Python 3 disponível:

```powershell
$fonte = Get-ChildItem -LiteralPath Datasets -Recurse -Filter 'Testday2_merged.csv' | Select-Object -First 1
New-Item -ItemType Directory -Force build | Out-Null
python -m diagnostico.pronto $fonte.FullName build/pronto-pressao.csv --unidade bar --amostras 60 --desvio-b
python -m diagnostico.offline --csv build/pronto-pressao.csv
python -m gateway.modbus --pressao build/pronto-pressao.csv
```

Nesse exemplo, `Mixture.zone.P` é a pressão manométrica na zona de mistura (PT417, em bar(g), conforme a tabela 2 do artigo). O argumento de unidade explicita a conversão. Confira a unidade do arquivo ao selecionar outra origem. O conversor cria um arquivo novo e rejeita leituras fora da faixa, em vez de limitá-las silenciosamente.

A série é uma medição física de um ponto. A replicação em três canais e a falha injetada servem para testar a integração de bancada. Para o ensaio com três medições independentes, coletar os três transmissores e uma referência de pressão.

Fonte dos dados: [PRONTO, DOI 10.5281/zenodo.1341583](https://zenodo.org/records/1341583). Artigo: [Stief et al., Journal of Process Control 79 (2019), 41–55](https://doi.org/10.1016/j.jprocont.2019.04.009).
