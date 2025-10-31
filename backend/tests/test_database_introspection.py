from sqlalchemy import inspect

from app.database.connection import ENGINE


def test_list_tables_and_counts(setup_database) -> None:
    """Test that database tables exist after setup_database fixture runs."""
    inspector = inspect(ENGINE)
    tables = sorted(inspector.get_table_names())
    # Print for visibility when running tests
    print("Tables:", tables)
    assert isinstance(tables, list)
    assert len(tables) >= 1, f"Expected at least 1 table, but found: {tables}"


