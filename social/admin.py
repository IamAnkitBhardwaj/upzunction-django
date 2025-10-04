# social/admin.py

from django.contrib import admin
from .models import Location, Post, Message

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'city')

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    # This shows detailed info in the admin panel as you requested
    list_display = ('title', 'author', 'location', 'is_active', 'created_at', 'expires_at')
    list_filter = ('is_active', 'location', 'location__city')
    search_fields = ('title', 'description', 'author__username')

    # To ensure you can see who posted it, even if the post is inactive
    def get_queryset(self, request):
        # Show all posts, regardless of is_active status
        return Post.objects.all()

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('post', 'sender', 'recipient', 'sent_at')
    search_fields = ('body', 'sender__username', 'recipient__username')