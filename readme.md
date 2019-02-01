# vDef and Agave

## Getting Started

Instructions to run the web application.

### Prerequisites

We first need to install Django.

`$ pip install django`

And install Django crispy forms.

`$ pip install django-crispy-forms`

### Running the web application

Before we can run the server, we need to run the migrations. In the repository run

`$ python manage.py migrate`

You can now run the server with

`$ python manage.py runserver`

You can create an admin account with

`$ python manage.py createsuperuser`