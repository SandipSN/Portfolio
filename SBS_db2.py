import random
import sqlite3


# SQL Queries
CREATE_ACCOUNTS_TABLE = "CREATE TABLE IF NOT EXISTS card (id INTEGER, number TEXT, pin TEXT, balance INTEGER DEFAULT 0);"
INSERT_ACCOUNT_DETAILS = "INSERT INTO card (number, pin) VALUES (?, ?);"
GET_ALL_ACCOUNTS = "SELECT * FROM card"
CHECK_ACCOUNT_BY_NUMBER = "SELECT * FROM card WHERE number = ?;"
CHECK_LOGIN_EXISTS = "SELECT * FROM card WHERE number = ? AND pin = ?;"
GET_BALANCE = "SELECT balance FROM card WHERE number = ?;"
UPDATE_FUNDS = "UPDATE card SET balance = ?  WHERE number = ?;"
ADD_FUNDS = "UPDATE card SET balance = (balance + ?)  WHERE number = ?;"
DELETE_ACCOUNT = "DELETE FROM card WHERE number = ?;"
# DROP_TABLE = "DROP TABLE card"

def connect():
    return sqlite3.connect('card.s3db')


def create_tables(connection):
    with connection:
        connection.execute(CREATE_ACCOUNTS_TABLE)


def add_account(connection, number, pin):
    with connection:
        connection.execute(INSERT_ACCOUNT_DETAILS, (number, pin))


def show_balance(connection, number):
    with connection:
        return connection.execute(GET_BALANCE, (number,)).fetchone()


def update_funds(connection, balance, number):
    with connection:
        connection.execute(UPDATE_FUNDS, (balance, number))


def add_funds(connection, balance, number):
    with connection:
        connection.execute(ADD_FUNDS, (balance, number))


def get_all_accounts(connection):
    with connection:
       return connection.execute(GET_ALL_ACCOUNTS).fetchall()


def check_account_exists(connection, number):
    with connection:
        return connection.execute(CHECK_ACCOUNT_BY_NUMBER, (number,)).fetchone()


def check_login(connection, number, pin):
    with connection:
        return connection.execute(CHECK_LOGIN_EXISTS, (number, pin)).fetchone()


def delete_account(connection, number):
    with connection:
        connection.execute(DELETE_ACCOUNT, (number,))

connection = connect()
create_tables(connection)
# a = get_all_accounts(connection)
# print(a)
# cur = connection.cursor()
# cur.execute(DROP_TABLE)



while True:
    print("")
    print("1. Create an account")
    print("2. Log into an account")
    print("0. Exit")
    print("")
    choose_option = int(input("Choose an option: "))

    # create

    if choose_option == 1:

        class Account:
            accounts = {}

            def __init__(self, acc_num, acc_pin_num):
                self.acc_num = acc_num
                self.acc_pin_num = acc_pin_num
                Account.accounts[self.acc_num] = self.acc_pin_num

        test_account = Account(random.randint(100000000, 999999999), random.randint(1000,9999))

        # Luhn Algorithm for Checksum (Last number on Card Number)

        bank_id = 400000 

        acc_bin = str(bank_id) + str(test_account.acc_num)

        acc_bin2 = []

        for index, num in enumerate(acc_bin):
            if index % 2 != 0:
                acc_bin2.append(int(num))
            else:
                n2 = int(num) * 2
                if n2 > 9:
                    n3 = n2 - 9
                    acc_bin2.append(int(n3))
                else:
                    acc_bin2.append(int(n2))
    
        checksum = 0

        sum_accbin = sum(acc_bin2)
        total_accbin = sum_accbin + checksum

        while total_accbin % 10 != 0:
            checksum += 1
            total_accbin = sum_accbin + checksum

        # CARD NUMBER
        card_num = str(bank_id) + str(test_account.acc_num) + str(checksum)
        # PIN NUMBER
        pin_num = test_account.acc_pin_num
        # ADD TO DATABASE
        add_account(connection, card_num, pin_num)
        connection.commit()

        print("Your card has been created")
        print("Your card number:")
        print(card_num)
        print("Your card PIN:")
        print(pin_num)

    # login

    elif choose_option == 2:
        login_card_num = input("Enter your card number:")
        login_pin_num = int(input("Enter your PIN:"))

      
        if check_login(connection, login_card_num, login_pin_num) == False:    
            print("Wrong card number or PIN!")

        else:
            print("You have successfully logged in!")
            while True:
                print("")
                print("1. Balance")
                print("2. Add income")
                print("3. Do transfer")
                print("4. Close account")
                print("5. Log out")
                print("0. Exit")
                print("")

                choose_option2 = int(input("Choose an option: "))
    
    # show balance
                if choose_option2 == 1:
                    balance = show_balance(connection, login_card_num)
                    connection.commit()
                    print(f'Balance: {balance}')

    # add funds
                elif choose_option2 == 2:
                    add_funds_input = int(input("Enter income:"))
                    add_funds(connection, add_funds_input, login_card_num)
                    connection.commit()
                    print("Income was added!")

    # transfer
                elif choose_option2 == 3:
                    enter_card_input = (input("Enter card number:"))
                    
                    #luhn check

                    acc_bin3 = []

                    for index, num in enumerate(enter_card_input):
                        if index % 2 != 0:
                            acc_bin3.append(int(num))
                        else:
                            n2 = int(num) * 2
                            if n2 > 9:
                                n3 = n2 - 9
                                acc_bin3.append(int(n3))
                            else:
                                acc_bin3.append(int(n2))
            
                    sum_accbin = sum(acc_bin3)
                    
                    if sum_accbin % 10 == 0:
                        if check_account_exists(connection, enter_card_input):
                            if enter_card_input == login_card_num:
                                print("You can't transfer money to the same account!")
                            else:
                                transfer_amt = int(input("Enter how much money you want to transfer:"))
                                balance = show_balance(connection, login_card_num)
                                connection.commit()
                                balance_sum = sum(balance)
                                if transfer_amt > balance_sum:
                                    print("Not enough money!")
                                else:
                                    new_balance = balance_sum - transfer_amt
                                    transferee_balance = transfer_amt + sum(show_balance(connection, enter_card_input))
                                    update_funds(connection, new_balance, login_card_num)
                                    update_funds(connection, transferee_balance, enter_card_input)
                                    connection.commit()
                                    print("Success!")
                        else:
                            print("Such a card does not exist.")                        
                    else:
                        print("Probably you made mistake in card number. Please try again!")

    # close account
                elif choose_option2 == 4:
                    delete_account(connection, login_card_num)    
                    print("The account has been closed!")
                    break
    # logout            
                elif choose_option2 == 5:
                    print("You have successfully logged out!")
                    break
    # exit                
                elif choose_option2 == 0:
                    print("Bye!")
                    exit()
    
    # exit
    elif choose_option == 0:
        print("Bye!")
        exit()

    