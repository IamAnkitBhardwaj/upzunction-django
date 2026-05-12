from django.contrib import admin
from .models import Bhandara

@admin.register(Bhandara)
class BhandaraAdmin(admin.ModelAdmin):
    list_display = ('area_name', 'business_name', 'is_approved', 'is_verified_owner', 'current_crowd_status', 'start_time')
    list_filter = ('is_approved', 'is_verified_owner', 'is_active', 'current_crowd_status')
    search_fields = ('area_name', 'business_name', 'organizer_name', 'menu_details')
    
    # Custom bulk actions
    actions = ['approve_bhandaras', 'verify_owners']

    def approve_bhandaras(self, request, queryset):
        queryset.update(is_approved=True)
    approve_bhandaras.short_description = "Mark selected as Approved (Go Live)"

    def verify_owners(self, request, queryset):
        queryset.update(is_verified_owner=True)
    verify_owners.short_description = "Give selected the Blue Tick"