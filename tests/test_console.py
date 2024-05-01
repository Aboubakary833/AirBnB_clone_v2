#!/usr/bin/python3
"""HBNBCommand tests"""
import json
import MySQLdb
import os
import sqlalchemy
import unittest
from io import StringIO
from typing import TextIO
from unittest.mock import patch

from console import HBNBCommand
from models import storage
from models.base_model import BaseModel
from models.user import User


class TestHBNBCommand(unittest.TestCase):
    """Represents the test class for the HBNBCommand class.
    """
    @unittest.skipIf(
        os.getenv('HBNB_TYPE_STORAGE') == 'db', 'FileStorage test')
    def test_fs_create(self):
        """Tests the create command with the file storage.
        """
        with patch('sys.stdout', new=StringIO()) as output:
            console = HBNBCommand()
            console.onecmd('create City name="Texas"')
            city_id = output.getvalue().strip()
            self.clear(output)
            self.assertIn('City.{}'.format(city_id), storage.all().keys())
            console.onecmd('show City {}'.format(city_id))
            self.assertIn("'name': 'California'", output.getvalue().strip())
            self.clear(output)
            console.onecmd('create User name="John" age=17 height=5.9')
            user_id = output.getvalue().strip()
            self.assertIn('User.{}'.format(user_id), storage.all().keys())
            self.clear(output)
            console.onecmd('show User {}'.format(user_id))
            self.assertIn("'name': 'James'", output.getvalue().strip())
            self.assertIn("'age': 17", output.getvalue().strip())
            self.assertIn("'height': 5.9", output.getvalue().strip())

    @unittest.skipIf(
        os.getenv('HBNB_TYPE_STORAGE') != 'db', 'DBStorage test')
    def test_db_create(self):
        """Tests the create command with the database storage.
        """
        with patch('sys.stdout', new=StringIO()) as output:
            console = HBNBCommand()
            # creating a model with non-null attribute(s)
            with self.assertRaises(sqlalchemy.exc.OperationalError):
                console.onecmd('create User')
            # creating a User instance
            self.clear(output)
            console.onecmd("""create User email=\"johndoe@gmail.com\"
                           password=\"123\"""")
            user_id = output.getvalue().strip()
            dbc = MySQLdb.connect(
                host=os.getenv('HBNB_MYSQL_HOST'),
                port=3306,
                user=os.getenv('HBNB_MYSQL_USER'),
                passwd=os.getenv('HBNB_MYSQL_PWD'),
                db=os.getenv('HBNB_MYSQL_DB')
            )
            cursor = dbc.cursor()
            cursor.execute('SELECT * FROM users WHERE id="{}"'.format(user_id))
            result = cursor.fetchone()
            self.assertTrue(result is not None)
            self.assertIn('johndoe@gmail.com', result)
            self.assertIn('123', result)
            cursor.close()
            dbc.close()

    @unittest.skipIf(
        os.getenv('HBNB_TYPE_STORAGE') != 'db', 'DBStorage test')
    def test_db_show(self):
        """Tests the show command with the database storage.
        """
        with patch('sys.stdout', new=StringIO()) as output:
            console = HBNBCommand()
            obj = User(email="john25@gmail.com", password="123")
            dbc = MySQLdb.connect(
                host=os.getenv('HBNB_MYSQL_HOST'),
                port=3306,
                user=os.getenv('HBNB_MYSQL_USER'),
                passwd=os.getenv('HBNB_MYSQL_PWD'),
                db=os.getenv('HBNB_MYSQL_DB')
            )
            cursor = dbc.cursor()
            cursor.execute('SELECT * FROM users WHERE id="{}"'.format(obj.id))
            result = cursor.fetchone()
            self.assertTrue(result is None)
            console.onecmd('show User {}'.format(obj.id))
            self.assertEqual(
                output.getvalue().strip(),
                '** no instance found **'
            )
            obj.save()
            dbc = MySQLdb.connect(
                host=os.getenv('HBNB_MYSQL_HOST'),
                port=3306,
                user=os.getenv('HBNB_MYSQL_USER'),
                passwd=os.getenv('HBNB_MYSQL_PWD'),
                db=os.getenv('HBNB_MYSQL_DB')
            )
            cursor = dbc.cursor()
            cursor.execute('SELECT * FROM users WHERE id="{}"'.format(obj.id))
            self.clear(output)
            console.onecmd('show User {}'.format(obj.id))
            result = cursor.fetchone()
            self.assertTrue(result is not None)
            self.assertIn('john25@gmail.com', result)
            self.assertIn('123', result)
            self.assertIn('john25@gmail.com', output.getvalue())
            self.assertIn('123', output.getvalue())
            cursor.close()
            dbc.close()

    @unittest.skipIf(
        os.getenv('HBNB_TYPE_STORAGE') != 'db', 'DBStorage test')
    def test_db_count(self):
        """Tests the count command with the database storage.
        """
        with patch('sys.stdout', new=StringIO()) as output:
            console = HBNBCommand()
            dbc = MySQLdb.connect(
                host=os.getenv('HBNB_MYSQL_HOST'),
                port=3306,
                user=os.getenv('HBNB_MYSQL_USER'),
                passwd=os.getenv('HBNB_MYSQL_PWD'),
                db=os.getenv('HBNB_MYSQL_DB')
            )
            cursor = dbc.cursor()
            cursor.execute('SELECT COUNT(*) FROM states;')
            res = cursor.fetchone()
            prev_count = int(res[0])
            console.onecmd('create State name="Enugu"')
            self.clear(output)
            console.onecmd('count State')
            cnt = output.getvalue().strip()
            self.assertEqual(int(cnt), prev_count + 1)
            self.clear(output)
            console.onecmd('count State')
            cursor.close()
            dbc.close()

    def clear(stream: TextIO):
        """clear stream content
        Args:
        stream (TextIO): stream
        """
        if stream.seekable():
            stream.seek(0)
            stream.truncate(0)

if __name__ == "__main__":
    unittest.main()
