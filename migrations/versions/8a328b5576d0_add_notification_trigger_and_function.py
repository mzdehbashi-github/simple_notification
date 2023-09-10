"""Add notification trigger and function

Revision ID: 8a328b5576d0
Revises: 3261387bf67c
Create Date: 2023-09-02 19:25:59.051935

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '8a328b5576d0'
down_revision: Union[str, None] = '3261387bf67c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Create the NOTIFY function
    notify_function = """
    CREATE OR REPLACE FUNCTION notify_new_notification()
    RETURNS TRIGGER AS $$
    BEGIN
        PERFORM pg_notify('new_notification_channel', 'New notification: ' || NEW.text);
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """
    op.execute(notify_function)

    # Create the trigger to call the NOTIFY function when a new notification is inserted
    trigger = """
    CREATE TRIGGER new_notification_trigger
    AFTER INSERT ON notification
    FOR EACH ROW
    EXECUTE FUNCTION notify_new_notification();
    """
    op.execute(trigger)

def downgrade():
    # Drop the trigger
    op.execute("DROP TRIGGER IF EXISTS new_notification_trigger ON notification")

    # Drop the NOTIFY function
    op.execute("DROP FUNCTION IF EXISTS notify_new_notification()")
