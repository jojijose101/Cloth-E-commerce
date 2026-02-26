from django.shortcuts import render

# Create your views here.
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET", "POST"])
def signup_view(request):
    if request.user.is_authenticated:
        return redirect("moc_app:index")  # change to your homepage url name

    if request.method == "POST":
        username = (request.POST.get("username") or "").strip()
        email = (request.POST.get("email") or "").strip()
        password1 = request.POST.get("password1") or ""
        password2 = request.POST.get("password2") or ""

        # Basic validation
        if not username or not password1 or not password2:
            messages.error(request, "All fields are required.")
            return render(request, "auth/signup.html")

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, "auth/signup.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return render(request, "auth/signup.html")

        if email and User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return render(request, "auth/signup.html")

        user = User.objects.create_user(username=username, email=email, password=password1)
        login(request, user)
        messages.success(request, "Account created successfully!")
        return redirect("moc_app:index")

    return render(request, "signup.html")


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        return redirect("moc_app:index")

    if request.method == "POST":
        username = (request.POST.get("username") or "").strip()
        password = request.POST.get("password") or ""

        user = authenticate(request, username=username, password=password)
        if user is None:
            messages.error(request, "Invalid username or password.")
            return render(request, "auth/login.html")

        login(request, user)
        messages.success(request, "Logged in successfully!")
        next_url = request.GET.get("next")
        return redirect(next_url or "moc_app:index")

    return render(request, "login.html")


def logout_view(request):
    logout(request)
    messages.info(request, "Logged out.")
    return redirect("moc_app:index")