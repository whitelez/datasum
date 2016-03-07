# code from Tango with Django http://www.tangowithdjango.com/book17/chapters/login.html

from traffic.forms import UserForm
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt

def register(request):

    # A boolean value for telling the template whether the registration was successful.
    # Set to False initially. Code changes value to True when registration succeeds.
    registered = False

    # If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
        # Attempt to grab information from the raw form information.
        # Note that we make use of both UserForm and UserProfileForm.
        user_form = UserForm(data=request.POST)

        # If the two forms are valid...
        if user_form.is_valid():
            # Save the user's form data to the database.
            #user = user_form.save()

            # Now we hash the password with the set_password method.
            # Once hashed, we can update the user object.
            #user.set_password(user.password)
            #user.save()

            # send an email to us for registration
            # email settings are in dataproject/settings.py
            message = 'username:%s\nemail:%s\norgnization:%s\nintended use:%s' %(user_form.cleaned_data['username'],user_form.cleaned_data['email'],user_form.cleaned_data['organization'],user_form.cleaned_data['intended_use'])
            #print message
            send_mail('Registration', message, 'mdap2205@gmail.com', ['mdap2205@gmail.com'], fail_silently = False)

            # Update our variable to tell the template registration was successful.
            registered = True

        # Invalid form or forms - mistakes or something else?
        # Print problems to the terminal.
        # They'll also be shown to the user.
        else:
            print user_form.errors

    # Not a HTTP POST, so we render our form using two ModelForm instances.
    # These forms will be blank, ready for user input.
    else:
        user_form = UserForm()

    # Render the template depending on the context.
    return render(request,
            'traffic/register.html',
            {'user_form': user_form, 'registered': registered} )

def user_login(request):

    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
                # We use request.POST.get('<variable>') as opposed to request.POST['<variable>'],
                # because the request.POST.get('<variable>') returns None, if the value does not exist,
                # while the request.POST['<variable>'] will raise key error exception
        username = request.POST.get('username')
        password = request.POST.get('password')
        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)

        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found.
        if user:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                # if the user do not choose to keep log in, remove session when the user close browser
                # else use global session length(2 weeks by default) for session length
                if 'remember_me' not in request.POST.keys():
                    request.session.set_expiry(0)
                # if there is a redirect page, redirect to that page, else to home page
                redirectURL = '/traffic/'
                if 'next' in request.POST:
                    redirectURL = request.POST['next']
                return HttpResponseRedirect(redirectURL)
            else:
                # An inactive account was used - no logging in!
                return HttpResponse("Your MDAP account is disabled.")
        else:
            # Bad login details were provided. So we can't log the user in.
            print "Invalid login details: {0}, {1}".format(username, password)
            return HttpResponse("Invalid login details supplied.")

    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
    else:
        # if there is a next parameter in URL, pass it to template for URLredirect use after login
        if request.method == 'GET' and 'next' in request.GET:
            return render(request, 'traffic/login.html', {'next':request.GET['next']})
        else:
            return render(request, 'traffic/login.html')

@login_required
def restricted(request):
    return HttpResponse("Since you're logged in, you can see this text!")

# Use the login_required() decorator to ensure only those logged in can access the view.
@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)

    # Take the user back to the login page.
    return HttpResponseRedirect('/traffic/login/')