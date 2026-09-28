import sqlite3
import unittest

class TestExpenseDatabase(unittest.TestCase):

    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.cur = self.conn.cursor()
        self.cur.execute("""
        CREATE TABLE expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            amount REAL,
            category TEXT,
            note TEXT
        )
        """)
        self.conn.commit()

    def test_add_expense(self):
        self.cur.execute(
            "INSERT INTO expenses(username, amount, category, note) VALUES (?, ?, ?, ?)",
            ("student", 100, "Food", "Lunch")
        )
        self.conn.commit()

        self.cur.execute("SELECT amount FROM expenses")
        result = self.cur.fetchone()[0]

        self.assertEqual(result, 100)

    def test_total_expense(self):
        self.cur.executemany(
            "INSERT INTO expenses(username, amount, category, note) VALUES (?, ?, ?, ?)",
            [
                ("student", 100, "Food", "Lunch"),
                ("student", 200, "Travel", "Bus")
            ]
        )
        self.conn.commit()

        self.cur.execute("SELECT SUM(amount) FROM expenses WHERE username=?",
                         ("student",))
        total = self.cur.fetchone()[0]

        self.assertEqual(total, 300)

    def tearDown(self):
        self.conn.close()

if __name__ == "__main__":
    unittest.main()
