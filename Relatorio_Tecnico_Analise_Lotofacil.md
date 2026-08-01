# Relatório Técnico de Análise Estatística da Lotofácil

> **Objetivo:** consolidar todas as análises realizadas sobre a base
> histórica da Lotofácil e registrar os principais padrões estatísticos
> observados.

------------------------------------------------------------------------

# 1. Introdução

Este documento reúne as análises produzidas a partir da planilha
histórica da Lotofácil fornecida pelo usuário.

A base analisada contém aproximadamente **3.750 concursos**.

**Importante:** os resultados apresentados descrevem o comportamento
histórico dos sorteios. Eles **não permitem prever resultados futuros**,
pois cada concurso é um evento aleatório independente.

------------------------------------------------------------------------

# 2. Frequência das dezenas

## Mais frequentes

    Dezena   Ocorrências
  -------- -------------
        20          2343
        10          2333
        25          2328
        11          2305
        13          2283
        24          2274
         1          2274
        14          2269
         4          2265
         3          2257

## Menos frequentes

    Dezena   Ocorrências
  -------- -------------
        16          2141
         8          2170
        23          2199
        17          2201
         6          2205
         7          2213
        21          2229
        18          2233
        19          2234
         9          2238

------------------------------------------------------------------------

# 3. Distribuição de ímpares e pares

  Configuração     Frequência
  -------------- ------------
  8×7                    1172
  7×8                     956
  9×6                     768
  6×9                     429
  10×5                    268
  5×10                    102

Conclusão: concursos com **7 a 9 ímpares** predominam.

------------------------------------------------------------------------

# 4. Soma das dezenas

-   Soma mínima: **133**
-   Soma máxima: **257**
-   Média: **195,13**
-   Mediana: **195**

Faixa histórica típica: **185--205**.

------------------------------------------------------------------------

# 5. Números atrasados

    Dezena   Atraso
  -------- --------
        16        5
        10        3
        18        2
         4        1
         5        1
         6        1
        13        1
        15        1
        20        1
        22        1

------------------------------------------------------------------------

# 6. Pares mais frequentes

1.  11--20
2.  10--25
3.  10--20
4.  13--20
5.  20--25
6.  14--20
7.  10--11
8.  1--10
9.  9--10
10. 10--14

------------------------------------------------------------------------

# 7. Sequências consecutivas

Foi observado que a maior parte dos concursos possui entre **8 e 9 pares
consecutivos**.

Portanto, eliminar jogos com sequências consecutivas não encontra
suporte nos dados históricos.

------------------------------------------------------------------------

# 8. Distribuição por linhas

A configuração mais recorrente foi:

    3 - 3 - 3 - 3 - 3

Outras distribuições comuns:

-   3-4-3-2-3
-   3-3-4-2-3
-   4-3-3-2-3

------------------------------------------------------------------------

# 9. Repetição de dezenas

Distribuição observada entre concursos consecutivos:

    Repetidas   Frequência
  ----------- ------------
            9         1217
            8          919
           10          823
            7          349
           11          315
           12           63

Conclusão:

A maior parte dos concursos repete **8 a 10 dezenas**.

------------------------------------------------------------------------

# 10. Moldura × Miolo

Distribuições predominantes:

    Moldura   Miolo
  --------- -------
         10       5
          9       6
         11       4
          8       7
         12       3

------------------------------------------------------------------------

# 11. Trincas mais frequentes

-   10--20--25
-   11--13--20
-   10--11--20
-   10--14--20
-   10--12--25

------------------------------------------------------------------------

# 12. Estratégia estatística sugerida

Um conjunto de filtros baseado no histórico seria:

-   Soma entre **185 e 205**
-   7 a 9 ímpares
-   8 a 10 dezenas repetidas
-   9 a 11 dezenas na moldura
-   Distribuição equilibrada nas linhas
-   Presença de diversas dezenas consecutivas

Esses filtros apenas aproximam um jogo do perfil histórico mais
frequente.

------------------------------------------------------------------------

# 13. Limitações

Não existe evidência matemática de que dezenas mais frequentes,
atrasadas ou determinadas combinações tenham maior probabilidade de
ocorrer no próximo concurso.

Cada sorteio permanece estatisticamente independente.

------------------------------------------------------------------------

# 14. Próximas análises recomendadas

-   Teste Qui-Quadrado para uniformidade.
-   Correlação entre dezenas.
-   Matriz de coocorrência.
-   Cadeias de Markov.
-   Análise de ciclos completos.
-   Mapas de calor.
-   Frequência móvel.
-   Ranking de jogos.
-   Simulações Monte Carlo.
-   Geração automática de apostas usando múltiplos filtros.

------------------------------------------------------------------------

# Conclusão

A análise mostra que existem padrões históricos consistentes na
distribuição dos resultados da Lotofácil. Esses padrões podem orientar a
construção de jogos mais aderentes ao histórico, mas **não constituem um
método de previsão** nem alteram as probabilidades fundamentais do
sorteio.
