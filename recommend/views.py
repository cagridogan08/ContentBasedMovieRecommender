from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.shortcuts import render, get_object_or_404, redirect

from .forms import *
from django.http import Http404, HttpResponseRedirect
from .models import Movie, MyList
from django.db.models import Q
from django.contrib import messages

import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
# Create your views here.


#Get main page list or search
def index(request):
    movies = Movie.objects.all().order_by('?')
    query = request.GET.get('q')
    #GetListDatas()
    if query:
        movies = Movie.objects.filter(Q(original_title__icontains=query)).distinct()
        return render(request, 'recommend/list.html', {'movies': movies})

    return render(request, 'recommend/list.html', {'movies': movies[:30]})
#Watchlist and  based recommadation for user
def watch(request):
    
    if not request.user.is_authenticated:
        return redirect("login")
    if not request.user.is_active:
        raise Http404

    movies = Movie.objects.filter(mylist__watch=True,mylist__user=request.user)
    query = request.GET.get('q')
    recs = []
    counters =[]
    if query:
        movies = Movie.objects.filter(Q(original_title__icontains=query)).distinct()
        return render(request, 'recommend/watch.html', {'movies': movies})
    if movies.count==0:
        counters = Movie.objects.all().order_by('?')
    else:
        aa = pd.DataFrame(list(Movie.objects.all().values()))
        movies_df,indices,cos_sim = BBBB(aa)
        for movie in movies:
          recommends = Recommend(movie.original_title,cos_sim,movies_df,indices,4)
          recs.append(recommends)
        for row in recs:
          for i in row:
            counters.append(Movie.objects.get(id=i))
    counters = GetDifference(counters,movies)
    context = {'movies':movies,'recommends':counters[:12]}
    return render(request, 'recommend/watch.html', context)
#User signUp
def signUp(request):
    form = UserForm(request.POST or None)

    if form.is_valid():
        user = form.save(commit=False)
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user.set_password(password)
        user.save()
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect("index")

    context = {'form': form}

    return render(request, 'recommend/signUp.html', context)

#User Login
def Login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect("index")
            else:
                return render(request, 'recommend/login.html', {'error_message': 'Your account disable'})
        else:
            return render(request, 'recommend/login.html', {'error_message': 'Invalid Login'})

    return render(request, 'recommend/login.html')


# Logout user
def Logout(request):
    logout(request)
    return redirect("login")

#Movie detail and recommends
def detail(request, movie_id):
    if not request.user.is_authenticated:
        return redirect("login")
    if not request.user.is_active:
        raise Http404
    movies = get_object_or_404(Movie, id=movie_id)
    movie = Movie.objects.get(id=movie_id)
    
    temp = list(MyList.objects.all().values().filter(movie_id=movie_id,user=request.user))
    if temp:
        update = temp[0]['watch']
    else:
        update = False
    if request.method == "POST":

        # For my list
        if 'watch' in request.POST:
            watch_flag = request.POST['watch']
            if watch_flag == 'on':
                update = True
            else:
                update = False
            if MyList.objects.all().values().filter(movie_id=movie_id,user=request.user):
                MyList.objects.all().values().filter(movie_id=movie_id,user=request.user).update(watch=update)
            else:
                q=MyList(user=request.user,movie=movie,watch=update)
                q.save()
            if update:
                messages.success(request, "Movie added to your list!")
            else:
                messages.success(request, "Movie removed from your list!")
        #For MyRating
        else:
            rate = request.POST['rating']
            if MyRating.objects.all().values().filter(movie_id=movie_id,user=request.user):
                MyRating.objects.all().values().filter(movie_id=movie_id,user=request.user).update(rating=rate)
            else:
                q=MyRating(user=request.user,movie=movie,rating=rate)
                q.save()

            messages.success(request, "Rating has been submitted!")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    out = list(MyRating.objects.filter(user=request.user.id).values())
    movie_rating = 0
    rate_flag = False
    for each in out:
        if each['movie_id'] == movie_id:
            movie_rating = each['rating']
            rate_flag = True
            break
    recs = getRecommendById(movie_id)
    context = {'movies': movies,'movie_rating':movie_rating,'rate_flag':rate_flag,'update':update,'recommends':recs[:24]}
    return render(request, 'recommend/detail.html', context)



def Recommend(title,cos,movies_df,indices,y):
    
    id_x = indices[title]
    sim_score = list(enumerate(cos[id_x]))
    sim_score = sorted(sim_score,key=lambda x:x[1],reverse=True)
    sim_score = sim_score[1:y]

    movie_indices = [ind[0] for ind in sim_score]
    movies = movies_df["id"].iloc[movie_indices]
    return movies.tolist()

def getRecommendById(movie_id):
    movie = Movie.objects.get(id=movie_id)
    aa = pd.DataFrame(list(Movie.objects.all().values()))
    movies_df,indices,cos_sim = BBBB(aa)
    recommends = Recommend(movie.original_title,cos_sim,movies_df,indices,30)
    recs = []
    for reco in recommends:
        recs.append(Movie.objects.get(id=reco))
    return recs
# Dataset Vectorizer amd similarity matrix    
def BBBB(df):
    movieData = df
    features = ["Director","Star1","Star2","Star3","Star4"]
    movieData["Genre"] = movieData["Genre"].apply(clean_Genre)
    for fe in features:
        movieData[fe] = movieData[fe].apply(clean_data)
    movieData["keywords"] = movieData.apply(KeywordsWithCast,axis=1)
    cVectorizer = CountVectorizer()
    CFit = cVectorizer.fit_transform(movieData["keywords"])
    cos_sim_matrix = cosine_similarity(CFit,CFit)

    movies_df = movieData.reset_index()
    indices = pd.Series(movies_df.index,index=movies_df["original_title"])
    indices = pd.Series(movies_df.index,index=movies_df["original_title"]).drop_duplicates()

    return movies_df,indices,cos_sim_matrix


def MovieList(df:pd.DataFrame)->list:
    return list(map(lambda x:Movie(id=x[0],link=x[1],title=x[2],year=x[3],certificate=x[4]
                                   ,time=x[5],genre=x[6],IMDB_Rating=x[7],OverView=x[8],mScore=x[9],direc=x[10]
                                   ,s1=x[11],s2=x[12],s3=x[13],s4=x[14],keywords=x[15]
                                   ),df.values.tolist()))


def clean_Genre(row):
        if isinstance(row, list):
            return [str.lower(i.replace(",", "")) for i in row]
        else:
            if isinstance(row, str):
                return str.lower(row.replace(",", ""))
            else:
                return ""

def clean_data(row):
        if isinstance(row, list):
            return [str.lower(i.replace(" ", "")) for i in row]
        else:
            if isinstance(row, str):
                return str.lower(row.replace(" ", ""))
            else:
                return ""
# Joining all features
def KeywordsWithCast(features):
        return ' '.join(features["keywords"]) + ' ' + (features["Genre"]) + ' ' + features["Star1"] + ' ' + (
        features["Director"]) + ' ' + features["Star2"] + ' ' + features["Star3"] + ' ' + features["Star4"]



def GetDifference(l1,l2):
    l1 = set(l1)
    l2 = set(l2)
    return list(l1-l2)



def recommend(request,pk):
    movie = Movie.objects.filter(id=pk)
    recs = getRecommendById(pk)
    return render(request,'recommend/recommend.html',{'pk':movie,'recommends':recs})


''' def GetListDatas():
    aa = pd.DataFrame(list(MyList.objects.all().values()))
    user_ids = aa["user_id"].unique().tolist()
    user2user_encoded = {x: i for i, x in enumerate(user_ids)}
    userencoded2user = {i: x for i, x in enumerate(user_ids)}
    movie_ids = aa["movie_id"].unique().tolist()
    movie2movie_encoded = {x: i for i, x in enumerate(movie_ids)}
    movie_encoded2movie = {i: x for i, x in enumerate(movie_ids)}
    aa["user"] = aa["user_id"].map(user2user_encoded)
    aa["movie"] = aa["movie_id"].map(movie2movie_encoded) '''
    
    