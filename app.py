from flask import Flask, request, render_template
import pymysql as sql
import requests
def connect():
    db = sql.connect(host='localhost', port=3306, user='root', password='', database='movie')
    cursor = db.cursor()
    return db, cursor

app = Flask(__name__)

omdb_key = "8bcace9e"

@app.route("/")
def login():
    return render_template("main_index.html")

@app.route("/register/")
def register():
    return render_template("signup.html")

@app.route("/login/")
def re_login():
    return render_template("login.html")

@app.route("/aftersignup/", methods=["GET","POST"])
def aftersignup():
    if request.method == 'GET':
        return render_template("signup.html")
    else:
        db, cursor = connect()
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        r_password = request.form.get("r_password")
        cmd = f"select * from movie_user where email = '{email}'"
        cursor.execute(cmd)
        data = cursor.fetchone()
        if data:
            msg = "Email Is already Exists.."
            return render_template("signup.html",e_msg= msg)
        else:
            if len(password) >= 8:
                upp = 0
                low = 0
                sp = 0
                num = 0
                for i in password:
                    if i.isupper():
                        upp += 1
                    elif i.islower():
                        low += 1
                    elif i in "#@%$&^!.*":
                        sp += 1
                    elif i in "1234567890":
                        num += 1
                if upp >= 1 and low>=1 and num>=1 and sp>=1:
                    if password == r_password:
                        cmd = f"insert into movie_user values('{name}', '{email}', '{password}')"
                        cursor.execute(cmd)
                        db.commit()
                        return render_template("login.html")
                    else:
                        msg = "Re-enter password does not match.."
                        return render_template("signup.html",r_p_msg = msg)
                else:
                    msg = "Must Write upper,small,number and special charachter.. "
                    return render_template("register.html", p_msg=msg)
            else:
                msg = "Password is not 8 characters long"
                return render_template("signup.html", p_msg=msg)

@app.route("/afterlogin/",methods=['GET','POST'])
def afterlogin():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")
        db, cursor = connect()
        cmd = f"select * from movie_user where email = '{email}' and password = '{password}'"
        cursor.execute(cmd)
        data = cursor.fetchone()
        if data:
            # popular_movie
            popular_movie = get_popular_movie()
            popular = {}
            i = 0
            for key,value in popular_movie.items():
                popular[key] = value
                i += 1
                if i == 5:
                    break
            # popular_movie Ends

            # popular_Tvshow
            popular_Tvshow = get_popular_TVshow()
            popular_tv = {}
            i = 0
            for key,value in popular_Tvshow.items():
                popular_tv[key] = value
                i += 1
                if i == 5:
                    break
            # popular_Tvshow Ends

            # coming_soon_movie
            upcoming_movie = get_cooming_soon_movie()
            coming_movie = {}
            i = 0
            for key,value in upcoming_movie.items():
                coming_movie[key] = value
                i += 1
                if i == 5:
                    break
            # coming_soon_movie Ends

            return render_template("index.html", popular_movie= popular, popular_Tvshow= popular_tv,upcoming_movie= coming_movie)
        else:
            msg = "Invalid Email or Password"
            return render_template("login.html",e_p_msg= msg)        
    else:
        return render_template("login.html")

@app.route("/movie_detail/<string:movie_imdbID>")
def movie_detail(movie_imdbID):
    # return f"Title :- {movie_title} , Movie_ID :- {movie_imdbID}"
    Id_movie = movie_imdbID
    movie_d = get_movie_detail(Id_movie)
    
    return render_template("movie_details.html",movie_d= movie_d)

@app.route("/index/")
def index():
    return render_template("index.html")

@app.route("/logout/")
def logout():
    return render_template("main_index.html")

# After Search
@app.route("/aftersearch/",methods=['GET',"POST"])
def aftersearch():
    search_movie = request.form.get("movie")
    # print(search_movie)
    search_m = get_search_movie(search_movie)

    return render_template("allMovie.html",search_m= search_m)

# After Show More
@app.route("/afterShowMore/<string:type_gener>")
def after_Show_More(type_gener):
    # print(type_gener)
    # return "Type Gener : " + type_gener
    if type_gener == 'popular':
        popular_movies = get_popular_movie()
        return render_template("allMovie.html",search_m= popular_movies)
    elif type_gener == 'tvShow':
        popular_tvShows = get_popular_TVshow()
        return render_template("allMovie.html",search_m= popular_tvShows)
    elif type_gener == 'coming':
        coming_movies = get_cooming_soon_movie()
        return render_template("allMovie.html",search_m= coming_movies)

#After Gener Select
@app.route("/afterGener/<string:gener_m>")
def after_gener_movie(gener_m):
    gener_movie = get_gener_movie(gener_m)
    return render_template("allMovie.html",search_m=gener_movie,title= gener_m)

# Popular Movie
def get_popular_movie():
    url = "https://imdb8.p.rapidapi.com/title/get-most-popular-movies"
    querystring = {"purchaseCountry":"US","homeCountry":"US","currentCountry":"US"}
    headers = {
        'x-rapidapi-key': "4fcda4c659msh9328752fbf269f5p1402b2jsn1063e4ecb951",
        'x-rapidapi-host': "imdb8.p.rapidapi.com"
        }
    response = requests.request("GET", url, headers=headers, params=querystring)
    if response.status_code == 200:
        data = []
        for i in response.json():
            data.append(i[7:-1])
        # print(data)
        popular_movie = {}
        j = 0
        for i in data[0:30]:
            url = f"http://www.omdbapi.com/?i={i}&apikey=8bcace9e"
            resp = requests.get(url)
            o_data = resp.json()
            if o_data['Poster'] != 'N/A':
                popular_movie[f"movie{j+1}"] = o_data
            j += 1 
        # movie_titla = popular_movie[f"movie1"]['Title']
        return popular_movie

#Gener movie
def get_gener_movie(gener):
    gener_mo = f"/chart/popular/genre/{gener}"
    url = "https://imdb8.p.rapidapi.com/title/get-popular-movies-by-genre"
    querystring = {"genre":gener_mo}
    headers = {
        'x-rapidapi-key': "4fcda4c659msh9328752fbf269f5p1402b2jsn1063e4ecb951",
        'x-rapidapi-host': "imdb8.p.rapidapi.com"
        }
    response = requests.request("GET", url, headers=headers, params=querystring)
    if response.status_code == 200:
        data = []
        for i in response.json():
            data.append(i[7:-1])
        # print(data)
        gener_movie = {}
        j = 0
        for i in data[0:15]:
            url = f"http://www.omdbapi.com/?i={i}&apikey=8bcace9e"
            resp = requests.get(url)
            o_data = resp.json()
            if o_data['Poster'] != 'N/A':
                gener_movie[f"gener_movie{j+1}"] = o_data
            j += 1 
        # movie_titla = popular_movie[f"movie1"]['Title']
        return gener_movie

#popular_TvShows
def get_popular_TVshow():
    url = "https://imdb8.p.rapidapi.com/title/get-most-popular-tv-shows"
    querystring = {"purchaseCountry":"US","currentCountry":"US","homeCountry":"US"}
    headers = {
        'x-rapidapi-key': "4fcda4c659msh9328752fbf269f5p1402b2jsn1063e4ecb951",
        'x-rapidapi-host': "imdb8.p.rapidapi.com"
        }
    response = requests.request("GET", url, headers=headers, params=querystring)
    if response.status_code == 200:
        data = []
        for i in response.json():
            data.append(i[7:-1])
        # print(data)
        popular_Tvshow = {}
        j = 0
        for i in data[0:30]:
            url = f"http://www.omdbapi.com/?i={i}&apikey=8bcace9e"
            resp = requests.get(url)
            o_data = resp.json()
            if o_data['Poster'] != 'N/A':
                popular_Tvshow[f"Tvshow{j+1}"] = o_data
            j += 1 
        # movie_titla = popular_movie[f"movie1"]['Title']
        return popular_Tvshow

#up-coming movie
def get_cooming_soon_movie():
    url = "https://imdb8.p.rapidapi.com/title/get-coming-soon-movies"
    querystring = {"homeCountry":"US","purchaseCountry":"US","currentCountry":"US"}
    headers = {
        'x-rapidapi-key': "4fcda4c659msh9328752fbf269f5p1402b2jsn1063e4ecb951",
        'x-rapidapi-host': "imdb8.p.rapidapi.com"
        }
    response = requests.request("GET", url, headers=headers, params=querystring)
    if response.status_code == 200:
        data = []
        for i in response.json():
            data.append(i[7:-1])
        # print(data)
        upcoming_movie = {}
        j = 0
        for i in data[0:30]:
            url = f"http://www.omdbapi.com/?i={i}&apikey=8bcace9e"
            resp = requests.get(url)
            o_data = resp.json()
            if o_data['Poster'] != 'N/A':
                upcoming_movie[f"coming_movie{j+1}"] = o_data
            j += 1 
        # movie_titla = popular_movie[f"movie1"]['Title']
        return upcoming_movie

#Search Movie
def get_search_movie(search_movie):
    key = "8bcace9e"
    movie_id = []
    for j in range(1,3):
        url = f"http://www.omdbapi.com/?apikey={key}&s={search_movie}&page={j}"
        resp = requests.get(url)
        if resp.status_code == 200:
            data = resp.json()
            # print(data)
            # print(len(data['Search'][0]))
            for i in range(len(data['Search'][0])):
                movie_id.append(data['Search'][i]['imdbID'])
    search_m = {}
    s_m = 0
    for k in movie_id:
        url = f"http://www.omdbapi.com/?apikey=8bcace9e&i={k}"
        resp = requests.get(url)
        if resp.status_code == 200:
            movie_data = resp.json()
            if movie_data['Poster'] != 'N/A':
                search_m[f'Movie{s_m+1}'] = movie_data
        s_m += 1
    return search_m

#get similar Movie
def get_similar_movie(movie_title):
    key = "8bcace9e"
    movie_id = []
    url = f"http://www.omdbapi.com/?apikey={key}&s={movie_title}"
    resp = requests.get(url)
    if resp.status_code == 200:
        data = resp.json()
        # print(data)
        # print(len(data['Search'][0]))
        for i in range(len(data['Search'][0])):
            movie_id.append(data['Search'][i]['imdbID'])
    search_m = {}
    s_m = 0
    for k in movie_id:
        url = f"http://www.omdbapi.com/?apikey=8bcace9e&i={k}"
        resp = requests.get(url)
        if resp.status_code == 200:
            movie_data = resp.json()
            if movie_data['Poster'] != 'N/A':
                search_m[f'Movie{s_m+1}'] = movie_data
        s_m += 1
    return search_m
#movie detail
def get_movie_detail(movie_imdbID):
    url = f"http://www.omdbapi.com/?apikey={omdb_key}&i={movie_imdbID}"
    resp = requests.get(url)
    if resp.status_code == 200:
        data = resp.json()
    return data

# def get_gener_movie(gener_movie):


app.run(host="localhost",port=80,debug=True)