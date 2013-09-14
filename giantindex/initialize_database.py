"""
First log in to MySQL on your server as root:

$ mysql -u root -p

And create a new user and database like so:

CREATE USER 'example'@'localhost' IDENTIFIED BY 'example_passwd';
CREATE USER 'example'@'%' IDENTIFIED BY 'example_passwd';
CREATE DATABASE example_db CHARACTER SET=utf8 COLLATE=utf8_general_ci;
GRANT ALL ON example_db.* TO 'example'@'localhost';
GRANT ALL ON example_db.* TO 'example'@'%';
FLUSH PRIVILEGES;

Then run this like:

$ python initialize_database.py host user passwd database
"""

__author__ = 'Michael Craft <mcraft@peak15.org>'

SQL = ('DROP TABLE IF EXISTS documentTags, thumbnails','DROP TABLE IF EXISTS documents, tags',"""CREATE TABLE IF NOT EXISTS documents (
  id int(11) unsigned NOT NULL AUTO_INCREMENT,
  path varchar(255) NOT NULL,
  added bigint(20) NOT NULL,
  modified bigint(20) NOT NULL,
  size bigint(20) NOT NULL,
  PRIMARY KEY (id),
  INDEX path_ind (path),
  INDEX added_ind (added),
  INDEX modified_ind (modified),
  INDEX size_ind (size)
) ENGINE=InnoDB CHARSET=utf8 COLLATE=utf8_general_ci;
""","""CREATE TABLE IF NOT EXISTS thumbnails (
  document int(11) unsigned NOT NULL,
  image varchar(255) NOT NULL,
  PRIMARY KEY (document),
  FOREIGN KEY (document) REFERENCES documents(id)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB CHARSET=utf8 COLLATE=utf8_general_ci;
""","""CREATE TABLE IF NOT EXISTS tags (
  id int(11) unsigned NOT NULL AUTO_INCREMENT,
  name varchar(255) NOT NULL,
  `numeric` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (id),
  INDEX name_ind (name)
) ENGINE=InnoDB CHARSET=utf8 COLLATE=utf8_general_ci;
""","""CREATE TABLE IF NOT EXISTS documentTags (
  tag int(11) unsigned NOT NULL,
  document int(11) unsigned NOT NULL,
  string_value varchar(255) DEFAULT NULL,
  int_value int(11) DEFAULT NULL,
  INDEX tag_ind (tag),
  INDEX document_ind (document),
  INDEX string_value_ind (string_value),
  INDEX int_value_ind (int_value),
  FOREIGN KEY (tag) REFERENCES tags(id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (document) REFERENCES documents(id)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB CHARSET=utf8 COLLATE=utf8_general_ci;
""","""INSERT INTO documents (id, path, added, modified, size)
VALUES (DEFAULT, '/testpath', DEFAULT, CURRENT_TIMESTAMP, 1337)""")

import MySQLdb
import contextlib
import sys


class DBConn(object):
    def __init__(self, host, user, passwd, db):
        self.db = MySQLdb.connect(
            host=host, user=user, passwd=passwd, db=db)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        self.db.close()

    def initialize(self):
        for cmd in SQL:
            with contextlib.closing(self.db.cursor()) as c:
                c.execute(cmd)
            self.db.commit()

if __name__ == '__main__':
    with DBConn(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]) as db:
        db.initialize()


