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
