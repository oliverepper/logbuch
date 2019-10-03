"""memberships

Revision ID: a7fec71c543c
Revises: f9c7049c7818
Create Date: 2019-09-28 18:51:40.023312

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a7fec71c543c'
down_revision = 'f9c7049c7818'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('memberships',
    sa.Column('log_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('type', sa.Enum('WRITE', 'READ', name='membershiptype'), nullable=True),
    sa.ForeignKeyConstraint(['log_id'], ['logs.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('log_id', 'user_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('memberships')
    # ### end Alembic commands ###