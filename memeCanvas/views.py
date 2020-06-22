from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Meme


# Create your views here.
def index(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return render(request, "memeCanvas/login.html", {"message": "Please login first to be able to save memes to your account"})
        else:
            topText = request.POST["topText"]
            topTextSize = request.POST["topTextSize"]
            bottomText = request.POST["bottomText"]
            bottomTextSize = request.POST["bottomTextSize"]
            temp = request.FILES["temp"]
            meme = Meme.objects.create(user=request.user, topText=topText, topTextSize=topTextSize, bottomText=bottomText, bottomTextSize=bottomTextSize, temp=temp)
            meme.save()
            return render(request, 'memeCanvas/index.html', {"message": "The meme is saved successfully", "user": "yes"})
    else: 
        return render(request, 'memeCanvas/index.html')
        
        
       

def register_view(request):
    if request.method == "GET":
        if not request.user.is_authenticated:
            return render(request, "memeCanvas/register.html", {"message": None})
        else:
            logout(request)
            return render(request, "memeCanvas/register.html", {"message": "You logged out to register another account"})
    else:
        username = request.POST["username"]
        first = request.POST["firstname"]
        last = request.POST["lastname"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirm = request.POST["confirm"]
        try :
            check1 = User.objects.get(username=username)
        except User.DoesNotExist:
            check1 = None
        try:    
            check2 = User.objects.get(email=email)
        except User.DoesNotExist:
            check2 = None
        if not username or not first or not last or not email or not password or password != confirm:
            return render(request, "memeCanvas/register.html", {"message": "Please Check your data again!"})
        if check1 or check2 is not None:
            return render(request, "memeCanvas/register.html", {"message": "Username or Email already exsits!"})
        user = User.objects.create_user(username, email, password)
        user.first_name = first
        user.last_name = last
        user.save()
        return HttpResponseRedirect(reverse("login"))

def login_view(request):
    if request.method == "GET":
        if not request.user.is_authenticated:
            return render(request, "memeCanvas/login.html", {"message": None})
        else:
            logout(request)
            return render(request, "memeCanvas/login.html", {"message": "You logged out, to login with another or the same account"})
    username = request.POST["username"]
    password = request.POST["password"]
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "memeCanvas/login.html", {"message": "Invald credintials"})

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def my_memes(request):
    if not request.user.is_authenticated:
        return render(request, "memeCanvas/login.html", {"message": "Please login first to be able to save memes to your account"})
    else:
        myMemes = Meme.objects.filter(user=request.user)
        n = 0
        for i in myMemes:
            n = n + 1
        return render(request, "memeCanvas/myMemes.html", {"myMemes": myMemes, "n": n})


def search(request):
    if not request.user.is_authenticated:
        return render(request, "memeCanvas/login.html", {"message": "Please login first to be able to search all"})
    else:
        if request.method == "POST":
            text = request.POST["text"]
            n = 0
            l = []
            for word in text.split():
                results = Meme.objects.filter(Q(topText__icontains = word) | Q(bottomText__icontains = word) | Q(temp__icontains  = word))
                for result in results:
                    l.append(result.topText)
                    l.append(result.topTextSize)
                    l.append(result.bottomText)
                    l.append(result.bottomTextSize)
                    l.append(result.temp.url)
                    n = n + 1

            return render(request, "memeCanvas/search.html", {"l": l, "n": n})
        else:
             return render(request, "memeCanvas/search.html")
