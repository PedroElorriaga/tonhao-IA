"""add_model_used_to_ticket_replies

Revision ID: b3f7a1c2e905
Revises: 415421bea99c
Create Date: 2026-05-21 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b3f7a1c2e905'
down_revision: Union[str, Sequence[str], None] = '415421bea99c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('ticket_replies', sa.Column(
        'model_used', sa.String(255), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('ticket_replies', 'model_used')
