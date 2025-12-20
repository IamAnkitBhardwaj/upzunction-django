# social/models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import datetime
from django.db.models.signals import post_save
from django.dispatch import receiver


class Location(models.Model):
    name = models.CharField(max_length=100) # e.g., Jankipuram, Gomti Nagar
    city = models.CharField(max_length=100, default="Lucknow")

    def __str__(self):
        return f"{self.name}, {self.city}"

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    location = models.ForeignKey("Location", on_delete=models.SET_NULL, null=True, blank=True)
    is_location_specific = models.BooleanField(default=False, help_text="Check this if the post is ONLY for the selected location.")
    
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    whatsapp_number = models.CharField(max_length=15, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        # Automatically set the expiration date on creation
        if not self.id:
            # THIS LINE IS NOW CHANGED TO 7 DAYS
            self.expires_at = timezone.now() + datetime.timedelta(days=7)
        super(Post, self).save(*args, **kwargs)

    def __str__(self):
        return f"'{self.title}' by {self.author.username}"


class Message(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages")
    body = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    sender_phone = models.CharField(max_length=15, blank=True, null=True)
    recipient_phone_on_approval = models.CharField(max_length=15, blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    def __str__(self):
        status = "Approved" if self.is_approved else "Pending"
        return f"Message from {self.sender.username} to {self.recipient.username} on '{self.post.title}' [{status}]"

    def __str__(self):
        return f"Message from {self.sender.username} to {self.recipient.username} on '{self.post.title}'"
    


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} Profile'
    

# --- NEW ANALYTICS MODEL ---
class DailyVisit(models.Model):
    date = models.DateField(auto_now_add=True, unique=True)
    count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.date}: {self.count}"

# This is a signal: it automatically creates a Profile whenever a new User is created.
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()