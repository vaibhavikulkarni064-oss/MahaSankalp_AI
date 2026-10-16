"""Run from project root:  python -m database.init_db"""
from backend import database
if __name__ == "__main__":
    database.init_db()
    print(f"Database ready with {len(database.get_catalogue())} careers.")
