"""initial

Revision ID: c62583709171
Revises:
Create Date: 2026-08-01 13:22:05.716962

"""
from typing import Sequence, Union

import sqlmodel
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c62583709171'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_type
                WHERE typname = 'shipmentstatus'
            ) THEN
                CREATE TYPE shipmentstatus AS ENUM (
                    'placed',
                    'in_transit',
                    'out_for_delivery',
                    'delivered'
                );
            END IF;
        END
        $$;
    """)

    op.create_table(
        'seller',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'shipment',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('delivery_partner_id', sa.UUID(), nullable=False),
        sa.Column(
            'status',
            postgresql.ENUM(
                'placed',
                'in_transit',
                'out_for_delivery',
                'delivered',
                name='shipmentstatus',
                create_type=False,
            ),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'shipment_event',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(), nullable=True),
        sa.Column('location', sa.Integer(), nullable=False),
        sa.Column(
            'status',
            postgresql.ENUM(
                'placed',
                'in_transit',
                'out_for_delivery',
                'delivered',
                name='shipmentstatus',
                create_type=False,
            ),
            nullable=True,
        ),
        sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('shipment_id', sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(['shipment_id'], ['shipment.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    op.add_column('seller', sa.Column('created_at', postgresql.TIMESTAMP(), nullable=True))
    op.add_column('seller', sa.Column('address', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.add_column('seller', sa.Column('zip_code', sa.Integer(), nullable=True))

    op.alter_column(
        'shipment',
        'delivery_partner_id',
        existing_type=sa.UUID(),
        nullable=False,
    )
    op.drop_column('shipment', 'status')


def downgrade() -> None:
    op.add_column(
        'shipment',
        sa.Column(
            'status',
            postgresql.ENUM(
                'placed',
                'in_transit',
                'out_for_delivery',
                'delivered',
                name='shipmentstatus',
            ),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.alter_column(
        'shipment',
        'delivery_partner_id',
        existing_type=sa.UUID(),
        nullable=True,
    )
    op.drop_column('seller', 'zip_code')
    op.drop_column('seller', 'address')
    op.drop_column('seller', 'created_at')
    op.drop_table('shipment_event')
    op.drop_table('shipment')
    op.drop_table('seller')