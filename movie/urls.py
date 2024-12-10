from django.urls import path
from movie.views import index,pagination,movieDetails, profile


urlpatterns = [
    path('',index, name='index'),
    path('search/<str:query>/page/<int:page_number>/', pagination, name='pagination'),
    path('movie/<str:imdb_id>/', movieDetails, name='movie-details'),
    path('profile/', profile, name='profile'),  # Doğru: Tek bir view fonksiyonu

]   
