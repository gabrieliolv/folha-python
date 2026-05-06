import re

RE_DOC = re.compile(r"^\d{11}$|^\d{14}$")


def limpar_digitos(valor: str) -> str:
    return re.sub(r"\D", "", valor or "")


def validar_cnpj_cpf(valor: str) -> bool:
    return bool(RE_DOC.match(limpar_digitos(valor)))


def mascara_documento(valor: str) -> str:
    dig = limpar_digitos(valor)
    if len(dig) == 11:
        return f"{dig[:3]}.{dig[3:6]}.{dig[6:9]}-{dig[9:]}"
    if len(dig) == 14:
        return f"{dig[:2]}.{dig[2:5]}.{dig[5:8]}/{dig[8:12]}-{dig[12:]}"
    return valor
