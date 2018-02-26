"""AirlineAPI URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from airline.views import findFlight
from airline.views import bookFlight
from airline.views import paymentMethods
from airline.views import payForBooking
from airline.views import finalizeBooking
from airline.views import bookingStatus
from airline.views import cancelBooking



# Define the endpoints paths
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/findflight/', findFlight),
    path('api/bookflight/', bookFlight),
    path('api/paymentmethods/', paymentMethods),
    path('api/payforbooking/', payForBooking),
    path('api/finalizebooking/', finalizeBooking),
    path('api/bookingstatus/', bookingStatus),
    path('api/cancelbooking/', cancelBooking),
]
