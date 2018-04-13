import requests
import json
import re
from datetime import datetime, timedelta
import getpass
import urllib

# Define the constants
SERVER = 'http://directory.pythonanywhere.com'
HEADER = {"content-type": "application/json"}
session = requests.Session()


def paymentOptions():

    # Display the options
    print("\n-----------------------\n")
    print("  1. Login")
    print("  2. Register")
    print("  3. Create an account")
    print("  4. Deposit")
    print("  5. Transfer")
    print("  6. Display balance")
    print("  7. Create invoice")
    print("  8. Pay invoice")
    print("  9. Statement")
    print(" 10. Logout\n")
    print(" 11. Go to the main menu")
    print("  0. Exit")


    # Get the input
    while True:
        select = raw_input("\nChoose an option: ")

        # Check if the input is valid
        try:
            if int(select) <= 11 and int(select) >= 0:
                break

            print("Please enter a valid input.")

        # Catch any exception
        except Exception, e:
            print("Please enter a valid input.")

    # If we want to exit
    if int(select) == 0:
        exit()
    
    # Return the option
    return int(select)



def loginData():

    # Get the username and password of the user
    username = ""
    password = ""

    while True:
        username = raw_input("Username: ")
        password = getpass.getpass()

        # Check that the input is valid
        if username == "" or password == "":
            print("Input not valid.")

        else:
            break

    return {"username": username, "password": password}



def getRegisterDetails():

    print("\nCustomer details\n")

    data = {}
    while True:
        
        # Get the input
        data["first_name"] = raw_input("First name: ")
        data["surname"] = raw_input("Surname: ")
        data["email"] = raw_input("Email: ")
        data["phone"] = raw_input("Phone number: ")
        data["username"] = raw_input("Username: ")
        data["password"] = getpass.getpass()
        data["customer_type"] = raw_input("Type of customer (Personal or Business): ")

        # Verify the input
        try:

            data["customer_type"] = data["customer_type"].lower()
            if len(data["first_name"]) > 1 and len(data["surname"]) > 1 and len(data["phone"]) > 7 and \
                re.match(r"[^@]+@[^@]+\.[^@]+", data["email"]) and len(data["username"]) > 1 and \
                len(data["password"]) > 1 and \
                (data["customer_type"] == "business" or data["customer_type"] == "personal"):

                return data


            else:
                print("Please enter a valid input.")

        except Exception, e:
            print("Please enter a valid input.")

    return data



def depositData():

    data = {}
    while True:
        
        # Get the input
        data["amount"] = raw_input("Amount: ")
        data["account_num"] = raw_input("Account number: ")

        # Verify the input
        try:

            data["amount"] = int(data["amount"])
            if len(data["account_num"]) > 1 and data["amount"] > 0:

                return data


            else:
                print("Please enter a valid input.")

        except Exception, e:
            print("Please enter a valid input.")

    return data



def transferData():

    data = {}
    while True:
        
        # Get the input
        data["amount"] = raw_input("Amount: ")
        data["from_account_num"] = raw_input("From account number: ")
        data["to_account_num"] = raw_input("To account number: ")

        # Verify the input
        try:

            data["amount"] = int(data["amount"])
            if len(data["from_account_num"]) > 1 and len(data["to_account_num"]) > 1 and data["amount"] > 0:

                return data


            else:
                print("Please enter a valid input.")

        except Exception, e:
            print("Please enter a valid input.")

    return data



def createInvoiceData():
    
    data = {}
    while True:
        
        # Get the input
        data["account_num"] = raw_input("To account number: ")
        data["client_ref_num"] = raw_input("Client reference number: ")
        data["amount"] = raw_input("Amount: ")

        # Verify the input
        try:

            data["amount"] = int(data["amount"])
            if len(data["account_num"]) > 1 and len(data["client_ref_num"]) > 1 and data["amount"] > 0:

                return data


            else:
                print("Please enter a valid input.")

        except Exception, e:
            print("Please enter a valid input.")

    return data



def payInvoiceData():
    
    data = {}
    while True:
        
        # Get the input
        data["payprovider_ref_num"] = raw_input("Payprovider reference number: ")
        data["client_ref_num"] = raw_input("Client reference number: ")
        data["amount"] = raw_input("Amount: ")

        # Verify the input
        try:

            data["amount"] = int(data["amount"])
            if len(data["payprovider_ref_num"]) > 1 and len(data["client_ref_num"]) > 1 and data["amount"] > 0:

                return data


            else:
                print("Please enter a valid input.")

        except Exception, e:
            print("Please enter a valid input.")

    return data



def statementData():
    
    data = {}
    while True:
        
        # Get the input
        data["account_num"] = raw_input("Account number: ")

        # Verify the input
        try:

            if len(data["account_num"]) > 1:

                return data

            else:
                print("Please enter a valid input.")

        except Exception, e:
            print("Please enter a valid input.")

    return data



def paymentManager(choice, company):

    # Login
    if choice == 1:

        # Send the request
        data = loginData()
        response = session.post(company["url"] + "/api/login/", data=urllib.urlencode(data),
            headers={"content-type": "application/x-www-form-urlencoded"})

        # If the request is successful
        if response.status_code == 200:
            print("\nYou are logged in!")

        # If the request is not successful
        else:
            print("\nLogin error")



    # Register
    elif choice == 2:
        
        data = getRegisterDetails()
        response = session.post(company["url"] + "/api/register/", data=json.dumps(data), headers=HEADER)

        # If the request is successful
        if response.status_code == 201:
            print("\nRegister successful")

        # If the request is not successful
        else:
            print("\nRegister error")



    # Create an account
    elif choice == 3:
        
        response = session.post(company["url"] + "/api/newaccount/")

        # If the request is successful
        if response.status_code == 201:
            print(response.text)

        # If the request is not successful
        else:
            print("\nCreate account error")
            print("You need to be logged in")



    # Deposit
    elif choice == 4:
        
        data = depositData()
        response = session.post(company["url"] + "/api/deposit/", data=json.dumps(data), headers=HEADER)

        # If the request is successful
        if response.status_code == 201:
            
            # Display the result
            deposit = json.loads(response.text)
            print("\n _________________________\n|")
            print("| Account number {}".format(deposit["account_num"]))
            print("| Balance: {}".format(deposit["balance"]))
            print("|__________________________\n")

        # If the request is not successful
        else:
            print("\nDeposit error")
            print("You need to be logged in")



    # Transfer
    elif choice == 5:
        
        data = transferData()
        response = session.post(company["url"] + "/api/transfer/", data=json.dumps(data), headers=HEADER)

        # If the request is successful
        if response.status_code == 201:

            # Display the result
            transfer = json.loads(response.text)
            print("\n ______________________________________________________________\n|")
            print("| Account number from which the money was taken from {}".format(transfer["account_num"]))
            print("| Balance: {}".format(transfer["balance"]))
            print("|_______________________________________________________________\n")

        # If the request is not successful
        else:
            print("\nTransfer error")
            print("You need to be logged in")



    # Display balance
    elif choice == 6:
        
        response = session.get(company["url"] + "/api/balance/")

        # If the request is successful
        if response.status_code == 200:

            # Display the result
            balance = json.loads(response.text)

            for account in balance["accounts"]:

                print("\n _______________________________________\n|")
                print("| Account number {}".format(account["account_num"]))
                print("| Balance: {}".format(account["balance"]))
                print("|_________________________________________\n")

        # If the request is not successful
        else:
            print("\nBalance error")
            print("You need to be logged in")



    # Create invoice
    elif choice == 7:
        
        data = createInvoiceData()
        response = session.post(company["url"] + "/api/createinvoice/", data=json.dumps(data), headers=HEADER)
        print(response.status_code)
        # If the request is successful
        if response.status_code == 201:

            # Display the result
            invoice = json.loads(response.text)
            print("\n ______________________________________________________________\n|")
            print("| Reference number {}".format(invoice["payprovider_ref_num"]))
            print("| Stamp code: {}".format(invoice["stamp_code"]))
            print("|_______________________________________________________________\n")

        # If the request is not successful
        else:
            print("\nInvoice error")
            print("You need to be logged in")



    # Pay invoice
    elif choice == 8:
        
        data = payInvoiceData()
        response = session.post(company["url"] + "/api/payinvoice/", data=json.dumps(data), headers=HEADER)

        # If the request is successful
        if response.status_code == 201:

            # Display the result
            invoice = json.loads(response.text)
            print("\n ______________________________________________________________\n|")
            print("| Stamp code: {}".format(invoice["stamp_code"]))
            print("|_______________________________________________________________\n")

        # If the request is not successful
        else:
            print("\nInvoice error")
            print("You need to be logged in")



    # Statement
    elif choice == 9:

        data = statementData()
        response = session.get(company["url"] + "/api/statement/", data=json.dumps(data), headers=HEADER)

        # If the request is successful
        if response.status_code == 201:

            # Display the result
            statement = json.loads(response.text)

            for s in statement["transactions"]:

                print("\n ______________________________________________________________\n|")
                print("| Transaction date: {}".format(s["date"]))
                print("| Reference number: {}".format(s["reference"]))
                print("| Amount: {}".format(s["amount"]))
                print("|_______________________________________________________________\n")

        # If the request is not successful
        else:
            print("\nStatement error")
            print("You need to be logged in")



    # Logout
    elif choice == 10:
        
        response = session.post(company["url"] + "/api/logout/")

        # If the request is successful
        if response.status_code == 200:
            print("You are now logged out")

        # If the request is not successful
        else:
            print("Logout error")