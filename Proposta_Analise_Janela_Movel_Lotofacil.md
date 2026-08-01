# Proposta de Estudo: Análise por Janela Móvel (Rolling Window Analysis) na Lotofácil

## Objetivo

Avaliar qual tamanho de janela histórica reproduz com maior fidelidade o
comportamento estatístico observado em toda a série histórica da
Lotofácil.

Em vez de analisar apenas o histórico completo, a ideia é estudar
subconjuntos consecutivos (janelas móveis) e medir o quanto eles se
aproximam do perfil global.

------------------------------------------------------------------------

# Motivação

A análise global representa uma fotografia da história completa dos
concursos.

Entretanto, ela não responde perguntas como:

-   Quantos concursos são necessários para representar o comportamento
    histórico?
-   Uma janela de 20 concursos é suficiente?
-   Existe um ponto de convergência estatística?
-   O comportamento recente difere significativamente do histórico
    completo?

A análise por janela móvel busca responder essas questões.

------------------------------------------------------------------------

# Conceito de Janela Móvel

Considere uma série de N concursos.

Para uma janela W:

-   Janela 1: concursos 1 até W
-   Janela 2: concursos 2 até W+1
-   Janela 3: concursos 3 até W+2
-   ...
-   Última janela: concursos N-W+1 até N

Cada janela gera um conjunto completo de estatísticas.

------------------------------------------------------------------------

# Estatísticas calculadas em cada janela

Para cada janela recomenda-se calcular:

-   frequência das 25 dezenas;
-   frequência relativa;
-   distribuição de pares e ímpares;
-   soma das dezenas;
-   amplitude;
-   moldura × miolo;
-   linhas e colunas;
-   quantidade de sequências consecutivas;
-   repetição em relação ao concurso anterior;
-   pares, trincas e quartetos mais frequentes.

Essas estatísticas são comparadas com o perfil obtido usando toda a base
histórica.

------------------------------------------------------------------------

# Métricas de comparação

## 1. Correlação de Pearson

Mede a semelhança entre os vetores de frequência.

Interpretação:

-   1,00 → praticamente idêntico;
-   0,95 → extremamente semelhante;
-   0,90 → muito semelhante;
-   abaixo de 0,80 → diferenças relevantes.

------------------------------------------------------------------------

## 2. Distância Euclidiana

Quantifica a diferença absoluta entre as frequências observadas.

Quanto menor o valor, mais próxima a janela está do histórico completo.

------------------------------------------------------------------------

## 3. Erro Quadrático Médio (RMSE)

Mede o erro médio entre a distribuição da janela e a distribuição
global.

Menor RMSE indica melhor aderência.

------------------------------------------------------------------------

## 4. Divergência de Jensen--Shannon

Compara distribuições de probabilidade.

É simétrica e limitada.

Valor zero representa distribuições idênticas.

------------------------------------------------------------------------

## 5. Distância de Cosseno (opcional)

Mede a semelhança angular entre os vetores de frequência.

Útil para comparar o formato da distribuição independentemente da
escala.

------------------------------------------------------------------------

# Procedimento Experimental

1.  Calcular o perfil estatístico global.
2.  Definir um intervalo de tamanhos de janela (por exemplo, de 10 a 500
    concursos).
3.  Para cada tamanho W:
    -   gerar todas as janelas móveis possíveis;
    -   calcular as estatísticas de cada janela;
    -   comparar com o perfil global usando as métricas escolhidas.
4.  Resumir os resultados por tamanho de janela (média, mediana,
    desvio-padrão e pior/melhor caso).

------------------------------------------------------------------------

# Produtos Esperados

## Curva de convergência

Gráfico mostrando como a semelhança aumenta conforme a janela cresce.

## Curva do erro

RMSE médio por tamanho de janela.

## Boxplots

Distribuição das métricas para todas as janelas de um mesmo tamanho.

## Heatmap

Mapa de calor com:

-   eixo X: tamanho da janela;
-   eixo Y: posição da janela;
-   cor: grau de semelhança com o histórico.

------------------------------------------------------------------------

# Critério de Convergência

Define-se um limiar objetivo, por exemplo:

-   Correlação ≥ 0,95;
-   RMSE abaixo de um valor previamente estabelecido;
-   Divergência Jensen--Shannon abaixo de um limite.

O menor tamanho de janela que satisfizer o critério será considerado a
**janela mínima de convergência**.

------------------------------------------------------------------------

# Hipóteses

Hipótese nula (H0):

O comportamento estatístico das janelas é compatível com o comportamento
do histórico completo.

Hipótese alternativa (H1):

Janelas pequenas apresentam comportamento significativamente diferente.

------------------------------------------------------------------------

# Possíveis Resultados

A análise poderá indicar, por exemplo:

-   janelas de 10 concursos são altamente instáveis;
-   a estabilidade cresce rapidamente entre 30 e 80 concursos;
-   acima de determinado tamanho, os ganhos tornam-se marginais.

O valor exato deve ser obtido empiricamente a partir dos dados.

------------------------------------------------------------------------

# Aplicações

-   definir a quantidade ideal de concursos para análises;
-   comparar o comportamento recente com o histórico;
-   detectar mudanças estatísticas ao longo do tempo;
-   construir modelos de geração de jogos baseados em janelas recentes;
-   identificar períodos atípicos.

------------------------------------------------------------------------

# Extensões

-   janelas ponderadas (mais peso para concursos recentes);
-   janelas exponenciais;
-   análise por regime;
-   detecção de pontos de mudança (change point detection);
-   comparação entre diferentes loterias;
-   integração com modelos preditivos para pesquisa.

------------------------------------------------------------------------

# Conclusão

A análise por janela móvel é uma metodologia robusta para estudar
estabilidade estatística. Em vez de assumir que todo o histórico deve
ser utilizado, ela permite determinar, com base em evidências
quantitativas, qual é o menor conjunto de concursos capaz de reproduzir
o comportamento global da Lotofácil.
