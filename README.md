# ku-polls: an Online poll for Kasetsart University

[![build](https://github.com/Halcyon905/ku-polls/actions/workflows/python-app.yml/badge.svg)](https://github.com/Halcyon905/ku-polls/actions/workflows/python-app.yml)
[![codecov](https://codecov.io/gh/Halcyon905/ku-polls/branch/main/graph/badge.svg?token=3CTQ6LKAQP)](https://codecov.io/gh/Halcyon905/ku-polls)

An application for conducting surveys, written in Python using django. This project is based off of [Django Tutorial project][django-tutorial],
with additional functionality.

## How to install and run.
In order to install the application:
1. clone the repo into desired directory
2. find the directory in terminal and run 
    ```sh
    python -m venv env
    ```
3. then run
    ```sh
    . env/Scripts/activate
    ```
4. then to install the requirements run
    ```sh
    pip install -r requirements.txt
    ```
5. exit the environment then use
    ```sh
    deactivate
    ```
6. Now you need to create a ```.env``` file in the project directory. Follow the example file called
sample.env. To generate a secret key go to [this site](https://djecrety.ir/)
7. then to create the database run 
    ```sh
    python manage.py migrate
    ```
8. finally, to load the data run 
    ```sh
    python manage.py loaddata data/polls.json data/users.json
    ```

In order to run the application, run the command:
```sh
python manage.py runserver
```
then you can go to `http://127.0.0.1:8000/` or `http://127.0.0.1:8000/polls` to use the web application.

## Demo Admin
| Username | password |
|----------|----------|
| Admin    | ilikeisp |

## Demo Users
| Username |  password  |
|----------|------------|
| test123  | thisisfine |
| person1  | hello123   |

##  Project Documents

All project documents are in the [Project Wiki](../../wiki/Home)

- [Vision Statement](../../wiki/Vision%20Statement)
- [Requirements](../../wiki/Requirements)
- [Project Plan](../../wiki/Software%20Development%20Plan)
- [Task Board](https://github.com/users/Halcyon905/projects/2/views/1)
- [Iteration 1 Plan](../../wiki/Iteration%201%20Plan)
- [Iteration 2 Plan](../../wiki/Iteration%202%20Plan)
- [Iteration 3 Plan](../../wiki/Iteration%203%20Plan)
- [Iteration 4 Plan](../../wiki/Iteration%204%20Plan)

[django-tutorial]: https://docs.djangoproject.com/en/4.1/intro/tutorial01/
