                                  **Flask RESTful Application with MongoDB Docker Setup**

This repository contains a Flask RESTful application that uses MongoDB for data storage, and it's set up to run in Docker containers. Follow the instructions below to set up and run the application.

Prerequisites
Before you begin, make sure you have the following software installed on your system:

1.Docker
2.Git (optional, for cloning the repository)

Getting Started

1.Clone this repository (if you haven't already) using Git:
git clone https://github.com/your-username/flask-mongodb-docker.git
Or, you can download the repository as a ZIP file and extract it to your local machine.

2.Change your working directory to the project folder:
cd flask-mongodb-docker

3.Running the Application
Start the Docker containers for the Flask application and MongoDB using Docker Compose:
docker-compose up -d
The -d flag runs the containers in detached mode (in the background).

4.Verify that both containers are running:
docker ps
You should see two containers, one for the Flask application and one for MongoDB.

5.Access the Flask application in your web browser or by using a tool like postman,curl:
http://localhost:5000
The application should be up and running.

6.Stopping the Application
To stop the Docker containers and shut down the application, run the following command in the project directory:
docker-compose down
This will stop and remove the containers, but it won't delete the data in your MongoDB container.

Usage
The Flask application is accessible at http://localhost:5000.
The MongoDB database is available on mongodb://mongodb:27017.
