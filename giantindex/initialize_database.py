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
"""

__author__ = 'Michael Craft <mcraft@peak15.org>'

import MySQLdb
import contextlib


def initialize_database(host, user, passwd, db):
        with MySQLdb.connect(
                host=host, user=user, passwd=passwd, db=db) \
                as conn:

            with contextlib.closing(conn.cursor()) as c:
                c.execute("""

CREATE TABLE IF NOT EXISTS documents (
  id int(11) unsigned NOT NULL AUTO_INCREMENT,
  path varchar(255) NOT NULL,
  modified timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  size bigint(20) NOT NULL,
  PRIMARY KEY (id),
  INDEX path_ind (path),
  INDEX modified_ind (modified),
  INDEX size_ind (size)
) ENGINE=InnoDB CHARSET=utf8 COLLATE=utf8_general_ci;

CREATE TABLE IF NOT EXISTS thumbnails (
  document int(11) unsigned NOT NULL,
  image varchar(255) NOT NULL,
  PRIMARY KEY (document),
  FOREIGN KEY (document) REFERENCES documents(id)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB CHARSET=utf8 COLLATE=utf8_general_ci;

CREATE TABLE IF NOT EXISTS tags (
  id int(11) unsigned NOT NULL AUTO_INCREMENT,
  name varchar(255) NOT NULL,
  `numeric` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (id),
  INDEX name_ind (name)
) ENGINE=InnoDB CHARSET=utf8 COLLATE=utf8_general_ci;

CREATE TABLE IF NOT EXISTS documentTags (
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

                """)

                conn.commit()

if __name__ == '__main__':
    initialize_database('localhost', 'test', 'test', 'test')