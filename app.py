import streamlit as st
import pandas as pd

# ---------------- LOGIN ----------------
def login():
    st.title("🔐 Login")
    user = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if user == "admin" and senha == "123":
            st.session_state["logado"] = True
        else:
            st.error("Login inválido")

if "logado" not in st.session_state:
    st.session_state["logado"] = False

if not st.session_state["logado"]:
    login()
    st.stop()

# ---------------- DADOS ----------------

if "lojas" not in st.session_state:
    st.session_state["lojas"] = pd.DataFrame([
        ["MDO CATALAO","ÓTICA D M LEITE LTDA","56.100.927/0001-58"],
        ["MDO UBERABA","ÓTICA D M LEITE LTDA","56.100.927/0001-58"]
    ], columns=["Loja","Nome Empresa","CNPJ"])

if "funcionarios" not in st.session_state:
    st.session_state["funcionarios"] = pd.DataFrame([
        ["MDO CATALAO","Andressa","GERENTE",3000],
        ["MDO CATALAO","Hellen","VENDAS",1744],
        ["MDO UBERABA","Gabrieli","FINANCEIRO",3300],
    ], columns=["Loja","Nome","Cargo","Salario"])

# ---------------- MENU ----------------

menu = st.sidebar.selectbox("Menu", ["Folha", "Cadastro Loja", "Cadastro Funcionário"])

# ================= CADASTRO LOJA =================

if menu == "Cadastro Loja":
    st.title("Cadastro de Loja")

    nome_loja = st.text_input("Nome da Loja")
    empresa = st.text_input("Nome da Empresa")
    cnpj = st.text_input("CNPJ")

    if st.button("Salvar Loja"):
        novo = pd.DataFrame([[nome_loja, empresa, cnpj]],
                            columns=["Loja","Nome Empresa","CNPJ"])
        st.session_state["lojas"] = pd.concat(
            [st.session_state["lojas"], novo], ignore_index=True
        )
        st.success("Loja cadastrada!")

# ================= CADASTRO FUNCIONARIO =================

if menu == "Cadastro Funcionário":
    st.title("Cadastro de Funcionário")

    lojas = st.session_state["lojas"]["Loja"]
    loja = st.selectbox("Loja", lojas)

    nome = st.text_input("Nome")
    cargo = st.text_input("Cargo")
    salario = st.number_input("Salário")

    if st.button("Salvar Funcionário"):
        novo = pd.DataFrame([[loja, nome, cargo, salario]],
                            columns=["Loja","Nome","Cargo","Salario"])
        st.session_state["funcionarios"] = pd.concat(
            [st.session_state["funcionarios"], novo], ignore_index=True
        )
        st.success("Funcionário cadastrado!")

# ================= FOLHA (PÁGINA PRINCIPAL) =================

if menu == "Folha":

    st.title("Folha de Pagamento")

    df = st.session_state["funcionarios"]
    lojas = st.session_state["lojas"]

    loja_sel = st.selectbox("Selecione a loja", df["Loja"].unique())
    df_loja = df[df["Loja"] == loja_sel]

    funcionario = st.selectbox("Funcionário", df_loja["Nome"])
    dados = df_loja[df_loja["Nome"] == funcionario].iloc[0]

    empresa = lojas[lojas["Loja"] == loja_sel].iloc[0]

    st.markdown("### Dados")
    st.write("Empresa:", empresa["Nome Empresa"])
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
