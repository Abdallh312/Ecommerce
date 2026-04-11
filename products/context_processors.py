from django.utils import timezone
from django.db.models import Q
from .models import Announcement


def active_announcements(request):
    """Inject active, in-range announcements into every template context."""
    now = timezone.now()
    announcements = Announcement.objects.filter(
        is_active=True,
        start_date__lte=now,
    ).filter(
        Q(end_date__isnull=True) | Q(end_date__gte=now)
    )
    return {'site_announcements': announcements}


def categories_processor(request):
    """Provides root categories and their subcategories for the global navigation."""
    from .models import Category
    return {
        'global_categories': Category.objects.filter(parent__isnull=True).prefetch_related('children')
    }
