from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone
import datetime
from .models import Location, Post, Message, DailyVisit, Profile

# --- 1. EXISTING CONFIGURATION (Preserved) ---

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'city')

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    # Preserving your specific list display and filters
    list_display = ('title', 'author', 'location', 'is_active', 'created_at', 'expires_at')
    list_filter = ('is_active', 'location', 'location__city')
    search_fields = ('title', 'description', 'author__username')

    # Preserving your specific queryset logic to see all posts
    def get_queryset(self, request):
        return Post.objects.all()

    # ADDED: Actions for management (Activate/Deactivate)
    actions = ['deactivate_posts', 'activate_posts']

    @admin.action(description='Deactivate selected posts')
    def deactivate_posts(self, request, queryset):
        queryset.update(is_active=False)

    @admin.action(description='Activate selected posts')
    def activate_posts(self, request, queryset):
        queryset.update(is_active=True)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('post', 'sender', 'recipient', 'sent_at')
    search_fields = ('body', 'sender__username', 'recipient__username')


# --- 2. NEW ADDITIONS FOR CUSTOM DASHBOARD & USER MANAGEMENT ---

# Unregister default User to replace with CustomUserAdmin
admin.site.unregister(User)

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile Info'

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline, )
    list_display = ('username', 'email', 'is_active', 'date_joined')
    list_filter = ('is_active', 'date_joined')
    actions = ['block_users', 'unblock_users']

    @admin.action(description='BLOCK selected users (Ban)')
    def block_users(self, request, queryset):
        # Setting is_active to False prevents login
        rows_updated = queryset.update(is_active=False)
        self.message_user(request, f"{rows_updated} user(s) blocked.")

    @admin.action(description='UNBLOCK selected users (Activate)')
    def unblock_users(self, request, queryset):
        rows_updated = queryset.update(is_active=True)
        self.message_user(request, f"{rows_updated} user(s) unblocked.")

@admin.register(DailyVisit)
class DailyVisitAdmin(admin.ModelAdmin):
    list_display = ('date', 'count')

# Custom Admin Site Class (The Dashboard Logic)
class UpzunctionAdminSite(admin.AdminSite):
    site_header = "Upzunction Management Console"
    site_title = "Upzunction Admin"
    index_title = "Business Intelligence Dashboard"

    def index(self, request, extra_context=None):
        # --- A. GATHER DATA ---
        today = timezone.now().date()
        
        # 1. Visitor Stats
        today_visit_obj = DailyVisit.objects.filter(date=today).first()
        visits_today = today_visit_obj.count if today_visit_obj else 0
        
        # 2. User Stats
        total_users = User.objects.count()
        
        # 3. Post Stats
        active_posts = Post.objects.filter(is_active=True).count()

        # --- B. AI / PREDICTIVE LOGIC ---
        
        # Prediction: Linear Growth
        # Logic: Calculate posts from last 7 days to predict next week's load
        last_7_days = timezone.now() - datetime.timedelta(days=7)
        recent_posts_count = Post.objects.filter(created_at__gte=last_7_days).count()
        # Simple heuristic: We expect 20% growth on current weekly trend
        predicted_new_posts = int(recent_posts_count * 1.2) 

        # Analysis: Market Activity Level
        # Logic: If many messages are sent recently, the market is "Hot"
        recent_messages = Message.objects.filter(sent_at__gte=last_7_days).count()
        if recent_messages > 50:
            market_status = "High Demand"
        elif recent_messages > 10:
            market_status = "Moderate"
        else:
            market_status = "Low / Quiet"

        # --- C. PASS DATA TO TEMPLATE ---
        extra_context = extra_context or {}
        extra_context['dashboard_stats'] = {
            'visits_today': visits_today,
            'total_users': total_users,
            'active_posts': active_posts,
            'predicted_new_posts': predicted_new_posts,
            'market_status': market_status,
        }
        return super().index(request, extra_context)

# Instantiate our custom admin
upzunction_admin = UpzunctionAdminSite(name='upzunction_admin')

# Register models to the CUSTOM admin site instance so they appear in the new dashboard
upzunction_admin.register(User, CustomUserAdmin)
upzunction_admin.register(Group)
upzunction_admin.register(Location, LocationAdmin)
upzunction_admin.register(Post, PostAdmin)
upzunction_admin.register(Message, MessageAdmin)
upzunction_admin.register(DailyVisit, DailyVisitAdmin)