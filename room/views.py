# imports
import os
from PIL import Image

from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm

from django.db.models import Q, Count
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import Group, User

from datetime import datetime, date, timedelta
import random
# Create your views here.
from accounts.models import *
from room.models import *
from hotel.models import *
from .forms import *
from django.core.files.storage import FileSystemStorage
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.files.storage import default_storage


@ login_required(login_url='login')
def rooms(request):
    role = str(request.user.groups.all()[0])
    path = role + "/"
    rooms = Room.objects.all()
    firstDayStr = None
    lastDateStr = None

    def chech_availability(fd, ed):
        availableRooms = []
        
        for room in rooms:
            availList = []
            bookingList = Booking.objects.filter(roomNumber=room)
            print("bookingList",bookingList)
            
            if room.statusStartDate == None:
                for booking in bookingList:
                    if booking.startDate > ed.date() or booking.endDate < fd.date():
                        availList.append(True)
                    else:
                        availList.append(False)
                if all(availList):
                    availableRooms.append(room)
            else:
                if room.statusStartDate > ed.date() or room.statusEndDate < fd.date():
                    for booking in bookingList:
                        if booking.startDate > ed.date() or booking.endDate < fd.date():
                            availList.append(True)
                        else:
                            availList.append(False)
                        if all(availList):
                            availableRooms.append(room)
        return availableRooms

    if request.method == "POST":
        if "dateFilter" in request.POST:
            firstDayStr = request.POST.get("fd", "")
            lastDateStr = request.POST.get("ld", "")

            firstDay = datetime.strptime(firstDayStr, '%Y-%m-%d')
            lastDate = datetime.strptime(lastDateStr, '%Y-%m-%d')

            rooms = chech_availability(firstDay, lastDate)

        if "filter" in request.POST:
            if (request.POST.get("number") != ""):
                rooms = rooms.filter(
                    number__contains=request.POST.get("number"))

            if (request.POST.get("capacity") != ""):
                rooms = rooms.filter(
                    capacity__gte=request.POST.get("capacity"))

            if (request.POST.get("nob") != ""):
                rooms = rooms.filter(
                    numberOfBeds__gte=request.POST.get("nob"))

            if (request.POST.get("type") != ""):
                rooms = rooms.filter(
                    roomType__contains=request.POST.get("type"))

            if (request.POST.get("price") != ""):
                rooms = rooms.filter(
                    price__lte=request.POST.get("price"))

            if (request.POST.get("address") != ""):
                rooms = rooms.filter(
                    address__contains=request.POST.get("address"))

            context = {
                "role": role,
                "rooms": rooms,
                "number": request.POST.get("number"),
                "capacity": request.POST.get("capacity"),
                "nob": request.POST.get("nob"),
                "price": request.POST.get("price"),
                "type": request.POST.get("type"),
                "address": request.POST.get("address")
            }
            return render(request, path + "rooms.html", context)

    context = {
        "role": role,
        'rooms': rooms,
        'fd': firstDayStr,
        'ld': lastDateStr
    }
    return render(request, path + "rooms.html", context)

# @receiver(post_save, sender=Room)
# def create_room_images(sender, instance, created, **kwargs):
#     if created:
#         for image in instance.images.all():
#             path = default_storage.save('room_images/' + str(image), image)
#             Room_image.objects.create(room=instance, image=path, image_url=default_storage.url(path))

@login_required(login_url='login')
def add_room(request):
    role = str(request.user.groups.all()[0])
    path = role + "/"

    # if request.method == "POST":
    #     guest = None
    #     if role == 'guest':
    #         guest = request.user.guest
    #     elif role == 'manager' or role == 'admin' or role == 'receptionist':
    #         guest = request.user.employee

    #     # announcement = Announcement(sender = sender, content = request.POST.get('textid'))
        
    #     # room = Room()

    #     number = request.POST.get('number')
    #     capacity = request.POST.get('capacity')
    #     numberOfBeds = request.POST.get('beds')
    #     roomType = request.POST.get('type')
    #     price = request.POST.get('price')
    #     address = request.POST.get('address')
    #     hotel_name = request.POST.get('hotel-name')
    #     room_include = request.POST.get('room-include')
    #     price_discount = request.POST.get('price-discount')
        
    #     # if len(request.FILES['images']) != 0:
    #     # images = request.POST.get('images')

    #     # print(capacity)
    #     room = Room(number=number, capacity=capacity,
    #                 numberOfBeds=numberOfBeds, roomType=roomType, price=price, address = address, hotel_name = hotel_name,room_include=room_include,price_discount=price_discount)
       
    #     if request.FILES.getlist('images'):
    #         images = request.FILES.getlist('images')
    #         for image in images:
    #             fs = FileSystemStorage()
    #             filename = fs.save(image.name, image)
    #             url = fs.url(filename)
    #             room_image = Room_image(room=room, image_url=url)
    #             room_image.save()

    #     room.save()

    #     messages.info(request,'ROOM is saved')

    #     return redirect('rooms')
   
    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES)
        if form.is_valid():
            room = form.save(commit=False)
            if 'images' in request.FILES:
                image = request.FILES['images']
                fs = FileSystemStorage()
                filename = fs.save(image.name, image)
                filepath = fs.path(filename)
                # Resize image if necessary
                img = Image.open(filepath)
                if img.height > 1000 or img.width > 1000:
                    img.thumbnail((1000, 1000))
                    img.save(filepath)
                # Set URL of image file in Room model
                room.images = fs.url(filename)
            room.save()
            messages.success(request, 'Room added successfully.')
            return redirect('rooms')
    else:
        form = RoomForm()

    context = {
        "role": role,
        "form": form
    }
    return render(request, path + "add-room.html", context)

@login_required(login_url='login')
def my_room(request):
    import datetime
    role = str(request.user.groups.all()[0])
    path = role + "/"
    rooms = Room.objects.all()
    bookings = Booking.objects.all()
    # calculating total for every booking:
    totals = {}  # <booking : total>
    for booking in bookings:
        start_date = datetime.datetime.strptime(
            str(booking.startDate), "%Y-%m-%d")
        end_date = datetime.datetime.strptime(str(booking.endDate), "%Y-%m-%d")
        numberOfDays = abs((end_date-start_date).days)
        # get room peice:
        room = Room.objects.get(number=booking.roomNumber.number)
        discounted_price = (room.price  * (100 - room.discount) / 100)
        if room.discount:
            total = discounted_price * numberOfDays
        else:
            total = room.price * numberOfDays
        totals[booking] = total

    context = {
        "role": role,
        'bookings': bookings,
        'rooms': rooms,
        'totals': totals
    }
    return render(request, path + "my-room.html", context)

@login_required(login_url='login')
def hotel_policy(request):
    role = str(request.user.groups.all()[0])
    path = role + "/"
    context = {
        "role": role
    }
    return render(request, path +  "hotel-policy.html", context)

@login_required(login_url='login')
def room_profile(request, pk):
    role = str(request.user.groups.all()[0])
    path = role + "/"
    user = request.user
    print("pk: ", pk)
    tempRoom = Room.objects.get(number=pk)
    curGuest = Guest.objects.get(user=request.user)

    bookings = Booking.objects.filter(roomNumber=tempRoom)
    bookings3 = Booking.objects.filter(roomNumber=tempRoom,guest=curGuest)
    print("bookings3:", bookings3)
    if (bookings3):
        is_reviewed = True
    else: 
        is_reviewed = False
    review = Review.objects.filter(room=tempRoom,user=curGuest,booking=bookings3)
    review_all_user_in_room = Review.objects.filter(room=tempRoom)
    guests = Guest.objects.all()
    context = {
        "is_reviewed": is_reviewed,
        "role": role,
        "bookings": bookings,
        "room": tempRoom,
        "guests": guests,
        "bookings3": bookings3,
        "review":review,
        "reviewalluser":review_all_user_in_room,
        'average_rating': tempRoom.averagereview(),
        'review_count': tempRoom.countreview(),
        # "form": form
    }

    if request.method == "POST":
        if "lockRoom" in request.POST:
            fd = request.POST.get("bsd")
            ed = request.POST.get("bed")
            fd = datetime.strptime(fd, '%Y-%m-%d')
            ed = datetime.strptime(ed, '%Y-%m-%d')
            check = True
            for b in bookings:
                if b.endDate >= fd.date() and b.startDate <= ed.date():
                    check = False
                    break
            if check:
                tempRoom.statusStartDate = fd
                tempRoom.statusEndDate = ed
                tempRoom.save()
            else:
                messages.error(request, "There is a booking in the interval!")
        if "unlockRoom" in request.POST:
            tempRoom.statusStartDate = None
            tempRoom.statusEndDate = None
            tempRoom.save()
        if "deleteRoom" in request.POST:
            check = True
            for b in bookings:
                if b.startDate <= datetime.now().date() or b.endDate >= datetime.now().date():
                    check = False
            if check:
                tempRoom.delete()
                return redirect("rooms")
            else:
                messages.error(request, "There is a booking in the interval!")

    return render(request, path + "room-profile.html", context)

def room_review(request, pk):
    role = str(request.user.groups.all()[0])
    path = role + "/"

    guests = Guest.objects.all()
    curGuest = Guest.objects.get(user=request.user)
    rooms = Room.objects.get(number=pk)
    review = Review.objects.filter(room=rooms, user = curGuest).last()
    reviews = Review.objects.all()


    # subject = request.GET.get('subject')

    # nếu đã đánh giá thì cập nhật, còn chưa thì tạo mới
    if request.method == 'POST':
        if "ratings" in request.POST:
            form = RatingForm(request.POST or None)
            if form.is_valid():
                new_review = form.save()
                new_review.room = rooms
                new_review.user = curGuest
                if review:
                    review.delete()  # delete previous review
                new_review.save()
                return redirect('room-profile',pk=rooms.number)
    else:
        form = RatingForm(instance=review)
    context = {
        "role": role,
        "guests": guests,
        "curGuest": curGuest,
        "rooms":rooms,
        "review":review,
        "reviews":reviews,
        "form": form
    }
    return render(request, path + "room-review.html", context) 

@login_required(login_url='login')
def room_edit(request, pk):
    role = str(request.user.groups.all()[0])
    path = role + "/"

    room = Room.objects.get(number=pk)
    old_image_path = str(room.images)
    print("old_image_path:" , old_image_path)
    # form1 = editRoom(instance=room)
    # form = editRoom(request.POST or None, request.FILES or None, instance=room)
   
    # if form.is_valid():
    #     form.save()
    #     return redirect("room-profile", id=room.number)
    if request.method == 'POST':
        form = editRoom(request.POST, request.FILES, instance=room)
        if form.is_valid():
            room = form.save(commit=False)
            if 'images' in request.FILES:
                # Delete old image
                # if room.images:
                    # fs = FileSystemStorage()
                    # if fs.exists(room.images.name):
                    #     fs.delete(room.images.name)

                # Save new image
                image = request.FILES['images']
                fs = FileSystemStorage()
                filename = fs.save(image.name, image)
                filepath = fs.path(filename)

                # Resize image if necessary
                img = Image.open(filepath)
                if img.height > 1000 or img.width > 1000:
                    img.thumbnail((1000, 1000))
                    img.save(filepath)

                # Update Room object with new image URL
                room.images = fs.url(filename)

            # Save updated Room object to database
            room.save()
            messages.success(request, 'Room updated successfully.')
            return redirect('rooms')
    else:
        form = editRoom(instance=room)
    context = {
        "role": role,
        "room": room,
        "form": form
    }
    return render(request, path + "room-edit.html", context)


@ login_required(login_url='login')
def room_services(request):
    role = str(request.user.groups.all()[0])
    path = role + "/"

    room_services = RoomServices.objects.all()
    context = {
        "role": role,
        "room_services": room_services
    }
    return render(request, path + "room-services.html", context)


@login_required(login_url='login')
def current_room_services(request):
    import datetime

    role = str(request.user.groups.all()[0])
    path = role + "/"

    curGuest = Guest.objects.get(user=request.user)
    curBooking = Booking.objects.filter(guest=curGuest).last()
    if curBooking is not None:
        curRoom = Room.objects.get(number=curBooking.roomNumber.number)
    else:
        context = {
            "role": role,
            "error": "You Don't Have Booking Right Now"
        }
        return render(request, path + "current-room-services.html", context)
    curRoomServices = RoomServices.objects.filter(curBooking=curBooking)

    room_services = RoomServices.objects.all()

    group = Group.objects.get(name='staff')
    users = User.objects.filter(groups=group)
    allEmployees = Employee.objects.filter(user__in=users)
    availableEmployee = list()
    maxTaskNum = 10

    for e in allEmployees:
        counter = 0
        empTasks = Task.objects.filter(employee=e)
        for t in empTasks:
            counter += 1
        if counter < maxTaskNum:
            availableEmployee.append(e)
    print("availableEmployee: ", availableEmployee)
    context = {
        "role": role,
        "room_services": room_services,
        "curGuest": curGuest,
        "curBooking": curBooking,
        "curRoom": curRoom,
        "curRoomServices": curRoomServices
    }

    if request.method == "POST":
        if "foodReq" in request.POST:
            newServiceReq = RoomServices(
                curBooking=curBooking, price=50.0, room=curRoom,  servicesType='Food')
            newServiceReq.save()

            chosenEmp = random.choice(availableEmployee)
            lastTask = Task.objects.filter(employee=chosenEmp).last()
            if(lastTask != None):
                newTask = Task(employee=chosenEmp, startTime=lastTask.endTime,
                               endTime=lastTask.endTime+datetime.timedelta(minutes=30), description="Food Request")
            else:
                newTask = Task(employee=chosenEmp, startTime=datetime.datetime.now(),
                               endTime=datetime.datetime.now()+datetime.timedelta(minutes=30), description="Food Request")
            newTask.save()
            return redirect("current-room-services")
        
        if "drinkReq" in request.POST:
            newServiceReq = RoomServices(
                curBooking=curBooking, price=50.0, room=curRoom,  servicesType='Drink')
            newServiceReq.save()

            chosenEmp = random.choice(availableEmployee)
            lastTask = Task.objects.filter(employee=chosenEmp).last()
            if(lastTask != None):
                newTask = Task(employee=chosenEmp, startTime=lastTask.endTime,
                               endTime=lastTask.endTime+datetime.timedelta(minutes=30), description="Drink Request")
            else:
                newTask = Task(employee=chosenEmp, startTime=datetime.datetime.now(),
                               endTime=datetime.datetime.now()+datetime.timedelta(minutes=30), description="Drink Request")
            newTask.save()
            return redirect("current-room-services")

        if "cleaningReq" in request.POST:
            newServiceReq = RoomServices(
                curBooking=curBooking, price=0.0, room=curRoom,  servicesType='Cleaning')
            newServiceReq.save()
            chosenEmp = random.choice(availableEmployee)
            lastTask = Task.objects.filter(employee=chosenEmp).last()

            if(lastTask != None):
                newTask = Task(employee=chosenEmp, startTime=lastTask.endTime,
                               endTime=lastTask.endTime+datetime.timedelta(minutes=30), description="Cleaning Request")
            else:
                newTask = Task(employee=chosenEmp, startTime=datetime.datetime.now(),
                               endTime=datetime.datetime.now()+datetime.timedelta(minutes=30), description="Cleaning Request")
            newTask.save()
            return redirect("current-room-services")

        if "techReq" in request.POST:
            newServiceReq = RoomServices(
                curBooking=curBooking, price=0.0, room=curRoom,  servicesType='Technical')
            newServiceReq.save()
            chosenEmp = random.choice(availableEmployee)
            lastTask = Task.objects.filter(employee=chosenEmp).last()
            if(lastTask != None):
                newTask = Task(employee=chosenEmp, startTime=lastTask.endTime,
                               endTime=lastTask.endTime+datetime.timedelta(minutes=30), description="Tech Request")
            else:
                newTask = Task(employee=chosenEmp, startTime=datetime.datetime.now(),
                               endTime=datetime.datetime.now()+datetime.timedelta(minutes=30), description="Tech Request")
            newTask.save()
            return redirect("current-room-services")

    return render(request, path + "current-room-services.html", context)


@login_required(login_url='login')
def bookings(request):
    import datetime
    role = str(request.user.groups.all()[0])
    path = role + "/"

    bookings = Booking.objects.all()
    # calculating total for every booking:
    totals = {}  # <booking : total>
    for booking in bookings:
        start_date = datetime.datetime.strptime(
            str(booking.startDate), "%Y-%m-%d")
        end_date = datetime.datetime.strptime(str(booking.endDate), "%Y-%m-%d")
        numberOfDays = abs((end_date-start_date).days)
        # get room peice:
        room = Room.objects.get(number=booking.roomNumber.number)
        discounted_price = (room.price  * (100 - room.discount) / 100)
        if room.discount:
            total = discounted_price * numberOfDays
        else:
            total = room.price * numberOfDays
        totals[booking] = total

    if request.method == "POST":
        if "filter" in request.POST:
            if (request.POST.get("number") != ""):
                rooms = Room.objects.filter(
                    number__contains=request.POST.get("number"))
                bookings = bookings.filter(
                    roomNumber__in=rooms)

            if (request.POST.get("name") != ""):
                users = User.objects.filter(
                    Q(first_name__contains=request.POST.get("name")) | Q(last_name__contains=request.POST.get("name")))
                guests = Guest.objects.filter(user__in=users)
                bookings = bookings.filter(
                    guest__in=guests)

            if (request.POST.get("rez") != ""):
                bookings = bookings.filter(
                    dateOfReservation=request.POST.get("rez"))

            if (request.POST.get("fd") != ""):
                bookings = bookings.filter(
                    startDate__gte=request.POST.get("fd"))

            if (request.POST.get("ed") != ""):
                bookings = bookings.filter(
                    endDate__lte=request.POST.get("ed"))

            context = {
                "role": role,
                'bookings': bookings,
                'totals': totals,
                "name": request.POST.get("name"),
                "number": request.POST.get("number"),
                "rez": request.POST.get("rez"),
                "fd": request.POST.get("fd"),
                "ed": request.POST.get("ed")
            }

            return render(request, path + "bookings.html", context)

    context = {
        "role": role,
        'bookings': bookings,
        'totals': totals
    }
    return render(request, path + "bookings.html", context)


@login_required(login_url='login')
def booking_make(request):
    role = str(request.user.groups.all()[0])
    path = role + "/"

    # room = Room()
    # room.number = request.POST.get('roomid')
    # room.save()
    numbers=request.POST.get('roomid')
    room = Room.objects.get(number=numbers)
    guests = Guest.objects.all()  # we pass this to context
    names = []
    if request.method == 'POST':
        if request.POST.get("fd") == "" or request.POST.get("ld") == "":
            messages.warning(request, "You must choose date!")
            return redirect("rooms")

        start_date = datetime.strptime(
            str(request.POST.get("fd")), "%Y-%m-%d")
        end_date = datetime.strptime(
            str(request.POST.get("ld")), "%Y-%m-%d")
        numberOfDays = abs((end_date-start_date).days)
        # get room peice:
        discounted_price = (room.price  * (100 - room.discount) / 100)
        if room.discount:
            total = discounted_price * numberOfDays
        else:
            total = room.price * numberOfDays

        if 'add' in request.POST:  # add dependee
            name = request.POST.get("depName")
            names.append(name)
            for i in range(room.capacity-2):
                nameid = "name" + str(i+1)
                if request.POST.get(nameid) != "":
                    names.append(request.POST.get(nameid))

        if 'bookGuestButton' in request.POST:
            if "guest" in request.POST:
                curguest = Guest.objects.get(id=request.POST.get("guest"))
            else:
                curguest = request.user.guest
            curbooking = Booking(guest=curguest, roomNumber=room, startDate=request.POST.get(
                "fd"), endDate=request.POST.get("ld"))
            curbooking.has_reviewed = True
            curbooking.save()

            for i in range(room.capacity-1):
                nameid = "name" + str(i+1)
                if request.POST.get(nameid) != "":
                    if request.POST.get(nameid) != None:
                        d = Dependees(booking=curbooking,
                                      name=request.POST.get(nameid))
                        d.save()
            return redirect("payment")

    context = {
        "fd": request.POST.get("fd"),
        "ld": request.POST.get("ld"),
        "role": role,
        "guests": guests,
        "room": room,
        "total": total,
        "names": names
    }

    return render(request, path + "booking-make.html", context)


@login_required(login_url='login')
def deleteBooking(request, pk):
    role = str(request.user.groups.all()[0])
    path = role + "/"

    booking = Booking.objects.get(id=pk)
    if request.method == "POST":
        booking.delete()
        return redirect('bookings')

    context = {
        "role": role,
        'booking': booking

    }
    return render(request, path + "deleteBooking.html", context)


@ login_required(login_url='login')
def refunds(request):
    role = str(request.user.groups.all()[0])
    path = role + "/"

    refunds = Refund.objects.all()
    context = {
        "role": role,
        'refunds': refunds
    }

    if request.method == "POST":
        if "decline" in request.POST or "approve" in request.POST:
            refundId = request.POST.get("refund", "")
            guestUserId = request.POST.get("guestUserId", "")

            tempUser = User.objects.get(id=guestUserId)
            receiver = Guest.objects.get(user=tempUser)

            def send(request, receiver, text, subject):

                message_email = 'bong15042021@gmail.com'
                message = text
                receiver_name = receiver.user.first_name + " " + receiver.user.last_name

                # send email
                send_mail(
                    receiver_name + " " + subject,   # subject
                    message,                          # message
                    message_email,                    # from email
                    [receiver.user.email],                    # to email
                    fail_silently=False,              # for user in users :
                    # user.email
                )

                messages.success(
                    request, 'Feedback E-Mail Was Successfully Sent')

                Refund.objects.filter(id=refundId).delete()
                return render(request, path + "refunds.html", context)

            def send_mail_refund_approved(request, receiver):
                subject = "Refund"
                text = """
                    Dear {guestName},
                    We are pleased to confirm that your refund request has been accepted.
                    The amount of refund will be on your account in 24 hours.
                    This time interval can change up to 48 hours according to your bank.
                    We are very sorry for this inconvenience. We hope to see you soon.
                """
                email_text = text.format(
                    guestName=receiver.user.first_name + " " + receiver.user.last_name)

                send(request, receiver, email_text, subject)

            def send_mail_refund_declined(request, receiver):
                subject = "Refund"
                text = """
                    Dear {guestName},
                    We are sorry to inform you that your refund request has been declined.
                    After our examinations, we see that your request can not be done according to our Hotel Policy.
                    We are very sorry for this inconvenience. We hope to see you soon.
                """
                email_text = text.format(
                    guestName=receiver.user.first_name + " " + receiver.user.last_name)

                send(request, receiver, email_text, subject)

            if "decline" in request.POST:
                send_mail_refund_declined(request, receiver)
            if "approve" in request.POST:
                send_mail_refund_approved(request, receiver)

            refundId = None
            statu = None

        if "filter" in request.POST:
            users = User.objects.all()
            if (request.POST.get("gid") != ""):
                users = users.filter(
                    id__contains=request.POST.get("gid"))
                guests = Guest.objects.filter(user__in=users)
                refunds = refunds.filter(guest__in=guests)

            if (request.POST.get("name") != ""):
                users = users.filter(
                    Q(first_name__contains=request.POST.get("name")) | Q(last_name__contains=request.POST.get("name")))
                guests = Guest.objects.filter(user__in=users)
                refunds = refunds.filter(guest__in=guests)

            if (request.POST.get("booking") != ""):
                booking = Booking.objects.get(id=request.POST.get("booking"))
                refunds = refunds.filter(reservation=booking)

            if (request.POST.get("reason") != ""):
                refunds = refunds.filter(
                    reason__contains=request.POST.get("reason"))

            context = {
                "role": role,
                "refunds": refunds,
                "gid": request.POST.get("gid"),
                "name": request.POST.get("name"),
                "booking": request.POST.get("booking"),
                "reason": request.POST.get("reason")
            }
            return render(request, path + "refunds.html", context)

    return render(request, path + "refunds.html", context)


@login_required(login_url='login')
def request_refund(request):
    role = str(request.user.groups.all()[0])
    path = role + "/"

    curGuest = Guest.objects.get(user=request.user)

    if request.method == "POST":
        if "sendReq" in request.POST:
            reason = request.POST.get("reqExp")
            curBookingId = request.POST.get("bid")
            currentBooking = Booking.objects.get(id=curBookingId)
            temp = Refund.objects.filter(reservation=currentBooking)
            if not temp:
                currentReq = Refund(
                    guest=curGuest, reservation=currentBooking, reason=reason)
                currentReq.save()
                messages.success(
                    request, "Your request was successfully sent.")
            else:
                messages.error(
                    request, "We already have your refund request for this reservation!")

    context = {
        "role": role,
        "curGuest": curGuest,
        "id": request.POST.get("bookingId")
    }

    return render(request, path + "request-refund.html", context)
