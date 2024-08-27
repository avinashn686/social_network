# social_network
This repository contains a Django REST framework (DRF) API with PostgreSQL as the database backend. Below are the details and instructions for setting up and using the API.

Installation
Clone this repository to your local machine:
git clone git@github.com:avinashn686/social_network.git
cd social_network

API Endpoints
User Authentication

Signup:

URL: http://127.0.0.1:8000/register/
Method: POST
Body (form data):
username: abc
email: abc@gmail.com
password: abc
first_name: abc
last_name: abc


Login:
URL: http://127.0.0.1:8000/login/
Method: POST
Body (form data):
username: test3
password: test
Token returned in response: Use it in the header as Authorization: Token <your_token>
Logout:
URL: http://127.0.0.1:8000/logout/
Method: POST


Friend Requests

Send Friend Request:
URL: http://localhost:8000/friend-request/send/
Method: POST
Body (raw JSON):
JSON

{
    "receiver_id": 5
}

Accept/Reject Friend Request:

URL: http://localhost:8000/friend-request/respond/
Method: POST
Body (raw JSON):
JSON

{
    "request_id": 1,
    "response": "accepted"
}

User Lists

User List with Search:

URL: http://127.0.0.1:8000/users/?q=abc@gmail.com
Method: GET
Query parameter: q (search query)

Pending Friend Requests List:
URL: http://localhost:8000/friend-requests/pending/
Method: GET

Friend List:
URL: http://localhost:8000/friends/
Method: GET
Remember to include the token returned from the login API in the header as Authorization: Token <your_token> for all authenticated endpoints.

Authentication
All endpoints, except for signup and login, require authentication. You must provide the token returned from the login API in the header as follows:

Authorization: Token <your-token-here>


This `README.md` file provides a comprehensive guide to set up and use the Django REST API project.


Docker
To use Docker, follow these steps:

Install Docker on your system.

Build and run your containers:
docker-compose build
docker-compose up

to run migrations
docker-compose exec web python manage.py makemigrations

docker-compose exec web python manage.py migrate


