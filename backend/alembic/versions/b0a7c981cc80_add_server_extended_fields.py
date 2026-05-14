"""add_server_extended_fields

Revision ID: b0a7c981cc80
Revises: 8c4d3e9027bf
Create Date: 2026-05-14 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'b0a7c981cc80'
down_revision: Union[str, None] = '8c4d3e9027bf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('servers', sa.Column('odoo_port', sa.Integer(), nullable=False, server_default='8069'))
    op.add_column('servers', sa.Column('db_port', sa.Integer(), nullable=False, server_default='5432'))
    op.add_column('servers', sa.Column('db_user', sa.String(100), nullable=False, server_default='postgres'))
    op.add_column('servers', sa.Column('db_password_encrypted', sa.String(1000), nullable=True))


def downgrade() -> None:
    op.drop_column('servers', 'db_password_encrypted')
    op.drop_column('servers', 'db_user')
    op.drop_column('servers', 'db_port')
    op.drop_column('servers', 'odoo_port')
