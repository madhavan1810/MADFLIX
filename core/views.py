from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import re

from .models import Movie, MovieList


# Home page
@login_required(login_url='login')
def index(request):
    featured_movie = Movie.objects.first()  # Or add fallback/random
    genre_choices = Movie._meta.get_field('genre').choices
    movies = Movie.objects.all()

    context = {
        'featured_movie': featured_movie,
        'genre_choices': genre_choices,
        'movies': movies,
    }
    return render(request, 'index.html', context)




# Individual movie view
@login_required(login_url='login')
def movie(request, pk):
    movie_details = get_object_or_404(Movie, uu_id=pk)

    context = {
        'movie_details': movie_details
    }
    return render(request, 'movie.html', context)


# Genre page
@login_required(login_url='login')
def genre(request, pk):
    movies = Movie.objects.filter(genre=pk)

    context = {
        'movies': movies,
        'movie_genre': pk,
    }
    return render(request, 'genre.html', context)


# Search results
@login_required(login_url='login')
def search(request):
    if request.method == 'POST':
        search_term = request.POST.get('search_term', '')
        movies = Movie.objects.filter(title__icontains=search_term)

        context = {
            'movies': movies,
            'search_term': search_term,
        }
        return render(request, 'search.html', context)
    return redirect('/')


# My List page
@login_required(login_url='login')
def my_list(request):
    movie_list = MovieList.objects.filter(owner_user=request.user)
    user_movie_list = [entry.movie for entry in movie_list]

    context = {
        'movies': user_movie_list
    }
    return render(request, 'my_list.html', context)


# Add to My List
@login_required(login_url='login')
def add_to_list(request):
    if request.method == 'POST':
        movie_url_id = request.POST.get('movie_id')
        uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
        match = re.search(uuid_pattern, movie_url_id)
        movie_id = match.group() if match else None

        if not movie_id:
            return JsonResponse({'status': 'error', 'message': 'Invalid movie ID'}, status=400)

        movie = get_object_or_404(Movie, uu_id=movie_id)
        movie_list, created = MovieList.objects.get_or_create(owner_user=request.user, movie=movie)

        if created:
            return JsonResponse({'status': 'success', 'message': 'Added ✓'})
        else:
            return JsonResponse({'status': 'info', 'message': 'Movie already in list'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


# Login
def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)
        if user:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Credentials Invalid')
            return redirect('login')

    return render(request, 'login.html')


# Signup
def signup(request):
    if request.method == 'POST':
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email Taken')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username Taken')
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                auth.login(request, user)
                return redirect('/')
        else:
            messages.info(request, 'Passwords do not match')
            return redirect('signup')

    return render(request, 'signup.html')


# Logout
@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    return redirect('login')
