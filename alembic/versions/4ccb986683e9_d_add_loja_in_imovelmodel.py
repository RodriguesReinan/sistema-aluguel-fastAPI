"""d=add loja in imovelModel

Revision ID: 4ccb986683e9
Revises: 8a4a667a5928
Create Date: 2025-05-06 23:22:19.336939

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import ENUM


# revision identifiers, used by Alembic.
revision: str = '4ccb986683e9'
down_revision: Union[str, None] = '8a4a667a5928'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        'imoveis',
        'casa_apartamento',
        existing_type=ENUM('casa', 'apartamento', 'loja', name="casa_ou_apartamento"),
        nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        'imoveis',
        'casa_apartamento',
        existing_type=ENUM('casa', 'apartamento', name="casa_ou_apartamento"),
        nullable=False,
    )
