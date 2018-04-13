import requests
import json
import re
from datetime import datetime, timedelta
import getpass
import urllib

# Define the constants
SERVER = 'http://directory.pythonanywhere.com'
HEADER = {"content-type": "application/json"}



"""
Function used to welcome the user and choose what to do
    RETURNS: Integer representing the option selected
"""
def airlineOptions():

    # Display the options
    print("\n-------------------------")
    print(" 1. Check a booking status")
    print(" 2. Cancel a booking\n")
    print(" 3. Go to the main menu")
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
    
    # Return the option
    return int(select)



"""
Function used to get the details of a flight
    RETURNS:    The details as a dictionary
"""
def getFlightDetails():
    
    print("\nDetails of the flight\n")

    requestData = {}
    while True:
        
        # Get the input
        requestData["dep_airport"] = raw_input("Departure Airport: ")
        requestData["dest_airport"] = raw_input("Destination Airport: ")
        requestData["dep_date"] = raw_input("Departure Date (Eg: 2018-02-20): ")
        requestData["num_passengers"] = raw_input("Number of passengers: ")
        requestData["is_flex"] = raw_input("Is the date flexible ? [Y/N]: ")

        # Verify the input
        try:

            if len(requestData["dep_airport"]) > 1 and len(requestData["dest_airport"]) > 1 and \
                re.match(r"20\d{2}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])", requestData["dep_date"]) and \
                int(requestData["num_passengers"]) > 0 and \
                (requestData["is_flex"].lower() == "y" or requestData["is_flex"].lower() == "n"):

                # Assign the values
                requestData["num_passengers"] = int(requestData["num_passengers"])

                if requestData["is_flex"].lower() == "y":
                    requestData["is_flex"] = True
                else:
                    requestData["is_flex"] = False

                # Return the data
                return requestData

            else:
                print("Please enter a valid input.")

        except Exception, e:
            print("Please enter a valid input.")


    return requestData



"""
Function used to get the list of airlines available
    RETURNS:    The list of airlines
"""
def airlineList():

    # Request the list of Airlines
    response = requests.get(SERVER + "/api/list/", data=json.dumps({ "company_type": "airline" }), headers=HEADER)

    # If the request is successful
    if response.status_code == 200:
        responseData = json.loads(response.text)
        return responseData


    # If the response is not successful
    else:
        print(response.text)
        return None



"""
Function used to search a flight
    ARGUMENTS:  The request data
    RETURNS:    The number of flights found and the details of the flights as a dictionary
"""
def searchFlight(requestData):

    # Get the list of Airlines
    airlines = airlineList()

    if airlines == None:
        return 0, None

    flights = []

    # Get the flights
    for airline in airlines["company_list"]:

        # Sends the request
        response = requests.get(airline["url"] + "/api/findflight/", data=json.dumps(requestData), headers=HEADER)

        try:
            responseData = json.loads(response.text)

            # Add the url and company code
            for flight in responseData["flights"]:
                flight["url"] = airline["url"]
                flight["company_code"] = airline["company_code"]

            # Add the flights to the list
            flights += responseData["flights"]

        except Exception:
            pass


    # If we have found flights
    if len(flights) > 0:

        print("{} flight(s) have been found.".format(len(flights)))
        index = 1

        # Shows the details of each flight
        for row in flights:

            print(" _________________________________________________________________________")
            print("|\n|\tFlight {}\n|".format(index))
            print("|\tFlight number: {}".format(row["flight_num"]))
            print("|\tCompany: {}".format(row["company_code"]))
            print("|\tTakes off from {} at {}.".format(row["dep_airport"], row["dep_datetime"]))
            print("|\tLands in {} at {}.".format(row["dest_airport"], row["arr_datetime"]))
            print("|\tFlight duration: {} hours.".format(row["duration"]))
            print("|\tPrice per seat: {}".format(row["price"]))
            print("|__________________________________________________________________________\n")

            index += 1


        # Returns the data
        return index, flights


    # Error
    else:
        print("No flight found.")
        return 0, None



"""
Function used to pick a flight
    ARGUMENTS:  Number Of Flights and flights data
    RETURNS:    The data of the selected flight
"""
def pickFlight(numberOfFlights, data):

    # PICK FLIGHT
    while True:

        select = raw_input("Select a flight or enter \"exit\" to cancel: ")

        # If the user want to stop the process
        if select == "exit":
            exit()

        # Check if the input is valid
        try:
            if int(select) <= numberOfFlights and int(select) > 0:
                break

            print("Please enter a valid input.")

        # Catch any exception
        except Exception, e:
            print("Please enter a valid input.")

    # Return the selected flight details
    return data[int(select) - 1]



"""
Function used to book a flight
    ARGUMENTS:  The flight and the passengers details
    RETURNS:    The booking number and the total price 
"""
def bookFlight(flight, passengers):

    # Send the request
    requestData = {}
    requestData["flight_id"] = flight["flight_id"]
    requestData["passengers"] = passengers

    response = requests.post(flight["url"] + "/api/bookflight/", data=json.dumps(requestData), headers=HEADER)

    # If the request is successfull
    if response.status_code == 201:

        # Read the JSON data
        booking = json.loads(response.text)

        # Display the information
        print(" _________________________________________________________________________")
        print("|\n|\tBooking number {}\n|".format(booking["booking_num"]))
        print("|\tAirline company code: {}".format(flight["company_code"]))
        print("|\tBooking status: {}".format(booking["booking_status"]))
        print("|\tTotal price: {}".format(booking["tot_price"]))
        print("|__________________________________________________________________________\n")
        
        return booking["booking_num"], booking["tot_price"]

    # Error
    else:

        print(response.text)
        return None



"""
Function used to get the passengers details
    ARGUMENTS:  Number of passengers
    RETURNS:    The list of passengers details
"""
def getPassengersDetails(numberOfPassengers):

    passengers = []

    for x in range(numberOfPassengers):

        while True:

            # Get the input
            print("\n-----------------------------------------------------\n")
            print("Passenger " + str(x+1))
            firstName = raw_input("First name: ")
            surname = raw_input("Surname: ")
            email = raw_input("Email: ")
            phone = raw_input("Phone number: ")

            # Check that the input is valid
            if len(firstName) > 1 and len(surname) > 1 and len(phone) > 7 and \
                re.match(r"[^@]+@[^@]+\.[^@]+", email):

                # Add the passenger to the list
                currentPassenger = {}
                currentPassenger["first_name"] = firstName
                currentPassenger["surname"] = surname
                currentPassenger["email"] = email
                currentPassenger["phone"] = phone
                passengers.append(currentPassenger)

                break

            # Error in the data
            print("\nInput error: The information provided is not valid!")

    print("\n-----------------------------------------------------\n")
    return passengers



"""
Function used to get the booking data
    RETURNS:    The booking number
"""
def getBookingData():

    # Get the data
    number = raw_input("\nEnter your booking number: ")

    # Verify the data
    while len(number) != 6:
        print("Error: booking number invalid.")
        number = raw_input("\nEnter your booking number: ")

    return number



"""
Function used to get the booking status
    ARGUMENT:   company   The company details
"""
def bookingStatus(company):
    
    # Get the booking data
    number = getBookingData()

    # Create the json data
    data = json.dumps({"booking_num": number})

    # Send the request
    response = requests.get(company["url"] + "/api/bookingstatus/", data=data, headers=HEADER)

    # If the request is successful
    if response.status_code == 200:
        
        # Display the booking details
        booking = json.loads(response.text)

        print(" _________________________________________________________________________")
        print("|\n|\tBooking number: {}".format(booking["booking_num"]))
        print("|\tFlight number: {}".format(booking["flight_num"]))
        print("|\tBooking status: {}".format(booking["booking_status"]))
        print("|\tTakes off from {} at {}.".format(booking["dep_airport"], booking["dep_datetime"]))
        print("|\tLands in {} at {}.".format(booking["dest_airport"], booking["arr_datetime"]))
        print("|\tFlight duration: {} hours.".format(booking["duration"]))
        print("|__________________________________________________________________________\n")


    # If the request is not successful
    else:
        print(response.text)



"""
Function used to cancel a booking
    ARGUMENT:   company   The company details
"""
def cancelBooking(company):

    # Get the booking data
    number = getBookingData()

    # Create the json data
    data = json.dumps({"booking_num": number})

    # Send the request
    response = requests.post(company["url"] + "/api/cancelbooking/", data=data, headers=HEADER)

    # If the request is successful
    if response.status_code == 201:
        
        # Display the booking details
        booking = json.loads(response.text)

        print(" _________________________________________________________________________")
        print("|\n|\tBooking number: {}".format(booking["booking_num"]))
        print("|\tBooking status: {}".format(booking["booking_status"]))
        print("|__________________________________________________________________________")


    # If the request is not successful
    else:
        print(response.text)



"""
Function used to get the list of payment providers
    ARGUMENTS:  The url of the flight company
    RETURNS:    The payment provider selected
"""
def selectPaymentProvider(url):

    # Request the list of payment providers
    response = requests.get(url + "/api/paymentmethods/")

    # Parse JSON data
    providers = json.loads(response.text)

    # Show the list
    print(" _________________________________________________________________________\n|")
    print("| Payment providers available:")
    index = 1

    for row in providers["pay_providers"]:
        
        print("|\t{}. {}".format(index, row["pay_provider_name"]))
        index += 1

    print("|__________________________________________________________________________\n")


    # Select a provider
    while True:

        select = raw_input("Select a payment provider or enter \"exit\" to cancel: ")

        # If the user want to stop the process
        if select == "exit":
            exit()

        # Check if the input is valid
        try:
            return providers["pay_providers"][int(select) - 1]

        # Catch any exception
        except Exception, e:
            print("Please enter a valid input.")



"""
Function used to pay for a booking
    ARGUMENTS:  The booking number, the Payment Provider ID, the total price and the flight data
"""
def payForBooking(bookingNumber, paymentProvider, totalPrice, flight):

    # Send the request to create an invoice
    data = json.dumps({"booking_num": bookingNumber, "pay_provider_id": paymentProvider["pay_provider_id"]})
    response = requests.post(flight["url"] + "/api/payforbooking/", data=data, headers=HEADER)

    # If the request is successful
    if response.status_code == 201:
        
        # Parse the JSON data
        invoiceData = json.loads(response.text)

        # Get the username and password of the user
        username = ""
        password = ""
        print("\nPlease login")

        while True:
            username = raw_input("Username: ")
            password = getpass.getpass()

            # Check that the input is valid
            if username == "" or password == "":
                print("Input not valid.")

            else:
                break

        # Send the request
        session = requests.Session()
        data = {"username": username, "password": password}
        response = session.post(invoiceData["url"] + "/api/login/", data=urllib.urlencode(data), 
            headers={"content-type": "application/x-www-form-urlencoded"})

        # If the request is successful
        if response.status_code == 200:
            
            # Pay the invoice
            data = json.dumps({
                    "payprovider_ref_num": invoiceData["invoice_id"],
                    "client_ref_num": invoiceData["booking_num"],
                    "amount": totalPrice
                })
            response = session.post(invoiceData["url"] + "/api/payinvoice/", data=data, headers=HEADER)

            # If the request is successful
            if response.status_code == 201:
                
                # Get the stamp
                stamp = json.loads(response.text)["stamp_code"]

                # Finalize the booking
                data = json.dumps({
                        "booking_num": bookingNumber,
                        "pay_provider_id": paymentProvider,
                        "stamp": stamp
                    })
                response = session.post(flight["url"] + "/api/finalizebooking/", data=data, headers=HEADER)

                # If the request is successful
                if response.status_code == 201:

                    # Display that booking successful
                    print("\nThe booking {} has been paid successfully.".format(bookingNumber))

                # If the request is not successful
                else:
                    print(response.text)

            # If the request is not successful
            else:
                print(response.text)

        # If the request is not successful
        else:
            print(response.text)

    # If the request is not successful
    else:
        print(response.text)