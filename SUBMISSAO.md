# Submissão ao Hack Brasil 2026

- **Nome** T3-Guard
- **Trilha proposta** Cibersegurança
- **Frase de apresentação** T3-Guard verifica a origem das medições e identifica canais de pressão que merecem investigação.

## Proposta para o painel

Uma leitura suspeita no supervisório pode apontar para uma mensagem alterada ou para um transmissor que merece inspeção. O T3-Guard dá à equipe de instrumentação sinais distintos para investigar cada caso. O gateway autentica as medições localmente, bloqueia amostras alteradas ou repetidas e disponibiliza o diagnóstico por Modbus TCP de leitura. No ensaio integrado, o votador 2oo3 em SystemVerilog recebe somente medições aceitas. O cliente Modbus confirma que rejeições preservam a última leitura válida e que o RTL sinaliza um canal autenticado quando sua pressão diverge das outras. O primeiro caso de uso é um skid industrial de pressão, com processamento local em bancada.

**Resultado demonstrado.** Em quatro cenários com produtores simulados, a leitura de B permaneceu em 124 kPa após duas rejeições. Quando B passou a enviar 324 kPa em três rodadas autenticadas, o RTL sinalizou a divergência e o Modbus expôs o modo degradado. Buscamos uma equipe de instrumentação para medir o tempo de investigação em um piloto físico.

**Proteção demonstrada.** As amostras de bancada são autenticadas com HMAC-SHA-256 e chaves distintas por canal. A sessão e a sequência permitem identificar repetições. Quando uma amostra é rejeitada, o gateway preserva a última leitura válida e expõe o motivo ao supervisório. O cliente consulta o diagnóstico pelo Modbus TCP de leitura.

## Contexto e aplicações

O incidente de 2023 em uma estação de bombeamento de Aliquippa, na Pensilvânia, e o caso Stuxnet na instalação de enriquecimento de urânio de Natanz ilustram o impacto que incidentes digitais podem ter sobre operações físicas. O roubo de tokens do Facebook em 2018 ilustra a proteção de credenciais em um contexto distinto de controle de acesso digital. Esses casos contextualizam a proposta de monitoramento defensivo. [Registro legislativo sobre Aliquippa](https://www.palegis.us/legislation/bills/text/PDF/2025/0/HR0087/PN0717) · [Audiência sobre Natanz](https://www.govinfo.gov/content/pkg/CHRG-119hhrg62627/html/CHRG-119hhrg62627.htm) · [Comunicado do Facebook](https://about.fb.com/news/2018/10/update-on-security-issue/amp/)

A mesma arquitetura pode ser adaptada a linhas de processo e bombeamento que medem pressão, vazão, nível ou temperatura. Cada aplicação pede instrumentação e validação próprias. O monitoramento de eventos de trancas eletrônicas é uma possível extensão civil, com dados de acesso e critérios específicos.

## Base de dados e artigo

Usamos a base pública PRONTO para reproduzir medições reais de uma bancada de escoamento multifásico. O ensaio toma uma série de pressão do ponto PT417, deriva três canais a partir dela e introduz um desvio em B. A árvore de decisão foi treinada e testada offline em um conjunto sintético separado. A integração do modelo ao fluxo de diagnóstico e a validação em bancada com três transmissores independentes são etapas seguintes. [Base PRONTO](https://zenodo.org/records/1341583) · [Stief et al., *Journal of Process Control*, 2019](https://doi.org/10.1016/j.jprocont.2019.04.009)

## Escopo de cibersegurança para a inscrição

O protótipo atual demonstra diagnóstico de discrepância, registro de eventos e consulta Modbus de leitura. O replay PRONTO usa três canais derivados de uma medição e um desvio injetado em B. Esse ensaio confirma que a divergência chega à supervisão. A mesma divergência pode ocorrer por falha física e exige investigação da causa.

A demonstração integrada usa três produtores simulados que assinam amostras com chaves próprias. O gateway verifica a sessão e o contador de cada canal e acumula as rodadas aceitas. O Icarus executa o RTL sobre essas rodadas. O cliente lê via Modbus TCP o resultado do RTL, a pressão e os contadores de rejeição de cada etapa. A captura reproduzível roda com `python3 -m gateway.demo_integrada`.

- **Amostra válida.** O cliente Modbus lê B em 124 kPa e confirma a primeira rodada no RTL.
- **Amostra alterada.** O contador de integridade aumenta para 1. B permanece em 124 kPa e o RTL permanece na primeira rodada.
- **Amostra repetida.** O contador de repetições aumenta para 1. A leitura e a rodada do RTL permanecem iguais.
- **Canal autenticado divergente.** B envia 324 kPa em três rodadas aceitas. O RTL sinaliza B e entra no modo degradado. O cliente Modbus lê esse diagnóstico.

## Vídeo e roteiro

- **0:00–0:30** Usar o caso de Aliquippa para apresentar o risco de usar dados comprometidos em uma operação crítica.
- **0:30–1:20** Mostrar a aceitação de uma amostra válida e a rejeição de amostras alteradas ou repetidas em bancada isolada.
- **1:20–2:00** Mostrar o diagnóstico 2oo3 e o que o operador enxerga no Modbus TCP.
- **2:00–2:30** Explicar o uso dos dados do PRONTO, citar o artigo e apresentar a avaliação da IA local como próxima etapa.

O [vídeo de integridade](docs/video-integridade.mp4) e o [painel](docs/index.html) reproduzem a captura integrada por FC04 em loopback. O [vídeo do RTL](docs/video.mp4) mostra os cenários adicionais de disparo. A validação com três transmissores, FPGA física e CLP permanece pendente.

## Proposta de piloto para uma startup

**Cliente inicial.** Equipe de instrumentação ou integradora de automação que atende skids de pressão. O operador precisa identificar o canal suspeito e recuperar a sequência do evento durante uma investigação.

**Oferta inicial.** Um piloto de diagnóstico local em um skid de bancada, com três transmissores, um CLP e o supervisório do parceiro. Entregar configuração, mapa Modbus, registros de ensaio e um relatório comparando a identificação do canal suspeito com e sem o diagnóstico do T3-Guard.

**Aceite do piloto.** Repetir as mesmas condições com e sem o diagnóstico no supervisório e medir tempo mediano até identificar o canal, alarmes indevidos por ensaio e horas de integração. Definir as metas com o parceiro antes de executar a bancada. [Plano de validação](VALIDACAO.md)

**Hipótese comercial.** Um piloto pago com escopo fechado, seguido da oferta de um módulo por skid. Validar quem aprova a compra e se o tempo poupado na investigação justifica o custo de instalação e suporte.

**Convite.** Buscamos uma equipe de instrumentação ou integração de CLP para validar um piloto de pressão em bancada. Podemos demonstrar a rejeição de telemetria alterada, indicar o canal divergente no supervisório e medir o tempo de investigação com a equipe.

## Publicação

O regulamento pede repositório público novo no GitHub, demo acessível, vídeo de até três minutos sem login e aceite no painel do time até 30 de novembro de 2026, às 23h59. [Regulamento oficial](https://hackbrasil.com/regulamento)

- [Demo integrada](docs/index.html)
- [Vídeo principal](docs/video-integridade.mp4) e [vídeo complementar do RTL](docs/video.mp4)
- [Manifesto SHA-256 da entrega](docs/SHA256SUMS)

- [Repositório no GitHub](https://github.com/JoaoVitorCLima/T3-Guard)
