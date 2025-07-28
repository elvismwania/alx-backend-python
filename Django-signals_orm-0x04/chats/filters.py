

import django_filters
from .models import Message



class MessageFilter(django_filters.FilterSet):
    timestamp_after = django_filters.DateTimeFilter(field_name='timestamp', lookup_expr='gte')
    timestamp_before = django_filters.DateTimeFilter(field_name='timestamp', lookup_expr='lte')

    class Meta:
        model = Message
        fields = ['conversation', 'timestamp_after', 'timestamp_before']
