from django.forms import ModelForm
from django import forms
from django.contrib.auth.models import User
from .models import *

class RatingForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rate'].required = True
        self.fields['trip_date'].required = True
        self.fields['subject'].required = True
        self.fields['comment'].required = True

    images = forms.ImageField(widget=forms.ClearableFileInput(attrs={'multiple': True}), required=False)
    subject = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Write title your review'} ), label= "Title review:")

    class Meta:
        model = Review
        fields = (
            "rate","trip_date", "subject", "comment", 
        )
        widgets = {
            "comment": forms.Textarea(attrs={"rows": 4,"placeholder": "Write your review"})
        }
        labels = {
        "comment": "Your review",
        }

        label_suffix = ' <span class="font-size-22px">*</span>'

    rate = forms.IntegerField(
        widget=forms.RadioSelect(attrs={'class': ''}, choices=[(1, '★☆☆☆☆'),
                                                               (2, '★★☆☆☆'),
                                                               (3, '★★★☆☆'),
                                                               (4, '★★★★☆'),
                                                               (5, '★★★★★'),]),
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        label='How would you rate your experience?'
       
    )

    def save(self, commit=True):
        instance = super(RatingForm, self).save(commit=False)
        
        if self.cleaned_data.get('images'):
            for image in self.cleaned_data.get('images'):
                review_image = ReviewImage(review=instance, image=image)
                review_image.save()
                
        return instance

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['hotel_name', 'number', 'address',  'room_include', 'images',
                  'capacity', 'numberOfBeds', 'roomType', 'price', 'discount']


class editRoom(ModelForm):
    class Meta:
        model = Room
        fields = ['hotel_name', 'number', 'address',  'room_include', 'images',
                  'capacity', 'numberOfBeds', 'roomType', 'price', 'discount']


class editBooking(ModelForm):
    class Meta:
        model = Booking
        fields = ["startDate", "endDate"]


class editDependees(ModelForm):
    class Meta:
        model = Dependees
        fields = ["booking", "name"]
