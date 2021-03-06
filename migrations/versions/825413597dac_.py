"""empty message

Revision ID: 825413597dac
Revises: ca7e0ae6fe12
Create Date: 2020-12-23 14:22:53.553884

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '825413597dac'
down_revision = 'ca7e0ae6fe12'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('show',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('artist_id', sa.Integer(), nullable=True),
    sa.Column('venue_id', sa.Integer(), nullable=True),
    sa.Column('start_time',sa.String(),nullable=True),
    sa.ForeignKeyConstraint(['artist_id'], ['artist.id'], ),
    sa.ForeignKeyConstraint(['venue_id'], ['venue.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('show')
    # ### end Alembic commands ###
