# Movie Booking API

This project is a simple API for managing movies, built with FastAPI and using MongoDB. 
The project is fully containerized with Docker for easy deployment and scalability.

📌 **Features**

- Browse the list of movies via a web page.
- Provides an API to get, add, and delete movies.
- MongoDB availability is checked, and errors are handled gracefully.
- Swagger UI is available for testing the API.

🌐 **Available Pages**

- Main movies page: [http://localhost:8000/](http://localhost:8000/)
- Swagger UI for API: [http://localhost:8000/docs](http://localhost:8000/docs)

🐳 **Running with Docker**

The project uses Docker and Docker Compose. To run it:

```bash
docker-compose up --build
