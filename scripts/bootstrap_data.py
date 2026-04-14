from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from database import Database


def main() -> None:
    db = Database()
    db.init_db()
    db.seed_demo_data()
    print("Database initialized and seeded")


if __name__ == "__main__":
    main()
