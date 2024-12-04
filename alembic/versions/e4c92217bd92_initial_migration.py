"""Initial migration

Revision ID: e4c92217bd92
Revises: 
Create Date: 2024-12-04 16:22:57.102927

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e4c92217bd92'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('organizations',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('api_key', sa.String(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('settings', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('api_key')
    )
    op.create_table('knowledge_bases',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('organization_id', sa.UUID(), nullable=True),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('vector_store_ids', sa.JSON(), nullable=True),
    sa.Column('extra_metadata', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('usage_metrics',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('organization_id', sa.UUID(), nullable=True),
    sa.Column('date', sa.DateTime(timezone=True), nullable=False),
    sa.Column('query_count', sa.Integer(), nullable=True),
    sa.Column('token_count', sa.Integer(), nullable=True),
    sa.Column('embedding_count', sa.Integer(), nullable=True),
    sa.Column('extra_metadata', sa.JSON(), nullable=True),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('whatsapp_users',
    sa.Column('phone_number', sa.String(), nullable=False),
    sa.Column('organization_id', sa.UUID(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('settings', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('last_active', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
    sa.PrimaryKeyConstraint('phone_number')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('whatsapp_users')
    op.drop_table('usage_metrics')
    op.drop_table('knowledge_bases')
    op.drop_table('organizations')
    # ### end Alembic commands ###
