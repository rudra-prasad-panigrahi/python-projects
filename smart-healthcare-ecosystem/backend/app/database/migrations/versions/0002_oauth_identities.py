"""Store verified external sign-in identities."""

from alembic import op
import sqlalchemy as sa

revision = "0002_oauth_identities"
down_revision = "0001_initial_personal_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "oauth_identities",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("provider", sa.String(length=32), nullable=False),
        sa.Column("subject", sa.String(length=255), nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.UniqueConstraint("provider", "subject", name="uq_oauth_provider_subject"),
        sa.UniqueConstraint("user_id", "provider", name="uq_oauth_user_provider"),
    )
    op.create_index(op.f("ix_oauth_identities_user_id"), "oauth_identities", ["user_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_oauth_identities_user_id"), table_name="oauth_identities")
    op.drop_table("oauth_identities")
