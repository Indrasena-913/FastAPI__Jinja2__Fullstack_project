"""added phonenumber

Revision ID: 375c545b80b4
Revises: <previous_revision_id>
Create Date: 2025-05-17 12:00:00.000000

"""
from tokenize import String

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '375c545b80b4'
down_revision = '<previous_revision_id>'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column("users", sa.Column("phonenumber", sa.String(), nullable=True))

def downgrade():
    op.drop_column("users", "phonenumber")
