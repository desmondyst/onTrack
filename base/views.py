from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages

from django.contrib.auth.decorators import login_required
from django.db.models import Q

from django.contrib.auth import authenticate, login, logout

from .models import Room, Topic, Message, User
from .forms import RoomForm, UserForm, MyUserCreationForm

# Create your views here.


def loginPage(request):

    page = 'login'

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get("email").lower()
        password = request.POST.get("password")
    
        try:
            user = User.objects.get(email = email)
        except:
            messages.error(request, 'User does not exist')
        
        user = authenticate(request, email=email, password=password)

        # if the user is authenticated
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Password is wrong')


    context = {'page': page}
    return render(request, 'base/login_register.html', context)



def logoutUser(request):
    # deleting the token hence deleting the user
    logout(request)
    return redirect('home')



def registerPage(request):
    page = 'register'
    form = MyUserCreationForm()
    context = {"page": page, "form": form}

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            # Create, but don't save the new author instance.
            # Because we want to edit it for it be lower case
            user = form.save(commit=False)
            user.username = user.username.lower()
            # now then we save the user
            user.save()
            # log the user in
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occurred during registration')

    return render(request, 'base/login_register.html', context)



def home(request):
    # request.GET = A dictionary-like object containing all given HTTP GET parameters.
    q = request.GET.get('q')

    if request.GET.get('q') == None:
        q = ''

    # get the data from the database
    # I think topic__name the __ is the query upwards, on topic.name
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)   
        ) 
    topics = Topic.objects.all()[0:5]
    rooms_count = rooms.count()
    rooms_messages = Message.objects.filter(Q(room__topic__name__icontains=q))


    
    context = {'rooms': rooms, 'topics': topics, 'room_count': rooms_count, 'room_messages': rooms_messages}
    return render(request, 'base/home.html', context)


def room(request, pk):
    room = Room.objects.get(id=pk)

    # Give us the set of messages that is related to this specific room
    # Give us the children messages of this room
    #
    room_messages = room.message_set.all()

    # not set -> see documentation
    participants = room.participants.all()


    # If there is post request from user trying to submit a message using the form
    # in room.html
    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user,
            room=room,
            # whatever this is passed in using the <input> in room.html
            body=request.POST.get('body')
        )
        room.participants.add(request.user)

        # Redirect to prevent post request from messing up
        return redirect('room', pk=room.id)


    context = {'room': room, 'room_messages': room_messages, 'participants': participants}
    return render(request, "base/room.html", context)

def userProfile(request, pk):
    user = User.objects.get(id=pk)
    # use underscore to get all the rooms for the user
    rooms = user.room_set.all()

    room_messages = user.message_set.all()
    topics = Topic.objects.all()

    context = {'user': user, 'rooms': rooms, 'room_messages': room_messages, 'topics': topics}
    return render(request, "base/profile.html", context)

@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        # Returns a tuple of (object, created), where object is the retrieved or created object and created is a boolean specifying whether a new object was created.
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room = Room.objects.create(
            host = request.user,
            topic = topic,
            name = request.POST.get('name'),
            description = request.POST.get('description'),
        )

        room.participants.add(request.user)
        
        # # Passing in all the POST data into the form 
        # form = RoomForm(request.POST)
        # if form.is_valid():
        #     # ModelForm.save() returns the instance of Model that was created/updated by the ModelForm.
        #     # in this case, the form is a room form so it return the room
        #     room = form.save(commit=False)
        #     room.host = request.user
        #     room.save()
        return redirect('home')

    context = {'form': form, 'topics': topics}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    topics = Topic.objects.all()

    # give us empty form, but with the (instance=room) give us a 
    # prefield form with the current values
    form = RoomForm(instance=room)

    if request.user != room.host:
        return HttpResponse('You are not allowed to edit')


    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        # Returns a tuple of (object, created), where object is the retrieved or created object and created is a boolean specifying whether a new object was created.
        topic, created = Topic.objects.get_or_create(name=topic_name)

        # need to tell it what room to update, if not it will 
        # create a new room
        # form = RoomForm(request.POST, instance=room)
        # if form.is_valid():
        #     form.save()

        # update the values
        room.name = request.POST.get('name')
        # either get nearly created topic or from database
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')

    context={'form': form, 'topics': topics, 'room': "room"}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)


    if request.user != room.host:
        return HttpResponse('You are not allowed to delete')

    # POST method means we click confirm
    if request.method == 'POST':
        # remove from database
        room.delete()
        return redirect('home')

    return render(request, 'base/delete.html', {'obj': room})


@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)


    if request.user != message.user:
        return HttpResponse('You are not allowed to delete')

    # POST method means we click confirm
    if request.method == 'POST':
        # remove from database
        message.delete()

        # ownself do one: to remove participants if no longer participant
        # get owner of this message
        owner = message.user
        if not Message.objects.filter(Q(user=owner)):
            message.room.participants.remove(owner)

        # redirection to room is ownself do
        return redirect('room', pk = message.room.id)

    return render(request, 'base/delete.html', {'obj': message})


@login_required(login_url='login')
def updateUser(request):
    user = request.user
    # get the initial value
    form = UserForm(instance=user)

    if request.method == 'POST':
        # request.FILES is for the pictures 
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)

    return render(request, 'base/update-user.html', {'form': form})

def topicsPage(request):
    # request.GET = A dictionary-like object containing all given HTTP GET parameters.
    q = request.GET.get('q')

    if request.GET.get('q') == None:
        q = ''
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, 'base/topics.html', {'topics': topics})

def activityPage(request):
    room_messages = Message.objects.all()
    return render(request, 'base/activity.html', {'room_messages': room_messages})