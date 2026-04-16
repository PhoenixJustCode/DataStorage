"""
Unit tests for the transform() function.
"""

import pandas as pd
import pytest

from etl_pipeline import transform


def _make_user(email="john@example.com", gender="male", first="John", last="Doe",
               nat="US", age=25, dob_date="1999-01-15T00:00:00.000Z"):
    """Helper to build a single raw user row matching API structure."""
    return {
        "email": email,
        "gender": gender,
        "name": {"title": "Mr", "first": first, "last": last},
        "nat": nat,
        "dob": {"date": dob_date, "age": age},
    }


class TestTransformNormal:
    """Test 1: Normal input with valid data."""

    def test_age_group_young_adult(self):
        df = pd.DataFrame([_make_user(age=25)])
        result = transform(df)
        assert result.iloc[0]["age_group"] == "Young Adult"

    def test_age_group_child(self):
        df = pd.DataFrame([_make_user(age=10)])
        result = transform(df)
        assert result.iloc[0]["age_group"] == "Child"

    def test_age_group_adult(self):
        df = pd.DataFrame([_make_user(age=45)])
        result = transform(df)
        assert result.iloc[0]["age_group"] == "Adult"

    def test_age_group_senior(self):
        df = pd.DataFrame([_make_user(age=70)])
        result = transform(df)
        assert result.iloc[0]["age_group"] == "Senior"

    def test_email_domain(self):
        df = pd.DataFrame([_make_user(email="alice@gmail.com")])
        result = transform(df)
        assert result.iloc[0]["email_domain"] == "gmail.com"

    def test_name_flattening(self):
        df = pd.DataFrame([_make_user(first="Jane", last="Smith")])
        result = transform(df)
        assert result.iloc[0]["first_name"] == "Jane"
        assert result.iloc[0]["last_name"] == "Smith"

    def test_loaded_at_present(self):
        df = pd.DataFrame([_make_user()])
        result = transform(df)
        assert "loaded_at" in result.columns
        assert result.iloc[0]["loaded_at"] is not None


class TestTransformDuplicates:
    """Test 2: Input with duplicate emails."""

    def test_duplicates_removed(self):
        df = pd.DataFrame([
            _make_user(email="dup@example.com", first="A", last="One"),
            _make_user(email="dup@example.com", first="B", last="Two"),
        ])
        result = transform(df)
        assert len(result) == 1
        assert result.iloc[0]["first_name"] == "A"  # keep first


class TestTransformMissingEmail:
    """Test 3: Input with missing email."""

    def test_missing_email_dropped(self):
        df = pd.DataFrame([
            _make_user(email=None, first="Ghost", last="User"),
            _make_user(email="valid@example.com"),
        ])
        result = transform(df)
        assert len(result) == 1
        assert result.iloc[0]["email"] == "valid@example.com"


class TestTransformEmpty:
    """Test 4: Empty DataFrame."""

    def test_empty_input(self):
        df = pd.DataFrame()
        result = transform(df)
        assert result.empty
        assert "email" in result.columns
