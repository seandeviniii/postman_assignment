# Twitter Clone

## Setup local environment

1. Clone the repo by ```git clone https://github.com/himanshuc3/postman_assignment.git```.
2. ```cd postman_assignment```.
3. Create a virtual environment. I did it using ```python3 -m venv venv```.
4. Activate virtual environment by using ```source venv/bin/activate```.
5. Install dependencies by using ```pip install -r requirements.txt```.
6. Run ```export FLASK_APP=twitter_clone.py```. Run the server by ```flask run```.
7. Registration is done using username, email and password. Route ```http://localhost:5000/api/v1/users```. Json structure has to be passed in format  ```{'username': 'one', 'email':'two@gmail.com','password':'password'}```. I did it using httpie cli as ```http POST http://localhost:5000/api/v1/users username=him email=him@g.com password=1234```.
8. Login is done as ```http --auth <username>:<password> POST http://localhost:5000/api/tokens```. We get a token to pass to each authorized route.
9. Use ```http GET http://localhost:5000/api/v1/users/<user_id>``` with authorization token to access users profile.
10. Use ```http GET http://localhost:5000/api/v1/tweet/<int:id>``` with authorization token to get a tweet. Similarly, creating and deleting are made.
11. User ```http POST http://localhost:5000/api/v1/follows``` with json passing follower_id and followed_id to the endpoint.
12. Use ```http DELETE http://localhost:5000/api/tokens Authorization:"Bearer <token>"``` to log out a user and revoke the token.



*NOTE*: Some users and tweets may be present already.