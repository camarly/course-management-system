"""
MySQL connection factory.

Provides get_connection() which returns a PyMySQL connection with DictCursor.
All database access in every service must go through this function.
No ORM — raw SQL only.
"""

import logging
import pymysql
import pymysql.cursors
from app.config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

logger = logging.getLogger(__name__)


def get_connection():
    """Open and return a new MySQL connection.

    Returns:
        pymysql.connections.Connection configured with DictCursor.

    Raises:
        pymysql.err.OperationalError: if the database is unreachable.
    """
    logger.debug("Opening MySQL connection to %s:%s/%s", DB_HOST, DB_PORT, DB_NAME)
    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor,
    )
