# T3-Guard

**Três canais de entrada, uma decisão em RTL e uma linha do tempo para investigar o disparo.**

Projeto de bancada para a trilha **Logística & automação** do Hack Brasil 2026. O caso de uso é a investigação de paradas em skids e equipamentos industriais da Região Metropolitana de Salvador, com três leituras sintéticas de uma mesma variável, como pressão. Um canal discrepante pode ser sinalizado sem parar a bancada. Um disparo registra o estado dos canais e o ciclo da transição para orientar o diagnóstico.

[Demo](docs/index.html) · [Submissão e roteiro](SUBMISSAO.md) · [Bancada DE0-CV](fpga/README.md) · [Gateway Modbus](gateway/README.md)

O primeiro ensaio de bancada usa pressão. A arquitetura também pode ser adaptada para temperatura, nível ou vazão, com três canais da mesma variável, aquisição compatível e parâmetros específicos para o processo.

## Arquitetura

```text
Entradas sintéticas A/B/C → diagnóstico e votação em SystemVerilog → saída de trip (LED)
                                        └→ último evento com timestamp → UART → gateway FC04 local
Testbench do mesmo RTL → captura CSV → painel com reprodução ciclo a ciclo
```

- **Normal** com três canais saudáveis. São necessários dois votos altos para disparar.
- **Degradado** com um canal excluído. Um único voto alto dos dois restantes dispara.
- **Seguro** com menos de dois canais saudáveis. Disparo imediato e travado até rearme local.
- Um voto sobe em 700 e permanece alto até 650. A escala sintética vai de 0 a 1000. Uma entrada inválida ou fora da escala é excluída quando amostrada.
- A discrepância só isola um canal quando os outros dois concordam entre si e o canal se afasta dos dois por três amostras consecutivas. No teste, a diferença precisa passar de 180 unidades. Votos divergentes sem um outlier isolável continuam sendo avaliados pela votação.
- O watchdog monitora a chegada da amostragem do conjunto. A perda de amostragem invalida os três canais. O trip só libera com um pedido explícito de rearme e uma amostra com três canais saudáveis e baixos.
- O registrador guarda o último evento, com carimbo de ciclo e contador. O CSV retém a sequência completa do testbench. A bancada transmite uma captura periódica; o contador permite perceber eventos intermediários perdidos.

## Executar

Abra [docs/index.html](docs/index.html) no navegador para percorrer a captura gravada. Para reproduzir os testes em Linux ou WSL, rode no diretório do projeto:

```bash
bash sim/run.sh
diff -u docs/trace.csv build/trace.csv
python3 -m unittest discover -s gateway
python3 gateway/modbus.py --replay docs/trace.csv
```

Com o Xcelium no PATH, use `bash sim/run.sh xrun`. O testbench passou no Xcelium 24.09-s013 e no Icarus. Ele percorre os oito padrões binários do 2oo3 e checa exclusão por discrepância, invalidação de canais, 1oo2, histerese, watchdog e condições de rearme.

Para gravar as formas de onda no Xcelium, execute `bash sim/run.sh xrun-waves` e copie o comando `simvision -waves -input ...` exibido no final. O script do visualizador carrega `a`, `b`, `c`, `discrep`, `bad`, `mode` e `trip` e ajusta o zoom para o intervalo completo.

## Diagnóstico offline

O [importador de CSV e experimento de classificação](diagnostico/README.md) comparam uma árvore de decisão com a regra de discrepância usando dados sintéticos reproduzíveis.

## Integridade de medições em bancada

O gateway valida amostras autenticadas e rejeita repetições em uma sessão de bancada. O [ensaio Modbus](gateway/README.md#verificação-de-integridade-em-bancada) usa produtores simulados e expõe frescor por canal e contadores de rejeição via FC04.

## Validação com uma empresa

Proposta inicial para a equipe de automação ou instrumentação da Acelen, em Mataripe, como hipótese de parceiro de bancada. O piloto usa chaves da FPGA e um notebook em ambiente isolado. Critérios de aceite são reproduzir cinco cenários, comparar os registros com a sequência aplicada e medir o tempo para identificar o primeiro evento. A economia de tempo e a redução de paradas indevidas ainda são hipóteses a medir.

Protótipo didático para bancada. A demonstração usa LED como saída. Sensores, estágio de saída, independência e cobertura diagnóstica, falhas de causa comum, deriva, travamento individual e atendimento de SIL dependem de projeto e validação específicos antes de qualquer aplicação industrial.

O [plano de validação](VALIDACAO.md) reúne fontes técnicas e descreve o experimento comparativo para um artigo.

## Referências

- [Regulamento do Hack Brasil](https://hackbrasil.com/regulamento)
- [Terasic DE0-CV](https://www.terasic.com.tw/cgi-bin/page/archive.pl?No=921)
- [Modbus Application Protocol V1.1b3](https://www.modbus.org/file/secure/modbusprotocolspecification.pdf)
