# Bancada DE0-CV

O projeto Quartus tem como alvo o Cyclone V 5CEBA4F23C7 da Terasic DE0-CV. Abra `de0cv.qpf` em uma instalação do Quartus com suporte ao Cyclone V, compile e programe o `output_files/de0cv.sof` pelo USB-Blaster em JTAG. Rode o teste a seguir com os atuadores representados pelos LEDs da placa.

| Controle | Função |
|---|---|
| KEY0 | Reset, com a saída de trip acionada |
| KEY1 | Pulso local de rearme, capturado até a próxima amostra |
| SW0–SW2 | Leituras A/B/C em 500 (desligada) ou 710 (ligada) |
| SW3–SW5 | Invalidação explícita de A/B/C |
| SW6 | Pausa da amostragem |
| LEDR0–2 | Votos altos A/B/C |
| LEDR3–5 | Canais excluídos A/B/C |
| LEDR6 | Trip travado |
| LEDR7–8 | Modo, com códigos 0 normal, 1 degradado, 2 seguro |
| LEDR9 | Timeout |

1. Baixe todas as chaves, pressione KEY0 e depois KEY1. Observe LEDR6 apagar.
2. Suba SW3. Observe exclusão de A e modo degradado. Suba SW1 e observe o trip conservador, mesmo com apenas um voto alto.
3. Baixe SW1 e SW3. Pressione KEY1. Suba SW0 e SW1 para demonstrar o trip por dois votos.
4. Baixe as chaves e rearme. Suba SW3 e SW4 para simular dois canais indisponíveis. Baixe as chaves. Observe que o trip só libera após KEY1.
5. Suba SW6 e observe a perda da amostragem. O relógio nominal é 50 MHz, com amostra a cada 10 ms e timeout após 40 ms sem amostra.

Para a telemetria, use o pino **GPIO_0_D0** (sinal mapeado para N16), com GND comum e entrada RX de um adaptador USB–UART TTL de 3,3 V. Consulte a posição física do pino no manual da placa. A UART envia capturas periódicas e funciona apenas no sentido FPGA → notebook. O demo de chaves usa diagnóstico explícito. O limiar de discrepância deste wrapper é maior que a diferença de 210 entre os dois valores das chaves, permitindo mostrar a votação com arranjos estáticos.

Pinagem conforme as tabelas 3-2, 3-3, 3-4, 3-6 e 3-7 do [manual da DE0-CV](https://elportal.pl/files/2021/11/15/560-de0cvusermanual112.pdf).
