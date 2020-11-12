#! /usr/bin/env python
import psycopg2

# Login details for database user
dbname = "alexapre" #Set in your UiO-username
user = "alexapre_priv" # Set in your priv-user (UiO-username + _priv)
pwd = "AaShahph9a" # Set inn the password for the _priv-user you got in a mail

# Gather all connection info into one string
connection = \
    "host='dbpg-ifi-kurs01.uio.no' " + \
    "dbname='" + dbname + "' " + \
    "user='" + user + "' " + \
    "port='5432' " + \
    "password='" + pwd + "'"

def administrator():
    conn = psycopg2.connect(connection)

    ch = 0
    while (ch != 3):
        print("\n-- ADMINISTRATOR --")
        print("Please choose an option:\n 1. Create bills\n 2. Insert new product\n 3. Exit")
        ch = get_int_from_user("Option: ", True)

        if (ch == 1):
            make_bills(conn)
        elif (ch == 2):
            insert_product(conn)

def make_bills(conn):
    print("\n-- BILLS --")
    username = str(input("Username: "))

    cur = conn.cursor()

    if (username == ""):
        cur.execute(
            "\
            SELECT uo.name, uo.address, sum(p.price * uo.num) as due \
            FROM \
                (SELECT u.name, u.address, u.uid, o.pid, o.num \
                FROM ws.users as u \
                    INNER JOIN ws.orders as o \
                    ON (u.uid = o.uid) WHERE o.payed = 0) as uo \
                INNER JOIN (SELECT pid, price FROM ws.products) as p \
                ON (uo.pid = p.pid) \
            GROUP BY uo.name, uo.address;\
            "
        )
    else:
        quotemark = "'"
        cur.execute(
            f'\
            SELECT uo.name, uo.address, sum(p.price * uo.num) as due \
            FROM \
                (SELECT u.name, u.address, u.uid, o.pid, o.num \
                FROM ws.users as u \
                    INNER JOIN ws.orders as o \
                    ON (u.uid = o.uid) WHERE o.payed = 0 and u.username = {quotemark}{username}{quotemark}) as uo \
                INNER JOIN (SELECT pid, price FROM ws.products) as p \
                ON (uo.pid = p.pid) \
            GROUP BY uo.name, uo.address;')

    rows = cur.fetchall()
    if (rows == []):
        print (f'ERROR: No information found on username: {username}\nEither the user has no outstanding payments, or the user does not exist.')
        return ''
    else:
        for row in rows:
            print("\n---Bill---")
            print(f'Name: {row[0]}')
            print(f'Address: {row[1]}')
            print(f'Total due: {row[2]}')
        return ''

def insert_product(conn):
    print("\n-- INSERT NEW PRODUCT --")
    name = input("Product name: ")
    price = input("Price: ")
    category = input("Category: ")
    description = input("Description: ")

    cur = conn.cursor()

    if (name == "" or price is None or category == "" or description == ""):
        print (f'ERROR: All fields must be filled')
        return ''

    try:
        price = float(price)
    except Exception as e:
        print (f'ERROR: Price must be a number (float): "{price}" not valid.')
        return ''

    quotemark = "'"
    cur.execute(
        f'\
        INSERT INTO ws.products(name, price, cid, description) \
        (SELECT {quotemark + name + quotemark}, {price}, c.cid, {quotemark + description + quotemark} FROM ws.categories c WHERE c.name = {quotemark + category + quotemark})\
        RETURNING name;')

    try:
        cur.fetchone()[0]
    except Exception as e:
        print(f'ERROR: Could not insert product {name}\nProbable cause: Category "{category}" may beundefined.')
        return ''

    conn.commit()
    print(f'New product {name} insterted.')

def get_int_from_user(msg, needed):
    # Utility method that gets an int from the user with the first argument as message
    # Second argument is boolean, and if false allows user to not give input, and will then
    # return None
    while True:
        numStr = input(msg)
        if (numStr == "" and not needed):
            return None;
        try:
            return int(numStr)
        except:
            print("Please provide an integer or leave blank.");

def get_uname_from_user(msg, needed):
    # Utility method that gets a username from the user with the first argument as message
    # Second argument is boolean, and if false allows user to not give input, and will then
    # return None
    while True:
        str = input(msg)
        if (str == "" and not needed):
            return None;
        try:
            return str(str)
        except:
            print("Please provide a username or leave blank for all users.");


if __name__ == "__main__":
    administrator()
