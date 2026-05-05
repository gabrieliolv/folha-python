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

if "funcionarios" not in st.session_state:
    st.session_state["funcionarios"] = pd.DataFrame([
        ["MDO CATALAO","Andressa","GERENTE",3000],
        ["MDO CATALAO","Hellen","VENDAS",1744],
        ["MDO CATALAO","Aline","VENDAS",1744],
        ["MDO CATALAO","Maria Gabriela","CAPTADOR",1800],
        ["MDO ITUIUTABA","Daiane","GERENTE",3000],
        ["MDO ITUIUTABA","Otaviano","VENDAS",1645.20],
        ["MDO ITUIUTABA","Maisa","CAPTADOR",2000],
        ["MDO ARAXA","Geisa","VENDAS",1745],
        ["MDO ARAXA","Emily","VENDAS",1745],
        ["MDO ARAXA","Beatriz","VENDAS",1644.50],
        ["MDO UBERABA","Alisson","GERENTE",4500],
        ["MDO UBERABA","Fabi","VENDAS",1644.50],
        ["MDO UBERABA","Thálita","CAPTADOR",2000],
        ["MDO UBERABA","Gabrieli","FINANCEIRO",3300],
        ["MDO UBERABA","Lara","ADM",1621],
    ], columns=["Loja","Nome","Cargo","Salario"])

# ---------------- MENU ----------------

menu = st.sidebar.selectbox("Menu", ["Folha", "Cadastro"])

# ---------------- CADASTRO ----------------

if menu == "Cadastro":
    st.title("Cadastro de Funcionário")

    loja = st.text_input("Loja")
    nome = st.text_input("Nome")
    cargo = st.text_input("Cargo")
    salario = st.number_input("Salário")

    if st.button("Salvar"):
        novo = pd.DataFrame([[loja,nome,cargo,salario]],
                            columns=["Loja","Nome","Cargo","Salario"])
        st.session_state["funcionarios"] = pd.concat(
            [st.session_state["funcionarios"], novo], ignore_index=True
        )
        st.success("Salvo!")

# ---------------- FOLHA ----------------

if menu == "Folha":
    st.title("Folha de Pagamento")

    df = st.session_state["funcionarios"]

    lojas = df["Loja"].unique()
    loja_sel = st.selectbox("Selecione a loja", lojas)

    df_loja = df[df["Loja"] == loja_sel]

    funcionario = st.selectbox("Funcionário", df_loja["Nome"])

    dados = df_loja[df_loja["Nome"] == funcionario].iloc[0]

    st.write("Cargo:", dados["Cargo"])
    st.write("Salário Base:", dados["Salario"])

    comissao = st.number_input("Comissão", 0.0)
    bonus = st.number_input("Bônus", 0.0)

    bruto = dados["Salario"] + comissao + bonus

    # INSS correto
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
