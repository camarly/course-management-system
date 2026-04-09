"""
Tests for report endpoints.

Covers:
    - GET /api/reports/courses-50-plus
    - GET /api/reports/students-5-plus-courses
    - GET /api/reports/lecturers-3-plus-courses
    - GET /api/reports/top10-enrolled-courses
    - GET /api/reports/top10-students-by-average
    - Role guard: all endpoints require admin (403 for student/lecturer)
"""

import pytest


class TestReports:
    """Test cases for admin report endpoints."""

    def test_placeholder(self):
        """Placeholder — replace with real tests."""
        pass
