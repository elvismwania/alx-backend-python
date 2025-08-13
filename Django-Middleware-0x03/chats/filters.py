import django_filters
from .models import Message


class MessageFilter(django_filters.FilterSet):
    start_time = django_filters.IsoDateTimeFilter(
        field_name='timestamp', lookup_expr='gte')
    end_time = django_filters.IsoDateTimeFilter(
        field_name='timestamp', lookup_expr='lte')
    sender = django_filters.NumberFilter(field_name='sender__id')
    conversation = django_filters.UUIDFilter(field_name='conversation__id')

    class Meta:
        model = Message
        fields = ['sender', 'conversation', 'start_time', 'end_time']
