import streamlit as st
import pandas as pd

# ---------------- ESTADO INICIAL ----------------

if "logado" not in st.session_state:
    st.session_state["logado"] = False

if "usuarios" not in st.session_state:
    st.session_state["usuarios"] = {"admin": "123"}

if "lojas" not in st.session_state:
    st.session_state["lojas"] = pd.DataFrame(
        columns=["Loja", "Empresa", "CNPJ"]
    )

if "funcionarios" not in st.session_state:
    st.session_state["funcionarios"] = pd.DataFrame(
        columns=["Loja", "Nome", "Cargo", "Salario"]
    )

# ---------------- LOGIN ----------------

def login():
    st.title("🔐 Login")

    user = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if user in st.session_state["usuarios"] and st.session_state["usuarios"][user] == senha:
            st.session_state["logado"] = True
            st.rerun()
        else:
            st.error("Login inválido")

if not st.session_state["logado"]:
    login()
    st.stop()

# ---------------- MENU ----------------

pagina = st.sidebar.radio(
    "MENU",
    [
        "📊 Gerar Folha de Pagamento",
        "🏪 Cadastro Loja",
        "👤 Cadastro Funcionário",
        "🔐 Cadastro Usuário",
        "📄 Folha de Ponto"
    ]
)

# ================= FOLHA =================

if pagina == "📊 Gerar Folha de Pagamento":

    st.title("Folha de Pagamento")

    df_func = st.session_state["funcionarios"]
    df_loja = st.session_state["lojas"]

    if df_func.empty:
        st.warning("Cadastre funcionários primeiro")
        st.stop()

    loja_sel = st.selectbox("Selecione a loja", df_func["Loja"].unique())

    df_filtrado = df_func[df_func["Loja"] == loja_sel]

    funcionario = st.selectbox("Funcionário", df_filtrado["Nome"])

    dados = df_filtrado[df_filtrado["Nome"] == funcionario].iloc[0]

    empresa = df_loja[df_loja["Loja"] == loja_sel]

    if not empresa.empty:
        empresa = empresa.iloc[0]
        st.write("Empresa:", empresa["Empresa"])
        st.write("CNPJ:", empresa["CNPJ"])

    st.write("Cargo:", dados["Cargo"])
    st.write("Salário Base:", dados["Salario"])

    comissao = st.number_input("Comissão", 0.0)
    bonus = st.number_input("Bônus", 0.0)

    bruto = dados["Salario"] + comissao + bonus

    # INSS
    def calcular_inss(salario):
        total = 0
        total += min(salario, 1412) * 0.075
        total += max(min(salario,2666.68)-1412,0)*0.09
        total += max(min(salario,4000.03)-2666.68,0)*0.12
        total += max(min(salario,7786.02)-4000.03,0)*0.14
        return total

    inss = calcular_inss(bruto)

    base_ir = bruto - inss
    irrf = 0 if base_ir <= 5000 else base_ir * 0.275 - 896

    liquido = bruto - inss - irrf

    st.markdown("---")
    st.subheader("Resultado")

    st.write("Bruto:", round(bruto,2))
    st.write("INSS:", round(inss,2))
    st.write("IRRF:", round(irrf,2))
    st.write("💵 Líquido:", round(liquido,2))

# ================= CADASTRO LOJA =================

if pagina == "🏪 Cadastro Loja":

    st.title("Cadastro de Loja")

    df = st.session_state["lojas"]

    loja = st.text_input("Nome da Loja")
    empresa = st.text_input("Empresa")
    cnpj = st.text_input("CNPJ")

    if st.button("Salvar Loja"):
        novo = pd.DataFrame([[loja, empresa, cnpj]], columns=df.columns)
        st.session_state["lojas"] = pd.concat([df, novo], ignore_index=True)
        st.success("Salvo!")

    st.markdown("---")

    for i, row in df.iterrows():
        col1, col2, col3, col4 = st.columns([2,2,2,1])

        col1.write(row["Loja"])
        col2.write(row["Empresa"])
        col3.write(row["CNPJ"])

        if col4.button("❌", key=f"del_loja_{i}"):
            st.session_state["lojas"] = df.drop(i).reset_index(drop=True)
            st.rerun()

# ================= CADASTRO FUNCIONARIO =================

if pagina == "👤 Cadastro Funcionário":

    st.title("Cadastro de Funcionário")

    df = st.session_state["funcionarios"]
    lojas = st.session_state["lojas"]["Loja"]

    if len(lojas) == 0:
        st.warning("Cadastre uma loja primeiro")
        st.stop()

    loja = st.selectbox("Loja", lojas)
    nome = st.text_input("Nome")
    cargo = st.text_input("Cargo")
    salario = st.number_input("Salário")

    if st.button("Salvar Funcionário"):
        novo = pd.DataFrame([[loja, nome, cargo, salario]], columns=df.columns)
        st.session_state["funcionarios"] = pd.concat([df, novo], ignore_index=True)
        st.success("Salvo!")

    st.markdown("---")

    for i, row in df.iterrows():
        col1, col2, col3, col4, col5 = st.columns([2,2,2,2,1])

        col1.write(row["Loja"])
        col2.write(row["Nome"])
        col3.write(row["Cargo"])
        col4.write(row["Salario"])

        if col5.button("❌", key=f"del_func_{i}"):
            st.session_state["funcionarios"] = df.drop(i).reset_index(drop=True)
            st.rerun()

# ================= CADASTRO USUARIO =================

if pagina == "🔐 Cadastro Usuário":

    st.title("Cadastro de Usuários")

    user = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Salvar"):
        st.session_state["usuarios"][user] = senha
        st.success("Usuário criado!")

    st.subheader("Usuários")

    for u in st.session_state["usuarios"]:
        st.write(u)

# ================= FOLHA DE PONTO =================

if pagina == "📄 Folha de Ponto":

    st.title("Folha de Ponto")

    arquivo = st.file_uploader("Enviar planilha Excel", type=["xlsx"])

    if arquivo:
        df = pd.read_excel(arquivo)

        st.write("Prévia:")
        st.dataframe(df)

        st.success("Planilha carregada com sucesso!")
