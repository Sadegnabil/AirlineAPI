from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.http import JsonResponse
from django.core import serializers
from airline.models import *
import json
import datetime
import random
import string
import requests
from urllib.parse import urlencode


# Constants
CHARS = string.ascii_uppercase + string.digits
HEADER = {"content-type": "application/json"}


"""
Function used to create a 503 Service Unavailable response
Takes a message as parameter
"""
def unavailableReponse(message):
    response = HttpResponse(message)
    response.status_code = 503
    response.content_type = "text/plain"
    return response



"""
Find a flight from a departure airport to a destination airport at some departure date.
The client sends a GET request to /api/findflight/.

JSON data:
    1. Departure airport ("dep_airport", string)
    2. Destination airport ("dest_airport", string)
    3. Departure date ("dep_date", string)
    4. Number of passengers ("num_passengers", number)
    5. A Boolean value indicating whether the departure date is exact or flexible ("is_flex" ,
    true or false)

If the request is processed successfully, the server responds with 200 OK and a list of flights in a JSON
payload:
    1. Flight identifier that uniquely identifies a flight on a certain date ("flight_id", string)
    2. Flight number ("flight_num" , string)
    3. Departure airport ("dep_airport", string)
    4. Destination airport ("dest_airport", string)
    5. Departure date and time ("dep_datetime", string)
    6. Arrival date and time ("arr_datetime", string)
    7. Flight duration ("duration" , string)
    8. Seat price for one passenger ("price" , number)

If no flights are found, the server responds with 503 Service Unavailable with text/plain payload
giving reason.
"""
def findFlight(request):

    # Check that we have a GET request
    if request.method == "GET":

        # Parse the JSON data
        requestData = json.loads(request.body.decode('utf-8'))

        # Find the flights with the right airports
        query = Flight.objects.filter(
            departureAirport__name=requestData["dep_airport"],
            destinationAirport__name=requestData["dest_airport"]
        )

        # If we don't have any result for the query
        if len(query) == 0:
            return unavailableReponse("No flight found from {} to {}.".format(requestData["dep_airport"],
                requestData["dest_airport"]))

        # Filter the one that have the right date
        results = []
        for row in query:
            add = False

            # If it is the exact day
            if row.departureTime.strftime("%Y-%m-%d") == requestData["dep_date"]:
                add = True

            # Add close dates if it is flexible
            elif requestData["is_flex"]:
                if (row.departureTime - datetime.timedelta(days=1)).strftime("%Y-%m-%d") == requestData["dep_date"] or \
                    (row.departureTime + datetime.timedelta(days=1)).strftime("%Y-%m-%d") == requestData["dep_date"]:

                    add = True


            # If we need to add it
            if add:

                # Create the entry
                entry = {}
                entry["flight_id"] = row.id
                entry["flight_num"] = row.number
                entry["dep_airport"] = Airport.objects.filter(name=requestData["dep_airport"]).values()[0]["name"]
                entry["dest_airport"] = Airport.objects.filter(name=requestData["dest_airport"]).values()[0]["name"]
                entry["dep_datetime"] = row.departureTime
                entry["arr_datetime"] = row.arrivalTime
                entry["duration"] = str(row.duration)
                entry["price"] = row.price
                results.append(entry)


        # If there is no flight available
        if len(results) == 0:
            return unavailableReponse("No flight found for this date.")

        # Return JSON data
        return JsonResponse({"flights": results})

    # Return 503 Service Unavailable
    return unavailableReponse("Error processing the request.")



"""
Book a flight given by its unique identifier.
POST request to /api/bookflight/.

JSON data:
    1. Flight unique identifier ("flight_id", string)
    2. A list of passengers ("passengers" , array) with the following details about each
        - First name ("first_name", string)
        - Surname ("surname" , string)
        - email ("email", string)
        - phone number ("phone", string)

If the request is processed successfully, the server responds with 201 CREATED and a JSON payload:
    1. Booking number ("booking_num", string)
    2. Booking status ("booking_status", string) = "ON_HOLD"
    3. Total price for this booking ("tot_price", number)

If a booking cannot be made for any reason, the server responds with 503 Service Unavailable with
text/plain payload giving reason.
"""
@csrf_exempt
def bookFlight(request):

    # Check that we have a POST request
    if request.method == "POST":

        # Parse the JSON data
        requestData = json.loads(request.body.decode('utf-8'))


        # Generate the booking number
        number = ''.join(random.choice(CHARS) for _ in range(6))

        while Booking.objects.filter(number=number).count() > 0:
            number = ''.join(random.choice(CHARS) for _ in range(6))


        # Create the booking
        booking = Booking(number=number,
            flight=Flight.objects.filter(id=requestData["flight_id"])[0],
            numberOfSeats=len(requestData["passengers"]),
            status="ONHOLD",
            expiration=datetime.datetime.now() + datetime.timedelta(days=1))

        booking.save()

        # Add the passengers
        for passenger in requestData["passengers"]:
            currentPassenger = Passenger(firstName=passenger["first_name"],
                surname=passenger["surname"], email=passenger["email"],
                phoneNumber=passenger["phone"])
            currentPassenger.save()
            booking.passengers.add(currentPassenger)

        booking.save()

        responseData = {}
        responseData["booking_num"] = booking.number
        responseData["booking_status"] = booking.status
        responseData["tot_price"] = booking.flight.price * booking.numberOfSeats

        # Return JSON data
        return JsonResponse(responseData, status=201)

    # Return 503 Service Unavailable
    return unavailableReponse("Error processing the request.")



"""
Request Payment Methods
GET request to /api/paymentmethods/.

If the request is processed successfully, the server responds with 200 OK and a list of payment service
providers in a JSON payload:
    1. The provider's unique identifier in the airline's database ("pay_provider_id", string)
    2. Provider name ("pay_provider_name", string)

If no providers are available, the server responds with 503 Service Unavailable with text/plain
payload giving reason.
"""
def paymentMethods(request):

    # Check that we have a GET request
    if request.method == "GET":

        # Create the response data
        responseData = []
        for provider in PaymentProvider.objects.all():

            responseData.append({  "pay_provider_id": provider.id,
                                    "pay_provider_name": provider.name
                                })

        # If there is no payment provider
        if len(responseData) == 0:
            return unavailableReponse("No payment provider available.")

        # Return JSON data
        return JsonResponse(responseData, safe=False)

    # Return 503 Service Unavailable
    return unavailableReponse("Error processing the request.")



"""
Pay for a Booking
POST request to /api/payforbooking/.

JSON data:
    1. Booking number ("booking_num", string)
    2. Payment provider identifier ("pay_provider_id", string)

If the request is processed successfully, the server responds with 201 CREATED and a JSON payload:
    1. Payment provider identifier ("pay_provider_id", string)
    2. Payment provider’s invoice unique id ("invoice_id", string)
    3. Booking number ("booking_num", string)
    4. The provider’s website address (“url” , string)

If the server is unable to process the request for any reason, the server responds with a 503 Service
Unavailable with text/plain payload giving reason.
"""
@csrf_exempt
def payForBooking(request):

    # Check that we have a POST request
    if request.method == "POST":

        # Parse the JSON data
        requestData = json.loads(request.body.decode('utf-8'))


        # Send a request to the Payment Service provider
        paymentProvider = PaymentProvider.objects.get(id=int(requestData["pay_provider_id"]))
        booking = Booking.objects.get(number=requestData["booking_num"])
        address = paymentProvider.address
        data = json.dumps({
            "account_num": paymentProvider.accountNumber,
            "client_ref_num": requestData["booking_num"],
            "amount": booking.numberOfSeats * booking.flight.price
            })

        session = requests.Session()
        response = session.post(address + "api/login/", 
            data=urlencode({"username": paymentProvider.login, "password": paymentProvider.password}), 
            headers={"content-type": "application/x-www-form-urlencoded"})

        response = session.post(address + "api/createinvoice/", data=data, headers=HEADER)

        # If the response is successful
        if response.status_code == 201:

            # Parse JSON data
            paymentProviderInvoice = json.loads(response.text)


            # Create the invoice in the database
            airlineInvoice = Invoice(airlineReferenceNumber=requestData["booking_num"],
                paymentProviderReferenceNumber=paymentProviderInvoice["payprovider_ref_num"],
                amount=booking.numberOfSeats * booking.flight.price, isPaid=False,
                stamp=paymentProviderInvoice["stamp_code"])

            airlineInvoice.save()


            # Create the response data
            responseData = {
                "pay_provider_id": requestData["pay_provider_id"],
                "invoice_id": paymentProviderInvoice["payprovider_ref_num"],
                "booking_num": requestData["booking_num"],
                "url": address
            }


            # Return JSON data
            return JsonResponse(responseData, status=201)


        # If the response is not successful
        if response.status_code == 503:
            return unavailableReponse("Error processing the request.")

    # Return 503 Service Unavailable
    return unavailableReponse("Error processing the request.")



"""
Service Aim: Finalize a Booking
POST request to /api/finalizebooking/.

JSON data:
    1. Booking number ("booking_num", string)
    2. Payment provider identifier ("pay_provider_id", string)
    3. Payment provider electronic stamp ("stamp", string)

If the request is processed successfully, the server responds with 201 CREATED and a JSON payload:
    1. Booking number ("booking_num", string)
    2. Booking status ("booking_status", string) = "CONFIRMED"

If the server is unable to process the request for any reason, the server responds with a 503
Service Unavailable with text/plain payload giving reason.
"""
@csrf_exempt
def finalizeBooking(request):

    # Check that we have a POST request
    if request.method == "POST":

        # Parse the JSON data
        requestData = json.loads(request.body.decode('utf-8'))

        # Compare the stamps
        invoice = Invoice.objects.get(airlineReferenceNumber=requestData["booking_num"])
        if requestData["stamp"] == invoice.stamp:

            # Update the invoice
            invoice.isPaid = True
            invoice.save()

            # Update the booking
            booking = Booking.objects.get(number=requestData["booking_num"])
            booking.status = "CONFIRMED"
            booking.save()

            # Return JSON data
            return JsonResponse({"booking_num": booking.number, "booking_status": booking.status},
                                    status=201)

        # If the stamps are different
        else:
            return unavailableReponse("Error processing the request.")

    # Return 503 Service Unavailable
    return unavailableReponse("Error processing the request.")



"""
Service Aim: Provide Booking Status
GET request to /api/bookingstatus/.

JSON data:
    1. Booking number ("booking_num", string)

If the request is processed successfully, the server responds with 200 OK and a JSON payload:
    1. Booking number ("booking_num", string)
    2. Booking status ("booking_status", string)
    3. Flight number ("flight_num" , string)
    4. Departure airport ("dep_airport", string)
    5. Destination airport ("dest_airport", string)
    6. Departure date and time ("dep_datetime", string)
    7. Arrival date and time ("arr_datetime", string)
    8. Flight duration ("duration" , string)

If the server is unable to process the request for any reason, the server responds with a 503
Service Unavailable with text/plain payload giving reason.
"""
def bookingStatus(request):

    # Check that we have a GET request
    if request.method == "GET":

        # Parse the JSON data
        requestData = json.loads(request.body.decode('utf-8'))

        # Get the booking
        try:
            booking = Booking.objects.get(number=requestData["booking_num"])

            # Format the data
            bookingData = {}
            bookingData["booking_num"] = booking.number
            bookingData["booking_status"] = booking.status
            bookingData["flight_num"] = booking.flight.number
            bookingData["dep_airport"] = booking.flight.departureAirport.country + \
                                         " (" + booking.flight.departureAirport.name + ")"
            bookingData["dest_airport"] = booking.flight.destinationAirport.country + \
                                         " (" + booking.flight.destinationAirport.name + ")"
            bookingData["dep_datetime"] = booking.flight.departureTime.strftime("%Y-%m-%d %H:%M")
            bookingData["arr_datetime"] = booking.flight.arrivalTime.strftime("%Y-%m-%d %H:%M")
            bookingData["duration"] = str(booking.flight.duration)[:-3]


            # Return JSON data
            return JsonResponse(bookingData)

        # If the booking doesn't exit
        except Exception as e:
            return unavailableReponse("The booking {} doesn't exist.".format(requestData["booking_num"]))

    # Return 503 Service Unavailable
    return unavailableReponse("Error processing the request.")



"""
Service Aim: Cancel a Booking
POST request to /api/cancelbooking/.

JSON data:
    Booking number ("booking_num", string)

If the request is processed successfully, the server responds with 201 CREATED and a JSON payload:
    1. Booking number ("booking_num", string)
    2. Booking status ("booking_status", string) = "CANCELLED"

If the server is unable to process the request for any reason, the server responds with a 503
Service Unavailable with text/plain payload giving reason.
"""
@csrf_exempt
def cancelBooking(request):

    # Check that we have a POST request
    if request.method == "POST":

        # Parse the JSON data
        requestData = json.loads(request.body.decode('utf-8'))

        # Get the booking
        try:
            booking = Booking.objects.get(number=requestData["booking_num"])

            if booking.status == "CANCELLED":
                return unavailableReponse("The booking {} is already cancelled.".format(requestData["booking_num"]))

            booking.status = "CANCELLED"
            booking.save()

            # Return JSON data
            return JsonResponse({"booking_num": booking.number, "booking_status": booking.status}, status=201)

        # If the booking doesn't exit
        except Exception as e:
            return unavailableReponse("The booking {} doesn't exist.".format(requestData["booking_num"]))

    # Return 503 Service Unavailable
    return unavailableReponse("Error processing the request.")