# -*- coding: utf-8 -*-
"""
Created on Tue Jul 10 14:32:51 2018

@author: antonio constandinou
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import datetime
import os


def table_exists(credentials):
    """
    check to see if table exists PostgreSQL database
    args:
        credentials: database credentials including host, user, password and db name, type array
    returns:
        boolean value (True or False)
    """
    db_host, db_user, db_password, db_name = credentials
    conn = psycopg2.connect(host=db_host, database=db_name, user=db_user, password=db_password)
    cur = conn.cursor()
    cur.execute("SELECT EXISTS(SELECT * FROM information_schema.tables WHERE table_name=%s)", (table_name,))
    return cur.fetchone()[0]


def create_db(db_credential_info):
    """
    create a new database if it does not exist in the PostgreSQL database
    will use method 'check_db_exists' before creating a new database
    args:
        db_credential_info: database credentials including host, user, password and db name, type array
    returns:
        NoneType
    """
    db_host, db_user, db_password, db_name = db_credential_info

    if check_db_exists(db_credential_info):
        pass
    else:
        print('Creating new database.')
        conn = psycopg2.connect(host=db_host, database='postgres', user=db_user, password=db_password)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        cur.execute("CREATE DATABASE %s  ;" % db_name)
        cur.close()


def check_db_exists(db_credential_info):
    """
    checks to see if a database already exists in the PostgreSQL database
    args:
        db_credential_info: database credentials including host, user, password and db name, type array
    returns:
        boolean value (True or False)
    """
    db_host, db_user, db_password, db_name = db_credential_info
    try:
        conn = psycopg2.connect(host=db_host, database=db_name, user=db_user, password=db_password)
        cur = conn.cursor()
        cur.close()
        print('Database exists.')
        return True
    except:
        print("Database does not exist.")
        return False


def create_mkt_tables(db_credential_info):
    """
    create table in designated PostgreSQL database
    will use method 'check_db_exists' before creating table
    args:
        db_credential_info: database credentials including host, user, password and db name, type array
    returns:
        NoneType
    """
    db_host, db_user, db_password, db_name = db_credential_info
    conn = None

    if check_db_exists(db_credential_info):
        commands = (
            """
            CREATE TABLE insider_trades (
            id SERIAL PRIMARY KEY,
            symbol TEXT NOT NULL,
            company TEXT NOT NULL,
            insider_name TEXT,
            insider_position TEXT,
            insider_order_type TEXT NOT NULL,
            trade_shares_quantity INTEGER,
            trade_shares_price NUMERIC(7,2),
            trade_value NUMERIC(10,2),
            reported_date TIMESTAMP NOT NULL, 
            created_date TIMESTAMP NOT NULL)
            """,
            """
            CREATE TABLE companies (
            id SERIAL PRIMARY KEY,
            company TEXT NULL,
            symbol TEXT UNIQUE NOT NULL,
            exchange VARCHAR(64) NULL,
            country VARCHAR(64) NULL,
            sector VARCHAR(64) NULL,
            marketcap integer NULL,
            cikNumber integer NOT NULL,
            created_date TIMESTAMP NOT NULL,
            last_updated_date TIMESTAMP NULL)
            """
        )

        try:
            for command in commands:
                print('Building tables.')
                conn = psycopg2.connect(host=db_host, database=db_name, user=db_user, password=db_password)
                cur = conn.cursor()
                cur.execute(command)
                # need to commit this change
                conn.commit()
                cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            cur.close()
        finally:
            if conn:
                conn.close()
    else:
        pass


def load_db_credential_info(f_name_path):
    """
    load text file holding our database credential info and the database name
    args:
        f_name_path: name of file preceded with "\\", type string
    returns:
        array of 4 values that should match text file info
    """
    cur_path = os.getcwd()
    # lets load our database credentials and info
    f = open(cur_path + f_name_path, 'r')
    lines = f.readlines()[1:]
    lines = lines[0].split(',')
    return lines


def load_txt_file(f_name_path):
    cik_dictionary = []
    now = datetime.datetime.utcnow()
    f = open(f_name_path, 'r')
    for line in f:
        cik_pairs = line.split("\t")

        symbol = cik_pairs[0]

        # we get rid of the \n at the end of the variable
        cik_number = cik_pairs[1][:-2]

        cik_dictionary.append([symbol, cik_number, now])

        print("The last added Symbol and CIK numbers are:" + str(cik_dictionary[-1]))
    return cik_dictionary


def insert_into_companies(cik_numbers, db_host, db_user, db_password, db_name):
    # Connect to our PostgreSQL database
    conn = psycopg2.connect(host=db_host, database=db_name, user=db_user, password=db_password)

    column_str = ('symbol, ciknumber,created_date')
    insert_str = ("%s," * 3)[:-1]
    final_str = "INSERT INTO companies (%s) VALUES (%s)" % (column_str, insert_str)
    with conn:
        cur = conn.cursor()
        cur.executemany(final_str, cik_numbers)


def main():
    # name of our database credential files (.txt)
    db_credential_info = "database_info.txt"

    # define the cik file
    cik_file = "outdated_testing_code/ticker.txt"

    # create a path version of our text file
    db_credential_info_p = '/' + db_credential_info

    # create our instance variables for host, username, password and database name
    db_host, db_user, db_password, db_name = load_db_credential_info(db_credential_info_p)

    # first lets create our database from postgres
    create_db([db_host, db_user, db_password, db_name])

    # second lets create our tables for our new database
    create_mkt_tables([db_host, db_user, db_password, db_name])

    # # After table is created, we update the database with CIK numbers and its respective tickers
    # cik_dictionary = load_txt_file(cik_file)
    #
    # # insert_int
    # insert_into_companies(cik_dictionary, db_host, db_user, db_password, db_name)


if __name__ == "__main__":
    main()
