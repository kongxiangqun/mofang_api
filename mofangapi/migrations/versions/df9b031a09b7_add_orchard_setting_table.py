"""add orchard setting table

Revision ID: df9b031a09b7
Revises: 6d36f153a1f4
Create Date: 2021-01-04 16:42:57.141681

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'df9b031a09b7'
down_revision = '6d36f153a1f4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('mf_orchard_setting',
    sa.Column('id', sa.Integer(), nullable=False, comment='主键ID'),
    sa.Column('name', sa.String(length=255), nullable=True, comment='名称/标题'),
    sa.Column('is_deleted', sa.Boolean(), nullable=True, comment='逻辑删除'),
    sa.Column('orders', sa.Integer(), nullable=True, comment='排序'),
    sa.Column('status', sa.Boolean(), nullable=True, comment='状态(是否显示,是否激活)'),
    sa.Column('created_time', sa.DateTime(), nullable=True, comment='创建时间'),
    sa.Column('updated_time', sa.DateTime(), nullable=True, comment='更新时间'),
    sa.Column('title', sa.String(length=255), nullable=True, comment='提示文本'),
    sa.Column('value', sa.String(length=255), nullable=True, comment='数值'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('mf_orchard_setting')
    # ### end Alembic commands ###
