# Libraries
import logging
import os
import sqlite3
import sys
from random import choice
from sqlite3 import Error

from Transmission.print_scheme import print_function

# Global variables
strings_table = 'strings'  # Table name
answer_table = 'answer'
question_table = 'question'
database = None  # Database path variable
conn = None  # Connection index to the database file

strings_table_sql = "CREATE TABLE {} (string TEXT NOT NULL PRIMARY KEY UNIQUE," \
                    "small TEXT NOT NULL," \
                    "type TEXT," \
                    "occurrences TEXT NOT NULL)".format(strings_table)

answer_table_sql = "CREATE TABLE {} (string TEXT NOT NULL PRIMARY KEY UNIQUE," \
                   "nw0 TEXT," \
                   "oc0 TEXT)".format(answer_table)

question_table_sql = "CREATE TABLE {} (string TEXT NOT NULL PRIMARY KEY UNIQUE," \
                     "nw0 TEXT," \
                     "oc0 TEXT)".format(question_table)


def database_list_column_names(table):
    column_name_list = []
    cursor = conn.cursor()
    sql = "SELECT * FROM {}".format(table)
    cursor.execute(sql)
    data = cursor.description

    for i in data:
        column_name_list.append(i[0])

    return column_name_list


def database_fetch_answer(content):
    answer_list = []
    i = 'nw0'
    qty = 0

    index = database_list_column_names(answer_table).index('nw0')
    column_names = database_list_column_names(answer_table)

    while True:
        if i in column_names:
            qty = qty + 1
            i = 'nw' + str(qty)
        else:
            break

    qty = index + (2 * qty)

    while index < qty:
        if content[index] is not None:
            answer_list.append(content[index])
            index = index + 2
        else:
            break

    return choice(answer_list)


def database_fetch_object_list(table, content, artifact):
    question_list = []
    count_list = []
    i = artifact + '0'
    qty = 0

    index = database_list_column_names(table).index(i)
    column_names = database_list_column_names(table)

    while True:
        if i in column_names:
            qty = qty + 1
            i = artifact + str(qty)
        else:
            break

    qty = index + (2 * qty)

    while index < qty:
        question_list.append(content[index])
        count_list.append(content[index + 1])
        if content[index] is not None:
            index = index + 2
        else:
            break

    return question_list, count_list


def database_add_string(string, small):
    """ create a table from the create_table_sql statement
    :param string: The string (word or sentence) to be added into the database table or increment the use counting.
    :param small: The same string but without the stops words.
    :return new_string: True if the string is a new one or False otherwise.
    """
    new_string = False
    cursor = conn.cursor()
    data = database_find_strings(strings_table, 'string', string)

    if len(data) is 0:
        sql = "INSERT INTO {} (string, small, type, occurrences) VALUES (?, ?, ?, ?)".format(strings_table)
        val = (string, small, '%Passive', '1')
        cursor.execute(sql, val)

        sql = "INSERT INTO {} (string) VALUES ('{}')".format(answer_table, string)
        cursor.execute(sql)

        new_string = True
    else:
        line_data = data[0]
        occurrences = str(int(line_data[database_list_column_names(strings_table).index('occurrences')]) + 1)
        sql = "UPDATE {} SET occurrences = {} WHERE string = '{}'".format(strings_table, occurrences, string)
        cursor.execute(sql)

    conn.commit()
    return new_string


def database_add_related_string(table, string, answer):
    """ create a table from the create_table_sql statement
    :param table:
    :param string: The string (word or sentence) to be found in the database table.
    :param answer: The string (word or sentence) that will be added in the same string's row.
    :return None
    """

    qty = '1'

    cursor = conn.cursor()
    data = database_find_strings(table, 'string', string)
    data, count = database_fetch_object_list(table, data[0], 'nw')

    if len(data) is not 0 and answer in data:
        index = data.index(answer)
        qty = str(int(count[index]) + 1)
        nw = 'nw' + str(index)
        oc = 'oc' + str(index)
        pass

    else:
        sql = "SELECT * FROM {}".format(table)
        cursor.execute(sql)

        qty_col = 0
        i = 'nw0'

        column_names = database_list_column_names(table)

        while True:
            if i in column_names:
                qty_col = qty_col + 1
                i = 'nw' + str(qty_col)
            else:
                break

        index = 0

        while True:
            if data[index] is None:
                nw = 'nw' + str(index)
                oc = 'oc' + str(index)
                break

            # Jump around the next word indexes.
            index = index + 1

            if (qty_col - 1) < index:
                nw = 'nw' + str(index)
                oc = 'oc' + str(index)

                sql = "ALTER TABLE {} ADD COLUMN {}".format(table, nw)
                cursor.execute(sql)
                sql = "ALTER TABLE {} ADD COLUMN {}".format(table, oc)
                cursor.execute(sql)

                data = database_find_strings(table, 'string', string)
                data, count = database_fetch_object_list(table, data[0], 'nw')

    sql = "UPDATE {} SET '{}' = '{}', '{}' = '{}' WHERE string = '{}'" \
        .format(table, nw, answer, oc, qty, string)

    cursor.execute(sql)
    conn.commit()
    return


def database_find_strings(table, column, string):
    """ create a table from the create_table_sql statement
    :param table:
    :param column: The name of column where the string will be fetched
    :param string: The string (word or sentence) to be found in the database table.
    :return all the raw information relative to the string that was searched or an empty list.
    """
    cursor = conn.cursor()
    sql = "SELECT * FROM {} WHERE {} = '{}'".format(table, column, string)
    cursor.execute(sql)
    return cursor.fetchall()


def database_bring_tablet(table):
    """
    :param table:
    :return:
    """
    cursor = conn.cursor()
    sql = "SELECT * FROM {}".format(table)
    cursor.execute(sql)
    return cursor.fetchall()


def delete_table_data():
    """ reset all database information
    :return None
    """
    try:
        cursor = conn.cursor()
        sql = "DROP TABLE IF EXISTS {}".format(strings_table)
        cursor.execute(sql)
        sql = "DROP TABLE IF EXISTS {}".format(answer_table)
        cursor.execute(sql)
        sql = "DROP TABLE IF EXISTS {}".format(question_table)
        cursor.execute(sql)

        conn.commit()
        print_function('OUT', '\n\nAll data were deleted!')
    except Error as e:
        logging.error(e)

    try:
        create_table(strings_table_sql)
        create_table(answer_table_sql)
        create_table(question_table_sql)

    except Error as e:
        logging.error(e)

    return


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return Connection object or None
    """

    try:
        connection = sqlite3.connect(db_file)
        logging.info('Connected to DB - version: {}'.format(sqlite3.version))
        return connection
    except Error as e:
        logging.error(e)

    return None


def create_table(create_table_sql):
    """ create a table from the create_table_sql statement
    :param create_table_sql: a CREATE TABLE statement
    :return None
    """

    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        logging.error(e)

    return None


def close_database():
    """ close the database connection
    :return None
    """
    try:
        cursor = conn.cursor()
        cursor.close()
    except Error as e:
        logging.error(e)

    return None


def connect_database():
    """ connect to the SQLite database named database.db
    :return None
    """

    # Store current working directory
    path = os.path.dirname(__file__)
    # Append current directory to the python path
    sys.path.append(path)

    global database
    database = path + "/database.db"

    # create a database connection
    global conn
    conn = create_connection(database)

    if conn is None:

        try:
            create_table(strings_table_sql)
            create_table(answer_table_sql)
        except Error as e:
            logging.error(e)

    return None
