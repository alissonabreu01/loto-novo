import streamlit as st
from game import Game
from feature_extractor import FeatureExtractor
from caixa_api import CaixaAPIError
from database import Database
from download_historico import baixar_concursos

st.set_page_config(page_title="Lotofácil Analytics", layout="wide")

st.title("🍀 Lotofácil Analytics - MVP")
st.markdown("""
Esta ferramenta permite analisar estatísticas e características de jogos da Lotofácil.
Insira 15 números (de 1 a 25) para ver as features calculadas.
""")


# ============================================================
# SIDEBAR - Download de Concursos
# ============================================================
st.sidebar.header("💾 Dados")
st.sidebar.caption("Baixe o histórico de concursos da API da Caixa para o SQLite.")

DB_PATH = "lotofacil.db"


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
        # Consultar último concurso disponível
        from caixa_api import CaixaAPIClient
        client = CaixaAPIClient(delay=0, timeout=10)
        try:
            ultimo_disponivel = client.get_ultimo_numero()
            st.write(f"📅 Último concurso disponível: **{ultimo_disponivel}**")
        except CaixaAPIError as e:
            st.error(f"❌ Erro ao consultar API: {e}")
            st.stop()

        # Definir faixa de download
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

        # Barra de progresso
        progress_bar = st.progress(0.0, text="Iniciando...")

        # Log em tempo real
        log_area = st.empty()

        # Callbacks de progresso e log
        def on_progress(atual, ultimo, baixados, erros):
            frac = (atual - inicio + 1) / total_concursos
            progress_bar.progress(
                min(frac, 1.0),
                text=f"Concursos {atual}/{fim} | "
                     f"{baixados} baixados | {erros} erros"
            )

        def on_log(msg):
            log_area.text(msg)

        # Executar download
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


st.sidebar.markdown("---")
st.sidebar.header("🎲 Novo Jogo")

input_numbers = st.sidebar.text_input(
    "Digite 15 números separados por espaço (ex: 1 2 3 ... 25)",
    placeholder="1 2 3 5 8 9 10 13 14 17 19 21 23 24 25"
)

# Botão para carregar exemplo
if st.sidebar.button("Carregar Exemplo"):
    input_numbers = "1 2 3 5 8 9 10 13 14 17 19 21 23 24 25"
    st.sidebar.success("Exemplo carregado!")

# Processamento
if input_numbers:
    try:
        numbers_list = [int(x) for x in input_numbers.split()]

        # Validações básicas
        if len(numbers_list) != 15:
            st.error(f"❌ Erro: São necessários exatamente 15 números. Você digitou {len(numbers_list)}.")
            st.stop()

        if not all(1 <= n <= 25 for n in numbers_list):
            st.error("❌ Erro: Todos os números devem estar entre 1 e 25.")
            st.stop()

        if len(numbers_list) != len(set(numbers_list)):
            st.error("❌ Erro: Existem números duplicados.")
            st.stop()

        # Ordenar números
        numbers_list.sort()

        # Criar objeto Game
        game = Game(concurso=0, data="Hoje", numbers=tuple(numbers_list))

        # Extrair features
        extractor = FeatureExtractor()
        features = extractor.extract(game)

        # Exibir resultados
        st.success("✅ Jogo válido! Veja as estatísticas abaixo:")

        # Colunas para organização
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

        # Sequências e Blocos
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

        # Distribuição Espacial
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

        # Visualização do Volante
        st.divider()
        st.subheader("🎨 Volante")

        # Criar grid visual
        grid = []
        for i in range(1, 26):
            if i in numbers_list:
                grid.append(f"✅ **{i}**")
            else:
                grid.append(f"⬜ {i}")

        # Exibir em formato 5x5
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

# Rodapé
st.divider()
st.markdown("Desenvolvido como parte do MVP Lotofácil Analytics")