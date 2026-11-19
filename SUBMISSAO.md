# Submissão ao Hack Brasil 2026

- **Nome** T3-Guard
- **Trilha proposta** Logística & automação
- **Frase de apresentação** Três canais em FPGA para decidir e registrar um disparo industrial.

## Descrição para o painel

Quando um skid para, descobrir qual sinal mudou primeiro pode exigir comparar alarmes e reproduzir condições de falha. O T3-Guard é um protótipo de bancada em SystemVerilog que recebe três leituras sintéticas, aplica uma votação de dois de três e registra transições com o carimbo de ciclo do hardware. Ao detectar um canal inválido ou discrepante, entra em modo degradado. Se perder dois canais, trava a saída de disparo até rearme local. A demonstração apresenta uma execução real do testbench com injeção de falhas. Um gateway Modbus TCP expõe a telemetria de leitura para validar a integração com supervisão industrial. O primeiro caso de uso proposto é monitorar pressão em uma bancada de instrumentação para skids. A arquitetura pode ser adaptada a outras variáveis de processos críticos, como temperatura, nível e vazão, com três canais independentes por variável.

## Vídeo e roteiro

- **0:00–0:25** Mostrar a tela com três canais saudáveis. “Quando um equipamento para, a primeira pergunta é o que aconteceu antes do disparo.”
- **0:25–0:55** Selecionar “Canal discrepante”. Mostrar a exclusão de C e a operação degradada. Explicar o significado de dois de três e de um de dois no modo degradado.
- **0:55–1:20** Selecionar “Dois canais indisponíveis”. Mostrar trip travado e a sequência dos eventos. Avançar pelo retorno dos canais e pelo rearme.
- **1:20–1:50** Demonstrar dois votos altos e perda de amostragem. Mostrar a leitura FC04 em localhost e identificar a origem dos dados usada na gravação.
- **1:50–2:15** Mostrar o arquivo RTL e o resultado dos simuladores, encerrar com o cenário de teste proposto para uma bancada de instrumentação na Bahia.

O vídeo legendado está em [docs/video.mp4](docs/video.mp4). O roteiro acima serve para uma versão narrada em bancada.

## Publicação

O regulamento pede repositório público novo no GitHub, demo acessível, vídeo de até três minutos sem login e aceite no painel do time até 30 de novembro de 2026, às 23h59. [Regulamento oficial](https://hackbrasil.com/regulamento)

- Demo e vídeo disponíveis localmente em [docs/index.html](docs/index.html) e [docs/video.mp4](docs/video.mp4).

- [Repositório no GitHub](https://github.com/JoaoVitorCLima/T3-Guard)
