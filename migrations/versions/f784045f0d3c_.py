"""empty message

Revision ID: f784045f0d3c
Revises: 
Create Date: 2018-03-26 20:41:57.667220

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f784045f0d3c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('bom_files',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('comment', sa.String(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('bom_session',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('material',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('size', sa.String(length=64), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('size')
    )
    op.create_table('material_length',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('length', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('length')
    )
    op.create_table('bom_file_contents',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('item_no', sa.String(length=64), nullable=True),
    sa.Column('part_number', sa.String(length=64), nullable=True),
    sa.Column('description', sa.String(length=64), nullable=True),
    sa.Column('BB_length', sa.Float(), nullable=True),
    sa.Column('BB_width', sa.Float(), nullable=True),
    sa.Column('BB_thickness', sa.Float(), nullable=True),
    sa.Column('length', sa.Float(), nullable=True),
    sa.Column('qty', sa.Integer(), nullable=True),
    sa.Column('parent', sa.Integer(), nullable=True),
    sa.Column('file_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['file_id'], ['bom_files.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('bom_result',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('comment', sa.String(), nullable=True),
    sa.Column('file_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['file_id'], ['bom_files.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('bom_session_size',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('size', sa.String(length=64), nullable=True),
    sa.Column('default', sa.Integer(), nullable=True),
    sa.Column('session_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['session_id'], ['bom_session.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('material_size_lengths',
    sa.Column('size_id', sa.Integer(), nullable=False),
    sa.Column('length_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['length_id'], ['material_length.id'], ),
    sa.ForeignKeyConstraint(['size_id'], ['material.id'], ),
    sa.PrimaryKeyConstraint('size_id', 'length_id')
    )
    op.create_table('bom_result_material',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('size', sa.String(length=64), nullable=True),
    sa.Column('result_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['result_id'], ['bom_result.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('bom_session_length',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('length', sa.Integer(), nullable=True),
    sa.Column('size_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['size_id'], ['bom_session_size.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('bom_result_beam',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('length', sa.Integer(), nullable=True),
    sa.Column('waste', sa.Integer(), nullable=True),
    sa.Column('material_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['material_id'], ['bom_result_material.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('bom_result_missing_part',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('item_no', sa.String(length=64), nullable=True),
    sa.Column('length', sa.Float(), nullable=True),
    sa.Column('qty', sa.Integer(), nullable=True),
    sa.Column('material_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['material_id'], ['bom_result_material.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('bom_result_beam_part',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('item_no', sa.String(length=64), nullable=True),
    sa.Column('length', sa.Float(), nullable=True),
    sa.Column('qty', sa.Integer(), nullable=True),
    sa.Column('beam_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['beam_id'], ['bom_result_beam.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('bom_result_beam_part')
    op.drop_table('bom_result_missing_part')
    op.drop_table('bom_result_beam')
    op.drop_table('bom_session_length')
    op.drop_table('bom_result_material')
    op.drop_table('material_size_lengths')
    op.drop_table('bom_session_size')
    op.drop_table('bom_result')
    op.drop_table('bom_file_contents')
    op.drop_table('material_length')
    op.drop_table('material')
    op.drop_table('bom_session')
    op.drop_table('bom_files')
    # ### end Alembic commands ###
