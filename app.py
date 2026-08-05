import streamlit as st
import pandas as pd
from game import Game
from feature_extractor import FeatureExtractor
from caixa_api import CaixaAPIError
from database import Database
from download_historico import baixar_concursos
from analise import AnaliseLotofacil

st.set_page_config(page_title="Lotofácil Analytics", layout="wide")

st.title("🍀 Lotofácil Analytics - MVP")
st.markdown("""
Ferramenta para analisar estatísticas e características da Lotofácil.
Use a aba **Análise** para ver o histórico completo, ou insira um jogo na sidebar.
""")

DB_PATH = "lotofacil.db"


# ============================================================
# SIDEBAR - Download de Concursos
# ============================================================
st.sidebar.header("💾 Dados")
st.sidebar.caption("Baixe o histórico de concursos da API da Caixa para o SQLite.")


def status_banco() -> str:
    """Retorna texto com o estado atual do banco."""
    try:
        with Database(DB_PATH) as db:
            total = db.count()
            ultimo = db.get_ultimo_numero()
    except Exception:
        return "❌ Banco indisponível"
    if total == 0:
        return "📭 Banco vazio (0 concursos)"
    return f"✅ {total} concursos salvos (até o nº {ultimo})"


if "download_status" not in st.session_state:
    st.session_state.download_status = status_banco()

st.sidebar.info(st.session_state.download_status)

# Opções de download
st.sidebar.markdown("---")
lote = st.sidebar.selectbox(
    "Quantidade de concursos por lote",
    options=[100, 200, 500, 1000, "Todos"],
    index=1,
    help="Baixa em lotes para evitar timeout. Use 'Todos' para baixar até o último."
)

# Botão para baixar
if st.sidebar.button("⬇️ Baixar concursos", type="primary", use_container_width=True):
    with st.status("📥 Baixando concursos da API da Caixa...", expanded=True) as status:
        from caixa_api import CaixaAPIClient
        client = CaixaAPIClient(delay=0, timeout=10)
        try:
            ultimo_disponivel = client.get_ultimo_numero()
            st.write(f"📅 Último concurso disponível: **{ultimo_disponivel}**")
        except CaixaAPIError as e:
            st.error(f"❌ Erro ao consultar API: {e}")
            st.stop()

        with Database(DB_PATH) as db_check:
            ultimo_salvo = db_check.get_ultimo_numero()
        inicio = (ultimo_salvo + 1) if ultimo_salvo else 1
        fim = ultimo_disponivel

        if lote != "Todos":
            fim = min(inicio + lote - 1, ultimo_disponivel)

        if inicio > ultimo_disponivel:
            st.success(f"✅ Banco já atualizado até o concurso {ultimo_disponivel}!")
            st.stop()

        total_concursos = fim - inicio + 1
        st.write(f"⏳ Baixando concursos **{inicio}** até **{fim}** "
                 f"({total_concursos} concursos)")

        progress_bar = st.progress(0.0, text="Iniciando...")
        log_area = st.empty()

        def on_progress(atual, ultimo, baixados, erros):
            frac = (atual - inicio + 1) / total_concursos
            progress_bar.progress(
                min(frac, 1.0),
                text=f"Concursos {atual}/{fim} | "
                     f"{baixados} baixados | {erros} erros"
            )

        def on_log(msg):
            log_area.text(msg)

        try:
            resultado = baixar_concursos(
                db_path=DB_PATH,
                inicio=inicio,
                delay=0.3,
                timeout=10,
                progress_callback=on_progress,
                log_callback=on_log,
            )
        except CaixaAPIError as e:
            st.error(f"❌ Erro durante o download: {e}")
            st.stop()

        progress_bar.progress(1.0, text="Concluído!")
        st.success(
            f"✅ Download concluído! "
            f"{resultado.baixados} baixados, {resultado.erros} erros, "
            f"{resultado.total_banco} concursos no banco "
            f"({resultado.tempo_total:.0f}s)."
        )
        status.update(label="✅ Download concluído!", state="complete")
        st.session_state.download_status = status_banco()
        st.rerun()


# ============================================================
# ABAS
# ============================================================
tab_jogo, tab_analise = st.tabs(["🎲 Jogo", "📊 Análise"])

# ============================================================
# ABA 1 - Jogo (análise de um jogo específico)
# ============================================================
with tab_jogo:
    st.sidebar.markdown("---")
    st.sidebar.header("🎲 Novo Jogo")

    input_numbers = st.sidebar.text_input(
        "Digite 15 números separados por espaço (ex: 1 2 3 ... 25)",
        placeholder="1 2 3 5 8 9 10 13 14 17 19 21 23 24 25"
    )

    if st.sidebar.button("Carregar Exemplo"):
        input_numbers = "1 2 3 5 8 9 10 13 14 17 19 21 23 24 25"
        st.sidebar.success("Exemplo carregado!")

    if input_numbers:
        try:
            numbers_list = [int(x) for x in input_numbers.split()]

            if len(numbers_list) != 15:
                st.error(f"❌ Erro: São necessários exatamente 15 números. Você digitou {len(numbers_list)}.")
                st.stop()

            if not all(1 <= n <= 25 for n in numbers_list):
                st.error("❌ Erro: Todos os números devem estar entre 1 e 25.")
                st.stop()

            if len(numbers_list) != len(set(numbers_list)):
                st.error("❌ Erro: Existem números duplicados.")
                st.stop()

            numbers_list.sort()
            game = Game(concurso=0, data="Hoje", numbers=tuple(numbers_list))
            extractor = FeatureExtractor()
            features = extractor.extract(game)

            st.success("✅ Jogo válido! Veja as estatísticas abaixo:")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.subheader("📊 Básicos")
                st.metric("Soma", features.soma)
                st.metric("Pares", features.pares)
                st.metric("Ímpares", features.impares)
                st.metric("Amplitude", features.amplitude)

            with col2:
                st.subheader("🎯 Região")
                st.metric("Moldura", features.moldura)
                st.metric("Miolo", features.miolo)

            with col3:
                st.subheader("🔢 Grupos")
                st.metric("Primos", features.primos)
                st.metric("Fibonacci", features.fibonacci)
                st.metric("Múltiplos de 3", features.multiplos_3)
                st.metric("Múltiplos de 4", features.multiplos_4)
                st.metric("Múltiplos de 5", features.multiplos_5)

            st.divider()

            st.subheader("🔗 Sequências e Blocos")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Qtd. Blocos", features.quantidade_blocos)
            with c2:
                st.metric("Maior Bloco", features.maior_bloco)
            with c3:
                st.metric("Menor Bloco", features.menor_bloco)

            if features.blocos:
                st.write(f"**Tamanhos dos blocos:** {features.blocos}")
                st.write(f"**Entropia dos blocos:** {features.entropia_blocos}")

            st.divider()

            st.subheader("📍 Distribuição Espacial")
            c_linhas, c_colunas = st.columns(2)

            with c_linhas:
                st.write("**Linhas (1-5):**")
                for i, count in enumerate(features.linhas, 1):
                    st.write(f"Linha {i}: {count} números")

            with c_colunas:
                st.write("**Colunas (1-5):**")
                for i, count in enumerate(features.colunas, 1):
                    st.write(f"Coluna {i}: {count} números")

            st.divider()
            st.subheader("🎨 Volante")

            grid = []
            for i in range(1, 26):
                if i in numbers_list:
                    grid.append(f"✅ **{i}**")
                else:
                    grid.append(f"⬜ {i}")

            cols = st.columns(5)
            for idx, item in enumerate(grid):
                row = idx // 5
                col = idx % 5
                with cols[col]:
                    st.markdown(item)

        except ValueError:
            st.error("❌ Erro: Por favor, digite apenas números inteiros separados por espaço.")

    else:
        st.info("👈 Digite os números na barra lateral para começar a análise.")


# ============================================================
# ABA 2 - Análise do Histórico
# ============================================================
with tab_analise:
    st.header("📊 Análise do Histórico")

    # Verificar se há dados no banco
    with Database(DB_PATH) as db:
        total_concursos = db.count()

    if total_concursos == 0:
        st.warning("📭 Nenhum concurso salvo no banco. "
                   "Use o botão **⬇️ Baixar concursos** na sidebar para baixar o histórico.")
        st.stop()

    # Carregar análise (com cache)
    @st.cache_data(ttl=300, show_spinner="Calculando features do histórico...")
    def carregar_analise():
        analise = AnaliseLotofacil(DB_PATH)
        return analise.gerar_dataframe()

    df = carregar_analise()

    if df.empty:
        st.error("❌ Não foi possível gerar a análise.")
        st.stop()

    st.success(f"✅ Analisados **{len(df)} concursos** "
               f"(do concurso {df['concurso'].min()} ao {df['concurso'].max()})")

    # Filtro por período
    st.markdown("---")
    col_filtro1, col_filtro2 = st.columns(2)
    with col_filtro1:
        concurso_min = int(df["concurso"].min())
        concurso_max = int(df["concurso"].max())
        faixa = st.slider(
            "Faixa de concursos",
            min_value=concurso_min,
            max_value=concurso_max,
            value=(concurso_min, concurso_max),
            step=50,
        )
    with col_filtro2:
        st.caption("")
        st.caption("Filtre a faixa de concursos para analisar um período específico.")

    df_filtrado = df[
        (df["concurso"] >= faixa[0]) & (df["concurso"] <= faixa[1])
    ].copy()

    st.info(f"📌 Analisando **{len(df_filtrado)} concursos** "
            f"(nº {faixa[0]} a {faixa[1]})")

    # ============================================================
    # 1. Features Estruturais
    # ============================================================
    st.subheader("📊 Features Estruturais")
    st.caption("Soma, pares, ímpares, amplitude, repetidas e novas")

    col_est1, col_est2 = st.columns(2)

    with col_est1:
        st.markdown("**Estatísticas descritivas**")
        colunas_estruturais = ["soma", "pares", "impares", "amplitude",
                               "repetidas", "novas"]
        st.dataframe(
            df_filtrado[colunas_estruturais].describe().T[
                ["mean", "std", "min", "25%", "50%", "75%", "max"]
            ].round(2),
            use_container_width=True,
        )

    with col_est2:
        st.markdown("**Frequência de pares e ímpares**")
        freq_pares = df_filtrado["pares"].value_counts().sort_index()
        freq_impares = df_filtrado["impares"].value_counts().sort_index()

        st.bar_chart(
            pd.DataFrame({
                "Pares": freq_pares,
                "Ímpares": freq_impares,
            }).fillna(0),
            use_container_width=True,
        )

    st.divider()

    # ============================================================
    # 2. Features Espaciais
    # ============================================================
    st.subheader("📍 Features Espaciais")
    st.caption("Distribuição por linhas, colunas, moldura e miolo do volante 5x5")

    col_esp1, col_esp2 = st.columns(2)

    with col_esp1:
        st.markdown("**Média por linha do volante**")
        linhas_df = pd.DataFrame({
            "Linha 1": df_filtrado["linha_1"].mean(),
            "Linha 2": df_filtrado["linha_2"].mean(),
            "Linha 3": df_filtrado["linha_3"].mean(),
            "Linha 4": df_filtrado["linha_4"].mean(),
            "Linha 5": df_filtrado["linha_5"].mean(),
        }, index=["Média"]).T
        st.dataframe(linhas_df.round(2), use_container_width=True)

        st.markdown("**Média por coluna do volante**")
        colunas_df = pd.DataFrame({
            "Coluna 1": df_filtrado["coluna_1"].mean(),
            "Coluna 2": df_filtrado["coluna_2"].mean(),
            "Coluna 3": df_filtrado["coluna_3"].mean(),
            "Coluna 4": df_filtrado["coluna_4"].mean(),
            "Coluna 5": df_filtrado["coluna_5"].mean(),
        }, index=["Média"]).T
        st.dataframe(colunas_df.round(2), use_container_width=True)

    with col_esp2:
        st.markdown("**Distribuição média de linhas**")
        st.bar_chart(
            pd.DataFrame({
                "Linha 1": df_filtrado["linha_1"].mean(),
                "Linha 2": df_filtrado["linha_2"].mean(),
                "Linha 3": df_filtrado["linha_3"].mean(),
                "Linha 4": df_filtrado["linha_4"].mean(),
                "Linha 5": df_filtrado["linha_5"].mean(),
            }, index=["Média"]).T,
            use_container_width=True,
        )

        st.markdown("**Distribuição média de colunas**")
        st.bar_chart(
            pd.DataFrame({
                "Coluna 1": df_filtrado["coluna_1"].mean(),
                "Coluna 2": df_filtrado["coluna_2"].mean(),
                "Coluna 3": df_filtrado["coluna_3"].mean(),
                "Coluna 4": df_filtrado["coluna_4"].mean(),
                "Coluna 5": df_filtrado["coluna_5"].mean(),
            }, index=["Média"]).T,
            use_container_width=True,
        )

    st.markdown("**Moldura vs Miolo**")
    col_mol1, col_mol2 = st.columns(2)
    with col_mol1:
        st.metric("Média Moldura", f"{df_filtrado['moldura'].mean():.2f}")
        st.metric("Média Miolo", f"{df_filtrado['miolo'].mean():.2f}")
    with col_mol2:
        freq_moldura = df_filtrado["moldura"].value_counts().sort_index()
        freq_miolo = df_filtrado["miolo"].value_counts().sort_index()
        st.bar_chart(
            pd.DataFrame({
                "Moldura": freq_moldura,
                "Miolo": freq_miolo,
            }).fillna(0),
            use_container_width=True,
        )

    st.divider()

    # ============================================================
    # 3. Features Numéricas Especiais
    # ============================================================
    st.subheader("🔢 Features Numéricas Especiais")
    st.caption("Primos, Fibonacci e múltiplos de 3, 4 e 5")

    col_num1, col_num2 = st.columns(2)

    with col_num1:
        st.markdown("**Estatísticas descritivas**")
        colunas_numericas = ["primos", "fibonacci",
                             "multiplos_3", "multiplos_4", "multiplos_5"]
        st.dataframe(
            df_filtrado[colunas_numericas].describe().T[
                ["mean", "std", "min", "25%", "50%", "75%", "max"]
            ].round(2),
            use_container_width=True,
        )

    with col_num2:
        st.markdown("**Frequência de primos**")
        freq_primos = df_filtrado["primos"].value_counts().sort_index()
        st.bar_chart(freq_primos, use_container_width=True)

        st.markdown("**Frequência de Fibonacci**")
        freq_fib = df_filtrado["fibonacci"].value_counts().sort_index()
        st.bar_chart(freq_fib, use_container_width=True)

    st.divider()

    # ============================================================
    # 4. Tabela completa
    # ============================================================
    st.subheader("📋 Tabela Completa")
    st.caption("Todas as features calculadas por concurso")

    colunas_exibicao = [
        "concurso", "data", "soma", "pares", "impares", "amplitude",
        "repetidas", "novas", "moldura", "miolo",
        "primos", "fibonacci", "multiplos_3", "multiplos_4", "multiplos_5",
        "linha_1", "linha_2", "linha_3", "linha_4", "linha_5",
        "coluna_1", "coluna_2", "coluna_3", "coluna_4", "coluna_5",
    ]
    st.dataframe(
        df_filtrado[colunas_exibicao],
        use_container_width=True,
        height=400,
    )

    # Download CSV
    csv = df_filtrado[colunas_exibicao].to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Baixar CSV",
        data=csv,
        file_name=f"lotofacil_analise_{faixa[0]}_{faixa[1]}.csv",
        mime="text/csv",
    )


# Rodapé
st.divider()
st.markdown("Desenvolvido como parte do MVP Lotofácil Analytics")