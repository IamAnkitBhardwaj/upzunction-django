from django.core.management.base import BaseCommand
from django.utils import timezone
from social.models import Post

class Command(BaseCommand):
    help = 'Finds and deactivates all posts that have passed their expiration time.'

    def handle(self, *args, **kwargs):
        now = timezone.now()
        # Find all active posts where the expiration time is in the past
        expired_posts = Post.objects.filter(is_active=True, expires_at__lte=now)
        
        count = expired_posts.count()
        if count > 0:
            # Deactivate them
            expired_posts.update(is_active=False)
            self.stdout.write(self.style.SUCCESS(f'Successfully deactivated {count} expired post(s).'))
        else:
            self.stdout.write(self.style.SUCCESS('No expired posts found to deactivate.'))