from django.db import models
from django.utils.text import slugify
import requests
from io import BytesIO
from django.core import files


from actor.models import Actor

class Genre(models.Model):
    title=models.CharField(max_length=25)
    slug=models.SlugField(null=False, unique=True)
    
    def __str__(self):
        return self.title
    
    def save(self,*args,**kwargs):
        if not self.slug:
            self.title = self.title.replace(" ", "")
            self.slug=slugify(self.title)
        return super().save(*args, **kwargs)
    
class Rating(models.Model):
    source = models.CharField(max_length=50)
    rating = models.FloatField(max_length=10)
    
    def __str__(self):
        return self.source

class Movie(models.Model):
    title = models.CharField(max_length=200)  # Film adı
    year = models.CharField(max_length=25, blank=True)  # Yıl
    rated = models.CharField(max_length=10, blank=True)  # Derecelendirme
    released = models.CharField(max_length=25, blank=True)  # Yayın tarihi
    runtime = models.CharField(max_length=25, blank=True)  # Süre
    genre = models.ManyToManyField(Genre, blank=True)  # Türler
    director = models.CharField(max_length=100, blank=True)  # Yönetmen
    writer = models.CharField(max_length=300, blank=True)  # Senarist
    actors = models.ManyToManyField(Actor, blank=True)  # Oyuncular
    plot = models.CharField(max_length=900, blank=True)  # Konu
    language = models.CharField(max_length=300, blank=True)  # Dil
    country = models.CharField(max_length=100, blank=True)  # Ülke
    awards = models.CharField(max_length=200, blank=True)  # Ödüller
    poster = models.URLField(default='http://127.0.0.1:8000/static/img/default-poster.jpeg')  # Varsayılan değer # Poster
    poster_url = models.URLField(blank=True)  # Poster URL'si
    ratings = models.ManyToManyField(Rating, blank=True)  # Derecelendirmeler
    metascore = models.CharField(max_length=5, blank=True)  # Metascore
    imdb_rating = models.CharField(max_length=5, blank=True)  # IMDb Derecelendirmesi
    imdb_votes = models.CharField(max_length=100, blank=True)  # IMDb Oylama Sayısı
    imdb_id = models.CharField(max_length=100, unique=True)  # IMDb ID
    type = models.CharField(max_length=10, blank=True)  # Tür (film, dizi vb.)
    
    def __str__(self):
        return self.title
    
    def save(self,*args, **kwargs):
        if self.poster == '' and self.poster_url !='':
            resp=requests.get(self.poster_url)
            pb=BytesIO()
            pb.write(resp.content)
            pb.flush()
            file_name = self.poster_url.split("/")[-1]
            self.poster.save(file_name, files.File(pb), save=False)
       
        return super().save(*args, **kwargs)