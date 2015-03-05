"""create project table

Revision ID: 1162611363e2
Revises:
Create Date: 2015-02-27 14:04:12.569384

"""

# revision identifiers, used by Alembic.
revision = '1162611363e2'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'project',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(50), nullable=False, unique=True),
    )


def downgrade():
    op.drop_table('project')
