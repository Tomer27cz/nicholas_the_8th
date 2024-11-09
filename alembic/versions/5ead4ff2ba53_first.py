"""first

Revision ID: 5ead4ff2ba53
Revises: 
Create Date: 2024-11-09 02:32:07.374628

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5ead4ff2ba53'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('discord_commands',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('category', sa.String(), nullable=True),
    sa.Column('attributes', sa.JSON(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('guilds',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('connected', sa.Boolean(), nullable=True),
    sa.Column('last_updated', sa.JSON(), nullable=True),
    sa.Column('keep_alive', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('guild_data',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('key', sa.CHAR(length=6), nullable=True),
    sa.Column('member_count', sa.Integer(), nullable=True),
    sa.Column('text_channel_count', sa.Integer(), nullable=True),
    sa.Column('voice_channel_count', sa.Integer(), nullable=True),
    sa.Column('role_count', sa.Integer(), nullable=True),
    sa.Column('owner_id', sa.Integer(), nullable=True),
    sa.Column('owner_name', sa.String(), nullable=True),
    sa.Column('created_at', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('large', sa.Boolean(), nullable=True),
    sa.Column('icon', sa.String(), nullable=True),
    sa.Column('banner', sa.String(), nullable=True),
    sa.Column('splash', sa.String(), nullable=True),
    sa.Column('discovery_splash', sa.String(), nullable=True),
    sa.Column('voice_channels', sa.JSON(), nullable=True),
    sa.ForeignKeyConstraint(['id'], ['guilds.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('now_playing',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('position', sa.Integer(), nullable=True),
    sa.Column('class_type', sa.String(), nullable=True),
    sa.Column('author', sa.JSON(), nullable=True),
    sa.Column('guild_id', sa.Integer(), nullable=True),
    sa.Column('url', sa.String(), nullable=True),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('picture', sa.String(), nullable=True),
    sa.Column('duration', sa.String(), nullable=True),
    sa.Column('channel_name', sa.String(), nullable=True),
    sa.Column('channel_link', sa.String(), nullable=True),
    sa.Column('radio_info', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.Integer(), nullable=True),
    sa.Column('played_duration', sa.JSON(), nullable=True),
    sa.Column('stream_url', sa.String(), nullable=True),
    sa.Column('discord_channel', sa.JSON(), nullable=True),
    sa.ForeignKeyConstraint(['guild_id'], ['guilds.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('options',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('stopped', sa.Boolean(), nullable=True),
    sa.Column('loop', sa.Boolean(), nullable=True),
    sa.Column('is_radio', sa.Boolean(), nullable=True),
    sa.Column('language', sa.String(length=2), nullable=True),
    sa.Column('response_type', sa.String(length=5), nullable=True),
    sa.Column('buttons', sa.Boolean(), nullable=True),
    sa.Column('volume', sa.Float(), nullable=True),
    sa.Column('buffer', sa.Integer(), nullable=True),
    sa.Column('player_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['id'], ['guilds.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('queue',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('position', sa.Integer(), nullable=True),
    sa.Column('class_type', sa.String(), nullable=True),
    sa.Column('author', sa.JSON(), nullable=True),
    sa.Column('guild_id', sa.Integer(), nullable=True),
    sa.Column('url', sa.String(), nullable=True),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('picture', sa.String(), nullable=True),
    sa.Column('duration', sa.String(), nullable=True),
    sa.Column('channel_name', sa.String(), nullable=True),
    sa.Column('channel_link', sa.String(), nullable=True),
    sa.Column('radio_info', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.Integer(), nullable=True),
    sa.Column('played_duration', sa.JSON(), nullable=True),
    sa.Column('stream_url', sa.String(), nullable=True),
    sa.Column('discord_channel', sa.JSON(), nullable=True),
    sa.ForeignKeyConstraint(['guild_id'], ['guilds.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('queue')
    op.drop_table('options')
    op.drop_table('now_playing')
    op.drop_table('guild_data')
    op.drop_table('guilds')
    op.drop_table('discord_commands')
    # ### end Alembic commands ###
