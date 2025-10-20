from sqlalchemy import inspect

from app.database.connection import ENGINE


def test_list_tables_and_counts() -> None:
    inspector = inspect(ENGINE)
    tables = sorted(inspector.get_table_names())
    # Print for visibility when running tests
    print("Tables:", tables)
    assert isinstance(tables, list)
    assert len(tables) >= 1


