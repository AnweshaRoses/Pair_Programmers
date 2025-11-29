
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid


revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'rooms',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('room_id', sa.String(32), nullable=False),
        sa.Column('code', sa.Text(), server_default=''),
        sa.Column('language', sa.String(20), server_default='python'),
        sa.UniqueConstraint('room_id', name='uq_rooms_room_id')
    )


def downgrade():
    op.drop_table('rooms')

