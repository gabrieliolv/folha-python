import streamlit as st
import pandas as pd
import json
import os

# ---------------- FUNÇÕES JSON ----------------

def carregar_dados():
    if os.path.exists("dados.json"):
        with open("dados.json", "r") as f:
            return json.load(f)
    return {"lojas": [], "funcionarios": [], "usuarios": {"admin": "123"}}

def salvar_dados():
    with open("dados.json", "w") as f:
        json.dump(st.session_state["dados"], f, indent=4)

# ---------------- INICIALIZA ----------------

if "dados" not in st.session_state:
    st.session_state["dados"] = carregar_dados()

if "logado" not in st.session_state:
    st.session_state["logado"] = False

# ---------------- LOGIN ----------------

def login():
    st.title("🔐 Login")

    user = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if user in st.session_state["dados"]["usuarios"] and st.session_state["dados"]["usuarios"][user] == senha:
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

    df_func = pd.DataFrame(st.session_state["dados"]["funcionarios"])
    df_loja = pd.DataFrame(st.session_state["dados"]["lojas"])

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

    loja = st.text_input("Nome da Loja")
    empresa = st.text_input("Empresa")
    cnpj = st.text_input("CNPJ")

    if st.button("Salvar Loja"):
        st.session_state["dados"]["lojas"].append({
            "Loja": loja,
            "Empresa": empresa,
            "CNPJ": cnpj
        })
        salvar_dados()
        st.success("Salvo!")
        st.rerun()

    st.markdown("---")

    for i, row in enumerate(st.session_state["dados"]["lojas"]):
        col1, col2, col3, col4 = st.columns([2,2,2,1])

        col1.write(row["Loja"])
        col2.write(row["Empresa"])
        col3.write(row["CNPJ"])

        if col4.button("❌", key=f"del_loja_{i}"):
            st.session_state["dados"]["lojas"].pop(i)
            salvar_dados()
            st.rerun()

# ================= CADASTRO FUNCIONARIO =================

if pagina == "👤 Cadastro Funcionário":

    st.title("Cadastro de Funcionário")

    lojas = [l["Loja"] for l in st.session_state["dados"]["lojas"]]

    if not lojas:
        st.warning("Cadastre uma loja primeiro")
        st.stop()

    loja = st.selectbox("Loja", lojas)
    nome = st.text_input("Nome")
    cargo = st.text_input("Cargo")
    salario = st.number_input("Salário")

    if st.button("Salvar Funcionário"):
        st.session_state["dados"]["funcionarios"].append({
            "Loja": loja,
            "Nome": nome,
            "Cargo": cargo,
            "Salario": salario
        })
        salvar_dados()
        st.success("Salvo!")
        st.rerun()

    st.markdown("---")

    for i, row in enumerate(st.session_state["dados"]["funcionarios"]):
        col1, col2, col3, col4, col5 = st.columns([2,2,2,2,1])

        col1.write(row["Loja"])
        col2.write(row["Nome"])
        col3.write(row["Cargo"])
        col4.write(row["Salario"])

        if col5.button("❌", key=f"del_func_{i}"):
            st.session_state["dados"]["funcionarios"].pop(i)
            salvar_dados()
            st.rerun()

# ================= CADASTRO USUARIO =================

if pagina == "🔐 Cadastro Usuário":

    st.title("Cadastro de Usuários")

    user = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Salvar"):
        st.session_state["dados"]["usuarios"][user] = senha
        salvar_dados()
        st.success("Usuário criado!")
        st.rerun()

    st.subheader("Usuários")

    for u in st.session_state["dados"]["usuarios"]:
        st.write(u)

# ================= FOLHA DE PONTO =================

if pagina == "📄 Folha de Ponto":

    st.title("Folha de Ponto")

    arquivo = st.file_uploader("Enviar planilha Excel", type=["xlsx"])

    if arquivo:
        df = pd.read_excel(arquivo)

        st.write("Prévia:")
        st.dataframe(df)

        st.success("Planilha carregada!")
