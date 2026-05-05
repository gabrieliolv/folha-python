import streamlit as st
import pandas as pd
from supabase import create_client

# ================= CONFIG SUPABASE =================

SUPABASE_URL = "https://llaikgnepnvppqdaujbg.supabase.co"
SUPABASE_KEY = "sb_publishable_Zp_d7qXsU9Ir7y2TOOyJsQ_3tnCYhKd"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ================= LOGIN =================

if "logado" not in st.session_state:
    st.session_state["logado"] = False

def login():
    st.title("🔐 Login")

    user = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        res = supabase.table("usuarios").select("*").eq("usuario", user).execute()

        if res.data and res.data[0]["senha"] == senha:
            st.session_state["logado"] = True
            st.rerun()
        else:
            st.error("Login inválido")

if not st.session_state["logado"]:
    login()
    st.stop()

# ================= MENU =================

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

# ================= FUNÇÃO BUSCAR DADOS =================

def get_lojas():
    res = supabase.table("lojas").select("*").execute()
    return pd.DataFrame(res.data)

def get_funcionarios():
    res = supabase.table("funcionarios").select("*").execute()
    return pd.DataFrame(res.data)

# ================= FOLHA =================

if pagina == "📊 Gerar Folha de Pagamento":

    st.title("Folha de Pagamento")

    df_lojas = get_lojas()
    df_func = get_funcionarios()

    if df_func.empty:
        st.warning("Cadastre funcionários primeiro")
        st.stop()

    df = df_func.merge(df_lojas, left_on="loja_id", right_on="id")

    loja_sel = st.selectbox("Selecione a loja", df["nome_loja"].unique())

    df_filtrado = df[df["nome_loja"] == loja_sel]

    funcionario = st.selectbox("Funcionário", df_filtrado["nome"])

    dados = df_filtrado[df_filtrado["nome"] == funcionario].iloc[0]

    st.write("Empresa:", dados["empresa"])
    st.write("CNPJ:", dados["cnpj"])
    st.write("Cargo:", dados["cargo"])
    st.write("Salário Base:", dados["salario"])

    comissao = st.number_input("Comissão", 0.0)
    bonus = st.number_input("Bônus", 0.0)

    bruto = dados["salario"] + comissao + bonus

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
        supabase.table("lojas").insert({
            "nome_loja": loja,
            "empresa": empresa,
            "cnpj": cnpj
        }).execute()

        st.success("Salvo!")
        st.rerun()

    st.markdown("---")

    df_lojas = get_lojas()

    for _, row in df_lojas.iterrows():
        col1, col2, col3, col4 = st.columns([2,2,2,1])

        col1.write(row["nome_loja"])
        col2.write(row["empresa"])
        col3.write(row["cnpj"])

        if col4.button("❌", key=f"del_loja_{row['id']}"):
            supabase.table("lojas").delete().eq("id", row["id"]).execute()
            st.rerun()

# ================= CADASTRO FUNCIONARIO =================

if pagina == "👤 Cadastro Funcionário":

    st.title("Cadastro de Funcionário")

    df_lojas = get_lojas()

    if df_lojas.empty:
        st.warning("Cadastre uma loja primeiro")
        st.stop()

    loja_sel = st.selectbox("Loja", df_lojas["nome_loja"])
    loja_id = df_lojas[df_lojas["nome_loja"] == loja_sel]["id"].values[0]

    nome = st.text_input("Nome")
    cargo = st.text_input("Cargo")
    salario = st.number_input("Salário")

    if st.button("Salvar Funcionário"):
        supabase.table("funcionarios").insert({
            "loja_id": int(loja_id),
            "nome": nome,
            "cargo": cargo,
            "salario": salario
        }).execute()

        st.success("Salvo!")
        st.rerun()

    st.markdown("---")

    df_func = get_funcionarios()

    for _, row in df_func.iterrows():
        col1, col2, col3, col4, col5 = st.columns([2,2,2,2,1])

        col1.write(row["loja_id"])
        col2.write(row["nome"])
        col3.write(row["cargo"])
        col4.write(row["salario"])

        if col5.button("❌", key=f"del_func_{row['id']}"):
            supabase.table("funcionarios").delete().eq("id", row["id"]).execute()
            st.rerun()

# ================= CADASTRO USUARIO =================

if pagina == "🔐 Cadastro Usuário":

    st.title("Cadastro de Usuários")

    user = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Salvar"):
        supabase.table("usuarios").insert({
            "usuario": user,
            "senha": senha
        }).execute()

        st.success("Usuário criado!")
        st.rerun()

    res = supabase.table("usuarios").select("*").execute()

    for u in res.data:
        st.write(u["usuario"])

# ================= FOLHA DE PONTO =================

if pagina == "📄 Folha de Ponto":

    st.title("Folha de Ponto")

    arquivo = st.file_uploader("Enviar planilha Excel", type=["xlsx"])

    if arquivo:
        df = pd.read_excel(arquivo)

        st.write("Prévia:")
        st.dataframe(df)

        st.success("Planilha carregada!")
