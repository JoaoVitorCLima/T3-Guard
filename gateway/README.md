# Gateway Modbus TCP

O notebook publica o último estado recebido pela serial da FPGA ou por reprodução do CSV de simulação. O servidor de bancada escuta apenas em 127.0.0.1:1502, unidade 1, função FC04 (input registers). A interface é de leitura.

```bash
python3 gateway/modbus.py --replay docs/trace.csv
# Para entrada real, instale pyserial no ambiente Python e selecione a porta.
python3 gateway/modbus.py --serial /dev/ttyUSB0
```

No Windows, substitua /dev/ttyUSB0 por uma porta como COM4. Use as opções TCP, porta 1502 e unidade 1 no cliente. Leia 8 registradores a partir do offset 0.

| Offset | Valor |
|---|---|
| 0 | Identificador 0x0201 |
| 1 | Captura recebida nos últimos 2 s |
| 2–3 | ID do evento, palavra alta primeiro |
| 4–5 | Ciclo RTL do evento, palavra alta primeiro |
| 6 | Bits 9 timeout, 8:7 modo, 6 trip, 5:3 excluídos C/B/A, 2:0 votos altos C/B/A |
| 7 | Estimativa de eventos pulados na captura, saturada em 65535 |

Na placa, cada ciclo corresponde a 20 ns nominais. Os contadores RTL são de 32 bits e retornam a zero por overflow ou reset. A estimativa de perda cobre saltos ascendentes do ID observados pelo gateway. Para eventos rápidos, a captura pode pular estados intermediários.

UART 115200 8N1. Cada quadro tem 13 bytes, com prefixo hexadecimal 02 21, ID e ciclo de 32 bits, estado de 16 bits em little-endian e XOR dos 12 bytes anteriores. O XOR detecta erros simples de transmissão para a demonstração.

## Reprodução de pressão e integração com CLP

O modo de bancada `python -m gateway.modbus --pressao build/pronto-pressao.csv` lê o CSV pelo mesmo validador do diagnóstico e executa uma passagem. Atualiza a telemetria a cada 600 ms. Dois segundos após a última atualização o indicador de frescor fica em zero. Para uma bancada com CLP externo, acrescente `--bind IP_DO_NOTEBOOK` com o endereço específico da interface da bancada. No CLP ou no supervisório, configure cliente Modbus TCP, porta 1502, unidade 1, função FC04. O servidor escuta em localhost por padrão.

Neste modo, leia dez registradores a partir do offset 0. O mapa original de oito registradores continua associado a replay RTL e UART.

| Offset | Valor no modo pressão |
|---|---|
| 0 | Identificador de mapa 0x0301 |
| 1 | Frescor da captura (1 em atualização, 0 obsoleta) |
| 2–3 | Número da amostra, palavra alta primeiro |
| 4–6 | Pressão A, B e C em kPa inteiros, 65535 para leitura ausente |
| 7 | Máscara de ausência, bits 0/1/2 para A/B/C |
| 8 | Máscara de suspeita, bits 0/1/2 para A/B/C |
| 9 | Fonte 1, reprodução CSV com diagnóstico em software |

No programa do CLP, valide o identificador e o frescor antes de exibir valores como atuais. O protocolo implementado oferece leitura para diagnóstico e supervisão. A saída de disparo do protótipo FPGA fica na lógica local.

Para o produto, a arquitetura candidata é aquisição isolada dos transmissores, processamento local e uma interface Ethernet de diagnóstico. Validar com o CLP do piloto, definir segmentação e controle de acesso da rede e documentar o mapa. Onde a infraestrutura permitir, considerar a variante [Modbus Security com TLS](https://www.modbus.org/modbus-specifications). Avaliar requisitos de campo e de segurança funcional com a engenharia da planta para usos em sistemas instrumentados de segurança. [IEC 61511](https://webstore.iec.ch/en/publication/24241)

## Verificação de integridade em bancada

Na raiz do repositório, rode a demonstração automática. Ela inicia um servidor temporário em loopback e lê a resposta de cada estágio por FC04.

```bash
python3 -m gateway.demo_integridade
python3 -m unittest discover -s gateway
```

Para acompanhar a sequência com um cliente externo, abra primeiro o cliente e inicie a reprodução abaixo. O gateway disponibiliza quatro etapas, com um segundo de intervalo e uma passagem por execução. O servidor permanece disponível para consulta depois da reprodução. As pressões expiram dois segundos após a última amostra aceita de cada canal.

```bash
python3 -m gateway.modbus --demo-integridade
```

Configure a leitura FC04, unidade 1, offset 0 e 12 registradores em 127.0.0.1:1502. O protótipo usa três produtores simulados no mesmo processo. Cada produtor autentica sessão, canal, sequência e pressão por HMAC-SHA-256, com chave própria gerada para a execução. Entradas rejeitadas atualizam os contadores de diagnóstico. Apenas entradas aceitas atualizam a pressão e seu frescor.

| Offset | Valor |
|---|---|
| 0 | Identificador do modo de bancada 0x0401 |
| 1 | Máscara de frescor, bits 0/1/2 para A/B/C |
| 2–4 | Pressões A/B/C em kPa inteiros. 65535 representa indisponível |
| 5 | Máscara de discrepância, bits 0/1/2 para A/B/C |
| 6–9 | Contadores saturados de aceitas, inválidas, falhas de integridade e repetições |
| 10 | Último resultado. 0 inicial, 1 aceita, 2 formato ou faixa inválida, 3 autenticação falhou, 4 sequência ou sessão rejeitada |
| 11 | Canal indicado na última mensagem. 0=A, 1=B, 2=C, 65535=desconhecido. Para rejeições, é uma indicação do quadro recebido |

Nesta prova de conceito a entrada autenticada percorre uma interface interna com dados sintéticos e o diagnóstico de discrepância roda em Python. A FPGA e o PRONTO permanecem disponíveis em seus modos próprios. Integração com produtores físicos, provisionamento de chaves e proteção do enlace Modbus ficam para um piloto.

[Vídeo da bancada com dados capturados por FC04](../docs/video-integridade.mp4)
