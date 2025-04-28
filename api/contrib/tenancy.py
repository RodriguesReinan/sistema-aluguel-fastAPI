from sqlalchemy import Select, Update, Delete
from sqlalchemy.orm import AliasedClass


def filter_by_tenant(statement, tenant_id: str):
    if not isinstance(statement, (Select, Update, Delete)):
        raise ValueError("Statement deve ser SELECT, UPDATE ou DELETE")

    # Captura as entidades principais (models envolvidos no SELECT)
    entities = statement._raw_columns if hasattr(statement, "_raw_columns") else []

    if not entities:
        return statement

    # Se for SELECT(ContratoModel, InquilinoModel, ImovelModel, UsuarioModel)
    # entities = [ContratoModel, InquilinoModel, ImovelModel, UsuarioModel]

    # Vamos encontrar o primeiro model que realmente tenha tenant_id
    for entity in entities:
        if hasattr(entity, "c"):  # Para tabelas
            if "tenant_id" in entity.c:
                return statement.filter(entity.c.tenant_id == tenant_id)
        elif hasattr(entity, "tenant_id"):  # Para models
            return statement.filter(entity.tenant_id == tenant_id)
        elif isinstance(entity, AliasedClass) and hasattr(entity, "tenant_id"):  # Caso use alias
            return statement.filter(entity.tenant_id == tenant_id)

    # Se nenhuma entidade tiver tenant_id, retorna o statement original
    return statement





# from sqlalchemy import Select, Update, Delete
#
#
# def filter_by_tenant(statement, tenant_id: str):
#     if not isinstance(statement, (Select, Update, Delete)):
#         raise ValueError("Statement deve ser SELECT, UPDATE ou DELETE")
#
#     # Pega as entidades envolvidas no statement
#     entities = statement.get_final_froms()
#
#     # se tiver alguma entidade, tentamos aplicar o filtro
#     if entities:
#         first_entity = entities[0]
#
#         # Aqui verificamos se existe a coluna tenant_id
#         if 'tenant_id' in first_entity.c:
#             return statement.filter(first_entity.c.tenant_id == tenant_id)
#
#     # Se não tiver tenant_id ou não for aplicável, retorna o statement original
#     return statement
