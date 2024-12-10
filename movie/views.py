from django import template
from django.shortcuts import render
from django.utils.text import slugify
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader

from datetime import datetime
import requests

from movie.models import Movie,Genre,Rating
from actor.models import Actor


def format_date(date_str):
    # TMDb API'den gelen tarihi 'yyyy-mm-dd' formatından 'dd.mm.yyyy' formatına çeviriyoruz.
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.strftime('%d.%m.%Y')
    except (ValueError, TypeError):
        return ''  # Eğer tarih boşsa ya da geçersizse boş döner.

def index(request):
    query = request.GET.get('q', '').strip()

    if query:
        url = f'https://api.themoviedb.org/3/search/movie?api_key=b9ab9730b2361f2b69dd705fba78ea16&query={query}&language=tr-TR'

        response = requests.get(url)
        movie_data = response.json()
        
        movies = movie_data.get('results', [])
        
        sorted_movies = sorted(movies, key=lambda x: x.get('release_date', ''), reverse=True)
        
        for movie in sorted_movies:
            if 'release_date' in movie and movie.get('release_date'):
                movie['release_date'] = format_date(movie['release_date'])
            if not movie.get('imdb_id'):
                movie['imdb_id'] = 'default_id'  # Boş olan IMDb ID'ler için geçici bir çözüm


        context = {
            'query': query,
            'movie_data': sorted_movies,
            'page_number':1,
        }

        template = loader.get_template('search_result.html')
        return HttpResponse(template.render(context, request))

    return render(request, 'index.html')

def pagination(request, query, page_number):
    url = f'https://api.themoviedb.org/3/search/movie?api_key=b9ab9730b2361f2b69dd705fba78ea16&query={query}&language=tr-TR&page={page_number}'
    response = requests.get(url)
    movie_data = response.json()
    page_number = movie_data.get('page', int(page_number)) + 1  # Güncel sayfa numarasını çekiyoruz
    
    context = {
        'query': query,
        'movie_data': movie_data.get('results', []),  # Sadece `results` verisini geçiriyoruz
        'page_number': page_number,
    }
    template = loader.get_template('search_result.html')
    return HttpResponse(template.render(context, request))

def movieDetails(request, imdb_id):
    
    
    if Movie.objects.filter(imdb_id=imdb_id).exists():
        movie_data = Movie.objects.get(imdb_id=imdb_id)
        our_db = True
    else:
        url = f'https://api.themoviedb.org/3/find/{imdb_id}?api_key=b9ab9730b2361f2b69dd705fba78ea16&language=tr-TR&external_source=imdb_id'
        response = requests.get(url)
        movie_data = response.json()
        print(movie_data)
         
        tmdb_results = movie_data.get('movie_results', [])
        tmdb_id = tmdb_results[0]['id'] if tmdb_results else None
        if tmdb_id:
            # Film detaylarını ve oyuncuları almak için yeni istek
            credits_url = f'https://api.themoviedb.org/3/movie/{tmdb_id}/credits?api_key=b9ab9730b2361f2b69dd705fba78ea16&language=tr-TR'
            credits_response = requests.get(credits_url)
            credits_data = credits_response.json()
            actor_objs = []
            # Aktörleri al
            for actor in credits_data.get('cast', []):
                a, created = Actor.objects.get_or_create(name=actor['name'])
                actor_objs.append(a)
        
        rating_objs = []
        genre_objs = []


        # Türleri al
        if 'genres' in movie_data:
            genre_list = list(movie_data['genres'].replace(" ", "").split(','))
            for genre in genre_list:
                genre_slug = slugify(genre)
                g, created = Genre.objects.get_or_create(title=genre, slug=genre_slug)
                genre_objs.append(g)
        else:
            print("No genre found in movie_data.")

        # Derecelendirmeleri al
        if 'vote_average' in movie_data:
            for rate in movie_data['vote_average']:
                r, created = Rating.objects.get_or_create(source=rate['source'], rating=rate['value'])
                rating_objs.append(r)
        else:
            print("No ratings found in movie_data.")

        # Film verilerini al ve varsayılan değerleri ayarla
        title = movie_data.get('title', 'Unknown Title')
        year = movie_data.get('release_date', 'Unknown Year')
        #rated = movie_data.get('rated', 'Not Rated')
        #released = movie_data.get('released', 'Unknown Release Date')
        runtime = movie_data.get('runtime', 'Unknown Runtime')
        #director = movie_data.get('director', 'Unknown Director')
        #writer = movie_data.get('writer', 'Unknown Writer')
        plot = movie_data.get('overwiev', 'No Plot Available')
        #language = movie_data.get('language', 'Unknown Language')
        #country = movie_data.get('country', 'Unknown Country')
        #awards = movie_data.get('awards', 'No Awards')
        #poster_url = movie_data.get('poster_url', 'http://127.0.0.1:8000/static/img/default-poster.jpeg')
        #metascore = movie_data.get('metascore', 'No Metascore')
        imdb_rating = movie_data.get('vote_average', 'No Rating')
        imdb_votes = movie_data.get('vote_count', 'No Votes')
        #movie_type = movie_data.get('type', 'Unknown Type')
        

        # Film nesnesini oluştur
        m, created = Movie.objects.get_or_create(
            title=title,
            year=year,
            #rated=rated,
            #released=released,
            runtime=runtime,
            #director=director,
            #writer=writer,
            plot=plot,
            #language=language,
            #country=country,
            #awards=awards,
            #poster_url=poster_url,
            #metascore=metascore,
            imdb_rating=imdb_rating,
            imdb_votes=imdb_votes,
            imdb_id=imdb_id,
            #type=movie_type,
            
        )

        # İlişkileri ayarla
        m.genre.set(genre_objs)
        m.actors.set(actor_objs)
        m.ratings.set(rating_objs)


        m.save()
        our_db = False

    context = {
        'movie_data': movie_data,
        'our_db': our_db,
    }
    template = loader.get_template('movie_details.html')
    return HttpResponse(template.render(context, request))

def profile(request):
    return render(request, 'actual_base.html')