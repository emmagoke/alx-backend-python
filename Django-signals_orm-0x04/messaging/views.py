from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages

from .models import Message


@login_required
def delete_user_account(request):
    """
    Handles the user account deletion process.

    On a GET request, it displays a confirmation page.
    On a POST request, it deletes the user and all associated data,
    logs them out, and redirects to the homepage.
    """
    if request.method == 'POST':
        user = request.user
        # The post_delete signal on the User model will handle data cleanup.
        # We store the username to display it after deletion.
        username = user.username
        
        # Logout the user before deleting the account to invalidate the session
        logout(request)
        
        # Delete the user object
        user.delete()
        
        messages.success(request, f"Account for '{username}' has been successfully deleted.")
        return redirect('home') # Assumes you have a 'home' URL name in your project's root urls.py

    return render(request, 'messaging/delete_account_confirm.html')


@login_required
def view_thread(request, pk):
    """
    Displays a message and its entire reply thread.
    Uses a recursive CTE to fetch the whole thread in one query
    and prefetch_related to optimize access to related objects.
    Ensures the requesting user is part of the conversation.
    """
    # Get the root message of the thread, ensuring the current user is a participant.
    root_message = get_object_or_404(
        Message, 
        Q(pk=pk),
        Q(sender=request.user) | Q(receiver=request.user)
    )
    
    # A recursive CTE to fetch the entire message thread
    # This requires PostgreSQL, Oracle, or SQLite 3.25+ with CTE support.
    thread_cte = Message.objects.filter(pk=root_message.pk).ctes(
        'thread_cte',
        initial_term=Message.objects.filter(pk=root_message.pk),
        recursive_term=lambda cte: Message.objects.filter(parent_message=cte)
    )

    # Fetch all messages in the thread using the CTE
    thread_messages = (
        Message.objects.filter(pk__in=thread_cte)
        .select_related('sender', 'receiver')
        .prefetch_related('replies')
        .order_by('timestamp')
    )
    
    # Structure the messages into a nested dictionary for the template
    message_map = {msg.pk: msg for msg in thread_messages}
    for msg in thread_messages:
        if msg.parent_message_id:
            parent = message_map.get(msg.parent_message_id)
            if parent:
                if not hasattr(parent, 'child_replies'):
                    parent.child_replies = []
                parent.child_replies.append(msg)

    # The final list contains only the root-level message for this thread view
    # The template will recursively render the children
    display_thread = [msg for msg in thread_messages if msg.pk == root_message.pk]

    return render(request, 'messaging/thread_view.html', {'thread_messages': display_thread})
