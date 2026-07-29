"""init

Revision ID: be7065fa1f74
Revises: 
Create Date: 2026-07-29
"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import sqlmodel
from alembic import op


# revision identifiers
revision: str = 'be7065fa1f74'
down_revision: Union[str, Sequence[str], None] = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ✅ 1. Create ENUM safely (idempotent)
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM pg_type WHERE typname = 'shipmentstatus'
        ) THEN
            CREATE TYPE shipmentstatus AS ENUM (
                'placed',
                'in_transit',
                'out_for_delivery',
                'delivered'
            );
        END IF;
    END$$;
    """)

    # ✅ 2. seller table
    op.create_table(
        'seller',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('email', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('password_hash', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # ✅ 3. shipment table
    op.create_table(
        'shipment',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('content', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('weight', sa.Float(), nullable=False),
        sa.Column('destination', sa.Integer(), nullable=False),

        # ✅ FIXED (Postgres ENUM, no auto create)
        sa.Column(
            'status',
            postgresql.ENUM(
                'placed',
                'in_transit',
                'out_for_delivery',
                'delivered',
                name='shipmentstatus',
                create_type=False
            ),
            nullable=False
        ),  # ✅ ← THIS COMMA WAS MISSING

        sa.Column('estimated_delivery', sa.DateTime(), nullable=False),
        sa.Column('seller_id', sa.UUID(), nullable=False),

        sa.ForeignKeyConstraint(['seller_id'], ['seller.id']),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    # ✅ 1. Drop tables first
    op.drop_table('shipment')
    op.drop_table('seller')

    # ✅ 2. Drop ENUM safely
    op.execute("""
    DO $$
    BEGIN
        IF EXISTS (
            SELECT 1 FROM pg_type WHERE typname = 'shipmentstatus'
        ) THEN
            DROP TYPE shipmentstatus;
        END IF;
    END$$;
    """)