from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page  # ✅ import added
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .models import Message

@login_required
def send_message(request, receiver_id):
    receiver = get_object_or_404(User, id=receiver_id)

    if request.method == 'POST':
        content = request.POST.get('content')
        parent_id = request.POST.get('parent_message')
        parent_message = Message.objects.filter(id=parent_id).first() if parent_id else None

        Message.objects.create(
            sender=request.user,
            receiver=receiver,
            content=content,
            parent_message=parent_message
        )
        return redirect('inbox')

    return render(request, 'messaging/send_message.html', {'receiver': receiver})

@cache_page(60)  # ✅ cache for 60 seconds
@login_required
def inbox(request):
    messages = (
        Message.objects
        .filter(receiver=request.user, parent_message__isnull=True)
        .select_related('sender', 'receiver', 'edited_by')
        .prefetch_related('replies')
        .order_by('-timestamp')
    )
    return render(request, 'messaging/inbox.html', {'messages': messages})


@login_required
def unread_messages(request):
    messages = (
        Message.unread.unread_for_user(request.user)
        .only('id', 'sender', 'content', 'timestamp')
    )
    return render(request, 'messaging/unread.html', {'messages': messages})
