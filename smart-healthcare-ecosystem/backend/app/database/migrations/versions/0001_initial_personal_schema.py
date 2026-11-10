"""Initial schema for personal health users and profiles."""

from alembic import op
import sqlalchemy as sa

revision = "0001_initial_personal_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("first_name", sa.String(length=80), nullable=False),
        sa.Column("middle_name", sa.String(length=80), nullable=True),
        sa.Column("last_name", sa.String(length=80), nullable=False),
        sa.Column("date_of_birth", sa.Date(), nullable=True),
        sa.Column("gender", sa.String(length=32), nullable=False, server_default="prefer_not_to_say"),
        sa.Column("phone", sa.String(length=32), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("city", sa.String(length=128), nullable=True),
        sa.Column("state", sa.String(length=128), nullable=True),
        sa.Column("country", sa.String(length=128), nullable=True),
        sa.Column("postal_code", sa.String(length=32), nullable=True),
        sa.Column("blood_group", sa.String(length=16), nullable=True),
        sa.Column("important_notes", sa.Text(), nullable=True),
        sa.Column("preferred_hospital", sa.Text(), nullable=True),
        sa.Column("emergency_directives", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.create_table(
        "personal_profiles",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("user_id", sa.String(length=64), nullable=False, unique=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=32), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("city", sa.String(length=128), nullable=True),
        sa.Column("state", sa.String(length=128), nullable=True),
        sa.Column("country", sa.String(length=128), nullable=True),
        sa.Column("postal_code", sa.String(length=32), nullable=True),
        sa.Column("blood_group", sa.String(length=16), nullable=True),
        sa.Column("allergies", sa.Text(), nullable=True, server_default="[]"),
        sa.Column("conditions", sa.Text(), nullable=True, server_default="[]"),
        sa.Column("important_notes", sa.Text(), nullable=True),
        sa.Column("preferred_hospital", sa.Text(), nullable=True),
        sa.Column("emergency_directives", sa.Text(), nullable=True),
        sa.Column("emergency_contacts", sa.Text(), nullable=True, server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
    )
    op.create_index(op.f("ix_personal_profiles_user_id"), "personal_profiles", ["user_id"], unique=True)

    op.create_table(
        "audit_events",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("user_id", sa.String(length=64), nullable=True),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(op.f("ix_audit_events_user_id"), "audit_events", ["user_id"])
    op.create_index(op.f("ix_audit_events_event_type"), "audit_events", ["event_type"])


def downgrade() -> None:
    op.drop_index(op.f("ix_audit_events_event_type"), table_name="audit_events")
    op.drop_index(op.f("ix_audit_events_user_id"), table_name="audit_events")
    op.drop_table("audit_events")
    op.drop_index(op.f("ix_personal_profiles_user_id"), table_name="personal_profiles")
    op.drop_table("personal_profiles")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
