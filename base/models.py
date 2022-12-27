from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # null =True because alrdy has user here, dw conflict in database?
    name = models.CharField(max_length=200, null=True)
    email = models.EmailField(unique=True, null=True)
    bio = models.TextField(null=True)

    avatar = models.ImageField(null = True, default="avatar.svg")

    USERNAME_FIELD = 'email'
    # REQUIRED_FIELDS must contain all required fields on your user model, but should not contain the USERNAME_FIELD or password as these fields will always be prompted for.
    REQUIRED_FIELDS = []



# Create your models here.

class Topic(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Room(models.Model):
   
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    #blank = True is for the saving of the form when the form is blank
    description = models.TextField(null=True, blank=True)
    # The related_name attribute specifies the name of the reverse relation from the User model back to your model.
    participants = models.ManyToManyField(User, related_name='participants', blank=True)

    #everytime the save method is called, go ahead and take the timestamp
    updated = models.DateTimeField(auto_now=True)
    #take timestamp when first create
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        # specify ordering, most recently updated first then created
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.name


class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # delete all message in the room if the room is deleted
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        # specify ordering, most recently updated first then created
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.body[0:50]