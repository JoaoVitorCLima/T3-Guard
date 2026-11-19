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
