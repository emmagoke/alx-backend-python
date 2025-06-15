from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages


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
