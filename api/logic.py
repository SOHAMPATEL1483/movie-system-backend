import numpy as np
import json
from .models import Profile, Movies
import pickle
from django.db.models import Q
from django.contrib.auth.models import User


def makeProfile(user):
    print("makeProfile successfully called")
    r = []
    lastrating = []
    for i in range(10):
        lastrating.append(-1)
    userprofile = Profile.objects.create(
        user=user, Lastrating=str(lastrating), R=str(r)
    )
    userprofile.save()


def getFeature(user):
    print("getFeature is successfully called")
    userprofile = None
    try:
        userprofile = Profile.objects.get(user=user)

    except:
        makeProfile(user)

    return getMovieList(userprofile)


def getMovieList(userprofile):
    print("getMovieList succesfully called")
    R = json.loads(userprofile.R)
    r = []
    for i in R:
        r.append(i[0])
    lr = json.loads(userprofile.Lastrating)
    movie_ids = []
    for i in range(9, -1, -1):
        if lr[i] != -1:
            movie_ids.append(lr[i])
        if len(movie_ids) == 4:
            break
    similarity = pickle.load(open("./static/similarity.pkl", "rb"))
    keyToimdb = pickle.load(open("./static/keyToImdb.pkl", "rb"))

    movies = []
    for i in movie_ids:
        cnt = 5
        for j in similarity[i]:
            if j[0] not in r:
                movies.append(keyToimdb[j[0] + 1])
                cnt -= 1
            if cnt == 0:
                break
        if len(movies) == 20:
            break
    moives = getPopularMovies(movies, r)
    return getMovieDetails(moives)


def getPopularMovies(movies, r=[]):
    print("getPopularMovies successfully called")
    index = 0
    popularity_list = pickle.load(open("./static/popularity_list.pkl", "rb"))
    imdbTokey = pickle.load(open("./static/imdbTokey.pkl", "rb"))
    while len(movies) < 20 and index < 974:
        if imdbTokey[popularity_list[index][0]] - 1 not in r:
            movies.append(popularity_list[index][0])
        index += 1
    return movies


def getMovieDetails(movies):
    movie_list = []
    for i in movies:
        movie = Movies.objects.get(Imdb_id=i)
        dicc = {
            "Imdb_id": movie.Imdb_id,
            "Title": movie.Title,
            "Poster_path": movie.Poster_path,
        }
        movie_list.append(dicc)
    return movie_list
    return movie_list


def updateRating(movieID, user, rating):
    print("Succsessfully called updateRating")
    userprofile = Profile.objects.get(user=user)
    R = json.loads(userprofile.R)
    r = []
    for i in R:
        r.append(i[0])
    lr = json.loads(userprofile.Lastrating)
    imdbTokey = pickle.load(open("./static/imdbTokey.pkl", "rb"))
    lr[rating - 1] = imdbTokey[movieID] - 1
    if imdbTokey[movieID] - 1 not in r:
        R.append([imdbTokey[movieID] - 1, rating])

    userprofile.R = str(R)
    userprofile.Lastrating = str(lr)
    try:
        userprofile.full_clean()
        userprofile.save()
    except:
        print("Validation error in updateRating method")
    print("Succsessfully updated Rating")


def getMovies(moviePrefix):
    print("sucsessfully called getMovie")
    movies = Movies.objects.filter(Q(Title__icontains=moviePrefix)).values()
    return movies


def getMovie(movieID, user):
    print("getMovie successfully called")
    movie = Movies.objects.filter(Imdb_id__contains=movieID).values()
    dictionary = {}
    keyToImdb = pickle.load(open("./static/keyToImdb.pkl", "rb"))
    if len(movie) > 0:
        dictionary["Movie"] = movie[0]
    if user != None:
        userprofile = Profile.objects.get(user=user)
        R = json.loads(userprofile.R)
        for i in R:
            if keyToImdb[i[0] + 1] == movieID:
                dictionary["Rating"] = i[1]
                break
    return dictionary


def getUser(user):
    print("getUser successfully called")
    userprofile = Profile.objects.get(user=user)
    R = json.loads(userprofile.R)
    keyToImdb = pickle.load(open("./static/keyToImdb.pkl", "rb"))
    movie_list = []
    for i in R:
        curr = {}
        print()
        val = i[0]
        val += 1
        imdb_id = keyToImdb[val]
        curr["Imdb_id"] = imdb_id
        movie = Movies.objects.get(Imdb_id=imdb_id)
        curr["Title"] = movie.Title
        curr["Poste_path"] = movie.Poster_path
        curr["Rating"] = i[1]
        movie_list.append(curr)
    return movie_list
