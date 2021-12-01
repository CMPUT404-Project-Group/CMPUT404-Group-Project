# CMPUT404-Group-Project: Social Distribution

Group Project for CMPUT404; A distributed social networking webapp.

LICENSE'D under the Apache license by Anthony Ma, Dalton Ronan, Xueying Luo, Chase Warwick, Zijian Zhou.

## Connecting

App (frontend) URL: https://social-distribution-t10.herokuapp.com/app/

Api (backend service) URL: https://social-distribution-t10.herokuapp.com/api/

Api documentation: https://social-distribution-t10.herokuapp.com/api/swagger/

Frontend documentation: [here](FrontendDocumentation)

## Development

The app is built with the Django web framework, and as such requires Python. We are using Django 3.2 which requires Python 3.6+.

To run the app, you should create and activate a virtual environment running the correct Python version.

```
virtualenv venv --python=python3.X.X
source venv/bin/activate
```

and install the libraries included in `requirements.txt`.

```
python -m pip install -r requirements.txt
```

Before beginning local development, make sure your database schema is up to date by pulling and running the latest migrations from the `integration` branch.

```
git pull origin integration
python manage.py migrate
```

To run the development server on `localhost:8000`, run the command

```
python manage.py runserver
```

The front-end of the application is seperated in the project app `/app/`.

The back-end and API of the application is located in the project app `/api/`.

Swagger API documentation can be found at `localhost:8000/api/swagger/`
<br>
<br>
<br>
<br>
<br>
<br>
<br>

# CMPUT404-project-socialdistribution

CMPUT404-project-socialdistribution

See project.org (plain-text/org-mode) for a description of the project.

Make a distributed social network!

# Contributing

Send a pull request and be sure to update this file with your name.

# Contributors / Licensing

Generally everything is LICENSE'D under the Apache 2 license by Abram Hindle.

All text is licensed under the CC-BY-SA 4.0 http://creativecommons.org/licenses/by-sa/4.0/deed.en_US

Contributors:

    Karim Baaba
    Ali Sajedi
    Kyle Richelhoff
    Chris Pavlicek
    Derek Dowling
    Olexiy Berjanskii
    Erin Torbiak
    Abram Hindle
    Braedy Kuzma
    Nhan Nguyen
    Anthony Ma
    Xueying Luo
    Zijian Zhou
