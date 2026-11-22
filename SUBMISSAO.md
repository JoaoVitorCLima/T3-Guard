# Submissão ao Hack Brasil 2026

- **Nome** T3-Guard
- **Trilha proposta** Cibersegurança
- **Frase de apresentação** Cibersegurança local para detectar cedo sinais de comprometimento em sistemas industriais críticos.

## Proposta para o painel

Quando uma leitura chega alterada ao supervisório, a equipe precisa descobrir cedo quais dados merecem investigação. O T3-Guard é uma proposta de cibersegurança industrial com processamento local e sem dependência de internet. Em bancada, o gateway verifica a integridade e a origem das amostras, rejeita mensagens alteradas ou repetidas e publica qualidade e frescor por Modbus TCP de leitura. O projeto também demonstra, em simulação, a votação 2oo3 para comparar canais e registrar transições. Pressão em um skid é o primeiro caso de uso. A próxima etapa é validar um modelo de IA treinado offline para emitir alertas locais e avaliar a inferência na FPGA.

## Contexto e aplicações

O incidente de 2023 em uma estação de bombeamento de Aliquippa, na Pensilvânia, e o caso Stuxnet na instalação de enriquecimento de urânio de Natanz ilustram o impacto que incidentes digitais podem ter sobre operações físicas. O roubo de tokens do Facebook em 2018 ilustra a proteção de credenciais em um contexto distinto de controle de acesso digital. Esses casos contextualizam a proposta de monitoramento defensivo. [Registro legislativo sobre Aliquippa](https://www.palegis.us/legislation/bills/text/PDF/2025/0/HR0087/PN0717) · [Audiência sobre Natanz](https://www.govinfo.gov/content/pkg/CHRG-119hhrg62627/html/CHRG-119hhrg62627.htm) · [Comunicado do Facebook](https://about.fb.com/news/2018/10/update-on-security-issue/amp/)

A mesma arquitetura pode ser adaptada a linhas de processo e bombeamento que medem pressão, vazão, nível ou temperatura. Cada aplicação pede instrumentação e validação próprias. O monitoramento de eventos de trancas eletrônicas é uma possível extensão civil, com dados de acesso e critérios específicos.

## Base de dados e artigo

Usamos a base pública PRONTO para reproduzir medições reais de uma bancada de escoamento multifásico. O ensaio toma uma série de pressão do ponto PT417, deriva três canais a partir dela e introduz um desvio em B. A árvore de decisão foi treinada e testada offline em um conjunto sintético separado. A integração do modelo ao fluxo de diagnóstico e a validação em bancada com três transmissores independentes são etapas seguintes. [Base PRONTO](https://zenodo.org/records/1341583) · [Stief et al., *Journal of Process Control*, 2019](https://doi.org/10.1016/j.jprocont.2019.04.009)

## Escopo de cibersegurança para a inscrição

O protótipo atual demonstra diagnóstico de discrepância, registro de eventos e consulta Modbus de leitura. O replay PRONTO usa três canais derivados de uma medição e um desvio injetado em B. Esse ensaio confirma que a divergência chega à supervisão. A mesma divergência pode ocorrer por falha física e exige investigação da causa.

A demonstração de cibersegurança autentica a origem e a integridade das amostras na entrada interna do gateway. Três produtores simulados assinam suas amostras com chaves próprias. O gateway verifica a sessão e o contador de cada canal antes de atualizar a leitura. A regra de discrepância em Python compara leituras aceitas e a telemetria Modbus expõe os motivos de rejeição e o frescor por canal.

- **Amostra válida:** aceitar a leitura e mostrar qualidade e frescor pelo FC04.
- **Amostra alterada:** demonstrar em uma fixture local que a verificação de integridade rejeita a leitura e registra o motivo.
- **Amostra repetida:** confirmar que uma leitura já aceita é rejeitada e que o frescor permanece associado à última amostra válida.
- **Canal autenticado divergente:** sinalizar discrepância pela votação. A autenticação confirma a procedência da mensagem. A comparação ajuda a avaliar a leitura.

## Vídeo e roteiro

- **0:00–0:30** Usar o caso de Aliquippa para apresentar o risco de usar dados comprometidos em uma operação crítica.
- **0:30–1:20** Mostrar a aceitação de uma amostra válida e a rejeição de amostras alteradas ou repetidas em bancada isolada.
- **1:20–2:00** Mostrar o diagnóstico 2oo3 e o que o operador enxerga no Modbus TCP.
- **2:00–2:30** Explicar o uso dos dados do PRONTO, citar o artigo e apresentar a avaliação da IA local como próxima etapa.

O [vídeo de integridade](docs/video-integridade.mp4) usa registradores capturados via FC04 em loopback. O [vídeo do RTL](docs/video.mp4) demonstra a votação 2oo3. A integração com produtores físicos e um CLP permanece pendente.

## Publicação

O regulamento pede repositório público novo no GitHub, demo acessível, vídeo de até três minutos sem login e aceite no painel do time até 30 de novembro de 2026, às 23h59. [Regulamento oficial](https://hackbrasil.com/regulamento)

- Demo RTL, vídeo de votação e vídeo de integridade disponíveis localmente em [docs/index.html](docs/index.html), [docs/video.mp4](docs/video.mp4) e [docs/video-integridade.mp4](docs/video-integridade.mp4).

- [Repositório no GitHub](https://github.com/JoaoVitorCLima/T3-Guard)
