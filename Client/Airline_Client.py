import requests
import json
import re
from datetime import datetime, timedelta
import getpass
from airline import *
from payment import *

# Define the constants
SERVER = 'http://directory.pythonanywhere.com'
HEADER = {"content-type": "application/json"}



"""
Function used to welcome the user and choose what to do
Returns an int representing the option selected
"""
def greetings():

    # Display the options
    print("\n** Main menu **\n")

    print(" 1. Access a specific company")
    print(" 2. Search for a flight")
    print(" 0. Exit")


    # Get the input
    while True:
        select = raw_input("\nChoose an option: ")

        # Check if the input is valid
        try:
            if int(select) <= 2 and int(select) >= 0:
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



"""
Function used to get the list of companies
"""
def companiesList():

    print("\n-------------------------")
    print("Select a company type\n")
    print(" 1. Airlines")
    print(" 2. Payment providers")
    print(" 3. All")
    print(" 0. Exit")


    # Get the input
    while True:
        select = raw_input("\nChoose an option: ")

        # Check if the input is valid
        try:
            if int(select) <= 3 and int(select) >= 0:
                break

            print("Please enter a valid input.")

        # Catch any exception
        except Exception, e:
            print("Please enter a valid input.")

    # If we want to exit
    if int(select) == 0:
        exit()

    choice = int(select)
    
    # Airline companies
    if choice == 1:
        response = requests.get(SERVER + "/api/list/", data=json.dumps({ "company_type": "airline" }), headers=HEADER)

    # Payment providers companies
    elif choice == 2:
        response = requests.get(SERVER + "/api/list/", data=json.dumps({ "company_type": "payment" }), headers=HEADER)

    # All companies
    elif choice == 3:
        response = requests.get(SERVER + "/api/list/", data=json.dumps({ "company_type": "*" }), headers=HEADER)

    # Successful request
    if response.status_code == 200:
        companies = json.loads(response.text)

        # Display the list of companies
        i = 1
        print(" ______________________________________________________\n|")
        for c in companies["company_list"]:
            print("| {}. {} {}".format(i, c["company_name"], c["company_code"]))
            i += 1
        print("|______________________________________________________\n")


        # Get the input
        while True:
            select = raw_input("\nChoose an option: ")

            # Check if the input is valid
            try:
                if int(select) <= i and int(select) >= 1:
                    break

                print("Please enter a valid input.")

            # Catch any exception
            except Exception, e:
                print("Please enter a valid input.")

        # Return the selected company
        return companies["company_list"][int(select) - 1]


    # If there is an error
    else:
        print("Error loading the list of companies")
        return None





"""
Main function of the client
"""
def main():

    while True:

        # Get the first choice
        choice = greetings()

        # If the user wants to access a specific company
        if choice == 1:

            # Select a company
            company = companiesList()

            # Error selecting the company
            if company == None:
                print("Error selecting a company")

            # If it is an Airline
            if company["company_type"] == "airline":

                while True:

                    # Select an option
                    choice = airlineOptions()

                    # If the user wants to check the status of a booking
                    if choice == 1:

                        print("\n-------------------------------------------")
                        bookingStatus(company)
                        print("\n-------------------------------------------")


                    # If the user wants to cancel a flight
                    elif choice == 2:

                        print("\n-------------------------------------------")
                        cancelBooking(company)
                        print("\n-------------------------------------------")

                    # Go to the main menu
                    elif choice == 3:
                        break


            # If it is a Payment provider
            elif company["company_type"] == "payment":

                while True:

                    # Prompt the user
                    choice = paymentOptions()

                    # Go to the main menu
                    if choice == 11:
                        break

                    # Do what the user wants
                    else:
                        paymentManager(choice, company)


        # If the user wants to search for a flight
        elif choice == 2:

            print("\n-------------------------------------------")

            # Gets the search details
            requestData = getFlightDetails()

            # Search for a flight
            numberOfFlights, data = searchFlight(requestData)

            # If we have found flights we can continue
            if numberOfFlights > 0:
                
                # The user picks a flight
                flight = pickFlight(numberOfFlights, data)

                # The user anter the details about the passengers
                passengers = getPassengersDetails(requestData["num_passengers"])

                # Create the booking
                bookingNumber, totalPrice = bookFlight(flight, passengers)
                if bookingNumber != None:
                    
                    # Get the payment provider ID
                    paymentProvider = selectPaymentProvider(flight["url"])

                    # Pay for booking
                    payForBooking(bookingNumber, paymentProvider, totalPrice, flight)


            print("\n-------------------------------------------")


# Start the main function
main()
