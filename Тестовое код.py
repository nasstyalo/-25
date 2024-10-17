# -*- coding: utf-8 -*-
"""Тестовое

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1KcayCqLtfcddvVEMDSTCpewxNVOV0vD8
"""

!wget https://ai.stanford.edu/~amaas/data/sentiment/aclImdb_v1.tar.gz

!tar -xvzf aclImdb_v1.tar.gz

!ls aclImdb/train/pos | head

import os

DATA_DIR = "aclImdb"  # Относительный путь в Colab

def load_data(data_dir):
    texts, labels = [], []
    for label_type in ['pos', 'neg']:
        dir_name = os.path.join(data_dir, label_type)
        if not os.path.exists(dir_name):
            raise FileNotFoundError(f"Directory not found: {dir_name}")
        for fname in os.listdir(dir_name):
            if fname.endswith('.txt'):
                with open(os.path.join(dir_name, fname), encoding='utf-8') as f:
                    texts.append(f.read())
                    labels.append(1 if label_type == 'pos' else 0)
    return texts, labels

# Загружаем данные
texts, labels = load_data(os.path.join(DATA_DIR, 'train'))
print(f"Loaded {len(texts)} reviews.")

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer

# Разделение на тренировочные и тестовые данные
X_train, X_test, y_train, y_test = train_test_split(
    texts, labels, test_size=0.2, random_state=42
)

# Векторизация текстов с помощью TF-IDF
vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')
X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

# Обучение модели
model = LogisticRegression(max_iter=100)
model.fit(X_train_tfidf, y_train)

# Предсказание на тестовых данных
y_pred = model.predict(X_test_tfidf)

# Оценка точности модели
accuracy = accuracy_score(y_test, y_pred)
print(f"Test Accuracy: {accuracy * 100:.2f}%")

import joblib

# Сохранение модели и векторизатора
joblib.dump(model, 'model.joblib')
joblib.dump(vectorizer, 'vectorizer.joblib')

print("Model and vectorizer saved.")

# Загрузка модели и векторизатора
model = joblib.load('model.joblib')
vectorizer = joblib.load('vectorizer.joblib')

# Пример отзыва для тестирования
sample_review = ["This movie was absolutely fantastic! The plot was engaging."]
sample_tfidf = vectorizer.transform(sample_review)

# Предсказание
prediction = model.predict(sample_tfidf)[0]
sentiment = 'Positive' if prediction == 1 else 'Negative'

print(f"Sentiment: {sentiment}")

!pip install django joblib pyngrok

!rm -rf movie_review_service

!django-admin startproject movie_review_service

# Commented out IPython magic to ensure Python compatibility.
# %cd /content/movie_review_service/review_classifier

!mkdir templates
with open("templates/review_form.html", "w") as f:
    f.write('''
<!DOCTYPE html>
<html>
<head>
    <title>Movie Review</title>
</head>
<body>
    <h1>Enter your movie review</h1>
    <form method="post">
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit">Submit</button>
    </form>
</body>
</html>
''')
with open("templates/result.html", "w") as f:
    f.write('''
<!DOCTYPE html>
<html>
<head>
    <title>Review Result</title>
</head>
<body>
    <h1>Review Result</h1>
    <p>Rating: {{ rating }}</p>
    <p>Sentiment: {{ sentiment }}</p>
    <a href="/">Submit another review</a>
</body>
</html>
''')
with open("/content/movie_review_service/review_classifier/urls.py", "w") as f:
    f.write('''
from django.urls import path
from . import views

urlpatterns = [
    path('', views.classify_review, name='classify_review'),
]
''')
with open("/content/movie_review_service/movie_review_service/urls.py", "w") as f:
    f.write('''
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('review_classifier.urls')),
]
''')
with open("/content/movie_review_service/review_classifier/forms.py", "w") as f:
    f.write('''
from django import forms

class ReviewForm(forms.Form):
    review = forms.CharField(
        label='Your Review',
        widget=forms.Textarea(attrs={'rows': 5, 'cols': 40})
    )
''')
with open("/content/movie_review_service/review_classifier/views.py", "w") as f:
    f.write('''
from django.shortcuts import render
from .forms import ReviewForm
import joblib

# Загрузка модели и векторизатора
model = joblib.load('/content/model.joblib')
vectorizer = joblib.load('/content/vectorizer.joblib')

def predict_review(text):
    transformed_text = vectorizer.transform([text])
    prediction = model.predict(transformed_text)[0]
    rating = 10 if prediction == 1 else 1
    sentiment = 'Positive' if prediction == 1 else 'Negative'
    return rating, sentiment

def classify_review(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review_text = form.cleaned_data['review']
            rating, sentiment = predict_review(review_text)
            return render(request, 'result.html', {'rating': rating, 'sentiment': sentiment})
    else:
        form = ReviewForm()
    return render(request, 'review_form.html', {'form': form})
''')

!ls -R /content/movie_review_service
!cat /content/movie_review_service/movie_review_service/settings.py

# Django settings for movie_review_service project.

import os
from pathlib import Path

# Определение BASE_DIR без использования __file__
BASE_DIR = Path(os.getcwd()).resolve()

SECRET_KEY = 'django-insecure-*!ef9*h^22wlu2lr^!z#bco9c9^p9g+7(=wdt*_asduq!1sf6_'

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'review_classifier',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'movie_review_service.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'movie_review_service.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

with open('/content/movie_review_service/movie_review_service/settings.py', 'w') as f:
    f.write('''
import os
from pathlib import Path

BASE_DIR = Path(os.getcwd()).resolve()

SECRET_KEY = 'django-insecure-*!ef9*h^22wlu2lr^!z#bco9c9^p9g+7(=wdt*_asduq!1sf6_'

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'review_classifier',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'movie_review_service.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'movie_review_service.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
''')

!python /content/movie_review_service/manage.py migrate
!python /content/movie_review_service/manage.py runserver 0.0.0.0:8000

!apt-get install -y nodejs npm
!npm install -g localtunnel

!python /content/movie_review_service/manage.py runserver 0.0.0.0:8000

!lt --port 8000