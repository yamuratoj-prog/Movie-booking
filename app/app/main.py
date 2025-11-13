from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pymongo import MongoClient, errors
from bson import ObjectId
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="Movie Booking API", version="3.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.app.health import router as health_router
app.include_router(health_router)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017/")
MONGO_DB = os.getenv("MONGO_DB", "movie_booking")

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client[MONGO_DB]
    client.server_info()
except errors.ServerSelectionTimeoutError:
    db = None
    print("MongoDB не доступна!")

@app.get("/", response_class=HTMLResponse)
async def root():
    if db is None:
        return HTMLResponse("<h1>Ошибка подключения к MongoDB</h1>", status_code=500)

    try:
        movies = list(db.movies.find())
    except Exception as e:
        return HTMLResponse(f"<h1>Ошибка при чтении MongoDB: {str(e)}</h1>", status_code=500)

    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>🎬 Movie Booking</title>
        <style>
            body {
                margin: 0;
                font-family: 'Poppins', sans-serif;
                background: radial-gradient(circle at top left, #0d0d0d, #000);
                color: #fff;
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
            }
            .container {
                width: 90%;
                max-width: 1200px;
                background: rgba(20, 20, 20, 0.9);
                border-radius: 20px;
                padding: 50px;
                box-shadow: 0 0 60px rgba(245,197,24,0.2);
            }
            h1 {
                text-align: center;
                font-size: 4em;
                color: #f5c518;
                margin-bottom: 50px;
                text-shadow: 0 0 10px rgba(255, 255, 255, 0.2);
            }
            .grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
                gap: 35px;
            }
            .card {
                background: linear-gradient(145deg, #111, #1c1c1c);
                border-radius: 15px;
                padding: 25px;
                text-align: center;
                transition: all 0.3s ease;
                box-shadow: 0 0 15px rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.1);
                position: relative;
            }
            .card:hover {
                transform: translateY(-8px) scale(1.03);
                box-shadow: 0 0 25px rgba(245,197,24,0.3);
                border-color: rgba(245,197,24,0.4);
            }
            .title {
                font-size: 1.8em;
                font-weight: 600;
                margin-bottom: 10px;
                color: #f5c518;
            }
            .year, .seats-info {
                font-size: 1.3em;
                color: #bbb;
                margin-bottom: 10px;
            }
            .delete-btn {
                position: absolute;
                top: 15px;
                right: 15px;
                background: transparent;
                color: rgba(255, 68, 68, 0.8);
                border: none;
                font-size: 1.5em;
                font-weight: bold;
                cursor: pointer;
                transition: all 0.3s;
            }
            .delete-btn:hover {
                color: #ff4444;
                transform: scale(1.3);
            }
            .add-form {
                margin-top: 60px;
                text-align: center;
            }
            input {
                padding: 10px 15px;
                font-size: 1em;
                border-radius: 8px;
                border: none;
                outline: none;
                margin: 5px;
                background: #222;
                color: #fff;
            }
            button {
                padding: 10px 20px;
                font-size: 1em;
                border: none;
                border-radius: 8px;
                background: #f5c518;
                color: #000;
                cursor: pointer;
                font-weight: bold;
                transition: background 0.3s, transform 0.2s;
            }
            button:hover {
                background: #ffda47;
                transform: scale(1.05);
            }
            .no-movies {
                text-align: center;
                font-size: 1.5em;
                opacity: 0.8;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎞 Movie Booking</h1>
            <div class="grid">
    """

    if movies:
        for movie in movies:
            available = movie.get("available_seats", 50) - len(movie.get("booked_seats", []))
            html += f"""
            <div class="card">
                <button class="delete-btn" onclick="deleteMovie('{movie['_id']}')">×</button>
                <div class="title">{movie.get("title", "Untitled")}</div>
                <div class="year">📅 {movie.get("year", "N/A")}</div>
                <div class="seats-info">🎟 Доступно мест: {available}</div>
                <input type="number" id="seats-{movie['_id']}" placeholder="Количество билетов" min="1" max="{available}">
                <button onclick="bookMovie('{movie['_id']}')">Забронировать</button>
            </div>
            """
    else:
        html += '<div class="no-movies">No movies available 🎬</div>'

    html += """
            </div>
            <div class="add-form">
                <input id="title" placeholder="Title">
                <input id="year" placeholder="Year">
                <button onclick="addMovie()">Add Movie</button>
            </div>
        </div>
        <script>
            async function addMovie() {
                const title = document.getElementById('title').value;
                const year = document.getElementById('year').value;
                if (!title || !year) {
                    alert('Please fill both fields!');
                    return;
                }
                await fetch('/movies', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({title, year, available_seats:50, booked_seats:[]})
                });
                location.reload();
            }

            async function deleteMovie(id) {
                if (confirm('Are you sure you want to delete this movie?')) {
                    await fetch('/movies/' + id, { method: 'DELETE' });
                    location.reload();
                }
            }

            async function bookMovie(movieId) {
                const seatsInput = document.getElementById('seats-' + movieId);
                const seats = parseInt(seatsInput.value);
                if (!seats || seats < 1) {
                    alert('Введите корректное количество билетов!');
                    return;
                }
                const res = await fetch('/movies/' + movieId + '/book?seats=' + seats, {
                    method: 'POST'
                });
                const data = await res.json();
                if (data.error) {
                    alert(data.error);
                } else {
                    alert(data.message + "\\nМеста: " + data.seats.join(", "));
                    location.reload();
                }
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


@app.get("/movies")
async def get_movies():
    if db is None:
        return {"error": "MongoDB не доступна"}
    movies = []
    for m in db.movies.find():
        m["_id"] = str(m["_id"])
        movies.append(m)
    return {"movies": movies}


@app.post("/movies")
async def add_movie(movie: dict):
    if db is None:
        return {"error": "MongoDB не доступна"}
    # добавляем бронируемые места при создании фильма
    movie.setdefault("available_seats", 50)
    movie.setdefault("booked_seats", [])
    result = db.movies.insert_one(movie)
    return {"message": "Movie added successfully", "id": str(result.inserted_id)}


@app.delete("/movies/{movie_id}")
async def delete_movie(movie_id: str):
    if db is None:
        return {"error": "MongoDB не доступна"}
    result = db.movies.delete_one({"_id": ObjectId(movie_id)})
    if result.deleted_count:
        return {"message": "Movie deleted"}
    return {"error": "Movie not found"}


@app.post("/movies/{movie_id}/book")
async def book_movie(movie_id: str, seats: int = 1):
    if db is None:
        return {"error": "MongoDB не доступна"}

    movie = db.movies.find_one({"_id": ObjectId(movie_id)})
    if not movie:
        return {"error": "Фильм не найден"}

    available = movie.get("available_seats", 0) - len(movie.get("booked_seats", []))
    if seats > available:
        return {"error": f"Только {available} мест доступно"}

    booked_seats = movie.get("booked_seats", [])
    start_seat = len(booked_seats) + 1
    new_seats = list(range(start_seat, start_seat + seats))
    booked_seats.extend(new_seats)

    db.movies.update_one(
        {"_id": ObjectId(movie_id)},
        {"$set": {"booked_seats": booked_seats}}
    )

    return {"message": f"{seats} билет(а/ов) забронировано", "seats": new_seats}
