"""
MySQL connection factory.

Provides get_connection() which returns a PyMySQL connection.
All database access in every service must go through this function.
No ORM — raw SQL only.
"""

import os
import pymysql
import pymysql.cursors
