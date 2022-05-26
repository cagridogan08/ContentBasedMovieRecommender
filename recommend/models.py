from calendar import month
from email.policy import default
from typing_extensions import Self
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
# Create your models here.

class Movie(models.Model):
    Poster_Link = models.TextField()
    original_title = models.TextField()
    Released_Year = models.IntegerField()
    Certificate = models.TextField()
    Runtime = models.IntegerField()
    Genre = models.TextField()
    IMDB_Rating = models.FloatField()
    Overview = models.TextField(default="Overview")
    Meta_score = models.IntegerField()
    Director = models.TextField()
    Star1 = models.TextField()
    Star2 = models.TextField()
    Star3 = models.TextField()
    Star4 = models.TextField()
    Gross = models.IntegerField()
    keywords = models.TextField()

    def GetCast(self):
        return str("Cast:"+self.Star1+","+ self.Star2+","+self.Star3+","+self.Star4)
    def GetGenre(self):
        return str("Genres: "+self.Genre)
    def GetRatings(self):
        return str("IMDB:"+ str(self.IMDB_Rating)+ "      Meta Score: "+ str(self.Meta_score))

    def GetTitleWithReleaseYear(self):
        return str(self.original_title+"("+str(self.Released_Year)+")")
    def GetDirector(self):
        return str("Director: "+self.Director)
    def GetOverview(self):
        return str("Overview: "+self.Overview)

    



class MyList(models.Model):

    user = models.ForeignKey(User,on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie,on_delete=models.CASCADE)
    watch = models.BooleanField(default=False)

class MyRating(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    movie=models.ForeignKey(Movie,on_delete=models.CASCADE)
    rating = models.IntegerField(default=0, validators=[MaxValueValidator(5), MinValueValidator(0)])