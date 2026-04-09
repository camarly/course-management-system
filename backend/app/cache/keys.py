"""
Redis cache key constants and builder functions.

Centralises every cache key string so that route handlers and
invalidation logic always reference the same key for the same resource.

Convention:  lms:<resource>:<identifier>
Example:     lms:courses:all
             lms:course:42
             lms:course:42:members

Owner: Camarly Thomas
"""

# TTL constants (seconds)
TTL_SHORT  = 30
TTL_MEDIUM = 60
TTL_LONG   = 300
