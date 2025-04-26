
def formatar_valor_br(valor) -> str:
    """
    Converte um valor numérico ou string para o formato brasileiro com duas casas decimais.
    Exemplos:
    - '1.500,00' ➝ '1.500,00'
    - '750' ➝ '750,00'
    - 1234.56 ➝ '1.234,56'
    - '1234.56' ➝ '1.234,56'
    """
    if isinstance(valor, str):
        if "," in valor and "." in valor:
            # Ex: '1.234,56' (BR) ➝ remove ponto milhar, troca vírgula decimal
            valor = valor.replace(".", "").replace(",", ".")
        elif "," in valor:
            # Ex: '1234,56' ➝ só trocar vírgula por ponto
            valor = valor.replace(",", ".")
        # se for '1234.56', não faz nada
        valor = float(valor)

    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
