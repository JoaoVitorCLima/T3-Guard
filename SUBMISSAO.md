# Submissão ao Hack Brasil 2026

- **Nome** T3-Guard
- **Trilha proposta** Cibersegurança
- **Frase de apresentação** Monitoramento da integridade de medições em sistemas industriais críticos.

## Proposta para o painel

Equipes de operação e cibersegurança industrial precisam saber se uma leitura recebida pelo supervisório pode ser usada para tomar uma decisão. O T3-Guard propõe monitorar três canais de pressão, registrar divergências e expor a qualidade das medições ao CLP e ao supervisório por Modbus TCP de leitura. A prova de conceito combina uma lógica de votação 2oo3 em FPGA com um gateway de diagnóstico. Pressão em um skid é o primeiro caso de uso proposto.

## Escopo de cibersegurança para a inscrição

O protótipo atual demonstra diagnóstico de discrepância, registro de eventos e consulta Modbus de leitura. O replay PRONTO usa três canais derivados de uma medição e um desvio injetado em B. Esse ensaio confirma que a divergência chega à supervisão. A mesma divergência pode ocorrer por falha física e exige investigação da causa.

A demonstração de cibersegurança autentica a origem e a integridade das amostras na entrada interna do gateway. Três produtores simulados assinam suas amostras com chaves próprias. O gateway verifica a sessão e o contador de cada canal antes de atualizar a leitura. A regra de discrepância em Python compara leituras aceitas e a telemetria Modbus expõe os motivos de rejeição e o frescor por canal.

- **Amostra válida:** aceitar a leitura e mostrar qualidade e frescor pelo FC04.
- **Amostra alterada:** demonstrar em uma fixture local que a verificação de integridade rejeita a leitura e registra o motivo.
- **Amostra repetida:** confirmar que uma leitura já aceita é rejeitada e que o frescor permanece associado à última amostra válida.
- **Canal autenticado divergente:** sinalizar discrepância pela votação. A autenticação confirma a procedência da mensagem. A comparação ajuda a avaliar a leitura.

## Vídeo e roteiro

- **0:00–0:30** Apresentar a equipe de operação como público e explicar o risco de consumir medições alteradas ou antigas.
- **0:30–1:20** Mostrar a aceitação de uma amostra válida e a rejeição de amostras alteradas ou repetidas em bancada isolada.
- **1:20–2:00** Mostrar o diagnóstico 2oo3 e o que o operador enxerga no Modbus TCP.
- **2:00–2:30** Apresentar os resultados de bancada e explicar a origem dos dados usados.

O [vídeo de integridade](docs/video-integridade.mp4) usa registradores capturados via FC04 em loopback. O [vídeo do RTL](docs/video.mp4) demonstra a votação 2oo3. A integração com produtores físicos e um CLP permanece pendente.

## Publicação

O regulamento pede repositório público novo no GitHub, demo acessível, vídeo de até três minutos sem login e aceite no painel do time até 30 de novembro de 2026, às 23h59. [Regulamento oficial](https://hackbrasil.com/regulamento)

- Demo RTL, vídeo de votação e vídeo de integridade disponíveis localmente em [docs/index.html](docs/index.html), [docs/video.mp4](docs/video.mp4) e [docs/video-integridade.mp4](docs/video-integridade.mp4).

- [Repositório no GitHub](https://github.com/JoaoVitorCLima/T3-Guard)
