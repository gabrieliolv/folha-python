import streamlit as st

st.title("💰 Folha de Pagamento")

funcionarios = {
    "Gabrieli": 3300,
    "Alisson": 4500,
    "Andressa": 3000
}

nome = st.selectbox("Funcionário", list(funcionarios.keys()))
salario = funcionarios[nome]

comissao = st.number_input("Comissão", 0.0)
bonus = st.number_input("Bônus", 0.0)

bruto = salario + comissao + bonus

# INSS simples (vamos melhorar depois)
inss = bruto * 0.08

# IRRF (isento até 5000)
irrf = 0 if bruto <= 5000 else bruto * 0.27

liquido = bruto - inss - irrf

st.write("Bruto:", bruto)
st.write("INSS:", inss)
st.write("IRRF:", irrf)
st.write("💵 Líquido:", liquido)
