from .models import DailyVisit
from django.utils import timezone

class VisitorTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Count visits only for real pages (exclude admin and static files)
        if not request.path.startswith('/admin') and not request.path.startswith('/static'):
            today = timezone.now().date()
            # Get the counter for today, or create it if it's a new day
            visit_obj, created = DailyVisit.objects.get_or_create(date=today)
            visit_obj.count += 1
            visit_obj.save()

        response = self.get_response(request)
        return response