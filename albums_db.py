"""
Albums Database Project (Python + SQLite)

Features:
- SQLite database in same folder
- CRUD operations
- Fuzzy search
- ASCII table output
- Random data generation
- Menu-driven interface
- Built-in unit tests
"""

import os
import sqlite3
import random
import unittest

# ================= DATABASE PATH =================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "albums.db")

# ================= DATABASE INITIALIZATION =================
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS albums (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        artist TEXT NOT NULL,
        tracks TEXT NOT NULL,
        genre TEXT NOT NULL,
        rating REAL NOT NULL CHECK (rating >= 0 AND rating <= 10),
        year INTEGER NOT NULL
    )
    """)
    conn.commit()
    conn.close()

init_db()

# ================= HELPER FUNCTIONS =================
def row_to_dict(row):
    if row is None:
        return None
    keys = ["id", "title", "artist", "tracks", "genre", "rating", "year"]
    return dict(zip(keys, row))


def print_table(records):
    if not records:
        print("No records found")
        return

    headers = ["id", "title", "artist", "tracks", "genre", "rating", "year"]
    col_widths = {
        h: max(len(h), max(len(str(r[h])) for r in records))
        for h in headers
    }

    def border():
        print("+" + "+".join("-" * (col_widths[h] + 2) for h in headers) + "+")

    def header():
        print("|" + "|".join(f" {h.ljust(col_widths[h])} " for h in headers) + "|")

    def row(r):
        print("|" + "|".join(f" {str(r[h]).ljust(col_widths[h])} " for h in headers) + "|")

    border()
    header()
    border()
    for r in records:
        row(r)
    border()

# ================= CRUD FUNCTIONS =================
def add_album(id, title, artist, tracks, genre, rating, year):
    if not (0 <= rating <= 10):
        raise ValueError("Rating must be between 0 and 10")

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute("SELECT 1 FROM albums WHERE id=?", (id,))
    if cur.fetchone():
        conn.close()
        raise ValueError("Album ID already exists")

    cur.execute(
        "INSERT INTO albums VALUES (?, ?, ?, ?, ?, ?, ?)",
        (id, title, artist, tracks, genre, rating, year)
    )
    conn.commit()
    conn.close()


def delete_album(id):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute("SELECT 1 FROM albums WHERE id=?", (id,))
    if not cur.fetchone():
        conn.close()
        raise ValueError("Album not found")

    cur.execute("DELETE FROM albums WHERE id=?", (id,))
    conn.commit()
    conn.close()


def update_album(id, title, artist, tracks, genre, rating, year):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute("SELECT 1 FROM albums WHERE id=?", (id,))
    if not cur.fetchone():
        conn.close()
        raise ValueError("Album not found")

    cur.execute("""
    UPDATE albums
    SET title=?, artist=?, tracks=?, genre=?, rating=?, year=?
    WHERE id=?
    """, (title, artist, tracks, genre, rating, year, id))

    conn.commit()
    conn.close()


def get_album_by_id(id):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT * FROM albums WHERE id=?", (id,))
    row = cur.fetchone()
    conn.close()
    return row_to_dict(row)


def fuzzy_query(column, value):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        f"SELECT * FROM albums WHERE LOWER({column}) LIKE ?",
        (f"%{value.lower()}%",)
    )
    rows = cur.fetchall()
    conn.close()
    return [row_to_dict(r) for r in rows]


def get_album_by_title(title): return fuzzy_query("title", title)
def get_album_by_artist(artist): return fuzzy_query("artist", artist)
def get_album_by_track(track): return fuzzy_query("tracks", track)
def get_album_by_genre(genre): return fuzzy_query("genre", genre)


def get_album_by_rating(min_rating):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT * FROM albums WHERE rating >= ?", (min_rating,))
    rows = cur.fetchall()
    conn.close()
    return [row_to_dict(r) for r in rows]


def get_album_by_year(year):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT * FROM albums WHERE year=?", (year,))
    rows = cur.fetchall()
    conn.close()
    return [row_to_dict(r) for r in rows]


def get_all_albums():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT * FROM albums")
    rows = cur.fetchall()
    conn.close()
    return [row_to_dict(r) for r in rows]


def clear_albums():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("DELETE FROM albums")
    conn.commit()
    conn.close()

# ================= RANDOM DATA =================
def generate_random_albums(n=5):
    titles = ["Abbey Road", "AM", "Blonde", "Igor", "Currents"]
    artists = ["The Beatles", "Radiohead", "Drake", "Lorde", "Daft Punk"]
    tracks = ["Track A", "Track B", "Track C", "Track D"]
    genres = ["Rock", "Pop", "Indie", "Electronic"]

    for i in range(1, n + 1):
        try:
            add_album(
                i,
                random.choice(titles),
                random.choice(artists),
                ",".join(random.sample(tracks, 3)),
                ",".join(random.sample(genres, 2)),
                round(random.uniform(0, 10), 1),
                random.randint(1990, 2023)
            )
        except:
            pass

# ================= UNIT TESTS =================
class TestAlbumDatabase(unittest.TestCase):

    def setUp(self):
        clear_albums()
        add_album(1, "Test Album", "Test Artist", "Song1,Song2", "Rock", 8.0, 2020)

    def tearDown(self):
        clear_albums()

    def test_add_album(self):
        add_album(2, "Album 2", "Artist 2", "A,B", "Pop", 7.5, 2021)
        self.assertIsNotNone(get_album_by_id(2))

    def test_delete_album(self):
        delete_album(1)
        self.assertIsNone(get_album_by_id(1))

    def test_update_album(self):
        update_album(1, "Updated", "Artist", "X,Y", "Indie", 9.0, 2022)
        album = get_album_by_id(1)
        self.assertEqual(album["title"], "Updated")

    def test_fuzzy_search(self):
        results = get_album_by_artist("test")
        self.assertTrue(len(results) > 0)


def run_tests():
    print("\nRunning unit tests...\n")
    unittest.TextTestRunner(verbosity=2).run(
        unittest.TestLoader().loadTestsFromTestCase(TestAlbumDatabase)
    )

# ================= MENU =================
def main_menu():
    while True:
        print("""
========= ALBUM DATABASE MENU =========
1) Add album
2) Delete album
3) Update album
4) View all albums
5) Get album by ID
6) Search by title
7) Search by artist
8) Search by track
9) Search by genre
10) Search by minimum rating
11) Search by year
12) Generate random albums
13) Run unit tests
14) Clear all data
0) Exit
""")

        choice = input("Choose an option: ").strip()

        try:
            if choice == "1":
                add_album(
                    int(input("id: ")),
                    input("title: "),
                    input("artist: "),
                    input("tracks: "),
                    input("genre: "),
                    float(input("rating: ")),
                    int(input("year: "))
                )
                print("Album added")

            elif choice == "2":
                delete_album(int(input("id: ")))
                print("Album deleted")

            elif choice == "3":
                update_album(
                    int(input("id: ")),
                    input("title: "),
                    input("artist: "),
                    input("tracks: "),
                    input("genre: "),
                    float(input("rating: ")),
                    int(input("year: "))
                )
                print("Album updated")

            elif choice == "4":
                print_table(get_all_albums())

            elif choice == "5":
                result = get_album_by_id(int(input("id: ")))
                print_table([result] if result else [])

            elif choice == "6":
                print_table(get_album_by_title(input("keyword: ")))

            elif choice == "7":
                print_table(get_album_by_artist(input("keyword: ")))

            elif choice == "8":
                print_table(get_album_by_track(input("keyword: ")))

            elif choice == "9":
                print_table(get_album_by_genre(input("keyword: ")))

            elif choice == "10":
                print_table(get_album_by_rating(float(input("min rating: "))))

            elif choice == "11":
                print_table(get_album_by_year(int(input("year: "))))

            elif choice == "12":
                generate_random_albums()
                print("Random albums generated")

            elif choice == "13":
                run_tests()

            elif choice == "14":
                clear_albums()
                print("All data cleared")

            elif choice == "0":
                print("Goodbye!")
                break

            else:
                print("Invalid option")

        except Exception as e:
            print("Error:", e)

# ================= MAIN =================
if __name__ == "__main__":
    main_menu()
