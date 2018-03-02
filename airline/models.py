from django.db import models


# Aircraft model used to define an aircraft
class Aircraft(models.Model):
    type = models.CharField(max_length=20, default="unknown")
    registrationNumber = models.CharField(primary_key=True, default="unknown", max_length=10)
    seats = models.IntegerField(default=0)


# Airport model used to define an airport
class Airport(models.Model):
    name = models.CharField(primary_key=True, max_length=30, default="unknown")
    country = models.CharField(max_length=20, default="unknown")
    timeZone = models.CharField(max_length=20, default="unknown")


# Flight model used to give the details of a filght
class Flight(models.Model):
    number = models.CharField(max_length=6, default="unknown")
    departureAirport = models.ForeignKey(Airport, related_name="departure", null=True, on_delete=models.SET_NULL)
    destinationAirport = models.ForeignKey(Airport, related_name="destination", null=True, on_delete=models.SET_NULL)
    departureTime = models.DateTimeField(null=True)
    arrivalTime = models.DateTimeField(null=True)
    duration = models.DurationField()
    aircraft = models.ForeignKey(Aircraft, null=True, on_delete=models.SET_NULL)
    price = models.FloatField(default=0)


# Passenger model used to hold the details of a passenger
class Passenger(models.Model):
    firstName = models.CharField(max_length=30, default="unknown")
    surname = models.CharField(max_length=30, default="unknown")
    email = models.EmailField()
    phoneNumber = models.CharField(max_length=15, default="unknown")


# Booking model used create a booking
class Booking(models.Model):
    number = models.CharField(primary_key=True, max_length=6, default="unknown")
    flight = models.ForeignKey(Flight, null=True, on_delete=models.SET_NULL)
    numberOfSeats = models.IntegerField(default=0)
    passengers = models.ManyToManyField(Passenger)
    status = models.CharField(max_length=9, default="unknown")
    expiration = models.DateTimeField()
    

# Payment provider model used to hold the details to login into a payment provider
class PaymentProvider(models.Model):
    name = models.CharField(max_length=20, default="unknown")
    address = models.URLField()
    accountNumber = models.CharField(max_length=30, default="unknown")
    login = models.CharField(max_length=20, default="unknown")
    password = models.CharField(max_length=20, default="unknown")


# Invoice model used to define an invoice
class Invoice(models.Model):
    airlineReferenceNumber = models.CharField(primary_key=True, max_length=6, default="unknown")
    paymentProviderReferenceNumber = models.CharField(max_length=10, default="unknown")
    amount = models.FloatField(default=0)
    isPaid = models.BooleanField(default=False)
    stamp = models.CharField(max_length=20, default="unknown")