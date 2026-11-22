# Plano de validação do T3-Guard

**Pergunta de pesquisa.** O que o diagnóstico acrescenta a um votador 2oo3 simples quando um canal falha?

## Fundamentação

- A [base PRONTO](https://zenodo.org/records/1341583) e o [artigo de Stief et al.](https://doi.org/10.1016/j.jprocont.2019.04.009) fundamentam a reprodução de medições de pressão de um processo físico. O ensaio existente usa a série PT417 e três canais derivados para avaliar a comunicação do diagnóstico ao Modbus.
- A [IEC 61511-1](https://webstore.iec.ch/en/publication/24241) contextualiza sistemas instrumentados de segurança na indústria de processos. O T3-Guard é um protótipo de bancada com saída representada por LED.
- O [artigo da NTNU sobre a configuração 2oo3](https://ntnuopen.ntnu.no/ntnu-xmlui/handle/11250/2772258?locale-attribute=en) fundamenta a arquitetura e a discussão sobre modelagem de confiabilidade.
- O [estudo de campo do SINTEF](https://www.sintef.no/en/publications/publication/0198cc8d8b30-4804a28f-9776-4e42-88cc-41539aff3f9c/) analisa falhas de causa comum reportadas na indústria de petróleo e gás e fundamenta a inclusão de cenários que afetam mais de um canal.

## Experimento proposto

1. Na bancada isolada, usar três sensores independentes medindo a mesma pressão e uma referência calibrada para rotular a demanda de disparo. Usar LED como saída e registrar a pressão de referência, a amostra disponibilizada ao RTL, a transição da saída e o timestamp do evento.
2. Aplicar a mesma sequência ao T3-Guard e a um votador de referência que dispara com dois votos altos. Manter o mesmo limiar, a mesma histerese e a mesma cadência de aquisição. Registrar os parâmetros de diagnóstico do T3-Guard.
3. Repetir com processo estável, cruzamento do limiar, um canal inválido, um canal discordante, dois canais inválidos e erro compartilhado por dois canais. Incluir o retorno à condição normal e o pedido de rearme.
4. Por cenário, reportar número de repetições, disparos sem demanda, demandas sem disparo e latência do primeiro disparo esperado. Relatar separadamente a latência entre amostra e saída e a latência total da cadeia de aquisição. Medir o atraso da telemetria Modbus à parte.

Se a bancada física ainda estiver indisponível, uma série real de processo do [SWaT, da SUTD](https://www.sutd.edu.sg/itrust/itrust-labs/datasets/dataset-characteristics/swat/) pode servir de entrada para um ensaio de reprodução. Ao derivar três canais da mesma série, identificar a origem comum das leituras e documentar as perturbações injetadas. Conferir os termos da base antes de redistribuir os arquivos.

A captura publicada com o painel vem de um testbench com dados sintéticos. O experimento de bancada e as medições comparativas acima permanecem propostos.

## Aceite do piloto com uma equipe de instrumentação

Em bancada isolada, reproduzir operação nominal, alteração de mensagem, repetição, divergência de um transmissor e perda de dois canais. Registrar a condição de referência, o instante do evento, o primeiro alerta e o instante em que o operador identifica o canal. Comparar as mesmas condições com o diagnóstico desabilitado e habilitado no supervisório. Usar a mediana do tempo de identificação, os alarmes indevidos por ensaio e as horas de integração como métricas. Registrar repetições e resultados por cenário. O parceiro define as metas do piloto junto com a equipe.

## Avaliação da detecção precoce com IA local

Treinar no notebook e separar as séries por ensaio completo. Registrar o instante de início de cada perturbação e comparar a árvore com a regra de discrepância em séries de teste reservadas. Medir falsos alarmes, eventos não detectados e tempo entre o primeiro sinal observável e o alerta. Repetir a comparação quando houver dados de três transmissores independentes. Para o modelo embarcado, usar os mesmos vetores no Python e no RTL e comparar as saídas antes de medir a latência na FPGA. A votação 2oo3 permanece responsável pela saída de disparo.
