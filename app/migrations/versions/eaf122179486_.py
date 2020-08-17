"""empty message

Revision ID: eaf122179486
Revises: 35c74f2021fd
Create Date: 2020-08-16 23:03:20.200650

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eaf122179486'
down_revision = '35c74f2021fd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('seeking_description', sa.Text(), nullable=True))
    op.add_column('Artist', sa.Column('seeking_venue', sa.Boolean(), nullable=True))
    op.add_column('Artist', sa.Column('website', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Artist', 'website')
    op.drop_column('Artist', 'seeking_venue')
    op.drop_column('Artist', 'seeking_description')
    # ### end Alembic commands ###