# Copyright 2013, Sean B. Palmer
# Source: http://inamidst.com/saxo/

import sqlite3

class Table(object):
    def __init__(self, connection, name):
        self.connection = connection
        self.name = name

    def __iter__(self):
        return self.rows()

    def __delitem__(self, row):
        fields = []
        for field in self.schema():
            fields.append(field[1])

        if len(row) == len(fields):
            query = "DELETE FROM %s WHERE " % self.name
            query += " AND ".join(["%s=?" % field for field in fields])
            cursor = self.connection.cursor()
            cursor.execute(query, row)
            self.connection.commit()
        else:
            raise ValueError("Wrong length: %s" % row)

    def create(self, *schema):
        cursor = self.connection.cursor()
        types = {
            None: "NULL",
            int: "INTEGER",
            float: "REAL",
            str: "TEXT",
            bytes: "BLOB"
        }
        schema = ", ".join(a + " " + types.get(b, b) for (a, b) in schema)
        query = "CREATE TABLE IF NOT EXISTS %s (%s)" % (self.name, schema)
        cursor.execute(query)

    def insert(self, row, *rows):
        cursor = self.connection.cursor()
        size = len(row)
        args = ",".join(["?"] * size)
        query = "INSERT INTO %s VALUES(%s)" % (self.name, args)

        cursor.execute(query, tuple(row))
        for extra in rows:
            cursor.execute(query, tuple(extra))
        self.connection.commit()

    def rows(self, order=None):
        cursor = self.connection.cursor()
        query = "SELECT * FROM %s" % self.name

        if isinstance(order, str):
            if order.isalpha():
                query += " ORDER BY %s" % order

        cursor.execute(query)
        while True:
            result = cursor.fetchone()
            if result is None:
                break
            yield result

    def schema(self):
        cursor = self.connection.cursor()
        query = "PRAGMA table_info(%s)" % self.name
        cursor.execute(query)
        while True:
            result = cursor.fetchone()
            if result is None:
                break
            yield result

class Database(object):
    def __init__(self, path):
        self.path = path
        self.connection = sqlite3.connect(path)

    def __iter__(self):
        raise NotImplemented

    def __contains__(self, key):
        cursor = self.connection.cursor()
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
        cursor.execute(query, (key,))
        return cursor.fetchone() is not None        

    def __getitem__(self, key):
        return Table(self.connection, key)

    def __enter__(self, *args, **kargs):
        return self

    def __exit__(self, *args, **kargs):
        # TODO: Check for changes to commit?
        # self.connection.commit()
        self.connection.close()

    def commit(self):
        self.connection.commit()

def test():
    import os

    filename = "/tmp/saxo-test.sqlite3"
    if os.path.isfile(filename):
        os.remove(filename)

    with Database(filename) as db:
        assert "example" not in db
        db["example"].create(
            ("name", str),
            ("size", int))

        assert "example" in db
        db["example"].insert(
            ("pqr", 5),
            ("abc", 10))

        print(list(db["example"]))
        assert list(db["example"].rows(order="name")) == [('abc', 10), ('pqr', 5)]
        assert list(db["example"].rows(order="size")) == [('pqr', 5), ('abc', 10)]
        print(list(db["example"].schema()))

        del db["example"][("pqr", 5)]
        print(list(db["example"]))

    os.remove(filename)

if __name__ == "__main__":
    test()
