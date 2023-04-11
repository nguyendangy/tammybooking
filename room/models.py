from django.db import models
from django.utils import timezone
from multiselectfield import MultiSelectField

from accounts.models import Guest
from django.db.models import Avg, Count

# Create your models here.

def upload_room_images(instance,filename):
    return "Room/Images/{room}/{filename}/".format(room=instance.room,filename=filename)


def upload_cover_image(instance,filename):
    return "Room/cover/{id}/{filename}/".format(id=instance.id,filename=filename)

class Room(models.Model):
    ROOM_TYPES = (
        ('King', 'King'),
        ('Luxury', 'Luxury'),
        ('Normal', 'Normal'),
        ('Economic', 'Economic'),

    )

    ROOM_ADDRESS = (
        ('Ha Noi','Ha Noi'),
        ('Da Nang','Da Nang'),
        ('Ho Chi Minh','Ho Chi Minh'),
    )

    ROOM_INCLUDE = (
        ('Breakfast','Breakfast'),
        ('Bar','Bar'),
        ('Free WiFi','Free WiFi'),
        ('Room service','Room service'),
        ('Private Bathroom','Private Bathroom'),
    )
    
    number = models.IntegerField(primary_key=True)
    capacity = models.SmallIntegerField()
    numberOfBeds = models.SmallIntegerField()
    # roomType = models.CharField(max_length=20, choices=ROOM_TYPES)
    roomType = models.TextField(max_length=20,choices=ROOM_TYPES)

    price = models.FloatField()
    statusStartDate = models.DateField(null=True)
    statusEndDate = models.DateField(null=True)
    address = models.CharField(max_length=20, choices=ROOM_ADDRESS)
    hotel_name = models.CharField(max_length=20)
    # rate = models.FloatField(default=0.0)
    # comment = models.TextField( default='')
    # room_include = MultiSelectField(choices=ROOM_INCLUDE,max_choices=3, max_length=20)
    room_include = MultiSelectField( max_length=30, choices=ROOM_INCLUDE,)

    #discount percent
    discount = models.FloatField(default=0.0)

    # cover_image = models.ImageField(upload_to =upload_room_images, blank=False )
    images = models.ImageField(upload_to='room_images/', blank=True)

    # def price_discount_percent(seft):

    #     return (seft.price_discount/seft.price) * 100
    
    def discounted_price(self):
        if self.discount:
            return float(self.price * (100 - self.discount) / 100)
        else:
            return self.price

    def average_rating(self):
        return self.reviews.aggregate(Avg('rate'))['rate__avg']

    def averagereview(self):
        review = Review.objects.filter(room=self).aggregate(avarage=Avg('rate'))
        avg=0
        if review["avarage"] is not None:
            avg=float(review["avarage"])
        return avg



    def countreview(self):
        reviews = Review.objects.filter(room=self).aggregate(count=Count('id'))
        cnt=0
        if reviews["count"] is not None:
            cnt = int(reviews["count"])
        return cnt
    
    def get_average_rating(self):
        return self.reviews.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0.0

    def get_review_count(self):
        return self.reviews.count()

    def __str__(self):
        return str(self.number)
    
# class Room_image(models.Model):
#     room = models.ForeignKey(Room, on_delete=models.CASCADE)
#     image = models.ImageField(upload_to='room_images/')
#     image_url = models.CharField(max_length=255, null=True, blank=True)




class Booking(models.Model):
    roomNumber = models.ForeignKey(Room, on_delete=models.CASCADE)
    guest = models.ForeignKey(Guest, null=True, on_delete=models.CASCADE)
    dateOfReservation = models.DateField(default=timezone.now)
    startDate = models.DateField()
    endDate = models.DateField()
    has_reviewed = models.BooleanField(default=False)

    def numOfDep(self):
        return Dependees.objects.filter(booking=self).count()

    def numOfBooking(self):
        return Booking.objects.filter(guest=self).count()
        # return self.bookings_set.filter(guest=self).count()

    def numOfDays(self):
        totalDay = 0
        bookings = Booking.objects.filter(guest=self)
        # bookings = self.bookings_set.filter(guest=self)
        for b in bookings:
            day = b.endDate - b.startDate
            totalDay += int(day.days)

        return totalDay

    def numOfLastBookingDays(self):
        try:
            return int((Booking.objects.filter(guest=self).last().endDate - Booking.objects.filter(guest=self).last().startDate).days)
            # return int((self.bookings_set.filter(guest=self).last().endDate - self.bookings.filter(guest=self).last().startDate).days)
        except:
            return 0

    def currentRoom(self):
        booking = Booking.objects.filter(guest=self).last()
        # booking = self.bookings.filter(guest=self).last()

        return booking.roomNumber

    def __str__(self):
        return str(self.roomNumber) + " " + str(self.guest)


class Dependees(models.Model):
    booking = models.ForeignKey(Booking,   null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def str(self):
        return str(self.booking) + " " + str(self.name)


class Refund(models.Model):
    guest = models.ForeignKey(Guest,   null=True, on_delete=models.CASCADE)
    reservation = models.ForeignKey(Booking, on_delete=models.CASCADE)
    reason = models.TextField()

    def __str__(self):
        return str(self.guest)


class RoomServices(models.Model):
    SERVICES_TYPES = (
        ('Food', 'Food'),
        ('Drink', 'Drink'),
        ('Cleaning', 'Cleaning'),
        ('Technical', 'Technical'),
    )

    curBooking = models.ForeignKey(
        Booking,   null=True, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    createdDate = models.DateField(default=timezone.now)
    servicesType = models.CharField(max_length=20, choices=SERVICES_TYPES)
    price = models.FloatField()

    def str(self):
        return str(self.curBooking) + " " + str(self.room) + " " + str(self.servicesType)
    
class Review(models.Model):
    user = models.ForeignKey(Guest, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='reviews')
    booking = models.ForeignKey(Booking, null=True, on_delete=models.CASCADE)

    subject = models.CharField(max_length = 100, null=True, blank=True)
    comment = models.TextField(max_length=250, null=True, blank=True)
    rate = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.room) + " " + str(self.comment)+ " " + str(self.user)+ " " + str(self.booking)

# class Room_image(models.Model):
#     # room=room=models.ForeignKey(Room,on_delete=models.SET_NULL,null=True,blank=True)
#     # image=models.ImageField(null=True ,blank=True)
#     room = models.ForeignKey(Room, on_delete=models.CASCADE ,related_name='room_images')
#     room_image = models.ImageField(upload_to=upload_room_images,null=False, blank=False)
  
    # def __str__(self):
    #     return str(self.room)