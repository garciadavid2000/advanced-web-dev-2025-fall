# Task Habit Tracker

### Authors

Ryan Don: 100824494

David Garcia: 100820537

## App Description

The Task Habit Tracker is an app we made to stay on top of recurring tasks we may want to do throughout the week. Say you want to go to the gym on Monday, Wednesday, and Friday.
Our app will neatly lay out all the tasks you have directly in your upcoming week so you don't get overwhelmed, while also encouraging you with a streak system. Not only this, but it also provides you with the option to sync your tasks to Google Calendar so you can easily reference what you have coming up during the week!

![Main Tasks Page](./documentation_screenshots/tasks_page.png)

## How to Run

There are two main ways you can use our app. The first is to visit the link we deployed on Railway (more on that later). Or to run it yourself with docker.

### Deployed Link

To access the deployed link go to [https://advanced-web-dev-2025-fall-production.up.railway.app/](https://advanced-web-dev-2025-fall-production.up.railway.app/)

### Docker Instructions

The second way to run the app is to use docker. The repository has a .env.example provided which you need to populate.

**IMPORTANT:** If you are a TA or the Prof of this class, the exact .env was provided in the .zip that was submitted in canvas with all the keys required.

If you have all the proper variables simply run the following command.

```bash
docker-compose --env-file .env.docker up --build
```

Then you should be able to access the project on `http://localhost:5000`!

## Project Structure



This project follows a Monolithic MVC architecture. The **Next.js** frontend does not compute any authentication and busines logic, that is all handled on the **flask** backend.

Further to this the backend is split into four main sections.

- Controllers
    - Contains the main endpoints split by auth, task, and user
- Services
    - Contains the main business logic for the endpoints and database read/writes
- Models
    - Contains the definitions for all the database tables. This is used to define how the database will be created
- Schemas
    - Uses marshmallow to easily deserialize the models for code readability

![backend structure](./documentation_screenshots/main_backend_structure.png)

### Docker Structure

Initially, the docker structure was setup such that we had three containers.

1. Frontend Container
2. Backend Container
3. Database Container

This setup worked well locally, but we began running into issues when trying do deploy. 

At first, we tried deploying the frontend on Vercel and the backend on Railway, but kept running into CORS issues, even though we explicitly allowed the relevant endpoints.
We then tried moving the frontend and backend as two seperate services on Railway, but that also failed as they still had seperate origins. After hours and hours of ripping our hair out, we
finally realized that the issue was exclusive to Firefox. The CORS policy yielded no issues on Chrome or Edge, but it seems Firefox has a more strict policy.

Given this we decided to change the way our docker was setup to just have two containers.

1. Webapp container
2. Backend container

This also required some changes in the logic in the backend as now we had to setup the dockerfile such that it would first `npm run build` the frontend javascript bundle,
and later copy it into the backend where the backend then serves the frontend files. This solved all our CORS issues.

## Database volume

When running docker compose locally, it creates a `MySQL` container that stores your data and persists it to a volume. You should notice that by default, the .env file for the backend has 
`FLASK_ENV="production"`. This is to help docker identify that it is meant to use the relevant `MySQL` connections in the same .env file.

## Deployment Info

In the previous section I went into detail about the struggles we had with deployment. Here I will go into more detail regarding how our deployment process works.

### CI 
Each feature we make is done on a branch off of main. When we are done with the feature we make a pull request into main. This initializes the CI pipeline that runs all of our tests to make sure our code is working as expected. This allows us to see if there are any problems **before** merging into main. 

### CD
After making sure that the tests all ran, we are then able to merge into main. Once the branch has been merged the testing pipeline is run one more time with the merged codebase
to make sure everything works as expected. If this succeeds, Railway then automatically detects that the pipeline was a success and begins the deployment process.

### Railway
The way we have railway setup is that we have two services.

1. Webapp service
2. Database service

![railway dashboard](./documentation_screenshots/railway_dashboard.png)
![railway webapp](./documentation_screenshots/railway_webapp.png)

The nice thing about Railway is that it automatically detects the Dockerfile and uses that to deploy the container for the service. The only issue is that it does not have support for docker-compose.
We managed to solve this issue by making an instance of a mysql database and then putting the relevant credentials in the environment as you can see in the images above.

## Database Schema

Below is the schema diagram for our database as taken with dbeaver:

![schema diagram](./documentation_screenshots/database_schema.png)

Here is a brief description of what purpose each table serves:

- users

Contains data on uses and securely stores Google Oauth access and refresh tokens.

- tasks 

Contains the general task information like name, streak, and google calendar data for syncing.

- task_occurrences

This table was meant to clearly distinguish between tasks that are meant to be completed on more than one day in the week.

- task_completions

This table is meant to keep track of every single task that has been completed for metrics and debugging.