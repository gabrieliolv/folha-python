from datetime import date

import pandas as pd
import streamlit as st
from supabase import create_client

from calculos import (
    calcular_decimo_terceiro_proporcional,
    calcular_eventos_ponto,
    calcular_ferias_proporcionais,
    calcular_folha_completa,
)
from validacoes import mascara_documento, validar_cnpj_cpf

SUPABASE_URL = "https://llaikgnepnvppqdaujbg.supabase.co"
SUPABASE_KEY = "sb_publishable_Zp_d7qXsU9Ir7y2TOOyJsQ_3tnCYhKd"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

for k, v in {"logado": False, "usuario": None, "perfil": "USER", "loja_id": None, "auditoria_habilitada": None}.items():
    st.session_state.setdefault(k, v)


def tabela_existe(nome_tabela: str) -> bool:
    try:
        supabase.table(nome_tabela).select("id").limit(1).execute()
        return True
    except Exception:
        return False


def log_acao(acao: str, tabela: str, registro_id=None, payload=None) -> None:
    if st.session_state["auditoria_habilitada"] is None:
        st.session_state["auditoria_habilitada"] = tabela_existe("auditoria_logs")
    if not st.session_state["auditoria_habilitada"]:
        return
    try:
        supabase.table("auditoria_logs").insert(
            {
                "usuario": st.session_state.get("usuario") or "sistema",
                "acao": acao,
                "tabela": tabela,
                "registro_id": str(registro_id) if registro_id is not None else None,
                "payload": payload or {},
            }
        ).execute()
    except Exception:
        st.session_state["auditoria_habilitada"] = False


def get_table(nome: str) -> pd.DataFrame:
    res = supabase.table(nome).select("*").execute()
    return pd.DataFrame(res.data)


def tem_acesso(loja_id: int | None) -> bool:
    perfil = (st.session_state.get("perfil") or "").upper()
    if perfil == "ADMIN":
        return True
    return st.session_state.get("loja_id") == loja_id


def login():
    st.title("🔐 Login")
    user = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        res = supabase.table("usuarios").select("*").eq("usuario", user).execute()
        if res.data and res.data[0]["senha"] == senha:
            usr = res.data[0]
            st.session_state.update(
                {
                    "logado": True,
                    "usuario": usr["usuario"],
                    "perfil": (usr.get("perfil") or "USER").upper(),
                    "loja_id": usr.get("loja_id"),
                }
            )
            st.rerun()
        st.error("Login inválido")


if not st.session_state["logado"]:
    login()
    st.stop()

menu = ["📊 Folha", "🏷️ Cargos", "🏪 Lojas", "👤 Funcionários", "📄 Ponto", "📑 Documentos", "📧 Envio", "🔐 Usuários"]
pagina = st.sidebar.radio("MENU", menu)

if pagina == "🏷️ Cargos":
    st.title("Cadastro de Cargos")
    nome_cargo = st.text_input("Nome do cargo")
    salario_base = st.number_input("Salário base", min_value=0.0)
    if st.button("Salvar Cargo"):
        supabase.table("cargos").insert({"nome_cargo": nome_cargo, "salario_base": salario_base or None}).execute()
        log_acao("INSERT", "cargos", payload={"nome_cargo": nome_cargo})
        st.success("Cargo salvo")
        st.rerun()
    st.dataframe(get_table("cargos"))

if pagina == "🏪 Lojas":
    st.title("Cadastro de Lojas")

    st.subheader("Nova loja")
    nome_loja = st.text_input("Nome da Loja")
    apelido = st.text_input("Apelido")
    empresa = st.text_input("Empresa")
    cnpj = st.text_input("CNPJ/CPF")
    endereco = st.text_input("Endereço")
    contato = st.text_input("Contato")
    if st.button("Salvar Loja"):
        if not validar_cnpj_cpf(cnpj):
            st.error("Documento inválido")
        else:
            res = supabase.table("lojas").insert({"nome_loja": nome_loja, "apelido": apelido, "empresa": empresa, "cnpj": cnpj, "endereco": endereco, "contato": contato}).execute()
            log_acao("INSERT", "lojas", registro_id=res.data[0].get("id") if res.data else None, payload={"nome_loja": nome_loja})
            st.success("Loja salva")
            st.rerun()

    df_lojas = get_table("lojas")
    if not df_lojas.empty:
        st.markdown("---")
        st.subheader("Editar / Excluir lojas")
        df_lojas["cnpj_formatado"] = df_lojas["cnpj"].apply(mascara_documento)
        loja_id_edit = st.selectbox("Selecione a loja", df_lojas["id"].tolist(), format_func=lambda x: f"{x} - {df_lojas[df_lojas['id']==x]['nome_loja'].iloc[0]}")
        loja_row = df_lojas[df_lojas["id"] == loja_id_edit].iloc[0]

        ed_nome = st.text_input("Nome da Loja (edição)", value=loja_row.get("nome_loja", ""))
        ed_apelido = st.text_input("Apelido (edição)", value=loja_row.get("apelido", ""))
        ed_empresa = st.text_input("Empresa (edição)", value=loja_row.get("empresa", ""))
        ed_cnpj = st.text_input("CNPJ/CPF (edição)", value=loja_row.get("cnpj", ""))
        ed_endereco = st.text_input("Endereço (edição)", value=loja_row.get("endereco", ""))
        ed_contato = st.text_input("Contato (edição)", value=loja_row.get("contato", ""))

        c1, c2 = st.columns(2)
        if c1.button("Atualizar Loja"):
            if not validar_cnpj_cpf(ed_cnpj):
                st.error("Documento inválido para atualização")
            else:
                supabase.table("lojas").update({"nome_loja": ed_nome, "apelido": ed_apelido, "empresa": ed_empresa, "cnpj": ed_cnpj, "endereco": ed_endereco, "contato": ed_contato}).eq("id", int(loja_id_edit)).execute()
                log_acao("UPDATE", "lojas", registro_id=int(loja_id_edit), payload={"nome_loja": ed_nome})
                st.success("Loja atualizada")
                st.rerun()

        if c2.button("Excluir Loja"):
            supabase.table("lojas").delete().eq("id", int(loja_id_edit)).execute()
            log_acao("DELETE", "lojas", registro_id=int(loja_id_edit))
            st.success("Loja excluída")
            st.rerun()

        st.dataframe(df_lojas.drop(columns=["cnpj_formatado"]))

if pagina == "👤 Funcionários":
    st.title("Cadastro de Funcionários")
    lojas = get_table("lojas")
    cargos = get_table("cargos")
    if lojas.empty or cargos.empty:
        st.warning("Cadastre loja e cargo primeiro")
        st.stop()
    lojas_visiveis = lojas if (st.session_state.get("perfil") == "ADMIN") else lojas[lojas["id"] == st.session_state.get("loja_id")]
    if lojas_visiveis.empty:
        st.error("Sem acesso a lojas")
        st.stop()
    loja_nome = st.selectbox("Loja", lojas_visiveis["nome_loja"])
    loja_id = int(lojas_visiveis[lojas_visiveis["nome_loja"] == loja_nome]["id"].iloc[0])
    if not tem_acesso(loja_id):
        st.error("Sem acesso a esta loja")
        st.stop()
    nome = st.text_input("Nome")
    cargo_nome = st.selectbox("Cargo", cargos["nome_cargo"])
    cargo_id = int(cargos[cargos["nome_cargo"] == cargo_nome]["id"].iloc[0])
    salario = st.number_input("Salário", min_value=0.0)
    carga = st.number_input("Carga horária dia", min_value=1.0, value=8.0)
    d_vt = st.checkbox("Desconto VT")
    p_vt = st.number_input("% VT", min_value=0.0, max_value=100.0)
    d_va = st.checkbox("Desconto VA/VR")
    p_va = st.number_input("% VA/VR", min_value=0.0, max_value=100.0)
    outros = st.number_input("Outros descontos", min_value=0.0)
    data_adm = st.date_input("Data admissão", value=date.today())
    contato = st.text_input("Contato")
    email = st.text_input("Email")
    tipo_pag = st.selectbox("Tipo pagamento", ["PIX", "BANCO"])
    chave_pix = st.text_input("Chave PIX") if tipo_pag == "PIX" else ""
    banco = st.text_area("Dados bancários (json)", value="{}") if tipo_pag == "BANCO" else "{}"
    if st.button("Salvar Funcionário"):
        supabase.table("funcionarios").insert({"loja_id": loja_id, "nome": nome, "cargo_id": cargo_id, "salario": salario, "carga_horaria_dia_semana": carga, "desconto_vt": d_vt, "desconto_va_vr": d_va, "percentual_vt": p_vt, "percentual_va_vr": p_va, "outros_descontos": outros, "data_admissao": str(data_adm), "contato": contato, "email": email or None, "tipo_pagamento": tipo_pag, "chave_pix": chave_pix or None, "dados_bancarios": banco}).execute()
        log_acao("INSERT", "funcionarios", payload={"nome": nome})
        st.success("Funcionário salvo")
        st.rerun()

# mantém páginas existentes
if pagina == "📄 Ponto":
    st.title("Folha de Ponto")
    arquivo = st.file_uploader("Enviar Excel", type=["xlsx"])
    if arquivo:
        df = pd.read_excel(arquivo)
        st.dataframe(df)
        if st.button("Processar e salvar ponto"):
            for _, r in df.iterrows():
                supabase.table("folha_ponto").insert({"funcionario_id": int(r["funcionario_id"]), "mes_referencia": str(pd.to_datetime(r["mes_referencia"]).date()), "horas_trabalhadas": float(r.get("horas_trabalhadas", 0)), "faltas_horas": float(r.get("faltas", 0)), "atestados_horas": float(r.get("atestados", 0)), "banco_horas": float(r.get("banco_horas", 0)), "horas_extras": float(r.get("horas_extras", 0)), "desconto_dsr_horas": float(r.get("desconto_dsr_horas", 0))}).execute()
            log_acao("IMPORT", "folha_ponto")
            st.success("Ponto importado")

if pagina == "📊 Folha":
    st.title("Cálculo de Folha")
    funcs = get_table("funcionarios")
    ponto = get_table("folha_ponto")
    if funcs.empty:
        st.stop()
    f = st.selectbox("Funcionário", funcs["nome"])
    row = funcs[funcs["nome"] == f].iloc[0]
    comissao = st.number_input("Comissão", min_value=0.0)
    bonus = st.number_input("Bônus", min_value=0.0)
    p = ponto[ponto["funcionario_id"] == row["id"]]
    ev = {"valor_horas_extras": 0, "desconto_falta": 0, "desconto_dsr": 0}
    if not p.empty:
        u = p.iloc[-1]
        ev = calcular_eventos_ponto(row["salario"], row.get("carga_horaria_dia_semana", 8), float(u.get("horas_extras", 0)), float(u.get("faltas_horas", 0)), float(u.get("desconto_dsr_horas", 0)))
    descontos = (row["salario"] * row.get("percentual_vt", 0) / 100 if row.get("desconto_vt") else 0) + (row["salario"] * row.get("percentual_va_vr", 0) / 100 if row.get("desconto_va_vr") else 0) + float(row.get("outros_descontos", 0))
    resultado = calcular_folha_completa(float(row["salario"]), comissao, bonus, descontos, ev)
    st.json({**ev, **resultado, "bases": resultado["bases"].__dict__})
    admissao = pd.to_datetime(row["data_admissao"]).date() if row.get("data_admissao") else date.today()
    st.write("Férias proporcionais:", calcular_ferias_proporcionais(admissao, row["salario"], date.today()))
    st.write("13º proporcional:", calcular_decimo_terceiro_proporcional(admissao, row["salario"], date.today()))

if pagina == "📑 Documentos":
    st.title("Documentos")
    st.info("Gerar holerite e folha de ponto em CSV para envio")

if pagina == "📧 Envio":
    st.title("Envio por Email")
    st.warning("Envio preparado: integrar SMTP/serviço transacional mantendo anexos de holerite e ponto.")

if pagina == "🔐 Usuários":
    st.title("Usuários")
    if st.session_state["perfil"] != "ADMIN":
        st.error("Somente ADMIN cria usuários")
        st.stop()
