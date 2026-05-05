from __future__ import annotations

from dataclasses import dataclass
from datetime import date

INSS_FAIXAS_2026 = [
    (1518.00, 0.075),
    (2793.88, 0.09),
    (4190.84, 0.12),
    (8157.41, 0.14),
]


@dataclass
class BasesCalculo:
    bruto: float
    base_inss: float
    base_irrf: float


def calcular_inss_progressivo_2026(salario_base: float) -> float:
    salario = max(0.0, float(salario_base))
    total = 0.0
    faixa_inferior = 0.0
    for teto, aliquota in INSS_FAIXAS_2026:
        if salario <= faixa_inferior:
            break
        faixa_atual = min(salario, teto) - faixa_inferior
        total += faixa_atual * aliquota
        faixa_inferior = teto
    return round(total, 2)


def calcular_irrf_2026(base_irrf: float) -> float:
    base = max(0.0, float(base_irrf))
    if base <= 5000:
        return 0.0
    return round(max(base * 0.275 - 896.0, 0.0), 2)


def calcular_fgts(bruto: float) -> float:
    return round(max(0.0, float(bruto)) * 0.08, 2)


def calcular_hora_valor(salario: float, carga_horaria_dia_semana: float) -> float:
    horas_mes = max((carga_horaria_dia_semana or 8) * 22, 1)
    return float(salario) / horas_mes


def calcular_eventos_ponto(salario: float, carga_horaria_dia_semana: float, horas_extras: float, faltas_horas: float, dsr_desconto_horas: float) -> dict:
    valor_hora = calcular_hora_valor(salario, carga_horaria_dia_semana)
    extra = valor_hora * max(horas_extras, 0) * 1.5
    desconto_falta = valor_hora * max(faltas_horas, 0)
    desconto_dsr = valor_hora * max(dsr_desconto_horas, 0)
    return {
        "valor_hora": round(valor_hora, 2),
        "valor_horas_extras": round(extra, 2),
        "desconto_falta": round(desconto_falta, 2),
        "desconto_dsr": round(desconto_dsr, 2),
    }


def calcular_ferias_proporcionais(data_admissao: date, salario: float, referencia: date) -> float:
    meses = max((referencia.year - data_admissao.year) * 12 + (referencia.month - data_admissao.month), 0)
    proporcionais = min(meses, 12) / 12
    return round((salario * proporcionais) + ((salario * proporcionais) / 3), 2)


def calcular_decimo_terceiro_proporcional(data_admissao: date, salario: float, referencia: date) -> float:
    meses = max((referencia.year - data_admissao.year) * 12 + referencia.month - data_admissao.month, 0)
    return round(salario * min(meses, 12) / 12, 2)


def calcular_folha_completa(salario_base: float, comissao: float, bonus: float, descontos_beneficios: float, eventos_ponto: dict) -> dict:
    bruto = salario_base + comissao + bonus + eventos_ponto["valor_horas_extras"]
    bruto -= eventos_ponto["desconto_falta"] + eventos_ponto["desconto_dsr"]
    base_inss = max(bruto, 0)
    inss = calcular_inss_progressivo_2026(base_inss)
    base_irrf = max(bruto - inss, 0)
    irrf = calcular_irrf_2026(base_irrf)
    fgts = calcular_fgts(bruto)
    liquido = bruto - inss - irrf - descontos_beneficios
    bases = BasesCalculo(bruto=round(bruto, 2), base_inss=round(base_inss, 2), base_irrf=round(base_irrf, 2))
    return {
        "bases": bases,
        "inss": inss,
        "irrf": irrf,
        "fgts": fgts,
        "liquido": round(liquido, 2),
    }
