from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from .models import *

class RatingForm(forms.ModelForm):
    rate = forms.IntegerField()
    class Meta:
        model = Review
        fields = (
            "rate", "comment"
        )

    def save(self):
        review = super().save(commit=False)
        return review

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['hotel_name','number', 'address',  'room_include', 'images', 'capacity', 'numberOfBeds', 'roomType', 'price', 'discount']

    
class editRoom(ModelForm):
    class Meta:
        model = Room
        fields = ['hotel_name','number', 'address',  'room_include', 'images', 'capacity', 'numberOfBeds', 'roomType', 'price', 'discount']


class editBooking(ModelForm):
    class Meta:
        model = Booking
        fields = ["startDate", "endDate"]


class editDependees(ModelForm):
    class Meta:
        model = Dependees
        fields = ["booking", "name"]
