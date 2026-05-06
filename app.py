import pandas as pd
import streamlit as st
from supabase import create_client
from datetime import date

SUPABASE_URL = "https://llaikgnepnvppqdaujbg.supabase.co"
SUPABASE_KEY = "sb_publishable_Zp_d7qXsU9Ir7y2TOOyJsQ_3tnCYhKd"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ================= SESSION =================

for k, v in {
    "logado": False,
    "usuario": None,
    "perfil": None,
    "loja_id": None
}.items():
    st.session_state.setdefault(k, v)

# ================= UTILS =================

def tabela_existe(nome):
    try:
        supabase.table(nome).select("*").limit(1).execute()
        return True
    except:
        return False

def log_acao(acao, tabela, registro_id=None, payload=None):
    try:
        if not tabela_existe("auditoria_logs"):
            return

        supabase.table("auditoria_logs").insert({
            "usuario": st.session_state.get("usuario"),
            "acao": acao,
            "tabela": tabela,
            "registro_id": str(registro_id) if registro_id else None,
            "payload": payload or {}
        }).execute()
    except:
        pass

def get_table(nome):
    res = supabase.table(nome).select("*").execute()
    return pd.DataFrame(res.data)

def pode_ver_loja(loja_id):
    if st.session_state.get("perfil") == "ADMIN":
        return True
    return st.session_state.get("loja_id") == loja_id

# ================= LOGIN =================

def login():
    st.title("🔐 Login")

    user = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        res = supabase.table("usuarios").select("*").eq("usuario", user).execute()

        if res.data and res.data[0]["senha"] == senha:
            usr = res.data[0]

            st.session_state.update({
                "logado": True,
                "usuario": usr["usuario"],
                "perfil": usr.get("tipo", "USER"),
                "loja_id": usr.get("loja_id")
            })

            st.rerun()
        else:
            st.error("Login inválido")

if not st.session_state["logado"]:
    login()
    st.stop()

# ================= MENU =================

menu = ["🏷️ Cargos", "🏪 Lojas", "👤 Funcionários"]
pagina = st.sidebar.radio("MENU", menu)

# ================= CARGOS =================

if pagina == "🏷️ Cargos":

    st.title("Cadastro de Cargos")

    nome = st.text_input("Nome do cargo")
    salario = st.number_input("Salário base")

    if st.button("Salvar Cargo"):
        supabase.table("cargos").insert({
            "nome_cargo": nome,
            "salario_base": salario
        }).execute()

        log_acao("INSERT", "cargos", payload={"nome": nome})

        st.success("Salvo!")
        st.rerun()

    st.dataframe(get_table("cargos"))

# ================= LOJAS =================

if pagina == "🏪 Lojas":

    st.title("Cadastro de Lojas")

    nome = st.text_input("Nome")
    empresa = st.text_input("Empresa")
    cnpj = st.text_input("CNPJ")

    if st.button("Salvar Loja"):
        supabase.table("lojas").insert({
            "nome_loja": nome,
            "empresa": empresa,
            "cnpj": cnpj
        }).execute()

        log_acao("INSERT", "lojas")

        st.success("Salvo!")
        st.rerun()

    df = get_table("lojas")

    for _, row in df.iterrows():
        col1, col2, col3, col4 = st.columns([2,3,2,1])

        col1.write(row["nome_loja"])
        col2.write(row["empresa"])
        col3.write(row["cnpj"])

        if col4.button("❌", key=f"del_loja_{row['id']}"):
            supabase.table("lojas").delete().eq("id", int(row["id"])).execute()
            log_acao("DELETE", "lojas", row["id"])
            st.rerun()

# ================= FUNCIONARIOS =================

if pagina == "👤 Funcionários":

    st.title("Cadastro de Funcionários")

    lojas = get_table("lojas")
    cargos = get_table("cargos")

    loja_nome = st.selectbox("Loja", lojas["nome_loja"])
    loja_id = int(lojas[lojas["nome_loja"] == loja_nome]["id"].iloc[0])

    if not pode_ver_loja(loja_id):
        st.error("Sem acesso a esta loja")
        st.stop()

    nome = st.text_input("Nome")
    cargo_nome = st.selectbox("Cargo", cargos["nome_cargo"])
    cargo_id = int(cargos[cargos["nome_cargo"] == cargo_nome]["id"].iloc[0])

    salario = st.number_input("Salário")

    if st.button("Salvar Funcionário"):
        supabase.table("funcionarios").insert({
            "nome": nome,
            "cargo_id": cargo_id,
            "loja_id": loja_id,
            "salario": salario
        }).execute()

        log_acao("INSERT", "funcionarios", payload={"nome": nome})

        st.success("Salvo!")
        st.rerun()
