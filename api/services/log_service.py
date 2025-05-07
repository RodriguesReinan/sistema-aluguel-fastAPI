from api.contrib.dependecies import DatabaseDependency
from api.routes.tables_logs.models import LogModel
from api.routes.usuarios.models.usuario_model import UsuarioModel


async def registrar_log(db_session: DatabaseDependency, acao: str, descricao: str,
                        current_user: UsuarioModel) -> None:
    log = LogModel(
        usuario_id=current_user.id,
        acao=acao,
        descricao=descricao,
        tenant_id=current_user.id
    )
    db_session.add(log)
    await db_session.commit()
