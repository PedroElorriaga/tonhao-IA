"""ticket_id_to_uuid

Revision ID: d4f8f0377461
Revises: 099af0f9c60a
Create Date: 2026-05-07 21:39:09.508076

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4f8f0377461'
down_revision: Union[str, Sequence[str], None] = '099af0f9c60a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('tickets') as batch_op:
        batch_op.alter_column('id',
                              existing_type=sa.INTEGER(),
                              type_=sa.String(length=36),
                              existing_nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('tickets') as batch_op:
        batch_op.alter_column('id',
                              existing_type=sa.String(length=36),
                              type_=sa.INTEGER(),
                              existing_nullable=False)
