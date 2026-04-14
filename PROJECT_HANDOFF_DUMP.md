# StudyBuddy Project Handoff Dump

Generated from the local project at `FrontEnd/studybuddy-ui` on 2026-04-11 (timezone: Asia/Manila).

Handoff addendum last updated on 2026-04-14 (timezone: Asia/Manila) to reflect newer system features added after the original dump.

## 1. Project Overview

What does this project do?
StudyBuddy is a web-based peer tutoring platform for university students. It lets tutees register, set preferences, search and book tutors, while tutors manage profiles, subjects, weekly availability, bookings, payments, and recommendation-driven discovery.

Tech stack
- Frontend: JavaScript, Vue 3, Vue Router, Pinia, Axios, Bootstrap 5, Vite
- Backend: Python, Django 6, Django REST Framework, SimpleJWT, django-cors-headers, Pillow, psycopg2-binary
- Data: PostgreSQL (via environment variables / Supabase-hosted Postgres credentials present in `backend/.env`)
- Recommendation modules: custom Python recommender code under `backend/studybuddy/recommender/` using content-based, collaborative-filtering, and hybrid logic

Runtime environment
- Installed Node.js: `v24.14.1`
- `package.json` engine constraint: `^20.19.0 || >=22.12.0`
- Installed Python: `Python 3.14.3`
- Frontend base URL env present: `VITE_API_BASE_URL=http://localhost:8000/api/v1`
- Backend DB/runtime env present in `backend/.env`
## 2. Project Structure

Expanded tree of authored/local project files captured for handoff:

```text
|-- .vscode
|   `-- extensions.json
|-- backend
|   |-- backend
|   |   |-- __init__.py
|   |   |-- asgi.py
|   |   |-- settings.py
|   |   |-- urls.py
|   |   `-- wsgi.py
|   |-- media
|   |   `-- profile_pics
|   |       |-- sql.jpg
|   |       `-- sql_5tVye1Y.jpg
|   |-- studybuddy
|   |   |-- migrations
|   |   |   |-- __init__.py
|   |   |   |-- 0001_initial.py
|   |   |   |-- 0002_userprofile_delete_user.py
|   |   |   |-- 0003_tutor_alter_userprofile_role.py
|   |   |   |-- 0004_subjects.py
|   |   |   |-- 0005_tutorsubjects.py
|   |   |   |-- 0006_tutoravailability.py
|   |   |   |-- 0007_booking.py
|   |   |   |-- 0008_alter_booking_availability_payment.py
|   |   |   |-- 0009_rating.py
|   |   |   |-- 0010_userprofile_bio_userprofile_profile_picture.py
|   |   |   |-- 0011_tutoravailability_day.py
|   |   |   |-- 0012_alter_tutoravailability_tutor.py
|   |   |   |-- 0013_alter_tutoravailability_unique_together_and_more.py
|   |   |   |-- 0014_paymentmethod_payment_method.py
|   |   |   |-- 0015_paymentmethod_code.py
|   |   |   |-- 0016_alter_paymentmethod_code.py
|   |   |   |-- 0017_userprofile_profile_completed.py
|   |   |   |-- 0018_preference.py
|   |   |   |-- 0019_alter_tutor_hourly_rate_alter_tutor_teaching_level.py
|   |   |   |-- 0020_course_strand_alter_userprofile_course_course_strand.py
|   |   |   |-- 0021_remove_preference_hourly_budget_and_more.py
|   |   |   `-- 0022_partnerinstitution_userprofile_institution_and_more.py
|   |   |-- recommender
|   |   |   |-- __init__.py
|   |   |   |-- cbf.py
|   |   |   |-- CF.py
|   |   |   `-- hybrid.py
|   |   |-- __init__.py
|   |   |-- admin.py
|   |   |-- apps.py
|   |   |-- models.py
|   |   |-- serializers.py
|   |   |-- tests.py
|   |   |-- urls.py
|   |   `-- views.py
|   |-- testapp
|   |   |-- migrations
|   |   |   |-- __init__.py
|   |   |   `-- 0001_initial.py
|   |   |-- __init__.py
|   |   |-- admin.py
|   |   |-- apps.py
|   |   |-- models.py
|   |   |-- tests.py
|   |   |-- urls.py
|   |   `-- views.py
|   |-- .env
|   |-- .gitignore
|   |-- {
|   |-- manage.py
|   `-- requirements.txt
|-- public
|   `-- favicon.ico
|-- src
|   |-- assets
|   |   |-- base.css
|   |   |-- hero.png
|   |   |-- logo.svg
|   |   `-- main.css
|   |-- components
|   |   |-- icons
|   |   |   |-- IconCommunity.vue
|   |   |   |-- IconDocumentation.vue
|   |   |   |-- IconEcosystem.vue
|   |   |   |-- IconSupport.vue
|   |   |   `-- IconTooling.vue
|   |   |-- HelloWorld.vue
|   |   |-- TheWelcome.vue
|   |   `-- WelcomeItem.vue
|   |-- router
|   |   `-- index.js
|   |-- services
|   |   |-- api
|   |   |   |-- api.js
|   |   |   |-- registerapi.js
|   |   |   `-- search-tutors.js
|   |   `-- auth
|   |       `-- idleSession.js
|   |-- stores
|   |   |-- auth.js
|   |   |-- bookedSessionDetails.js
|   |   |-- completedSessions.js
|   |   |-- counter.js
|   |   |-- initialbookingprefs.js
|   |   |-- preferences.js
|   |   |-- profile.js
|   |   |-- registrationinfo.js
|   |   |-- selectedSessions.js
|   |   |-- tuteePaymentDetails.js
|   |   |-- tutorBookingDetails.js
|   |   `-- tutorSched.js
|   |-- views
|   |   |-- BookingDetails.vue
|   |   |-- Dashboard.vue
|   |   |-- drive-download-20260305T061413Z-3-001.zip
|   |   |-- FindTutors.vue
|   |   |-- InitialBooking.vue
|   |   |-- LandingPage.vue
|   |   |-- Login.vue
|   |   |-- PaymentScreenTutee.vue
|   |   |-- PreferenceSetup.vue
|   |   |-- Profile.vue
|   |   |-- Register.vue
|   |   |-- Schedule.vue
|   |   |-- SessionsReports.vue
|   |   |-- TestApi.vue
|   |   |-- TuteeProfile.vue
|   |   |-- TutorDashboard.vue
|   |   |-- TutorDetails.vue
|   |   |-- TutorPaymentScreen.vue
|   |   |-- TutorPreferenceSetup.vue
|   |   |-- TutorProfile.vue
|   |   |-- TutorRequestedSessions.vue
|   |   `-- TutorSchedule.vue
|   |-- App.vue
|   `-- main.js
|-- .editorconfig
|-- .env
|-- .gitattributes
|-- .gitignore
|-- .oxlintrc.json
|-- .prettierrc.json
|-- eslint.config.js
|-- index.html
|-- jsconfig.json
|-- package.json
|-- package-lock.json
|-- PROJECT_HANDOFF_DUMP.md
|-- README.md
`-- vite.config.js
```

Additional local/generated directories present but not expanded above because they are dependency or VCS internals rather than authored project files:
- `.git/`
- `node_modules/`
- `backend/venv/`

## 3. Configuration Files

--- .editorconfig ---
```
[*.{js,jsx,mjs,cjs,ts,tsx,mts,cts,vue,css,scss,sass,less,styl}]
charset = utf-8
indent_size = 2
indent_style = space
insert_final_newline = true
trim_trailing_whitespace = true
end_of_line = lf
max_line_length = 100
```

--- .env ---
```
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

--- .gitattributes ---
```
* text=auto eol=lf
```

--- .gitignore ---
```
# Logs
logs
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*
lerna-debug.log*

node_modules
.DS_Store
dist
dist-ssr
coverage
*.local

# Editor directories and files
.vscode/*
!.vscode/extensions.json
.idea
*.suo
*.ntvs*
*.njsproj
*.sln
*.sw?

*.tsbuildinfo

.eslintcache

# Cypress
/cypress/videos/
/cypress/screenshots/

# Vitest
__screenshots__/

# Vite
*.timestamp-*-*.mjs
```

--- .oxlintrc.json ---
```
{
  "$schema": "./node_modules/oxlint/configuration_schema.json",
  "plugins": ["eslint", "unicorn", "oxc", "vue"],
  "env": {
    "browser": true
  },
  "categories": {
    "correctness": "error"
  }
}
```

--- .prettierrc.json ---
```
{
  "$schema": "https://json.schemastore.org/prettierrc",
  "semi": false,
  "singleQuote": true,
  "printWidth": 100
}
```

--- .vscode/extensions.json ---
```
{
  "recommendations": [
    "Vue.volar",
    "dbaeumer.vscode-eslint",
    "EditorConfig.EditorConfig",
    "oxc.oxc-vscode",
    "esbenp.prettier-vscode"
  ]
}
```

--- backend/.env ---
```
DB_NAME=postgres
DB_USER=postgres.roptktljurzhmervwsxn
DB_PASSWORD=INvF86uUu5MZThBS
DB_HOST=aws-1-ap-southeast-1.pooler.supabase.com
DB_PORT=5432

psql "postgresql://postgres.roptktljurzhmervwsxn:bp7tThvnbepyqv6e@aws-1-ap-southeast-1.pooler.supabase.com:5432/postgres" -f studybuddy_backup.sql

psql "postgresql://postgres.roptktljurzhmervwsxn:YOUR_PASSWORD@aws-1-ap-southeast-1.pooler.supabase.com:5432/postgres" -f studybuddy_backup.sql
```

--- backend/.gitignore ---
```
# Python
__pycache__/
*.pyc
*.pyo
*.pyd

# Virtual env
venv/
.env

# Django
db.sqlite3
```

--- backend/backend/settings.py ---
```
"""
Django settings for backend project.

Generated by 'django-admin startproject' using Django 6.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/6.0/ref/settings/
"""
from datetime import timedelta
from dotenv import load_dotenv
from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-p@^2u1gzwyov3&bo_2td(e8i-#m3(97ai@f^jg$l&k-0e%+fhc'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
}
# Application definition

INSTALLED_APPS = [
    'rest_framework',
    'corsheaders',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'testapp',
    'studybuddy',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases


""" 
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'studybuddy_db',
        'USER': 'postgres',
        'PASSWORD':'sysadmin2003',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
"""


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}

# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = 'static/'
CORS_ALLOW_ALL_ORIGINS = True

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

--- backend/requirements.txt ---
```
asgiref==3.11.1
Django==6.0.2
django-cors-headers==4.9.0
djangorestframework==3.16.1
djangorestframework_simplejwt==5.5.1
pillow==12.1.1
python-dotenv==1.1.1
psycopg2-binary==2.9.11
PyJWT==2.12.1
sqlparse==0.5.5
tzdata==2025.3
```

--- eslint.config.js ---
```
import { defineConfig, globalIgnores } from 'eslint/config'
import globals from 'globals'
import js from '@eslint/js'
import pluginVue from 'eslint-plugin-vue'
import pluginOxlint from 'eslint-plugin-oxlint'
import skipFormatting from 'eslint-config-prettier/flat'

export default defineConfig([
  {
    name: 'app/files-to-lint',
    files: ['**/*.{vue,js,mjs,jsx}'],
  },

  globalIgnores(['**/dist/**', '**/dist-ssr/**', '**/coverage/**']),

  {
    languageOptions: {
      globals: {
        ...globals.browser,
      },
    },
  },

  js.configs.recommended,
  ...pluginVue.configs['flat/essential'],
  {
    rules: {
      'vue/multi-word-component-names': 'off'
    }
  },

  ...pluginOxlint.buildFromOxlintConfigFile('.oxlintrc.json'),

  skipFormatting,
])
```

--- index.html ---
```
<!DOCTYPE html>
<html lang="">
  <head>
    <meta charset="UTF-8">
    <link rel="icon" href="/favicon.ico">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vite App</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.js"></script>
  </body>
</html>
```

--- jsconfig.json ---
```
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "exclude": ["node_modules", "dist"]
}
```

--- package-lock.json ---
Summary only because this file exceeds 300 lines (4846 lines).

This is the generated npm lockfile for the Vue/Vite frontend. It pins the exact resolved dependency graph and integrity hashes for the packages declared in package.json, including Vue 3, Vue Router, Pinia, Axios, Bootstrap, Vite, ESLint, Prettier, and their transitive dependencies. No hand-written application logic appears here.

--- package.json ---
```
{
  "name": "studybuddy-ui",
  "version": "0.0.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "lint": "run-s lint:*",
    "lint:oxlint": "oxlint . --fix",
    "lint:eslint": "eslint . --fix --cache",
    "format": "prettier --write --experimental-cli src/"
  },
  "dependencies": {
    "@popperjs/core": "^2.11.8",
    "axios": "^1.13.5",
    "bootstrap": "^5.3.8",
    "bootstrap-icons": "^1.13.1",
    "pinia": "^3.0.4",
    "vue": "^3.5.27",
    "vue-router": "^5.0.3"
  },
  "devDependencies": {
    "@eslint/js": "^9.39.2",
    "@vitejs/plugin-vue": "^6.0.3",
    "eslint": "^9.39.2",
    "eslint-config-prettier": "^10.1.8",
    "eslint-plugin-oxlint": "~1.42.0",
    "eslint-plugin-vue": "~10.7.0",
    "globals": "^17.3.0",
    "npm-run-all2": "^8.0.4",
    "oxlint": "~1.42.0",
    "prettier": "3.8.1",
    "vite": "^7.3.1",
    "vite-plugin-vue-devtools": "^8.0.5"
  },
  "engines": {
    "node": "^20.19.0 || >=22.12.0"
  }
}
```

--- vite.config.js ---
```
import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
})
```

pyproject.toml: N/A

.env.example: N/A

docker-compose.yml / docker-compose.yaml: N/A

## 4. Full Source Code

--- backend/{ ---
```
(empty file)
```

--- backend/backend/__init__.py ---
```
(empty file)
```

--- backend/backend/asgi.py ---
```
"""
ASGI config for backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

application = get_asgi_application()
```

--- backend/backend/urls.py ---
```
"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
"""from django.contrib import admin
from django.urls import path

urlpatterns = [

    path('admin/', admin.site.urls),
]
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('studybuddy.urls')),
]
```

--- backend/backend/wsgi.py ---
```
"""
WSGI config for backend project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

application = get_wsgi_application()
```

--- backend/manage.py ---
```
#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
```

--- backend/studybuddy/__init__.py ---
```
(empty file)
```

--- backend/studybuddy/admin.py ---
```
from django.contrib import admin
from .models import (
    Booking,
    Course,
    PartnerInstitution,
    Payment,
    PaymentMethod,
    Preference,
    Rating,
    Strand,
    Subjects,
    Tutor,
    TutorAvailability,
    TutorSubjects,
    UserProfile,
)

admin.site.register(UserProfile)
admin.site.register(Tutor)
admin.site.register(TutorAvailability)
admin.site.register(Booking)
admin.site.register(Payment)
admin.site.register(Rating)
admin.site.register(Subjects)
admin.site.register(TutorSubjects)
admin.site.register(PaymentMethod)
admin.site.register(Preference)
admin.site.register(Strand)
admin.site.register(Course)


@admin.register(PartnerInstitution)
class PartnerInstitutionAdmin(admin.ModelAdmin):
    list_display = ('institution_name', 'school_email_domain', 'is_active', 'contact_person', 'date_added')
    list_filter = ('is_active', 'date_added')
    search_fields = ('institution_name', 'school_email_domain', 'contact_person')
```

--- backend/studybuddy/apps.py ---
```
from django.apps import AppConfig


class StudybuddyConfig(AppConfig):
    name = 'studybuddy'
```

--- backend/studybuddy/migrations/__init__.py ---
```
(empty file)
```

--- backend/studybuddy/migrations/0001_initial.py ---
```
# Generated by Django 6.0.2 on 2026-02-23 14:05

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='user',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('password', models.CharField(max_length=255)),
                ('role', models.CharField(max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
```

--- backend/studybuddy/migrations/0002_userprofile_delete_user.py ---
```
# Generated by Django 6.0.2 on 2026-02-23 16:09

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fname', models.CharField(max_length=100)),
                ('mname', models.CharField(blank=True, max_length=100)),
                ('lname', models.CharField(max_length=100)),
                ('course', models.CharField(blank=True, max_length=100)),
                ('year_level', models.IntegerField(blank=True, null=True)),
                ('role', models.CharField(max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.DeleteModel(
            name='user',
        ),
    ]
```

--- backend/studybuddy/migrations/0003_tutor_alter_userprofile_role.py ---
```
# Generated by Django 6.0.2 on 2026-02-24 21:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0002_userprofile_delete_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tutor',
            fields=[
                ('profile', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='studybuddy.userprofile')),
                ('teaching_level', models.CharField(max_length=100)),
                ('can_online', models.BooleanField(default=True)),
                ('can_f2f', models.BooleanField(default=False)),
                ('rating_average', models.FloatField(default=0)),
                ('hourly_rate', models.DecimalField(decimal_places=2, max_digits=8)),
                ('total_sessions', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='role',
            field=models.CharField(choices=[('Tutee', 'Tutee'), ('Tutor', 'Tutor'), ('Admin', 'Admin')], max_length=20),
        ),
    ]
```

--- backend/studybuddy/migrations/0004_subjects.py ---
```
# Generated by Django 6.0.2 on 2026-02-24 21:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0003_tutor_alter_userprofile_role'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subjects',
            fields=[
                ('subject_code', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('subject_name', models.CharField(max_length=100)),
                ('department', models.CharField(max_length=100)),
            ],
        ),
    ]
```

--- backend/studybuddy/migrations/0005_tutorsubjects.py ---
```
# Generated by Django 6.0.2 on 2026-02-25 14:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0004_subjects'),
    ]

    operations = [
        migrations.CreateModel(
            name='TutorSubjects',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('expertise_level', models.IntegerField()),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='studybuddy.subjects')),
                ('tutor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='studybuddy.tutor')),
            ],
        ),
    ]
```

--- backend/studybuddy/migrations/0006_tutoravailability.py ---
```
# Generated by Django 6.0.2 on 2026-02-25 14:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0005_tutorsubjects'),
    ]

    operations = [
        migrations.CreateModel(
            name='TutorAvailability',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day_of_week', models.CharField(choices=[('Mon', 'Monday'), ('Tue', 'Tuesday'), ('Wed', 'Wednesday'), ('Thu', 'Thursday'), ('Fri', 'Friday'), ('Sat', 'Saturday'), ('Sun', 'Sunday')], max_length=3)),
                ('time_slot', models.TimeField()),
                ('is_active', models.BooleanField(default=False)),
                ('is_booked', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('tutor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='availabilities', to='studybuddy.tutor')),
            ],
            options={
                'unique_together': {('tutor', 'day_of_week', 'time_slot')},
            },
        ),
    ]
```

--- backend/studybuddy/migrations/0007_booking.py ---
```
# Generated by Django 6.0.2 on 2026-02-25 15:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0006_tutoravailability'),
    ]

    operations = [
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_date', models.DateField()),
                ('session_mode', models.CharField(choices=[('Online', 'Online'), ('F2F', 'Face-to-Face')], max_length=10)),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Confirmed', 'Confirmed'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled')], default='Pending', max_length=15)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('availability', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='studybuddy.tutoravailability')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_bookings', to='studybuddy.userprofile')),
                ('tutor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tutor_bookings', to='studybuddy.tutor')),
            ],
        ),
    ]
```

--- backend/studybuddy/migrations/0008_alter_booking_availability_payment.py ---
```
# Generated by Django 6.0.2 on 2026-02-25 15:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0007_booking'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='availability',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='studybuddy.tutoravailability'),
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('payment_status', models.CharField(choices=[('Pending', 'Pending'), ('Paid', 'Paid'), ('Failed', 'Failed'), ('Refunded', 'Refunded')], default='Pending', max_length=10)),
                ('transaction_reference', models.CharField(blank=True, max_length=100, null=True)),
                ('paid_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('booking', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='payment', to='studybuddy.booking')),
            ],
        ),
    ]
```

--- backend/studybuddy/migrations/0009_rating.py ---
```
# Generated by Django 6.0.2 on 2026-02-25 18:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0008_alter_booking_availability_payment'),
    ]

    operations = [
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating_score', models.IntegerField()),
                ('comment', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('booking', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='rating', to='studybuddy.booking')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='studybuddy.userprofile')),
                ('tutor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ratings', to='studybuddy.tutor')),
            ],
        ),
    ]
```

--- backend/studybuddy/migrations/0010_userprofile_bio_userprofile_profile_picture.py ---
```
# Generated by Django 6.0.2 on 2026-02-27 19:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0009_rating'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='bio',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='profile_picture',
            field=models.ImageField(blank=True, null=True, upload_to='profile_pics/'),
        ),
    ]
```

--- backend/studybuddy/migrations/0011_tutoravailability_day.py ---
```
# Generated by Django 6.0.2 on 2026-02-27 20:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0010_userprofile_bio_userprofile_profile_picture'),
    ]

    operations = [
        migrations.AddField(
            model_name='tutoravailability',
            name='day',
            field=models.CharField(choices=[('Mon', 'Monday'), ('Tue', 'Tuesday'), ('Wed', 'Wednesday'), ('Thu', 'Thursday'), ('Fri', 'Friday'), ('Sat', 'Saturday'), ('Sun', 'Sunday')], default='Mon', max_length=3),
            preserve_default=False,
        ),
    ]
```

--- backend/studybuddy/migrations/0012_alter_tutoravailability_tutor.py ---
```
# Generated by Django 6.0.2 on 2026-02-27 20:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0011_tutoravailability_day'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tutoravailability',
            name='tutor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='studybuddy.tutor'),
        ),
    ]
```

--- backend/studybuddy/migrations/0013_alter_tutoravailability_unique_together_and_more.py ---
```
# Generated by Django 6.0.2 on 2026-02-28 20:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0012_alter_tutoravailability_tutor'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='tutoravailability',
            unique_together={('tutor', 'day', 'time_slot')},
        ),
        migrations.AlterField(
            model_name='booking',
            name='availability',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to='studybuddy.tutoravailability'),
        ),
        migrations.AlterUniqueTogether(
            name='booking',
            unique_together={('availability', 'session_date')},
        ),
        migrations.RemoveField(
            model_name='tutoravailability',
            name='day_of_week',
        ),
    ]
```

--- backend/studybuddy/migrations/0014_paymentmethod_payment_method.py ---
```
# Generated by Django 6.0.2 on 2026-03-03 13:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0013_alter_tutoravailability_unique_together_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentMethod',
            fields=[
                ('method_id', models.AutoField(primary_key=True, serialize=False)),
                ('method_name', models.CharField(max_length=50)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AddField(
            model_name='payment',
            name='method',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='payments', to='studybuddy.paymentmethod'),
        ),
    ]
```

--- backend/studybuddy/migrations/0015_paymentmethod_code.py ---
```
# Generated by Django 6.0.2 on 2026-03-03 13:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0014_paymentmethod_payment_method'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentmethod',
            name='code',
            field=models.CharField(blank=True, choices=[('CASH', 'Cash'), ('GCASH', 'GCash'), ('BANK', 'Bank Transfer')], max_length=20, null=True, unique=True),
        ),
    ]
```

--- backend/studybuddy/migrations/0016_alter_paymentmethod_code.py ---
```
# Generated by Django 6.0.2 on 2026-03-03 13:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0015_paymentmethod_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymentmethod',
            name='code',
            field=models.CharField(choices=[('CASH', 'Cash'), ('GCASH', 'GCash'), ('BANK', 'Bank Transfer')], max_length=20, unique=True),
        ),
    ]
```

--- backend/studybuddy/migrations/0017_userprofile_profile_completed.py ---
```
# Generated by Django 6.0.2 on 2026-03-04 08:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0016_alter_paymentmethod_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='profile_completed',
            field=models.BooleanField(default=False),
        ),
    ]
```

--- backend/studybuddy/migrations/0018_preference.py ---
```
# Generated by Django 6.0.2 on 2026-03-04 09:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0017_userprofile_profile_completed'),
    ]

    operations = [
        migrations.CreateModel(
            name='Preference',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('preferred_mode', models.CharField(choices=[('Online', 'Online'), ('F2F', 'Face-to-Face')], max_length=10)),
                ('hourly_budget', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('subjects', models.ManyToManyField(to='studybuddy.subjects')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='studybuddy.userprofile')),
            ],
        ),
    ]
```

--- backend/studybuddy/migrations/0019_alter_tutor_hourly_rate_alter_tutor_teaching_level.py ---
```
# Generated by Django 6.0.2 on 2026-03-04 10:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0018_preference'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tutor',
            name='hourly_rate',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True),
        ),
        migrations.AlterField(
            model_name='tutor',
            name='teaching_level',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
```

--- backend/studybuddy/migrations/0020_course_strand_alter_userprofile_course_course_strand.py ---
```
# Generated by Django 6.0.2 on 2026-03-04 15:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0019_alter_tutor_hourly_rate_alter_tutor_teaching_level'),
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('course_code', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('course_name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Strand',
            fields=[
                ('strand_code', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('strand_name', models.CharField(max_length=100)),
            ],
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='course',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='studybuddy.course'),
        ),
        migrations.AddField(
            model_name='course',
            name='strand',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='studybuddy.strand'),
        ),
    ]
```

--- backend/studybuddy/migrations/0021_remove_preference_hourly_budget_and_more.py ---
```
# Generated by Django 6.0.2 on 2026-03-05 09:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0020_course_strand_alter_userprofile_course_course_strand'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='preference',
            name='hourly_budget',
        ),
        migrations.RemoveField(
            model_name='preference',
            name='preferred_mode',
        ),
    ]
```

--- backend/studybuddy/migrations/0022_partnerinstitution_userprofile_institution_and_more.py ---
```
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0021_remove_preference_hourly_budget_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='PartnerInstitution',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('institution_name', models.CharField(max_length=255)),
                ('school_email_domain', models.CharField(max_length=255, unique=True)),
                ('is_active', models.BooleanField(default=True)),
                ('contact_person', models.CharField(blank=True, max_length=255)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['institution_name'],
            },
        ),
        migrations.AddField(
            model_name='userprofile',
            name='institution',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='studybuddy.partnerinstitution'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='is_domain_exempt',
            field=models.BooleanField(default=False),
        ),
    ]
```

--- backend/studybuddy/models.py ---
```
from django.db import models
from django.contrib.auth.models import User ### allows the use of auth user model for authentication and user management


# Create your models here.

class Strand(models.Model):

    strand_code = models.CharField(max_length=10, primary_key=True)
    strand_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.strand_code} - {self.strand_name}"
    
class Course(models.Model):

    course_code = models.CharField(max_length=20, primary_key=True)
    course_name = models.CharField(max_length=100)

    strand = models.ForeignKey(
        Strand,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.course_code} - {self.course_name}"


class PartnerInstitution(models.Model):
    institution_name = models.CharField(max_length=255)
    school_email_domain = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    contact_person = models.CharField(max_length=255, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['institution_name']

    def __str__(self):
        return f"{self.institution_name} ({self.school_email_domain})"



class UserProfile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    fname = models.CharField(max_length=100)
    mname = models.CharField(max_length=100, blank=True)
    lname = models.CharField(max_length=100)

    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    year_level = models.IntegerField(null=True, blank=True)

    bio = models.TextField(blank=True, null=True)

    profile_completed = models.BooleanField(default=False)

    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        blank=True,
        null=True
    )

    institution = models.ForeignKey(
        PartnerInstitution,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    is_domain_exempt = models.BooleanField(default=False)

    ROLE_CHOICES = [
        ('Tutee', 'Tutee'),
        ('Tutor', 'Tutor'),
        ('Admin', 'Admin'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.fname} {self.lname}"
    
#TUTOR TABLE
class Tutor(models.Model):

    profile = models.OneToOneField(
        UserProfile,
        on_delete=models.CASCADE,
        primary_key=True
    )

    # Tutor setup fields (filled later)
    teaching_level = models.CharField(max_length=100, null=True, blank=True)

    can_online = models.BooleanField(default=True)
    can_f2f = models.BooleanField(default=False)

    rating_average = models.FloatField(default=0)

    hourly_rate = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True
    )

    total_sessions = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Tutor: {self.profile.fname} {self.profile.lname}"

#Subjects Table 
class Subjects(models.Model):
    subject_code = models.CharField(max_length=20, primary_key=True)
    subject_name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.subject_code} - {self.subject_name}"
    
#Tutor Subjects Table

class TutorSubjects(models.Model):
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subjects, on_delete=models.CASCADE)
    
    expertise_level = models.IntegerField()  # e.g., Beginner, Intermediate, Advanced

    def __str__(self):
        return f"{self.tutor.profile.fname} {self.tutor.profile.lname} - {self.subject.subject_code}"


class TutorAvailability(models.Model):

    DAY_CHOICES = [
        ('Mon', 'Monday'),
        ('Tue', 'Tuesday'),
        ('Wed', 'Wednesday'),
        ('Thu', 'Thursday'),
        ('Fri', 'Friday'),
        ('Sat', 'Saturday'),
        ('Sun', 'Sunday'),
    ]

    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    day = models.CharField(max_length=3, choices=DAY_CHOICES)
    time_slot = models.TimeField()
    is_active = models.BooleanField(default=False)   # tutor toggles this
    is_booked = models.BooleanField(default=False)   # system controls this

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('tutor', 'day', 'time_slot')

    def __str__(self):
        return f"{self.tutor.profile.fname} - {self.day} {self.time_slot}"
    
class Booking(models.Model):

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    student = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="student_bookings"
    )

    tutor = models.ForeignKey(
        Tutor,
        on_delete=models.CASCADE,
        related_name="tutor_bookings"
    )

    availability = models.ForeignKey(
        TutorAvailability,
        on_delete=models.CASCADE,
        related_name="bookings"
    )

    session_date = models.DateField()

    session_mode = models.CharField(
        max_length=10,
        choices=[('Online', 'Online'), ('F2F', 'Face-to-Face')]
    )

    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default="Pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('availability', 'session_date')

class PaymentMethod(models.Model):

    METHOD_CODES = [
        ('CASH', 'Cash'),
        ('GCASH', 'GCash'),
        ('BANK', 'Bank Transfer'),
    ]

    method_id = models.AutoField(primary_key=True)

    code = models.CharField(             
        max_length=20,
        choices=METHOD_CODES,
        unique=True,
    )

    method_name = models.CharField(max_length=50)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.method_name} ({self.code})"

class Payment(models.Model):

    PAYMENT_STATUS = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Failed', 'Failed'),
        ('Refunded', 'Refunded'),
    ]

    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        related_name="payment"
    )

    method = models.ForeignKey(        # âœ… FK to PAYMENT_METHODS
        PaymentMethod,
        on_delete=models.SET_NULL,
        null=True,
        related_name="payments"
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    payment_status = models.CharField(
        max_length=10,
        choices=PAYMENT_STATUS,
        default='Pending'
    )

    transaction_reference = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    paid_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for Booking {self.booking.id} - {self.payment_status}"
    
class Rating(models.Model):

    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        related_name="rating"
    )

    student = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE
    )

    tutor = models.ForeignKey(
        Tutor,
        on_delete=models.CASCADE,
        related_name="ratings"
    )

    rating_score = models.IntegerField()  # 1â€“5

    comment = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.rating_score} â­ for {self.tutor.profile.fname}"
    
class Preference(models.Model):

    MODE_CHOICES = [
        ('Online', 'Online'),
        ('F2F', 'Face-to-Face'),
    ]

    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE)

    subjects = models.ManyToManyField(Subjects)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Preferences for {self.user.fname}"
```

--- backend/studybuddy/recommender/__init__.py ---
```
(empty file)
```

--- backend/studybuddy/recommender/cbf.py ---
```
from ..models import (
    Preference,
    Tutor,
    TutorSubjects
)

# -----------------------------
# WEIGHTS
# -----------------------------

W_SUBJECT = 0.35
W_EXPERTISE = 0.20
W_COURSE = 0.20
W_YEAR = 0.15
W_LEVEL = 0.10


# -----------------------------
# COMPUTE CBF SCORE
# -----------------------------

def compute_cbf_score(student_profile, tutor, requested_subject):

    print("\n==============================")
    print("Running CBF for Tutor:", tutor.profile.fname, tutor.profile.lname)

    # -----------------------------
    # STUDENT DATA
    # -----------------------------

    student_course = student_profile.course
    student_year = student_profile.year_level

    try:
        pref = Preference.objects.get(user=student_profile)

        student_subjects = list(
            pref.subjects.values_list("subject_code", flat=True)
        )

    except Preference.DoesNotExist:
        student_subjects = []

    # Add requested booking subject
    if requested_subject and requested_subject not in student_subjects:
        student_subjects.append(requested_subject)

    print("Student Subjects:", student_subjects)


    # -----------------------------
    # TUTOR DATA
    # -----------------------------

    tutor_profile = tutor.profile
    tutor_course = tutor_profile.course
    tutor_year = tutor_profile.year_level
    tutor_level = tutor.teaching_level

    tutor_subjects = TutorSubjects.objects.filter(tutor=tutor)

    tutor_subject_codes = [
        ts.subject.subject_code for ts in tutor_subjects
    ]

    print("Tutor Subjects:", tutor_subject_codes)


    # -----------------------------
    # SUBJECT MATCH + EXPERTISE
    # -----------------------------

    matching_expertise = []

    for ts in tutor_subjects:

        if ts.subject.subject_code in student_subjects:

            matching_expertise.append(ts.expertise_level)

    if matching_expertise:

        s_subject = 1
        ex_ave = sum(matching_expertise) / len(matching_expertise)
        s_expertise = ex_ave / 5

    else:

        s_subject = 0
        s_expertise = 0

    print("Subject Match Score:", s_subject)
    print("Expertise Score:", round(s_expertise, 3))


    # -----------------------------
    # COURSE SIMILARITY
    # -----------------------------

    s_course = 0

    if student_course == tutor_course:

        s_course = 1

    elif (
        student_course
        and tutor_course
        and student_course.strand == tutor_course.strand
    ):

        s_course = 0.5

    print("Course Score:", s_course)


    # -----------------------------
    # YEAR SIMILARITY
    # -----------------------------

    if student_year and tutor_year:

        year_diff = abs(student_year - tutor_year)
        s_year = 1 / (1 + year_diff)

    else:

        s_year = 0

    print("Year Score:", round(s_year, 3))


    # -----------------------------
    # TEACHING LEVEL RULE
    # -----------------------------

    s_level = 1

    if tutor_level == "SHS" and int(student_year) > 12:
        s_level = 0

    print("Teaching Level Score:", s_level)


    # -----------------------------
    # FINAL SCORE
    # -----------------------------

    score = (
        W_SUBJECT * s_subject +
        W_EXPERTISE * s_expertise +
        W_COURSE * s_course +
        W_YEAR * s_year +
        W_LEVEL * s_level
    )

    print("FINAL SCORE:", round(score, 3))
    print("==============================")

    return score


# -----------------------------
# RECOMMEND TUTORS
# -----------------------------

def recommend_tutors(student_profile, subject=None, preferred_mode=None):

    print("\n===== STARTING CBF RECOMMENDER =====")

    tutors = Tutor.objects.all().select_related("profile")

    # -----------------------------
    # FILTER BY MODE
    # -----------------------------

    if preferred_mode == "Online":
        tutors = tutors.filter(can_online=True)

    if preferred_mode == "Face-to-face":
        tutors = tutors.filter(can_f2f=True)

    results = []

    for tutor in tutors:

        score = compute_cbf_score(
            student_profile,
            tutor,
            subject
        )

        results.append({
            "tutor": tutor,
            "score": score
        })

    # Sort highest score first
    results.sort(key=lambda x: x["score"], reverse=True)

    print("===== RECOMMENDER FINISHED =====\n")

    return results
```

--- backend/studybuddy/recommender/CF.py ---
```
from collections import defaultdict
from ..models import Rating, Tutor
import math


# -----------------------------
# BUILD RATING MATRIX
# -----------------------------
def build_rating_matrix():

    ratings = defaultdict(dict)

    all_ratings = Rating.objects.select_related(
        "student",
        "tutor"
    )

    for r in all_ratings:

        student_id = r.student.id
        tutor_id = r.tutor.profile_id

        ratings[student_id][tutor_id] = r.rating_score

    return ratings


# -----------------------------
# PEARSON SIMILARITY
# -----------------------------
def sim(ratings, u, v):

    common = set(ratings[u]) & set(ratings[v])

    if not common:
        return 0

    u_avg = sum(ratings[u][i] for i in common) / len(common)
    v_avg = sum(ratings[v][i] for i in common) / len(common)

    numerator = sum(
        (ratings[u][i] - u_avg) *
        (ratings[v][i] - v_avg)
        for i in common
    )

    den1 = math.sqrt(
        sum((ratings[u][i] - u_avg) ** 2 for i in common)
    )

    den2 = math.sqrt(
        sum((ratings[v][i] - v_avg) ** 2 for i in common)
    )

    if den1 * den2 == 0:
        return 0

    return numerator / (den1 * den2)


# -----------------------------
# FIND TOP-K NEIGHBORS
# -----------------------------
def top_k(ratings, student_id, k=5):

    similarities = []

    for other_student in ratings:

        if other_student == student_id:
            continue

        similarity = sim(ratings, student_id, other_student)
            
       # if similarity >= 0:
           # similarities.append(other_student,similarity)
            
        similarities.append((other_student,similarity))

    similarities.sort(key=lambda x: x[1], reverse=True)

    return similarities[:k]


# -----------------------------
# PREDICT RATING
# -----------------------------
def compute_cf_score(ratings, student_id, tutor_id, k=5):

    if student_id not in ratings:
        return None

    neighbors = top_k(ratings, student_id, k)

    numerator = 0
    denominator = 0

    student_avg = sum(ratings[student_id].values()) / len(ratings[student_id])

    for neighbor, similarity in neighbors:

        if tutor_id not in ratings.get(neighbor, {}):
            continue

        neighbor_avg = sum(ratings[neighbor].values()) / len(ratings[neighbor])

        numerator += similarity * (
            ratings[neighbor][tutor_id] - neighbor_avg
        )

        denominator += abs(similarity)

    if denominator == 0:
        return None

    return student_avg + (numerator / denominator)


# -----------------------------
# RECOMMEND TUTORS
# -----------------------------
def recommend_tutors_cf(student_profile, k=5):

    ratings = build_rating_matrix()

    student_id = student_profile.id

    tutors = Tutor.objects.all()

    results = []

    for tutor in tutors:

        tutor_id = tutor.profile_id

        # skip tutors already rated
        if tutor_id in ratings.get(student_id, {}):
            continue

        score = compute_cf_score(ratings, student_id, tutor_id, k)

        if score is not None:

            results.append({
                "tutor": tutor,
                "score": score
            })

    results.sort(key=lambda x: x["score"], reverse=True)

    return results
```

--- backend/studybuddy/recommender/hybrid.py ---
```
from ..models import Tutor
from .CF import compute_cf_score
from .cbf import compute_cbf_score


# ---------------------------------------------
# HYBRID SCORE FOR ONE TUTOR
# ---------------------------------------------
def hybrid_prediction(ratings, student_profile, tutor, requested_subject):

    # -----------------------------
    # CBF SCORE
    # -----------------------------
    cbf_score = compute_cbf_score(
        student_profile,
        tutor,
        requested_subject
    )

    # -----------------------------
    # CF SCORE
    # -----------------------------
    tutor_id = tutor.profile_id

    cf_score = compute_cf_score(
        ratings,
        student_profile.id,
        tutor_id
    )

    if cf_score is None:
        cf_score = 0

    # -----------------------------
    # HYBRID SCORE
    # -----------------------------
    hybrid_score = (0.7 * cbf_score) + (0.3 * (cf_score / 5))

    # -----------------------------
    # DEBUG OUTPUT
    # -----------------------------
    print("\n-----------------------------------")
    print(f"Tutor: {tutor.profile.fname} {tutor.profile.lname}")
    print(f"CBF Score: {cbf_score:.3f}")
    print(f"CF Score: {cf_score:.3f}")
    print(f"Hybrid Score: {hybrid_score:.3f}")
    print("-----------------------------------")

    return hybrid_score


# ---------------------------------------------
# HYBRID RECOMMENDATION LIST
# ---------------------------------------------
def recommend_tutors_hybrid(ratings, student_profile, requested_subject):

    tutors = Tutor.objects.select_related("profile")

    recommendations = []

    for tutor in tutors:

        score = hybrid_prediction(
            ratings,
            student_profile,
            tutor,
            requested_subject
        )

        recommendations.append({
            "tutor": tutor,
            "score": score
        })

    # Sort tutors by score
    recommendations.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    # -----------------------------
    # PRINT FINAL RANKING
    # -----------------------------
    print("\n===================================")
    print("FINAL HYBRID RANKING")
    print("===================================")

    for i, r in enumerate(recommendations[:10], start=1):

        tutor = r["tutor"]
        score = r["score"]

        print(
            f"{i}. {tutor.profile.fname} {tutor.profile.lname} â€” Score: {score:.3f}"
        )

    print("===================================\n")

    return recommendations
```

--- backend/studybuddy/serializers.py ---
```

from rest_framework import serializers
from .models import Tutor, Subjects, TutorAvailability,Preference

# Create Serializers here.

class TutorSearchSerializer(serializers.ModelSerializer):

    fname = serializers.CharField(source='profile.fname')
    lname = serializers.CharField(source='profile.lname')

    class Meta:
        model = Tutor
        fields = [
            'profile_id',
            'fname',
            'lname',
            'rating_average',
            'hourly_rate',
            'total_sessions'
        ]

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subjects
        fields = ['subject_code', 'subject_name', 'department']


class TutorDetailSerializer(serializers.ModelSerializer):

    fname = serializers.CharField(source='profile.fname')
    lname = serializers.CharField(source='profile.lname')
    bio = serializers.CharField(source='profile.bio', allow_null=True)

    class Meta:
        model = Tutor
        fields = [
            'profile_id',
            'fname',
            'lname',
            'rating_average',
            'hourly_rate',
            'total_sessions',
            'bio'
        ]

class TutorAvailabilitySerializer(serializers.ModelSerializer):
    day = serializers.SerializerMethodField()

    class Meta:
        model = TutorAvailability
        fields = ['id', 'day', 'time_slot', 'is_booked']

    def get_day(self, obj):
        return obj.get_day_display()  # converts 'Mon' to 'Monday', etc.
    

class PreferenceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Preference
        fields = ['subjects']
```

--- backend/studybuddy/tests.py ---
```
from django.test import TestCase

# Create your tests here.
```

--- backend/studybuddy/urls.py ---
```
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from rest_framework_simplejwt.views import TokenRefreshView
from .views import(
                   complete_booking,
                   list_courses,
                   login_view, 
                   register_user, 
                   student_dashboard, 
                   SearchTutorsView,
                   SubjectListView, template_availability, tutor_availability, 
                   tutor_dashboard,
                    tutor_detail,
                    list_bookings,
                    approve_booking,
                    reject_booking,
                    booking_detail,
                    setup_profile,
                    profile_status,
                    get_tutor_profile
                   )
from . import views

print("STUDYBUDDY URLS LOADED")

urlpatterns = [
    path('register/', register_user),
    path('login/', login_view),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/status/', views.profile_status),
    path('preferences/', views.save_preferences),
    path('partner-institutions/', views.partner_institutions_list),
    path('dashboard/', student_dashboard),
    path('tutee/profile/', views.get_tutee_profile),
    path('tutee/profile/update/', views.update_tutee_profile),
    path('tutor/profile/', views.get_tutor_profile),
    path('tutor/subjects/', views.get_tutor_subjects),
    path('tutor/subjects/add/', views.add_tutor_subject),
    path('tutor/subjects/remove/<str:subject_code>/', views.remove_tutor_subject),
    path('search-tutors/', SearchTutorsView.as_view(), name='search-tutors'),
    path('subjects/',SubjectListView.as_view(), name='subjects'),
    path('courses/', list_courses),
    path('tutor-dashboard/', tutor_dashboard, name='tutor-dashboard'),
    path('tutors/<int:profile_id>/', tutor_detail),
    path('tutors/<int:tutor_id>/availability/', tutor_availability),
    path('profile/setup/', views.setup_profile),
    path('tutor/update/', views.update_tutor_profile),
    path('bookings/', views.list_bookings),
    path('bookings/<int:booking_id>/', views.booking_detail),
    path('payment-methods/', views.payment_methods),
    #Dynamic
    
    path('bookings/confirm/', views.confirm_payment_and_book),
    path('template-availability/', template_availability),
    path('template-availability/<int:pk>/', template_availability),
    path('bookings/<int:booking_id>/complete/', complete_booking),
    path('bookings/<int:booking_id>/approve/', views.approve_booking),
    path('bookings/<int:booking_id>/reject/', views.reject_booking),
    path('tutor/setup/', views.tutor_setup),
    path('recommend-tutors/', views.recommend_tutors_view),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

--- backend/studybuddy/views.py ---
Summary only because this file exceeds 300 lines (1075 lines).

This is the main Django REST API implementation module. It contains:
- Helper functions for institution-domain normalization and lookup.
- Auth/account endpoints: partner_institutions_list, egister_user, profile_status, login_view.
- Catalog/discovery endpoints: list_courses, SubjectListView, SearchTutorsView.
- Dashboard/profile endpoints: student_dashboard, 	utor_dashboard, get_tutor_profile, get_tutee_profile, update_tutee_profile, update_tutor_profile, setup_profile, 	utor_setup.
- Tutor data endpoints: 	utor_detail, 	utor_availability, get_tutor_subjects, dd_tutor_subject, emove_tutor_subject.
- Booking/payment endpoints: confirm_payment_and_book, 	emplate_availability, pprove_booking, eject_booking, list_bookings, ooking_detail, complete_booking, payment_methods.
- Recommendation/preference endpoints: save_preferences, ecommend_tutors_view.
- Internal/unused helper flow: ulk_booking, uild_combined_block.

Methods and request payload fields inferred from the code:
- egister_user: POST with email, password, name, mname, lname, ole, institution_id.
- login_view: POST with email, password; returns JWT access/refresh tokens plus user/profile metadata.
- list_courses: GET; returns course list.
- SearchTutorsView.get: GET with subject query param; returns tutor search serializer data.
- 	utor_availability: GET with date query param; returns per-day availability for a tutor on the selected week/date.
- confirm_payment_and_book: POST with 	utor_id, slots, payment_method; validates slots, creates bookings/payments, and returns a booking/payment result payload.
- 	emplate_availability: GET returns recurring template slots; POST accepts day and 	ime_slot; DELETE expects a slot id / pk and removes it.
- save_preferences: POST with subjects.
- 	utor_setup: POST with 	eaching_level, can_online, can_f2f, hourly_rate.
- ecommend_tutors_view: POST with subject and preferred_mode; returns recommendation data from the recommender modules.
- setup_profile: POST with course, year_level, io.
- update_tutee_profile: PUT with optional name, mname, lname, course, year_level, io, subjects.
- dd_tutor_subject: POST with subject_code.
- update_tutor_profile: PUT with optional hourly_rate, 	eaching_level, can_online, can_f2f.

Response patterns visible in the file:
- Frequent JSON payloads with keys such as message, error, token fields, serialized tutor/profile data, booking collections, payment-method collections, and recommendation results.
- Most protected endpoints use @permission_classes([IsAuthenticated]).

--- backend/testapp/__init__.py ---
```
(empty file)
```

--- backend/testapp/admin.py ---
```
from django.contrib import admin

# Register your models here.
```

--- backend/testapp/apps.py ---
```
from django.apps import AppConfig


class TestappConfig(AppConfig):
    name = 'testapp'
```

--- backend/testapp/migrations/__init__.py ---
```
(empty file)
```

--- backend/testapp/migrations/0001_initial.py ---
```
# Generated by Django 6.0.2 on 2026-02-19 15:58

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TestMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
```

--- backend/testapp/models.py ---
```
from django.db import models

class TestMessage(models.Model):
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message
```

--- backend/testapp/tests.py ---
```
from django.test import TestCase

# Create your tests here.
```

--- backend/testapp/urls.py ---
```
from django.urls import path
from .views import test_api

urlpatterns = [
    path('test/', test_api),
]
```

--- backend/testapp/views.py ---
```
from django.http import JsonResponse
from .models import TestMessage
from django.views.decorators.csrf import csrf_exempt
import json


@csrf_exempt
def test_api(request):

        if request.method == "GET":
            messages = list(TestMessage.objects.all().values())
            return JsonResponse(messages, safe=False)
        
        if request.method == "POST":
            data = json.loads(request.body)
            message_text = data.get("message")

            new_message = TestMessage.objects.create(
                message=message_text
            )

            return JsonResponse({
                "id": new_message.id,
                "message": new_message.message
            })
```

--- PROJECT_HANDOFF_DUMP.md ---
```
# StudyBuddy Project Handoff Dump

Generated from the local project at `FrontEnd/studybuddy-ui` on 2026-04-06 (timezone: Asia/Manila).

## 1. Project Overview

What does this project do?
StudyBuddy is a web-based peer tutoring platform for university students. It lets tutees register, set preferences, search and book tutors, while tutors manage profiles, subjects, weekly availability, bookings, payments, and recommendation-driven discovery.

Tech stack
- Frontend: JavaScript, Vue 3, Vue Router, Pinia, Axios, Bootstrap 5, Vite
- Backend: Python, Django 6, Django REST Framework, SimpleJWT, django-cors-headers, Pillow, psycopg2-binary
- Data: PostgreSQL (via environment variables / Supabase-hosted Postgres credentials present in `backend/.env`)
- Recommendation modules: custom Python recommender code under `backend/studybuddy/recommender/` using content-based, collaborative-filtering, and hybrid logic

Runtime environment
- Installed Node.js: `v24.14.1`
- `package.json` engine constraint: `^20.19.0 || >=22.12.0`
- Installed Python: `Python 3.14.3`
- Frontend base URL env present: `VITE_API_BASE_URL=http://localhost:8000/api/v1`
- Backend DB/runtime env present in `backend/.env`
## 2. Project Structure

Expanded tree of authored/local project files captured for handoff:

```text
|-- .vscode
`-- extensions.json
|-- backend
|-- backend
|-- __init__.py
|-- asgi.py
|-- settings.py
|-- urls.py
`-- wsgi.py
|-- media
`-- profile_pics
|-- sql.jpg
`-- sql_5tVye1Y.jpg
|-- studybuddy
|-- migrations
|-- __init__.py
|-- 0001_initial.py
|-- 0002_userprofile_delete_user.py
|-- 0003_tutor_alter_userprofile_role.py
|-- 0004_subjects.py
|-- 0005_tutorsubjects.py
|-- 0006_tutoravailability.py
|-- 0007_booking.py
|-- 0008_alter_booking_availability_payment.py
|-- 0009_rating.py
|-- 0010_userprofile_bio_userprofile_profile_picture.py
|-- 0011_tutoravailability_day.py
|-- 0012_alter_tutoravailability_tutor.py
|-- 0013_alter_tutoravailability_unique_together_and_more.py
|-- 0014_paymentmethod_payment_method.py
|-- 0015_paymentmethod_code.py
|-- 0016_alter_paymentmethod_code.py
|-- 0017_userprofile_profile_completed.py
|-- 0018_preference.py
|-- 0019_alter_tutor_hourly_rate_alter_tutor_teaching_level.py
|-- 0020_course_strand_alter_userprofile_course_course_strand.py
|-- 0021_remove_preference_hourly_budget_and_more.py
`-- 0022_partnerinstitution_userprofile_institution_and_more.py
|-- recommender
|-- __init__.py
|-- cbf.py
|-- CF.py
`-- hybrid.py
|-- __init__.py
|-- admin.py
|-- apps.py
|-- models.py
|-- serializers.py
|-- tests.py
|-- urls.py
`-- views.py
|-- testapp
|-- migrations
|-- __init__.py
`-- 0001_initial.py
|-- __init__.py
|-- admin.py
|-- apps.py
|-- models.py
|-- tests.py
|-- urls.py
`-- views.py
|-- .env
|-- .gitignore
|-- {
|-- manage.py
`-- requirements.txt
|-- public
`-- favicon.ico
|-- src
|-- assets
|-- base.css
|-- hero.png
|-- logo.svg
`-- main.css
|-- components
|-- icons
|-- IconCommunity.vue
|-- IconDocumentation.vue
|-- IconEcosystem.vue
|-- IconSupport.vue
`-- IconTooling.vue
|-- HelloWorld.vue
|-- TheWelcome.vue
`-- WelcomeItem.vue
|-- router
`-- index.js
|-- services
|-- api
|-- api.js
|-- registerapi.js
`-- search-tutors.js
`-- auth
`-- idleSession.js
|-- stores
|-- auth.js
|-- bookedSessionDetails.js
|-- completedSessions.js
|-- counter.js
|-- initialbookingprefs.js
|-- preferences.js
|-- profile.js
|-- registrationinfo.js
|-- selectedSessions.js
|-- tuteePaymentDetails.js
|-- tutorBookingDetails.js
`-- tutorSched.js
|-- views
|-- BookingDetails.vue
|-- Dashboard.vue
|-- drive-download-20260305T061413Z-3-001.zip
|-- FindTutors.vue
|-- InitialBooking.vue
|-- LandingPage.vue
|-- Login.vue
|-- PaymentScreenTutee.vue
|-- PreferenceSetup.vue
|-- Profile.vue
|-- Register.vue
|-- Schedule.vue
|-- SessionsReports.vue
|-- TestApi.vue
|-- TuteeProfile.vue
|-- TutorDashboard.vue
|-- TutorDetails.vue
|-- TutorPaymentScreen.vue
|-- TutorPreferenceSetup.vue
|-- TutorProfile.vue
|-- TutorRequestedSessions.vue
`-- TutorSchedule.vue
|-- App.vue
`-- main.js
|-- .editorconfig
|-- .env
|-- .gitattributes
|-- .gitignore
|-- .oxlintrc.json
|-- .prettierrc.json
|-- eslint.config.js
|-- index.html
|-- jsconfig.json
|-- package.json
|-- package-lock.json
|-- README.md
`-- vite.config.js
```

Additional local/generated directories present but not expanded above because they are dependency or VCS internals rather than authored project files:
- `.git/`
- `node_modules/`
- `backend/venv/`

## 3. Configuration Files

--- .editorconfig ---
```
[*.{js,jsx,mjs,cjs,ts,tsx,mts,cts,vue,css,scss,sass,less,styl}]
charset = utf-8
indent_size = 2
indent_style = space
insert_final_newline = true
trim_trailing_whitespace = true
end_of_line = lf
max_line_length = 100
```

--- .env ---
```
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

--- .gitattributes ---
```
* text=auto eol=lf
```

--- .gitignore ---
```
# Logs
logs
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*
lerna-debug.log*

node_modules
.DS_Store
dist
dist-ssr
coverage
*.local

# Editor directories and files
.vscode/*
!.vscode/extensions.json
.idea
*.suo
*.ntvs*
*.njsproj
*.sln
*.sw?

*.tsbuildinfo

.eslintcache

# Cypress
/cypress/videos/
/cypress/screenshots/

# Vitest
__screenshots__/

# Vite
*.timestamp-*-*.mjs
```

--- .oxlintrc.json ---
```
{
  "$schema": "./node_modules/oxlint/configuration_schema.json",
  "plugins": ["eslint", "unicorn", "oxc", "vue"],
  "env": {
    "browser": true
  },
  "categories": {
    "correctness": "error"
  }
}
```

--- .prettierrc.json ---
```
{
  "$schema": "https://json.schemastore.org/prettierrc",
  "semi": false,
  "singleQuote": true,
  "printWidth": 100
}
```

--- .vscode/extensions.json ---
```
{
  "recommendations": [
    "Vue.volar",
    "dbaeumer.vscode-eslint",
    "EditorConfig.EditorConfig",
    "oxc.oxc-vscode",
    "esbenp.prettier-vscode"
  ]
}
```

--- backend/.env ---
```
DB_NAME=postgres
DB_USER=postgres.roptktljurzhmervwsxn
DB_PASSWORD=INvF86uUu5MZThBS
DB_HOST=aws-1-ap-southeast-1.pooler.supabase.com
DB_PORT=5432

psql "postgresql://postgres.roptktljurzhmervwsxn:bp7tThvnbepyqv6e@aws-1-ap-southeast-1.pooler.supabase.com:5432/postgres" -f studybuddy_backup.sql

psql "postgresql://postgres.roptktljurzhmervwsxn:YOUR_PASSWORD@aws-1-ap-southeast-1.pooler.supabase.com:5432/postgres" -f studybuddy_backup.sql
```

--- backend/.gitignore ---
```
# Python
__pycache__/
*.pyc
*.pyo
*.pyd

# Virtual env
venv/
.env

# Django
db.sqlite3
```

--- backend/backend/settings.py ---
```
"""
Django settings for backend project.

Generated by 'django-admin startproject' using Django 6.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/6.0/ref/settings/
"""
from datetime import timedelta
from dotenv import load_dotenv
from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-p@^2u1gzwyov3&bo_2td(e8i-#m3(97ai@f^jg$l&k-0e%+fhc'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
}
# Application definition

INSTALLED_APPS = [
    'rest_framework',
    'corsheaders',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'testapp',
    'studybuddy',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases


""" 
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'studybuddy_db',
        'USER': 'postgres',
        'PASSWORD':'sysadmin2003',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
"""


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}

# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = 'static/'
CORS_ALLOW_ALL_ORIGINS = True

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

--- backend/requirements.txt ---
```
asgiref==3.11.1
Django==6.0.2
django-cors-headers==4.9.0
djangorestframework==3.16.1
djangorestframework_simplejwt==5.5.1
pillow==12.1.1
python-dotenv==1.1.1
psycopg2-binary==2.9.11
PyJWT==2.12.1
sqlparse==0.5.5
tzdata==2025.3
```

--- eslint.config.js ---
```
import { defineConfig, globalIgnores } from 'eslint/config'
import globals from 'globals'
import js from '@eslint/js'
import pluginVue from 'eslint-plugin-vue'
import pluginOxlint from 'eslint-plugin-oxlint'
import skipFormatting from 'eslint-config-prettier/flat'

export default defineConfig([
  {
    name: 'app/files-to-lint',
    files: ['**/*.{vue,js,mjs,jsx}'],
  },

  globalIgnores(['**/dist/**', '**/dist-ssr/**', '**/coverage/**']),

  {
    languageOptions: {
      globals: {
        ...globals.browser,
      },
    },
  },

  js.configs.recommended,
  ...pluginVue.configs['flat/essential'],
  {
    rules: {
      'vue/multi-word-component-names': 'off'
    }
  },

  ...pluginOxlint.buildFromOxlintConfigFile('.oxlintrc.json'),

  skipFormatting,
])
```

--- index.html ---
```
<!DOCTYPE html>
<html lang="">
  <head>
    <meta charset="UTF-8">
    <link rel="icon" href="/favicon.ico">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vite App</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.js"></script>
  </body>
</html>
```

--- jsconfig.json ---
```
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "exclude": ["node_modules", "dist"]
}
```

--- package-lock.json ---
Summary only because this file exceeds 300 lines (4846 lines).

This is the generated npm lockfile for the Vue/Vite frontend. It pins the exact resolved dependency graph and integrity hashes for the packages declared in package.json, including Vue 3, Vue Router, Pinia, Axios, Bootstrap, Vite, ESLint, Prettier, and their full transitive dependencies. No hand-written application logic appears here.

--- package.json ---
```
{
  "name": "studybuddy-ui",
  "version": "0.0.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "lint": "run-s lint:*",
    "lint:oxlint": "oxlint . --fix",
    "lint:eslint": "eslint . --fix --cache",
    "format": "prettier --write --experimental-cli src/"
  },
  "dependencies": {
    "@popperjs/core": "^2.11.8",
    "axios": "^1.13.5",
    "bootstrap": "^5.3.8",
    "bootstrap-icons": "^1.13.1",
    "pinia": "^3.0.4",
    "vue": "^3.5.27",
    "vue-router": "^5.0.3"
  },
  "devDependencies": {
    "@eslint/js": "^9.39.2",
    "@vitejs/plugin-vue": "^6.0.3",
    "eslint": "^9.39.2",
    "eslint-config-prettier": "^10.1.8",
    "eslint-plugin-oxlint": "~1.42.0",
    "eslint-plugin-vue": "~10.7.0",
    "globals": "^17.3.0",
    "npm-run-all2": "^8.0.4",
    "oxlint": "~1.42.0",
    "prettier": "3.8.1",
    "vite": "^7.3.1",
    "vite-plugin-vue-devtools": "^8.0.5"
  },
  "engines": {
    "node": "^20.19.0 || >=22.12.0"
  }
}
```

--- vite.config.js ---
```
import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
})
```

pyproject.toml: N/A

.env.example: N/A

docker-compose.yml / docker-compose.yaml: N/A

## 4. Full Source Code

--- backend/{ ---
```
(empty file)
```

--- backend/backend/__init__.py ---
```
(empty file)
```

--- backend/backend/asgi.py ---
```
"""
ASGI config for backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

application = get_asgi_application()
```

--- backend/backend/urls.py ---
```
"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
"""from django.contrib import admin
from django.urls import path

urlpatterns = [

    path('admin/', admin.site.urls),
]
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('studybuddy.urls')),
]
```

--- backend/backend/wsgi.py ---
```
"""
WSGI config for backend project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

application = get_wsgi_application()
```

--- backend/manage.py ---
```
#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
```

--- backend/studybuddy/__init__.py ---
```
(empty file)
```

--- backend/studybuddy/admin.py ---
```
from django.contrib import admin
from .models import (
    Booking,
    Course,
    PartnerInstitution,
    Payment,
    PaymentMethod,
    Preference,
    Rating,
    Strand,
    Subjects,
    Tutor,
    TutorAvailability,
    TutorSubjects,
    UserProfile,
)

admin.site.register(UserProfile)
admin.site.register(Tutor)
admin.site.register(TutorAvailability)
admin.site.register(Booking)
admin.site.register(Payment)
admin.site.register(Rating)
admin.site.register(Subjects)
admin.site.register(TutorSubjects)
admin.site.register(PaymentMethod)
admin.site.register(Preference)
admin.site.register(Strand)
admin.site.register(Course)


@admin.register(PartnerInstitution)
class PartnerInstitutionAdmin(admin.ModelAdmin):
    list_display = ('institution_name', 'school_email_domain', 'is_active', 'contact_person', 'date_added')
    list_filter = ('is_active', 'date_added')
    search_fields = ('institution_name', 'school_email_domain', 'contact_person')
```

--- backend/studybuddy/apps.py ---
```
from django.apps import AppConfig


class StudybuddyConfig(AppConfig):
    name = 'studybuddy'
```

--- backend/studybuddy/migrations/__init__.py ---
```
(empty file)
```

--- backend/studybuddy/migrations/0001_initial.py ---
```
# Generated by Django 6.0.2 on 2026-02-23 14:05

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='user',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('password', models.CharField(max_length=255)),
                ('role', models.CharField(max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
```

--- backend/studybuddy/migrations/0002_userprofile_delete_user.py ---
```
# Generated by Django 6.0.2 on 2026-02-23 16:09

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fname', models.CharField(max_length=100)),
                ('mname', models.CharField(blank=True, max_length=100)),
                ('lname', models.CharField(max_length=100)),
                ('course', models.CharField(blank=True, max_length=100)),
                ('year_level', models.IntegerField(blank=True, null=True)),
                ('role', models.CharField(max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.DeleteModel(
            name='user',
        ),
    ]
```

--- backend/studybuddy/migrations/0003_tutor_alter_userprofile_role.py ---
```
# Generated by Django 6.0.2 on 2026-02-24 21:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0002_userprofile_delete_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tutor',
            fields=[
                ('profile', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='studybuddy.userprofile')),
                ('teaching_level', models.CharField(max_length=100)),
                ('can_online', models.BooleanField(default=True)),
                ('can_f2f', models.BooleanField(default=False)),
                ('rating_average', models.FloatField(default=0)),
                ('hourly_rate', models.DecimalField(decimal_places=2, max_digits=8)),
                ('total_sessions', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='role',
            field=models.CharField(choices=[('Tutee', 'Tutee'), ('Tutor', 'Tutor'), ('Admin', 'Admin')], max_length=20),
        ),
    ]
```

--- backend/studybuddy/migrations/0004_subjects.py ---
```
# Generated by Django 6.0.2 on 2026-02-24 21:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0003_tutor_alter_userprofile_role'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subjects',
            fields=[
                ('subject_code', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('subject_name', models.CharField(max_length=100)),
                ('department', models.CharField(max_length=100)),
            ],
        ),
    ]
```

--- backend/studybuddy/migrations/0005_tutorsubjects.py ---
```
# Generated by Django 6.0.2 on 2026-02-25 14:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0004_subjects'),
    ]

    operations = [
        migrations.CreateModel(
            name='TutorSubjects',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('expertise_level', models.IntegerField()),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='studybuddy.subjects')),
                ('tutor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='studybuddy.tutor')),
            ],
        ),
    ]
```

--- backend/studybuddy/migrations/0006_tutoravailability.py ---
```
# Generated by Django 6.0.2 on 2026-02-25 14:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0005_tutorsubjects'),
    ]

    operations = [
        migrations.CreateModel(
            name='TutorAvailability',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day_of_week', models.CharField(choices=[('Mon', 'Monday'), ('Tue', 'Tuesday'), ('Wed', 'Wednesday'), ('Thu', 'Thursday'), ('Fri', 'Friday'), ('Sat', 'Saturday'), ('Sun', 'Sunday')], max_length=3)),
                ('time_slot', models.TimeField()),
                ('is_active', models.BooleanField(default=False)),
                ('is_booked', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('tutor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='availabilities', to='studybuddy.tutor')),
            ],
            options={
                'unique_together': {('tutor', 'day_of_week', 'time_slot')},
            },
        ),
    ]
```

--- backend/studybuddy/migrations/0007_booking.py ---
```
# Generated by Django 6.0.2 on 2026-02-25 15:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0006_tutoravailability'),
    ]

    operations = [
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_date', models.DateField()),
                ('session_mode', models.CharField(choices=[('Online', 'Online'), ('F2F', 'Face-to-Face')], max_length=10)),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Confirmed', 'Confirmed'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled')], default='Pending', max_length=15)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('availability', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='studybuddy.tutoravailability')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_bookings', to='studybuddy.userprofile')),
                ('tutor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tutor_bookings', to='studybuddy.tutor')),
            ],
        ),
    ]
```

--- backend/studybuddy/migrations/0008_alter_booking_availability_payment.py ---
```
# Generated by Django 6.0.2 on 2026-02-25 15:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0007_booking'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='availability',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='studybuddy.tutoravailability'),
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('payment_status', models.CharField(choices=[('Pending', 'Pending'), ('Paid', 'Paid'), ('Failed', 'Failed'), ('Refunded', 'Refunded')], default='Pending', max_length=10)),
                ('transaction_reference', models.CharField(blank=True, max_length=100, null=True)),
                ('paid_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('booking', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='payment', to='studybuddy.booking')),
            ],
        ),
    ]
```

--- backend/studybuddy/migrations/0009_rating.py ---
```
# Generated by Django 6.0.2 on 2026-02-25 18:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0008_alter_booking_availability_payment'),
    ]

    operations = [
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating_score', models.IntegerField()),
                ('comment', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('booking', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='rating', to='studybuddy.booking')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='studybuddy.userprofile')),
                ('tutor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ratings', to='studybuddy.tutor')),
            ],
        ),
    ]
```

--- backend/studybuddy/migrations/0010_userprofile_bio_userprofile_profile_picture.py ---
```
# Generated by Django 6.0.2 on 2026-02-27 19:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0009_rating'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='bio',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='profile_picture',
            field=models.ImageField(blank=True, null=True, upload_to='profile_pics/'),
        ),
    ]
```

--- backend/studybuddy/migrations/0011_tutoravailability_day.py ---
```
# Generated by Django 6.0.2 on 2026-02-27 20:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0010_userprofile_bio_userprofile_profile_picture'),
    ]

    operations = [
        migrations.AddField(
            model_name='tutoravailability',
            name='day',
            field=models.CharField(choices=[('Mon', 'Monday'), ('Tue', 'Tuesday'), ('Wed', 'Wednesday'), ('Thu', 'Thursday'), ('Fri', 'Friday'), ('Sat', 'Saturday'), ('Sun', 'Sunday')], default='Mon', max_length=3),
            preserve_default=False,
        ),
    ]
```

--- backend/studybuddy/migrations/0012_alter_tutoravailability_tutor.py ---
```
# Generated by Django 6.0.2 on 2026-02-27 20:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0011_tutoravailability_day'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tutoravailability',
            name='tutor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='studybuddy.tutor'),
        ),
    ]
```

--- backend/studybuddy/migrations/0013_alter_tutoravailability_unique_together_and_more.py ---
```
# Generated by Django 6.0.2 on 2026-02-28 20:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0012_alter_tutoravailability_tutor'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='tutoravailability',
            unique_together={('tutor', 'day', 'time_slot')},
        ),
        migrations.AlterField(
            model_name='booking',
            name='availability',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to='studybuddy.tutoravailability'),
        ),
        migrations.AlterUniqueTogether(
            name='booking',
            unique_together={('availability', 'session_date')},
        ),
        migrations.RemoveField(
            model_name='tutoravailability',
            name='day_of_week',
        ),
    ]
```

--- backend/studybuddy/migrations/0014_paymentmethod_payment_method.py ---
```
# Generated by Django 6.0.2 on 2026-03-03 13:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0013_alter_tutoravailability_unique_together_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentMethod',
            fields=[
                ('method_id', models.AutoField(primary_key=True, serialize=False)),
                ('method_name', models.CharField(max_length=50)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AddField(
            model_name='payment',
            name='method',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='payments', to='studybuddy.paymentmethod'),
        ),
    ]
```

--- backend/studybuddy/migrations/0015_paymentmethod_code.py ---
```
# Generated by Django 6.0.2 on 2026-03-03 13:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0014_paymentmethod_payment_method'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentmethod',
            name='code',
            field=models.CharField(blank=True, choices=[('CASH', 'Cash'), ('GCASH', 'GCash'), ('BANK', 'Bank Transfer')], max_length=20, null=True, unique=True),
        ),
    ]
```

--- backend/studybuddy/migrations/0016_alter_paymentmethod_code.py ---
```
# Generated by Django 6.0.2 on 2026-03-03 13:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0015_paymentmethod_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymentmethod',
            name='code',
            field=models.CharField(choices=[('CASH', 'Cash'), ('GCASH', 'GCash'), ('BANK', 'Bank Transfer')], max_length=20, unique=True),
        ),
    ]
```

--- backend/studybuddy/migrations/0017_userprofile_profile_completed.py ---
```
# Generated by Django 6.0.2 on 2026-03-04 08:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0016_alter_paymentmethod_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='profile_completed',
            field=models.BooleanField(default=False),
        ),
    ]
```

--- backend/studybuddy/migrations/0018_preference.py ---
```
# Generated by Django 6.0.2 on 2026-03-04 09:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0017_userprofile_profile_completed'),
    ]

    operations = [
        migrations.CreateModel(
            name='Preference',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('preferred_mode', models.CharField(choices=[('Online', 'Online'), ('F2F', 'Face-to-Face')], max_length=10)),
                ('hourly_budget', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('subjects', models.ManyToManyField(to='studybuddy.subjects')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='studybuddy.userprofile')),
            ],
        ),
    ]
```

--- backend/studybuddy/migrations/0019_alter_tutor_hourly_rate_alter_tutor_teaching_level.py ---
```
# Generated by Django 6.0.2 on 2026-03-04 10:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0018_preference'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tutor',
            name='hourly_rate',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True),
        ),
        migrations.AlterField(
            model_name='tutor',
            name='teaching_level',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
```

--- backend/studybuddy/migrations/0020_course_strand_alter_userprofile_course_course_strand.py ---
```
# Generated by Django 6.0.2 on 2026-03-04 15:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0019_alter_tutor_hourly_rate_alter_tutor_teaching_level'),
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('course_code', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('course_name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Strand',
            fields=[
                ('strand_code', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('strand_name', models.CharField(max_length=100)),
            ],
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='course',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='studybuddy.course'),
        ),
        migrations.AddField(
            model_name='course',
            name='strand',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='studybuddy.strand'),
        ),
    ]
```

--- backend/studybuddy/migrations/0021_remove_preference_hourly_budget_and_more.py ---
```
# Generated by Django 6.0.2 on 2026-03-05 09:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0020_course_strand_alter_userprofile_course_course_strand'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='preference',
            name='hourly_budget',
        ),
        migrations.RemoveField(
            model_name='preference',
            name='preferred_mode',
        ),
    ]
```

--- backend/studybuddy/migrations/0022_partnerinstitution_userprofile_institution_and_more.py ---
```
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0021_remove_preference_hourly_budget_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='PartnerInstitution',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('institution_name', models.CharField(max_length=255)),
                ('school_email_domain', models.CharField(max_length=255, unique=True)),
                ('is_active', models.BooleanField(default=True)),
                ('contact_person', models.CharField(blank=True, max_length=255)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['institution_name'],
            },
        ),
        migrations.AddField(
            model_name='userprofile',
            name='institution',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='studybuddy.partnerinstitution'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='is_domain_exempt',
            field=models.BooleanField(default=False),
        ),
    ]
```

--- backend/studybuddy/models.py ---
```
from django.db import models
from django.contrib.auth.models import User ### allows the use of auth user model for authentication and user management


# Create your models here.

class Strand(models.Model):

    strand_code = models.CharField(max_length=10, primary_key=True)
    strand_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.strand_code} - {self.strand_name}"
    
class Course(models.Model):

    course_code = models.CharField(max_length=20, primary_key=True)
    course_name = models.CharField(max_length=100)

    strand = models.ForeignKey(
        Strand,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.course_code} - {self.course_name}"


class PartnerInstitution(models.Model):
    institution_name = models.CharField(max_length=255)
    school_email_domain = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    contact_person = models.CharField(max_length=255, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['institution_name']

    def __str__(self):
        return f"{self.institution_name} ({self.school_email_domain})"



class UserProfile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    fname = models.CharField(max_length=100)
    mname = models.CharField(max_length=100, blank=True)
    lname = models.CharField(max_length=100)

    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    year_level = models.IntegerField(null=True, blank=True)

    bio = models.TextField(blank=True, null=True)

    profile_completed = models.BooleanField(default=False)

    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        blank=True,
        null=True
    )

    institution = models.ForeignKey(
        PartnerInstitution,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    is_domain_exempt = models.BooleanField(default=False)

    ROLE_CHOICES = [
        ('Tutee', 'Tutee'),
        ('Tutor', 'Tutor'),
        ('Admin', 'Admin'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.fname} {self.lname}"
    
#TUTOR TABLE
class Tutor(models.Model):

    profile = models.OneToOneField(
        UserProfile,
        on_delete=models.CASCADE,
        primary_key=True
    )

    # Tutor setup fields (filled later)
    teaching_level = models.CharField(max_length=100, null=True, blank=True)

    can_online = models.BooleanField(default=True)
    can_f2f = models.BooleanField(default=False)

    rating_average = models.FloatField(default=0)

    hourly_rate = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True
    )

    total_sessions = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Tutor: {self.profile.fname} {self.profile.lname}"

#Subjects Table 
class Subjects(models.Model):
    subject_code = models.CharField(max_length=20, primary_key=True)
    subject_name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.subject_code} - {self.subject_name}"
    
#Tutor Subjects Table

class TutorSubjects(models.Model):
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subjects, on_delete=models.CASCADE)
    
    expertise_level = models.IntegerField()  # e.g., Beginner, Intermediate, Advanced

    def __str__(self):
        return f"{self.tutor.profile.fname} {self.tutor.profile.lname} - {self.subject.subject_code}"


class TutorAvailability(models.Model):

    DAY_CHOICES = [
        ('Mon', 'Monday'),
        ('Tue', 'Tuesday'),
        ('Wed', 'Wednesday'),
        ('Thu', 'Thursday'),
        ('Fri', 'Friday'),
        ('Sat', 'Saturday'),
        ('Sun', 'Sunday'),
    ]

    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    day = models.CharField(max_length=3, choices=DAY_CHOICES)
    time_slot = models.TimeField()
    is_active = models.BooleanField(default=False)   # tutor toggles this
    is_booked = models.BooleanField(default=False)   # system controls this

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('tutor', 'day', 'time_slot')

    def __str__(self):
        return f"{self.tutor.profile.fname} - {self.day} {self.time_slot}"
    
class Booking(models.Model):

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    student = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="student_bookings"
    )

    tutor = models.ForeignKey(
        Tutor,
        on_delete=models.CASCADE,
        related_name="tutor_bookings"
    )

    availability = models.ForeignKey(
        TutorAvailability,
        on_delete=models.CASCADE,
        related_name="bookings"
    )

    session_date = models.DateField()

    session_mode = models.CharField(
        max_length=10,
        choices=[('Online', 'Online'), ('F2F', 'Face-to-Face')]
    )

    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default="Pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('availability', 'session_date')

class PaymentMethod(models.Model):

    METHOD_CODES = [
        ('CASH', 'Cash'),
        ('GCASH', 'GCash'),
        ('BANK', 'Bank Transfer'),
    ]

    method_id = models.AutoField(primary_key=True)

    code = models.CharField(             
        max_length=20,
        choices=METHOD_CODES,
        unique=True,
    )

    method_name = models.CharField(max_length=50)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.method_name} ({self.code})"

class Payment(models.Model):

    PAYMENT_STATUS = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Failed', 'Failed'),
        ('Refunded', 'Refunded'),
    ]

    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        related_name="payment"
    )

    method = models.ForeignKey(        # âœ… FK to PAYMENT_METHODS
        PaymentMethod,
        on_delete=models.SET_NULL,
        null=True,
        related_name="payments"
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    payment_status = models.CharField(
        max_length=10,
        choices=PAYMENT_STATUS,
        default='Pending'
    )

    transaction_reference = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    paid_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for Booking {self.booking.id} - {self.payment_status}"
    
class Rating(models.Model):

    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        related_name="rating"
    )

    student = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE
    )

    tutor = models.ForeignKey(
        Tutor,
        on_delete=models.CASCADE,
        related_name="ratings"
    )

    rating_score = models.IntegerField()  # 1â€“5

    comment = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.rating_score} â­ for {self.tutor.profile.fname}"
    
class Preference(models.Model):

    MODE_CHOICES = [
        ('Online', 'Online'),
        ('F2F', 'Face-to-Face'),
    ]

    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE)

    subjects = models.ManyToManyField(Subjects)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Preferences for {self.user.fname}"
```

--- backend/studybuddy/recommender/__init__.py ---
```
(empty file)
```

--- backend/studybuddy/recommender/cbf.py ---
```
from ..models import (
    Preference,
    Tutor,
    TutorSubjects
)

# -----------------------------
# WEIGHTS
# -----------------------------

W_SUBJECT = 0.35
W_EXPERTISE = 0.20
W_COURSE = 0.20
W_YEAR = 0.15
W_LEVEL = 0.10


# -----------------------------
# COMPUTE CBF SCORE
# -----------------------------

def compute_cbf_score(student_profile, tutor, requested_subject):

    print("\n==============================")
    print("Running CBF for Tutor:", tutor.profile.fname, tutor.profile.lname)

    # -----------------------------
    # STUDENT DATA
    # -----------------------------

    student_course = student_profile.course
    student_year = student_profile.year_level

    try:
        pref = Preference.objects.get(user=student_profile)

        student_subjects = list(
            pref.subjects.values_list("subject_code", flat=True)
        )

    except Preference.DoesNotExist:
        student_subjects = []

    # Add requested booking subject
    if requested_subject and requested_subject not in student_subjects:
        student_subjects.append(requested_subject)

    print("Student Subjects:", student_subjects)


    # -----------------------------
    # TUTOR DATA
    # -----------------------------

    tutor_profile = tutor.profile
    tutor_course = tutor_profile.course
    tutor_year = tutor_profile.year_level
    tutor_level = tutor.teaching_level

    tutor_subjects = TutorSubjects.objects.filter(tutor=tutor)

    tutor_subject_codes = [
        ts.subject.subject_code for ts in tutor_subjects
    ]

    print("Tutor Subjects:", tutor_subject_codes)


    # -----------------------------
    # SUBJECT MATCH + EXPERTISE
    # -----------------------------

    matching_expertise = []

    for ts in tutor_subjects:

        if ts.subject.subject_code in student_subjects:

            matching_expertise.append(ts.expertise_level)

    if matching_expertise:

        s_subject = 1
        ex_ave = sum(matching_expertise) / len(matching_expertise)
        s_expertise = ex_ave / 5

    else:

        s_subject = 0
        s_expertise = 0

    print("Subject Match Score:", s_subject)
    print("Expertise Score:", round(s_expertise, 3))


    # -----------------------------
    # COURSE SIMILARITY
    # -----------------------------

    s_course = 0

    if student_course == tutor_course:

        s_course = 1

    elif (
        student_course
        and tutor_course
        and student_course.strand == tutor_course.strand
    ):

        s_course = 0.5

    print("Course Score:", s_course)


    # -----------------------------
    # YEAR SIMILARITY
    # -----------------------------

    if student_year and tutor_year:

        year_diff = abs(student_year - tutor_year)
        s_year = 1 / (1 + year_diff)

    else:

        s_year = 0

    print("Year Score:", round(s_year, 3))


    # -----------------------------
    # TEACHING LEVEL RULE
    # -----------------------------

    s_level = 1

    if tutor_level == "SHS" and int(student_year) > 12:
        s_level = 0

    print("Teaching Level Score:", s_level)


    # -----------------------------
    # FINAL SCORE
    # -----------------------------

    score = (
        W_SUBJECT * s_subject +
        W_EXPERTISE * s_expertise +
        W_COURSE * s_course +
        W_YEAR * s_year +
        W_LEVEL * s_level
    )

    print("FINAL SCORE:", round(score, 3))
    print("==============================")

    return score


# -----------------------------
# RECOMMEND TUTORS
# -----------------------------

def recommend_tutors(student_profile, subject=None, preferred_mode=None):

    print("\n===== STARTING CBF RECOMMENDER =====")

    tutors = Tutor.objects.all().select_related("profile")

    # -----------------------------
    # FILTER BY MODE
    # -----------------------------

    if preferred_mode == "Online":
        tutors = tutors.filter(can_online=True)

    if preferred_mode == "Face-to-face":
        tutors = tutors.filter(can_f2f=True)

    results = []

    for tutor in tutors:

        score = compute_cbf_score(
            student_profile,
            tutor,
            subject
        )

        results.append({
            "tutor": tutor,
            "score": score
        })

    # Sort highest score first
    results.sort(key=lambda x: x["score"], reverse=True)

    print("===== RECOMMENDER FINISHED =====\n")

    return results
```

--- backend/studybuddy/recommender/CF.py ---
```
from collections import defaultdict
from ..models import Rating, Tutor
import math


# -----------------------------
# BUILD RATING MATRIX
# -----------------------------
def build_rating_matrix():

    ratings = defaultdict(dict)

    all_ratings = Rating.objects.select_related(
        "student",
        "tutor"
    )

    for r in all_ratings:

        student_id = r.student.id
        tutor_id = r.tutor.profile_id

        ratings[student_id][tutor_id] = r.rating_score

    return ratings


# -----------------------------
# PEARSON SIMILARITY
# -----------------------------
def sim(ratings, u, v):

    common = set(ratings[u]) & set(ratings[v])

    if not common:
        return 0

    u_avg = sum(ratings[u][i] for i in common) / len(common)
    v_avg = sum(ratings[v][i] for i in common) / len(common)

    numerator = sum(
        (ratings[u][i] - u_avg) *
        (ratings[v][i] - v_avg)
        for i in common
    )

    den1 = math.sqrt(
        sum((ratings[u][i] - u_avg) ** 2 for i in common)
    )

    den2 = math.sqrt(
        sum((ratings[v][i] - v_avg) ** 2 for i in common)
    )

    if den1 * den2 == 0:
        return 0

    return numerator / (den1 * den2)


# -----------------------------
# FIND TOP-K NEIGHBORS
# -----------------------------
def top_k(ratings, student_id, k=5):

    similarities = []

    for other_student in ratings:

        if other_student == student_id:
            continue

        similarity = sim(ratings, student_id, other_student)
            
       # if similarity >= 0:
           # similarities.append(other_student,similarity)
            
        similarities.append((other_student,similarity))

    similarities.sort(key=lambda x: x[1], reverse=True)

    return similarities[:k]


# -----------------------------
# PREDICT RATING
# -----------------------------
def compute_cf_score(ratings, student_id, tutor_id, k=5):

    if student_id not in ratings:
        return None

    neighbors = top_k(ratings, student_id, k)

    numerator = 0
    denominator = 0

    student_avg = sum(ratings[student_id].values()) / len(ratings[student_id])

    for neighbor, similarity in neighbors:

        if tutor_id not in ratings.get(neighbor, {}):
            continue

        neighbor_avg = sum(ratings[neighbor].values()) / len(ratings[neighbor])

        numerator += similarity * (
            ratings[neighbor][tutor_id] - neighbor_avg
        )

        denominator += abs(similarity)

    if denominator == 0:
        return None

    return student_avg + (numerator / denominator)


# -----------------------------
# RECOMMEND TUTORS
# -----------------------------
def recommend_tutors_cf(student_profile, k=5):

    ratings = build_rating_matrix()

    student_id = student_profile.id

    tutors = Tutor.objects.all()

    results = []

    for tutor in tutors:

        tutor_id = tutor.profile_id

        # skip tutors already rated
        if tutor_id in ratings.get(student_id, {}):
            continue

        score = compute_cf_score(ratings, student_id, tutor_id, k)

        if score is not None:

            results.append({
                "tutor": tutor,
                "score": score
            })

    results.sort(key=lambda x: x["score"], reverse=True)

    return results
```

--- backend/studybuddy/recommender/hybrid.py ---
```
from ..models import Tutor
from .CF import compute_cf_score
from .cbf import compute_cbf_score


# ---------------------------------------------
# HYBRID SCORE FOR ONE TUTOR
# ---------------------------------------------
def hybrid_prediction(ratings, student_profile, tutor, requested_subject):

    # -----------------------------
    # CBF SCORE
    # -----------------------------
    cbf_score = compute_cbf_score(
        student_profile,
        tutor,
        requested_subject
    )

    # -----------------------------
    # CF SCORE
    # -----------------------------
    tutor_id = tutor.profile_id

    cf_score = compute_cf_score(
        ratings,
        student_profile.id,
        tutor_id
    )

    if cf_score is None:
        cf_score = 0

    # -----------------------------
    # HYBRID SCORE
    # -----------------------------
    hybrid_score = (0.7 * cbf_score) + (0.3 * (cf_score / 5))

    # -----------------------------
    # DEBUG OUTPUT
    # -----------------------------
    print("\n-----------------------------------")
    print(f"Tutor: {tutor.profile.fname} {tutor.profile.lname}")
    print(f"CBF Score: {cbf_score:.3f}")
    print(f"CF Score: {cf_score:.3f}")
    print(f"Hybrid Score: {hybrid_score:.3f}")
    print("-----------------------------------")

    return hybrid_score


# ---------------------------------------------
# HYBRID RECOMMENDATION LIST
# ---------------------------------------------
def recommend_tutors_hybrid(ratings, student_profile, requested_subject):

    tutors = Tutor.objects.select_related("profile")

    recommendations = []

    for tutor in tutors:

        score = hybrid_prediction(
            ratings,
            student_profile,
            tutor,
            requested_subject
        )

        recommendations.append({
            "tutor": tutor,
            "score": score
        })

    # Sort tutors by score
    recommendations.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    # -----------------------------
    # PRINT FINAL RANKING
    # -----------------------------
    print("\n===================================")
    print("FINAL HYBRID RANKING")
    print("===================================")

    for i, r in enumerate(recommendations[:10], start=1):

        tutor = r["tutor"]
        score = r["score"]

        print(
            f"{i}. {tutor.profile.fname} {tutor.profile.lname} â€” Score: {score:.3f}"
        )

    print("===================================\n")

    return recommendations
```

--- backend/studybuddy/serializers.py ---
```

from rest_framework import serializers
from .models import Tutor, Subjects, TutorAvailability,Preference

# Create Serializers here.

class TutorSearchSerializer(serializers.ModelSerializer):

    fname = serializers.CharField(source='profile.fname')
    lname = serializers.CharField(source='profile.lname')

    class Meta:
        model = Tutor
        fields = [
            'profile_id',
            'fname',
            'lname',
            'rating_average',
            'hourly_rate',
            'total_sessions'
        ]

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subjects
        fields = ['subject_code', 'subject_name', 'department']


class TutorDetailSerializer(serializers.ModelSerializer):

    fname = serializers.CharField(source='profile.fname')
    lname = serializers.CharField(source='profile.lname')
    bio = serializers.CharField(source='profile.bio', allow_null=True)

    class Meta:
        model = Tutor
        fields = [
            'profile_id',
            'fname',
            'lname',
            'rating_average',
            'hourly_rate',
            'total_sessions',
            'bio'
        ]

class TutorAvailabilitySerializer(serializers.ModelSerializer):
    day = serializers.SerializerMethodField()

    class Meta:
        model = TutorAvailability
        fields = ['id', 'day', 'time_slot', 'is_booked']

    def get_day(self, obj):
        return obj.get_day_display()  # converts 'Mon' to 'Monday', etc.
    

class PreferenceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Preference
        fields = ['subjects']
```

--- backend/studybuddy/tests.py ---
```
from django.test import TestCase

# Create your tests here.
```

--- backend/studybuddy/urls.py ---
```
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from rest_framework_simplejwt.views import TokenRefreshView
from .views import(
                   complete_booking,
                   list_courses,
                   login_view, 
                   register_user, 
                   student_dashboard, 
                   SearchTutorsView,
                   SubjectListView, template_availability, tutor_availability, 
                   tutor_dashboard,
                    tutor_detail,
                    list_bookings,
                    approve_booking,
                    reject_booking,
                    booking_detail,
                    setup_profile,
                    profile_status,
                    get_tutor_profile
                   )
from . import views

print("STUDYBUDDY URLS LOADED")

urlpatterns = [
    path('register/', register_user),
    path('login/', login_view),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/status/', views.profile_status),
    path('preferences/', views.save_preferences),
    path('partner-institutions/', views.partner_institutions_list),
    path('dashboard/', student_dashboard),
    path('tutee/profile/', views.get_tutee_profile),
    path('tutee/profile/update/', views.update_tutee_profile),
    path('tutor/profile/', views.get_tutor_profile),
    path('tutor/subjects/', views.get_tutor_subjects),
    path('tutor/subjects/add/', views.add_tutor_subject),
    path('tutor/subjects/remove/<str:subject_code>/', views.remove_tutor_subject),
    path('search-tutors/', SearchTutorsView.as_view(), name='search-tutors'),
    path('subjects/',SubjectListView.as_view(), name='subjects'),
    path('courses/', list_courses),
    path('tutor-dashboard/', tutor_dashboard, name='tutor-dashboard'),
    path('tutors/<int:profile_id>/', tutor_detail),
    path('tutors/<int:tutor_id>/availability/', tutor_availability),
    path('profile/setup/', views.setup_profile),
    path('tutor/update/', views.update_tutor_profile),
    path('bookings/', views.list_bookings),
    path('bookings/<int:booking_id>/', views.booking_detail),
    path('payment-methods/', views.payment_methods),
    #Dynamic
    
    path('bookings/confirm/', views.confirm_payment_and_book),
    path('template-availability/', template_availability),
    path('template-availability/<int:pk>/', template_availability),
    path('bookings/<int:booking_id>/complete/', complete_booking),
    path('bookings/<int:booking_id>/approve/', views.approve_booking),
    path('bookings/<int:booking_id>/reject/', views.reject_booking),
    path('tutor/setup/', views.tutor_setup),
    path('recommend-tutors/', views.recommend_tutors_view),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

--- backend/studybuddy/views.py ---
Summary only because this file exceeds 300 lines (1075 lines).

This is the main Django REST API implementation module. It contains:
- Helper functions for institution-domain normalization and lookup.
- Auth/account endpoints: partner_institutions_list, egister_user, profile_status, login_view.
- Catalog/discovery endpoints: list_courses, SubjectListView, SearchTutorsView.
- Dashboard/profile endpoints: student_dashboard, 	utor_dashboard, get_tutor_profile, get_tutee_profile, update_tutee_profile, update_tutor_profile, setup_profile, 	utor_setup.
- Tutor data endpoints: 	utor_detail, 	utor_availability, get_tutor_subjects, dd_tutor_subject, emove_tutor_subject.
- Booking/payment endpoints: confirm_payment_and_book, 	emplate_availability, pprove_booking, eject_booking, list_bookings, ooking_detail, complete_booking, payment_methods.
- Recommendation/preference endpoints: save_preferences, ecommend_tutors_view.
- Internal/unused helper flow: ulk_booking, uild_combined_block.

Methods and request payload fields inferred from the code:
- egister_user: POST with email, password, name, mname, lname, ole, institution_id.
- login_view: POST with email, password; returns JWT access/refresh tokens plus user/profile metadata.
- list_courses: GET; returns course list.
- SearchTutorsView.get: GET with subject query param; returns tutor search serializer data.
- 	utor_availability: GET with date query param; returns per-day availability for a tutor on the selected week/date.
- confirm_payment_and_book: POST with 	utor_id, slots, payment_method; validates slots, creates bookings/payments, and returns a booking/payment result payload.
- 	emplate_availability: GET returns recurring template slots; POST accepts day and 	ime_slot; DELETE expects a slot id / pk and removes it.
- save_preferences: POST with subjects.
- 	utor_setup: POST with 	eaching_level, can_online, can_f2f, hourly_rate.
- ecommend_tutors_view: POST with subject and preferred_mode; returns recommendation data from the recommender modules.
- setup_profile: POST with course, year_level, io.
- update_tutee_profile: PUT with optional name, mname, lname, course, year_level, io, subjects.
- dd_tutor_subject: POST with subject_code.
- update_tutor_profile: PUT with optional hourly_rate, 	eaching_level, can_online, can_f2f.

Response patterns visible in the file:
- Frequent JSON payloads with keys such as message, error, token fields, serialized tutor/profile data, booking collections, payment-method collections, and recommendation results.
- Most protected endpoints use @permission_classes([IsAuthenticated]).

--- backend/testapp/__init__.py ---
```
(empty file)
```

--- backend/testapp/admin.py ---
```
from django.contrib import admin

# Register your models here.
```

--- backend/testapp/apps.py ---
```
from django.apps import AppConfig


class TestappConfig(AppConfig):
    name = 'testapp'
```

--- backend/testapp/migrations/__init__.py ---
```
(empty file)
```

--- backend/testapp/migrations/0001_initial.py ---
```
# Generated by Django 6.0.2 on 2026-02-19 15:58

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TestMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
```

--- backend/testapp/models.py ---
```
from django.db import models

class TestMessage(models.Model):
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message
```

--- backend/testapp/tests.py ---
```
from django.test import TestCase

# Create your tests here.
```

--- backend/testapp/urls.py ---
```
from django.urls import path
from .views import test_api

urlpatterns = [
    path('test/', test_api),
]
```

--- backend/testapp/views.py ---
```
from django.http import JsonResponse
from .models import TestMessage
from django.views.decorators.csrf import csrf_exempt
import json


@csrf_exempt
def test_api(request):

        if request.method == "GET":
            messages = list(TestMessage.objects.all().values())
            return JsonResponse(messages, safe=False)
        
        if request.method == "POST":
            data = json.loads(request.body)
            message_text = data.get("message")

            new_message = TestMessage.objects.create(
                message=message_text
            )

            return JsonResponse({
                "id": new_message.id,
                "message": new_message.message
            })
```

--- README.md ---
```
# ðŸ“š StudyBuddy: Peer Academic Tutoring Network

## Overview

StudyBuddy is a localized, web-based peer academic tutoring and knowledge-sharing network designed BY university students FOR university students.

### Core Objectives

- **Smart Matching:** A recommender system utilizing content-based and collaborative filtering to match tutees with compatible peer tutors based on subject expertise.
- **Flexible Scheduling:** A dynamic availability module that assesses assigned workloads and prevents tutor burnout.
- **Compensation Tracking:** A module calculating payments based on session completion.
- **Performance Reporting:** Comprehensive tracking of session history, earnings records, and tutoring metrics.
---

## ðŸ›  Tech Stack

- **Frontend Framework:** Vue 3 (Composition API)
- **Styling & UI:** Bootstrap 5 & Custom CSS Variables
- **Routing:** Vue Router
- **Build Tool:** Vite

---

## ðŸš€ Project Setup for Team Members

### 1. Prerequisites

Ensure you have [Node.js](https://nodejs.org/) installed on your machine.

### 2. Installation

Clone the repository and install the required dependencies (Vue, Bootstrap, etc.):

```bash
# Clone the repository
git clone <insert-your-repo-link-here>

# Navigate into the project directory
cd studybuddy-ui

# Install all dependencies
npm install
```
```

--- src/App.vue ---
```
<template>
  <div v-if="isPublicRoute" class="public-layout">
    <router-view />
  </div>

  <div v-else class="d-flex vh-100 overflow-hidden">
    <aside class="sidebar d-flex flex-column text-white p-3 shadow-sm" style="width: 250px; background-color: var(--sb-dark);">
      <div class="d-flex align-items-center mb-5 mt-3 px-2">
        <i class="bi bi-book text-sb-primary fs-4 me-2"></i>
        <h4 class="mb-0 fw-bold">StudyBuddy</h4>
      </div>

      <ul class="nav nav-pills flex-column mb-auto">
        <li class="nav-item mb-2">
          <router-link :to="userRole === 'tutor' ? '/tch-dashboard' : '/dashboard'" class="nav-link text-white opacity-75 d-flex align-items-center" active-class="active-nav">
            <i class="bi bi-grid-1x2 me-3"></i> Dashboard
          </router-link>
        </li>

        <li class="nav-item mb-2" v-if="userRole === 'tutee'">
          <router-link to="/tutors" class="nav-link text-white opacity-75 d-flex align-items-center" active-class="active-nav">
            <i class="bi bi-search me-3"></i> Find Tutors
          </router-link>
        </li>

        <li class="nav-item mb-2">
          <router-link to="/schedule" class="nav-link text-white opacity-75 d-flex align-items-center" active-class="active-nav">
            <i class="bi bi-calendar3 me-3"></i> Schedule
          </router-link>
        </li>

        <li class="nav-item mb-2" v-if="userRole === 'tutor'">
          <router-link to="/reports" class="nav-link text-white opacity-75 d-flex align-items-center" active-class="active-nav">
            <i class="bi bi-file-earmark-text me-3"></i> Sessions & Reports
          </router-link>
        </li>
      </ul>
    </aside>

    <main class="flex-grow-1 overflow-auto p-5" style="background-color: var(--sb-bg);">
      <header class="d-flex justify-content-between align-items-center mb-3 pb-3 border-bottom border-sb">
          <div>
            </div>
          <div class="d-flex gap-3 align-items-center">
            <router-link v-if="userRole === 'tutee'" to="/book" class="btn bg-sb-primary text-white px-4 py-2 rounded-3 fw-semibold shadow-sm">
              Book Session
            </router-link>

            <router-link v-if="userRole === 'tutor'" to="/tch-requestedSessions" class="btn bg-sb-primary text-white px-4 py-2 rounded-3 fw-semibold shadow-sm">
              Manage Pending Sessions
            </router-link>

            <div class="profileDropdown">
              <button 
              class="btn text-sb-primary fs-3 ms-2 transition-all hover-lift"
              @click="toggleDropdown"
              >
                <i class="bi bi-person-circle"></i>
              </button>
              <ul v-if="isOpen" class="dropdown-menu show position-absolute end-0 mt-2 me-2">
                <li>
                  <div class="dropdown-item" @click="goToProfile">
                    Manage your account
                  </div>
                </li>
                <li><hr class="dropdown-divider"></li>
                <li><button class="btn btn-success dropdown-item text-danger text-center px-4"
                            @click="logout">
                      Log-out
                    </button>
                </li>
              </ul>
            </div>
          </div>
        </header>
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth' // Import auth store
import router from './router'

const route = useRoute()
const authStore = useAuthStore()
const isOpen = ref(false)

const toggleDropdown = () => {
  isOpen.value = !isOpen.value
}

const manageAccount = () => {
  setTimeout(() => {
    router.push('/profile')
  }, 500)
}

const logout = () => {

  authStore.logout()
  router.push('/login') // Redirect to login after logout

  router.push
}

const goToProfile = () => {

  if (userRole.value === 'tutee') {
    router.push('/tutee-profile')
  }

  if (userRole.value === 'tutor') {
    router.push('/tutor-profile')
  }

  isOpen.value = false
}

const hideSessionButton = computed(() => {
  const hiddenPages = [
    'book',
    'tutors',
    'tutor-details',
    'payment',
    'tch-dashboard',
    'tutorpreferencesetup',
    'tch-availability',
    'tch-availability',
    'tch-payments',
    'tch-requestedSessions',
    'booking-details'
  ]
  return !hiddenPages.includes(route.name)
})

const hideReqSessionsButton = computed(() => {
  const hiddenPages = [
    'book',
    'tutors',
    'tutor-details',
    'paymentTutee',
    'preferencesetup',
    'dashboard',
    'tch-requestedSessions'
  ]
  return !hiddenPages.includes(route.name)
})

const isPublicRoute = computed(() => {
  return ['home', 'login', 'register', 'preferencesetup', 'tutorpreferencesetup'].includes(route.name)
})

// Get the role from the store to control the sidebar links
const userRole = computed(() => authStore.user?.role?.toLowerCase() || null)
</script>

<style>
/* Global styles */
:root {
  --sb-dark: #0A1916;
  --sb-primary: #00895A; /* Your exact Figma Green */
  --sb-primary-hover: #00704A; /* Slightly darker for button hovers */
  --sb-bg: #F8F9FA;
  --sb-card-border: #EAEAEA;
}

body {
  background-color: var(--sb-bg);
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
}

/* --- Brand Color Utility Classes --- */
.text-sb-primary {
  color: var(--sb-primary) !important;
}

.bg-sb-primary {
  background-color: var(--sb-primary) !important;
}

.border-sb {
  border-color: var(--sb-card-border) !important;
}

/* Button Hover State */
.btn.bg-sb-primary:hover {
  background-color: var(--sb-primary-hover) !important;
  color: #ffffff !important;
}

/* --- Sidebar Navigation Styles --- */
.active-nav {
  background-color: rgba(0, 137, 90, 0.1) !important;
  color: var(--sb-primary) !important;
  font-weight: 600;
  border-radius: 8px;
  opacity: 1 !important;
}
.nav-link:hover {
  opacity: 1 !important;
}
</style>
```

--- src/assets/base.css ---
```
/* color palette from <https://github.com/vuejs/theme> */
:root {
  --vt-c-white: #ffffff;
  --vt-c-white-soft: #f8f8f8;
  --vt-c-white-mute: #f2f2f2;

  --vt-c-black: #181818;
  --vt-c-black-soft: #222222;
  --vt-c-black-mute: #282828;

  --vt-c-indigo: #2c3e50;

  --vt-c-divider-light-1: rgba(60, 60, 60, 0.29);
  --vt-c-divider-light-2: rgba(60, 60, 60, 0.12);
  --vt-c-divider-dark-1: rgba(84, 84, 84, 0.65);
  --vt-c-divider-dark-2: rgba(84, 84, 84, 0.48);

  --vt-c-text-light-1: var(--vt-c-indigo);
  --vt-c-text-light-2: rgba(60, 60, 60, 0.66);
  --vt-c-text-dark-1: var(--vt-c-white);
  --vt-c-text-dark-2: rgba(235, 235, 235, 0.64);
}

/* semantic color variables for this project */
:root {
  --color-background: var(--vt-c-white);
  --color-background-soft: var(--vt-c-white-soft);
  --color-background-mute: var(--vt-c-white-mute);

  --color-border: var(--vt-c-divider-light-2);
  --color-border-hover: var(--vt-c-divider-light-1);

  --color-heading: var(--vt-c-text-light-1);
  --color-text: var(--vt-c-text-light-1);

  --section-gap: 160px;
}

@media (prefers-color-scheme: dark) {
  :root {
    --color-background: var(--vt-c-black);
    --color-background-soft: var(--vt-c-black-soft);
    --color-background-mute: var(--vt-c-black-mute);

    --color-border: var(--vt-c-divider-dark-2);
    --color-border-hover: var(--vt-c-divider-dark-1);

    --color-heading: var(--vt-c-text-dark-1);
    --color-text: var(--vt-c-text-dark-2);
  }
}

*,
*::before,
*::after {
  box-sizing: border-box;
  margin: 0;
  font-weight: normal;
}

body {
  min-height: 100vh;
  color: var(--color-text);
  background: var(--color-background);
  transition:
    color 0.5s,
    background-color 0.5s;
  line-height: 1.6;
  font-family:
    Inter,
    -apple-system,
    BlinkMacSystemFont,
    'Segoe UI',
    Roboto,
    Oxygen,
    Ubuntu,
    Cantarell,
    'Fira Sans',
    'Droid Sans',
    'Helvetica Neue',
    sans-serif;
  font-size: 15px;
  text-rendering: optimizeLegibility;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
```

--- src/assets/main.css ---
```
:root {
  --sb-dark: #0A1916;      /* Sidebar background */
  --sb-primary: #00895A;   /* Primary green (buttons, icons, active text) */
  --sb-bg: #F8F9FA;        /* Main background */
  --sb-card-border: #EAEAEA;
}

body {
  background-color: var(--sb-bg);
  font-family: 'Inter', system-ui, -apple-system, sans-serif; /* Standard modern font */
}

/* Custom Utilities to extend Bootstrap */
.text-sb-primary { color: var(--sb-primary) !important; }
.bg-sb-primary { background-color: var(--sb-primary) !important; }
.border-sb { border-color: var(--sb-card-border) !important; }
```

--- src/components/HelloWorld.vue ---
```
<script setup>
defineProps({
  msg: {
    type: String,
    required: true,
  },
})
</script>

<template>
  <div class="greetings">
    <h1 class="green">{{ msg }}</h1>
    <h3>
      Youâ€™ve successfully created a project with
      <a href="https://vite.dev/" target="_blank" rel="noopener">Vite</a> +
      <a href="https://vuejs.org/" target="_blank" rel="noopener">Vue 3</a>.
    </h3>
  </div>
</template>

<style scoped>
h1 {
  font-weight: 500;
  font-size: 2.6rem;
  position: relative;
  top: -10px;
}

h3 {
  font-size: 1.2rem;
}

.greetings h1,
.greetings h3 {
  text-align: center;
}

@media (min-width: 1024px) {
  .greetings h1,
  .greetings h3 {
    text-align: left;
  }
}
</style>
```

--- src/components/icons/IconCommunity.vue ---
```
<template>
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor">
    <path
      d="M15 4a1 1 0 1 0 0 2V4zm0 11v-1a1 1 0 0 0-1 1h1zm0 4l-.707.707A1 1 0 0 0 16 19h-1zm-4-4l.707-.707A1 1 0 0 0 11 14v1zm-4.707-1.293a1 1 0 0 0-1.414 1.414l1.414-1.414zm-.707.707l-.707-.707.707.707zM9 11v-1a1 1 0 0 0-.707.293L9 11zm-4 0h1a1 1 0 0 0-1-1v1zm0 4H4a1 1 0 0 0 1.707.707L5 15zm10-9h2V4h-2v2zm2 0a1 1 0 0 1 1 1h2a3 3 0 0 0-3-3v2zm1 1v6h2V7h-2zm0 6a1 1 0 0 1-1 1v2a3 3 0 0 0 3-3h-2zm-1 1h-2v2h2v-2zm-3 1v4h2v-4h-2zm1.707 3.293l-4-4-1.414 1.414 4 4 1.414-1.414zM11 14H7v2h4v-2zm-4 0c-.276 0-.525-.111-.707-.293l-1.414 1.414C5.42 15.663 6.172 16 7 16v-2zm-.707 1.121l3.414-3.414-1.414-1.414-3.414 3.414 1.414 1.414zM9 12h4v-2H9v2zm4 0a3 3 0 0 0 3-3h-2a1 1 0 0 1-1 1v2zm3-3V3h-2v6h2zm0-6a3 3 0 0 0-3-3v2a1 1 0 0 1 1 1h2zm-3-3H3v2h10V0zM3 0a3 3 0 0 0-3 3h2a1 1 0 0 1 1-1V0zM0 3v6h2V3H0zm0 6a3 3 0 0 0 3 3v-2a1 1 0 0 1-1-1H0zm3 3h2v-2H3v2zm1-1v4h2v-4H4zm1.707 4.707l.586-.586-1.414-1.414-.586.586 1.414 1.414z"
    />
  </svg>
</template>
```

--- src/components/icons/IconDocumentation.vue ---
```
<template>
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="17" fill="currentColor">
    <path
      d="M11 2.253a1 1 0 1 0-2 0h2zm-2 13a1 1 0 1 0 2 0H9zm.447-12.167a1 1 0 1 0 1.107-1.666L9.447 3.086zM1 2.253L.447 1.42A1 1 0 0 0 0 2.253h1zm0 13H0a1 1 0 0 0 1.553.833L1 15.253zm8.447.833a1 1 0 1 0 1.107-1.666l-1.107 1.666zm0-14.666a1 1 0 1 0 1.107 1.666L9.447 1.42zM19 2.253h1a1 1 0 0 0-.447-.833L19 2.253zm0 13l-.553.833A1 1 0 0 0 20 15.253h-1zm-9.553-.833a1 1 0 1 0 1.107 1.666L9.447 14.42zM9 2.253v13h2v-13H9zm1.553-.833C9.203.523 7.42 0 5.5 0v2c1.572 0 2.961.431 3.947 1.086l1.107-1.666zM5.5 0C3.58 0 1.797.523.447 1.42l1.107 1.666C2.539 2.431 3.928 2 5.5 2V0zM0 2.253v13h2v-13H0zm1.553 13.833C2.539 15.431 3.928 15 5.5 15v-2c-1.92 0-3.703.523-5.053 1.42l1.107 1.666zM5.5 15c1.572 0 2.961.431 3.947 1.086l1.107-1.666C9.203 13.523 7.42 13 5.5 13v2zm5.053-11.914C11.539 2.431 12.928 2 14.5 2V0c-1.92 0-3.703.523-5.053 1.42l1.107 1.666zM14.5 2c1.573 0 2.961.431 3.947 1.086l1.107-1.666C18.203.523 16.421 0 14.5 0v2zm3.5.253v13h2v-13h-2zm1.553 12.167C18.203 13.523 16.421 13 14.5 13v2c1.573 0 2.961.431 3.947 1.086l1.107-1.666zM14.5 13c-1.92 0-3.703.523-5.053 1.42l1.107 1.666C11.539 15.431 12.928 15 14.5 15v-2z"
    />
  </svg>
</template>
```

--- src/components/icons/IconEcosystem.vue ---
```
<template>
  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="20" fill="currentColor">
    <path
      d="M11.447 8.894a1 1 0 1 0-.894-1.789l.894 1.789zm-2.894-.789a1 1 0 1 0 .894 1.789l-.894-1.789zm0 1.789a1 1 0 1 0 .894-1.789l-.894 1.789zM7.447 7.106a1 1 0 1 0-.894 1.789l.894-1.789zM10 9a1 1 0 1 0-2 0h2zm-2 2.5a1 1 0 1 0 2 0H8zm9.447-5.606a1 1 0 1 0-.894-1.789l.894 1.789zm-2.894-.789a1 1 0 1 0 .894 1.789l-.894-1.789zm2 .789a1 1 0 1 0 .894-1.789l-.894 1.789zm-1.106-2.789a1 1 0 1 0-.894 1.789l.894-1.789zM18 5a1 1 0 1 0-2 0h2zm-2 2.5a1 1 0 1 0 2 0h-2zm-5.447-4.606a1 1 0 1 0 .894-1.789l-.894 1.789zM9 1l.447-.894a1 1 0 0 0-.894 0L9 1zm-2.447.106a1 1 0 1 0 .894 1.789l-.894-1.789zm-6 3a1 1 0 1 0 .894 1.789L.553 4.106zm2.894.789a1 1 0 1 0-.894-1.789l.894 1.789zm-2-.789a1 1 0 1 0-.894 1.789l.894-1.789zm1.106 2.789a1 1 0 1 0 .894-1.789l-.894 1.789zM2 5a1 1 0 1 0-2 0h2zM0 7.5a1 1 0 1 0 2 0H0zm8.553 12.394a1 1 0 1 0 .894-1.789l-.894 1.789zm-1.106-2.789a1 1 0 1 0-.894 1.789l.894-1.789zm1.106 1a1 1 0 1 0 .894 1.789l-.894-1.789zm2.894.789a1 1 0 1 0-.894-1.789l.894 1.789zM8 19a1 1 0 1 0 2 0H8zm2-2.5a1 1 0 1 0-2 0h2zm-7.447.394a1 1 0 1 0 .894-1.789l-.894 1.789zM1 15H0a1 1 0 0 0 .553.894L1 15zm1-2.5a1 1 0 1 0-2 0h2zm12.553 2.606a1 1 0 1 0 .894 1.789l-.894-1.789zM17 15l.447.894A1 1 0 0 0 18 15h-1zm1-2.5a1 1 0 1 0-2 0h2zm-7.447-5.394l-2 1 .894 1.789 2-1-.894-1.789zm-1.106 1l-2-1-.894 1.789 2 1 .894-1.789zM8 9v2.5h2V9H8zm8.553-4.894l-2 1 .894 1.789 2-1-.894-1.789zm.894 0l-2-1-.894 1.789 2 1 .894-1.789zM16 5v2.5h2V5h-2zm-4.553-3.894l-2-1-.894 1.789 2 1 .894-1.789zm-2.894-1l-2 1 .894 1.789 2-1L8.553.106zM1.447 5.894l2-1-.894-1.789-2 1 .894 1.789zm-.894 0l2 1 .894-1.789-2-1-.894 1.789zM0 5v2.5h2V5H0zm9.447 13.106l-2-1-.894 1.789 2 1 .894-1.789zm0 1.789l2-1-.894-1.789-2 1 .894 1.789zM10 19v-2.5H8V19h2zm-6.553-3.894l-2-1-.894 1.789 2 1 .894-1.789zM2 15v-2.5H0V15h2zm13.447 1.894l2-1-.894-1.789-2 1 .894 1.789zM18 15v-2.5h-2V15h2z"
    />
  </svg>
</template>
```

--- src/components/icons/IconSupport.vue ---
```
<template>
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor">
    <path
      d="M10 3.22l-.61-.6a5.5 5.5 0 0 0-7.666.105 5.5 5.5 0 0 0-.114 7.665L10 18.78l8.39-8.4a5.5 5.5 0 0 0-.114-7.665 5.5 5.5 0 0 0-7.666-.105l-.61.61z"
    />
  </svg>
</template>
```

--- src/components/icons/IconTooling.vue ---
```
<!-- This icon is from <https://github.com/Templarian/MaterialDesign>, distributed under Apache 2.0 (https://www.apache.org/licenses/LICENSE-2.0) license-->
<template>
  <svg
    xmlns="http://www.w3.org/2000/svg"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    aria-hidden="true"
    role="img"
    class="iconify iconify--mdi"
    width="24"
    height="24"
    preserveAspectRatio="xMidYMid meet"
    viewBox="0 0 24 24"
  >
    <path
      d="M20 18v-4h-3v1h-2v-1H9v1H7v-1H4v4h16M6.33 8l-1.74 4H7v-1h2v1h6v-1h2v1h2.41l-1.74-4H6.33M9 5v1h6V5H9m12.84 7.61c.1.22.16.48.16.8V18c0 .53-.21 1-.6 1.41c-.4.4-.85.59-1.4.59H4c-.55 0-1-.19-1.4-.59C2.21 19 2 18.53 2 18v-4.59c0-.32.06-.58.16-.8L4.5 7.22C4.84 6.41 5.45 6 6.33 6H7V5c0-.55.18-1 .57-1.41C7.96 3.2 8.44 3 9 3h6c.56 0 1.04.2 1.43.59c.39.41.57.86.57 1.41v1h.67c.88 0 1.49.41 1.83 1.22l2.34 5.39z"
      fill="currentColor"
    ></path>
  </svg>
</template>
```

--- src/components/TheWelcome.vue ---
```
<script setup>
import WelcomeItem from './WelcomeItem.vue'
import DocumentationIcon from './icons/IconDocumentation.vue'
import ToolingIcon from './icons/IconTooling.vue'
import EcosystemIcon from './icons/IconEcosystem.vue'
import CommunityIcon from './icons/IconCommunity.vue'
import SupportIcon from './icons/IconSupport.vue'

const openReadmeInEditor = () => fetch('/__open-in-editor?file=README.md')
</script>

<template>
  <WelcomeItem>
    <template #icon>
      <DocumentationIcon />
    </template>
    <template #heading>Documentation</template>

    Vueâ€™s
    <a href="https://vuejs.org/" target="_blank" rel="noopener">official documentation</a>
    provides you with all information you need to get started.
  </WelcomeItem>

  <WelcomeItem>
    <template #icon>
      <ToolingIcon />
    </template>
    <template #heading>Tooling</template>

    This project is served and bundled with
    <a href="https://vite.dev/guide/features.html" target="_blank" rel="noopener">Vite</a>. The
    recommended IDE setup is
    <a href="https://code.visualstudio.com/" target="_blank" rel="noopener">VSCode</a>
    +
    <a href="https://github.com/vuejs/language-tools" target="_blank" rel="noopener"
      >Vue - Official</a
    >. If you need to test your components and web pages, check out
    <a href="https://vitest.dev/" target="_blank" rel="noopener">Vitest</a>
    and
    <a href="https://www.cypress.io/" target="_blank" rel="noopener">Cypress</a>
    /
    <a href="https://playwright.dev/" target="_blank" rel="noopener">Playwright</a>.

    <br />

    More instructions are available in
    <a href="javascript:void(0)" @click="openReadmeInEditor"><code>README.md</code></a
    >.
  </WelcomeItem>

  <WelcomeItem>
    <template #icon>
      <EcosystemIcon />
    </template>
    <template #heading>Ecosystem</template>

    Get official tools and libraries for your project:
    <a href="https://pinia.vuejs.org/" target="_blank" rel="noopener">Pinia</a>,
    <a href="https://router.vuejs.org/" target="_blank" rel="noopener">Vue Router</a>,
    <a href="https://test-utils.vuejs.org/" target="_blank" rel="noopener">Vue Test Utils</a>, and
    <a href="https://github.com/vuejs/devtools" target="_blank" rel="noopener">Vue Dev Tools</a>. If
    you need more resources, we suggest paying
    <a href="https://github.com/vuejs/awesome-vue" target="_blank" rel="noopener">Awesome Vue</a>
    a visit.
  </WelcomeItem>

  <WelcomeItem>
    <template #icon>
      <CommunityIcon />
    </template>
    <template #heading>Community</template>

    Got stuck? Ask your question on
    <a href="https://chat.vuejs.org" target="_blank" rel="noopener">Vue Land</a>
    (our official Discord server), or
    <a href="https://stackoverflow.com/questions/tagged/vue.js" target="_blank" rel="noopener"
      >StackOverflow</a
    >. You should also follow the official
    <a href="https://bsky.app/profile/vuejs.org" target="_blank" rel="noopener">@vuejs.org</a>
    Bluesky account or the
    <a href="https://x.com/vuejs" target="_blank" rel="noopener">@vuejs</a>
    X account for latest news in the Vue world.
  </WelcomeItem>

  <WelcomeItem>
    <template #icon>
      <SupportIcon />
    </template>
    <template #heading>Support Vue</template>

    As an independent project, Vue relies on community backing for its sustainability. You can help
    us by
    <a href="https://vuejs.org/sponsor/" target="_blank" rel="noopener">becoming a sponsor</a>.
  </WelcomeItem>
</template>
```

--- src/components/WelcomeItem.vue ---
```
<template>
  <div class="item">
    <i>
      <slot name="icon"></slot>
    </i>
    <div class="details">
      <h3>
        <slot name="heading"></slot>
      </h3>
      <slot></slot>
    </div>
  </div>
</template>

<style scoped>
.item {
  margin-top: 2rem;
  display: flex;
  position: relative;
}

.details {
  flex: 1;
  margin-left: 1rem;
}

i {
  display: flex;
  place-items: center;
  place-content: center;
  width: 32px;
  height: 32px;
  color: var(--color-text);
}

h3 {
  font-size: 1.2rem;
  font-weight: 500;
  margin-bottom: 0.4rem;
  color: var(--color-heading);
}

@media (min-width: 1024px) {
  .item {
    margin-top: 0;
    padding: 0.4rem 0 1rem calc(var(--section-gap) / 2);
  }

  i {
    top: calc(50% - 25px);
    left: -26px;
    position: absolute;
    border: 1px solid var(--color-border);
    background: var(--color-background);
    border-radius: 8px;
    width: 50px;
    height: 50px;
  }

  .item:before {
    content: ' ';
    border-left: 1px solid var(--color-border);
    position: absolute;
    left: 0;
    bottom: calc(50% + 25px);
    height: calc(50% - 25px);
  }

  .item:after {
    content: ' ';
    border-left: 1px solid var(--color-border);
    position: absolute;
    left: 0;
    top: calc(50% + 25px);
    height: calc(50% - 25px);
  }

  .item:first-of-type:before {
    display: none;
  }

  .item:last-of-type:after {
    display: none;
  }
}
</style>
```

--- src/main.js ---
```
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import { useAuthStore } from '@/stores/auth' // 1. Import the store

// 1. Import Bootstrap CSS
import 'bootstrap/dist/css/bootstrap.min.css'
// 2. Import Bootstrap Icons
import 'bootstrap-icons/font/bootstrap-icons.css'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// 2. Initialize Auth state to load the token into Axios
const authStore = useAuthStore()
authStore.initializeAuth()

app.mount('#app')

// 3. Import Bootstrap JS at the end so it loads after the DOM
import 'bootstrap/dist/js/bootstrap.bundle.min.js'
```

--- src/router/index.js ---
```
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useProfileStore } from '@/stores/profile'

import Dashboard from '@/views/Dashboard.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [

    // ---------- PUBLIC ROUTES ----------
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/LandingPage.vue')
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/Login.vue')
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/Register.vue')
    },

    // ---------- STUDENT ROUTES ----------
    {
      path: '/preferencesetup',
      name: 'preferencesetup',
      component: () => import('@/views/PreferenceSetup.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: Dashboard,
      meta: { requiresAuth: true, role: 'Tutee' }
    },
    {
      path: '/tutee-profile',
      name: 'tutee-profile',
      component: () => import('@/views/TuteeProfile.vue'),
      meta: { requiresAuth: true, role: 'Tutee' }
    },
    {
      path: '/tutors',
      name: 'tutors',
      component: () => import('@/views/FindTutors.vue'),
      meta: { requiresAuth: true, role: 'Tutee' }
    },
    {
      path: '/book',
      name: 'book',
      component: () => import('@/views/InitialBooking.vue'),
      meta: { requiresAuth: true, role: 'Tutee' }
    },
    {
      path: '/tutor/:id',
      name: 'tutor-details',
      component: () => import('@/views/TutorDetails.vue'),
      meta: { requiresAuth: true, role: 'Tutee' }
    },
    {
      path: '/payment-tutee/:tutorId',
      name: 'PaymentTutee',
      component: () => import('@/views/PaymentScreenTutee.vue'),
      props: true,
      meta: { requiresAuth: true, role: 'Tutee' }
    },

    // ---------- TUTOR ROUTES ----------
    {
      path: '/tutor-setup',
      name: 'tutorpreferencesetup',
      component: () => import('@/views/TutorPreferenceSetup.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/tch-dashboard',
      name: 'tch-dashboard',
      component: () => import('@/views/TutorDashboard.vue'),
      meta: { requiresAuth: true, role: 'Tutor' }
    },
    {
      path: '/tutor-profile',
      name: 'tutor-profile',
      component: () => import('@/views/TutorProfile.vue'),
      meta: { requiresAuth: true, role: 'Tutor' }
    },
    {
      path: '/tch-availability',
      name: 'tch-availability',
      component: () => import('@/views/TutorSchedule.vue'),
      meta: { requiresAuth: true, role: 'Tutor' }
    },
    {
      path: '/tch-payments',
      name: 'tch-payments',
      component: () => import('@/views/TutorPaymentScreen.vue'),
      meta: { requiresAuth: true, role: 'Tutor' }
    },
    {
      path: '/tch-requestedSessions',
      name: 'tch-requestedSessions',
      component: () => import('@/views/TutorRequestedSessions.vue'),
      meta: { requiresAuth: true, role: 'Tutor' }
    },
    {
      path: '/booking-details/:id',
      name: 'booking-details',
      component: () => import('@/views/BookingDetails.vue'),
      meta: { requiresAuth: true, role: 'Tutor' }
    },

    // ---------- SHARED ROUTES ----------
    {
      path: '/schedule',
      name: 'schedule',
      component: () => import('@/views/Schedule.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/reports',
      name: 'reports',
      component: () => import('@/views/SessionsReports.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('@/views/Profile.vue'),
      meta: { requiresAuth: true }
    }

  ]
})

/*
  GLOBAL NAVIGATION GUARD
*/
router.beforeEach(async (to, from, next) => {

  const authStore = useAuthStore()
  const profileStore = useProfileStore()
  const normalizedUserRole = authStore.userRole?.toLowerCase?.() || null
  const normalizedRouteRole = to.meta.role?.toLowerCase?.() || null

  // 1ï¸âƒ£ Protect routes requiring authentication
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return next('/login')
  }

  if (authStore.isAuthenticated) {

    // Ensure token exists
    if (!authStore.token) {
      return next('/login')
    }

    // 2ï¸âƒ£ Load profile status
    if (!profileStore.loaded) {
      try {
        await profileStore.checkProfileStatus()
      } catch (error) {

        console.error("Profile check failed:", error)

        authStore.logout()
        return next('/login')
      }
    }

    // 3ï¸âƒ£ Profile completion guard
    if (!profileStore.profileCompleted) {

      const role = normalizedUserRole

      if (to.path === '/preferencesetup' || to.path === '/tutor-setup') {
        return next()
      }

      if (role === 'tutor') {
        return next('/tutor-setup')
      }

      return next('/preferencesetup')
    }

    // 4ï¸âƒ£ Role protection
    if (normalizedRouteRole && normalizedUserRole !== normalizedRouteRole) {

      if (normalizedUserRole === 'tutor') {
        return next('/tch-dashboard')
      }

      if (normalizedUserRole === 'tutee') {
        return next('/dashboard')
      }

      return next('/')
    }

  }

  next()

})

export default router
```

--- src/services/api/api.js ---
```
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'

const API_BASE_URL = 'http://127.0.0.1:8000/api/'

const api = axios.create({
  baseURL: API_BASE_URL,
})

let refreshPromise = null

const refreshAccessToken = async () => {
  if (!refreshPromise) {
    const authStore = useAuthStore()

    refreshPromise = authStore
      .refreshAccessToken()
      .finally(() => {
        refreshPromise = null
      })
  }

  return refreshPromise
}

api.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    const token = authStore.token || localStorage.getItem('access_token')

    if (token) {
      config.headers = config.headers ?? {}
      config.headers.Authorization = `Bearer ${token}`
    }

    return config
  },
  (error) => Promise.reject(error)
)

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (
      error.response &&
      error.response.status === 401 &&
      originalRequest &&
      !originalRequest._retry &&
      !originalRequest.url?.includes('token/refresh/')
    ) {
      originalRequest._retry = true

      try {
        const newAccessToken = await refreshAccessToken()

        originalRequest.headers = originalRequest.headers ?? {}
        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`

        return api(originalRequest)
      } catch (refreshError) {
        const authStore = useAuthStore()
        authStore.logout()
        router.push('/login')

        return Promise.reject(refreshError)
      }
    }

    if (error.response && error.response.status === 401) {
      const authStore = useAuthStore()
      authStore.logout()
      router.push('/login')
    }

    return Promise.reject(error)
  }
)

export default api
```

--- src/services/api/registerapi.js ---
```
import axios from 'axios'

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/',
})

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default api

export const registerUser = async (store) => {
  return await axios.post(`${API_URL}/register/`, {
    email: store.newUserEmail,
    password: store.newUserPassword,
    fname: store.newUserFname,
    mname: store.newUserMname,
    lname: store.newUserLname,
    role: store.newUserType
  })
}
```

--- src/services/api/search-tutors.js ---
```
(empty file)
```

--- src/services/auth/idleSession.js ---
```
const IDLE_LOGOUT_MS = 10 * 60 * 1000

const ACTIVITY_EVENTS = [
  'mousemove',
  'mousedown',
  'keydown',
  'scroll',
  'touchstart',
  'click'
]

let idleTimeoutId = null
let timeoutCallback = null
let listenersAttached = false

const clearIdleTimeout = () => {
  if (idleTimeoutId !== null && typeof window !== 'undefined') {
    window.clearTimeout(idleTimeoutId)
    idleTimeoutId = null
  }
}

const resetIdleTimer = () => {
  if (typeof window === 'undefined' || !timeoutCallback) {
    return
  }

  clearIdleTimeout()

  idleTimeoutId = window.setTimeout(() => {
    timeoutCallback?.()
  }, IDLE_LOGOUT_MS)
}

const handleUserActivity = () => {
  resetIdleTimer()
}

const attachActivityListeners = () => {
  if (typeof window === 'undefined' || listenersAttached) {
    return
  }

  ACTIVITY_EVENTS.forEach((eventName) => {
    window.addEventListener(eventName, handleUserActivity, true)
  })

  listenersAttached = true
}

const detachActivityListeners = () => {
  if (typeof window === 'undefined' || !listenersAttached) {
    return
  }

  ACTIVITY_EVENTS.forEach((eventName) => {
    window.removeEventListener(eventName, handleUserActivity, true)
  })

  listenersAttached = false
}

export const startIdleSessionTracking = (onTimeout) => {
  timeoutCallback = onTimeout

  attachActivityListeners()
  resetIdleTimer()
}

export const stopIdleSessionTracking = () => {
  clearIdleTimeout()
  detachActivityListeners()
  timeoutCallback = null
}

export { IDLE_LOGOUT_MS }
```

--- src/stores/auth.js ---
```
import axios from 'axios'
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api/api'
import { useProfileStore } from '@/stores/profile'
import {
  startIdleSessionTracking,
  stopIdleSessionTracking
} from '@/services/auth/idleSession'

const API_BASE_URL = 'http://127.0.0.1:8000/api/'
const ACCESS_REFRESH_INTERVAL_MS = 4 * 60 * 1000

let refreshIntervalId = null

export const useAuthStore = defineStore('auth', () => {
  const profileStore = useProfileStore()

  const normalizeRole = (role) => {
    if (!role) {
      return null
    }

    return String(role).toLowerCase()
  }

  const handleIdleLogout = () => {
    logout()

    if (typeof window !== 'undefined' && window.location.pathname !== '/login') {
      window.location.replace('/login')
    }
  }

  const token = ref(localStorage.getItem('access_token') || null)
  const refreshToken = ref(localStorage.getItem('refresh_token') || null)
  const user = ref(null)

  const isAuthenticated = computed(() => !!token.value)
  const userRole = computed(() => user.value?.role || null)

  const setTokens = ({ accessToken, refreshTokenValue }) => {
    token.value = accessToken
    refreshToken.value = refreshTokenValue

    localStorage.setItem('access_token', accessToken)
    localStorage.setItem('refresh_token', refreshTokenValue)
  }

  const updateAccessToken = (accessToken) => {
    token.value = accessToken
    localStorage.setItem('access_token', accessToken)
  }

  const stopAccessTokenRefresh = () => {
    if (refreshIntervalId !== null && typeof window !== 'undefined') {
      window.clearInterval(refreshIntervalId)
      refreshIntervalId = null
    }
  }

  const refreshAccessToken = async () => {
    const storedRefreshToken = refreshToken.value || localStorage.getItem('refresh_token')

    if (!storedRefreshToken) {
      throw new Error('No refresh token available.')
    }

    const response = await axios.post(`${API_BASE_URL}token/refresh/`, {
      refresh: storedRefreshToken
    })

    const newAccessToken = response.data.access

    if (!newAccessToken) {
      throw new Error('No access token returned from refresh endpoint.')
    }

    updateAccessToken(newAccessToken)
    return newAccessToken
  }

  const startAccessTokenRefresh = () => {
    stopAccessTokenRefresh()

    if (typeof window === 'undefined' || !refreshToken.value) {
      return
    }

    refreshIntervalId = window.setInterval(async () => {
      try {
        await refreshAccessToken()
      } catch {
        logout()

        if (window.location.pathname !== '/login') {
          window.location.replace('/login')
        }
      }
    }, ACCESS_REFRESH_INTERVAL_MS)
  }

  const startSessionTracking = () => {
    startIdleSessionTracking(handleIdleLogout)
    startAccessTokenRefresh()
  }

  const login = async (credentials) => {
    const response = await api.post('login/', credentials)

    const receivedToken = response.data.access
    const receivedRefreshToken = response.data.refresh

    if (!receivedToken || !receivedRefreshToken) {
      throw new Error('Missing authentication token(s) from server.')
    }

    setTokens({
      accessToken: receivedToken,
      refreshTokenValue: receivedRefreshToken
    })

    user.value = {
      email: response.data.email,
      role: normalizeRole(response.data.role),
      id: response.data.user_id,
      fname: response.data.fname,
      lname: response.data.lname
    }

    localStorage.setItem('user_role', normalizeRole(response.data.role))
    profileStore.resetProfileState()

    startSessionTracking()

    return response.data.role
  }

  const logout = () => {
    stopIdleSessionTracking()
    stopAccessTokenRefresh()

    token.value = null
    refreshToken.value = null
    user.value = null
    profileStore.resetProfileState()

    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user_role')
  }

  const initializeAuth = () => {
    const storedToken = localStorage.getItem('access_token')
    const storedRefreshToken = localStorage.getItem('refresh_token')
    const storedRole = localStorage.getItem('user_role')

    if (storedToken && storedRefreshToken) {
      token.value = storedToken
      refreshToken.value = storedRefreshToken
      startSessionTracking()
    }

    if (storedRole) {
      user.value = {
        role: normalizeRole(storedRole)
      }
    }
  }

  return {
    token,
    refreshToken,
    user,
    userRole,
    isAuthenticated,
    setTokens,
    updateAccessToken,
    refreshAccessToken,
    login,
    logout,
    initializeAuth
  }
})
```

--- src/stores/bookedSessionDetails.js ---
```
import { ref } from "vue";
import { defineStore } from "pinia";

export const useBookedSessionStore = defineStore('bookedSessionDetails', () => {

    const bookedSessionTutorID = ref(null)
    const bookedSessionTutorName = ref('')
    const bookedSessionSub = ref('')
    const bookedSessionTop = ref('')
    const bookedSessionMode = ref('')
    const bookedSessionDate = ref(null)
    const bookedSessions = ref([])

    const resetStore = () => {
        bookedSessionTutorID.value = null
        bookedSessionTutorName.value = ''
        bookedSessionSub.value = ''
        bookedSessionTop.value = ''
        bookedSessionMode.value = ''
        bookedSessionDate.value = null
        bookedSessions.value = []
    }

    return {
        bookedSessionTutorID,
        bookedSessionTutorName,
        bookedSessionSub,
        bookedSessionTop,
        bookedSessionMode,
        bookedSessionDate,
        bookedSessions,
        resetStore
    }
})
```

--- src/stores/completedSessions.js ---
```
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api/api'

export const useSessionsStore = defineStore('sessions', () => {

  const sessions = ref([])
  const loading = ref(false)
  const error = ref(null)

  const fetchSessions = async () => {
    loading.value = true
    error.value = null

    try {
      const response = await api.get('/bookings/')
      sessions.value = response.data
    } catch (err) {
      error.value = 'Failed to load sessions.'
    } finally {
      loading.value = false
    }
  }

  

  const normalizeStatus = (status) =>
    status?.toLowerCase() || ''

  const completedSessions = computed(() =>
    sessions.value
      .filter(s => normalizeStatus(s.status) === 'completed')
      .sort((a, b) => new Date(b.date) - new Date(a.date))
  )

  const upcomingSessions = computed(() =>
    sessions.value
      .filter(s => normalizeStatus(s.status) === 'confirmed')
      .sort((a, b) => new Date(a.date) - new Date(b.date))
  )

  const cancelledSessions = computed(() =>
    sessions.value
      .filter(s => normalizeStatus(s.status) === 'cancelled')
      .sort((a, b) => new Date(b.date) - new Date(a.date))
  )

  const requestedSessions = computed(() =>
  sessions.value
    .filter(s => normalizeStatus(s.status) === 'pending')
    .sort((a, b) => new Date(a.date) - new Date(b.date))
  )

  const approveSession = async (id) => {
  await api.post(`/bookings/${id}/approve/`)

  const session = sessions.value.find(s => s.id === id)
  if (session) {
    session.status = "Confirmed"
  }

  }

  const rejectSession = async (id) => {
  await api.post(`/bookings/${id}/reject/`)

  const session = sessions.value.find(s => s.id === id)
  if (session) {
    session.status = "Cancelled"
  }
  } 

  return {
    sessions,
    loading,
    error,
    fetchSessions,
    completedSessions,
    upcomingSessions,
    cancelledSessions,
    requestedSessions,
    approveSession,
    rejectSession
  }
})
```

--- src/stores/counter.js ---
```
import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export const useCounterStore = defineStore('counter', () => {
  const count = ref(0)
  const doubleCount = computed(() => count.value * 2)
  function increment() {
    count.value++
  }

  return { count, doubleCount, increment }
})
```

--- src/stores/initialbookingprefs.js ---
```
import { defineStore } from 'pinia';
import { ref } from 'vue'

export const useInitialBookingPrefsStore = defineStore('initialBookingPrefs', () => {
    const selectedSubject = ref('')
    const selectedTopic = ref('')
    const selectedDate = ref(null)
    const selectedMode = ref('')
    const selectedStartTime = ref(null)
    const selectedEndTime = ref(null)

    const resetPreferences = () => {
        selectedSubject.value = ''
        selectedTopic.value = ''
        selectedDate.value = null
        selectedMode.value = ''
        selectedStartTime.value = null
        selectedEndTime.value = null
    }

    return {
      selectedSubject,
      selectedTopic,
      selectedDate,
      selectedMode,
      selectedStartTime,
      selectedEndTime,
      resetPreferences
    }
})
```

--- src/stores/preferences.js ---
```
import { defineStore } from 'pinia';
import {ref} from 'vue'

export const usePreferenceStore = defineStore('preferences', () => {
    const selectedSubjects = ref([])
    const selectedLevel = ref(null)
    const selectedTime = ref(null)

    const resetPreferences = () => {
        selectedSubjects.value = []
        selectedLevel.value = null
        selectedTime.value = null
    }
    return {selectedSubjects, selectedLevel, selectedTime, resetPreferences}
})
```

--- src/stores/profile.js ---
```
import { defineStore } from 'pinia'
import api from '@/services/api/api'

export const useProfileStore = defineStore('profile', {

  state: () => ({
    profileCompleted: false,
    loaded: false
  }),

  actions: {
    resetProfileState() {
      this.profileCompleted = false
      this.loaded = false
    },

    async checkProfileStatus() {

      const res = await api.get('/profile/status/')

      this.profileCompleted = res.data.profile_completed
      this.loaded = true

      return res.data
    }

  }

})
```

--- src/stores/registrationinfo.js ---
```
import { ref } from "vue";
import { defineStore } from "pinia";

export const useRegistrationInfoStore= defineStore('newUserInfo', () => {
    const newUserFname = ref('')
    const newUserMname = ref('')
    const newUserLname = ref('')
    const newUserEmail = ref('')
    const newUserPassword = ref('')
    const newUserType = ref('')
    const selectedInstitutionId = ref('')

    return {
        newUserFname, 
        newUserMname, 
        newUserLname, 
        newUserEmail, 
        newUserPassword, 
        newUserType,
        selectedInstitutionId}
})
```

--- src/stores/selectedSessions.js ---
```
import { defineStore } from 'pinia';
import {ref} from 'vue'

export const useBookingPrefsStore = defineStore ('bookingPrefs', () => {
    const bookedSessions = ref([])

    const addBookings = (slots) => {
        bookedSessions.value = slots
    }

    return {bookedSessions, addBookings}
})
```

--- src/stores/tuteePaymentDetails.js ---
```
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const usePaymentStore = defineStore('payment', () => {

  const selectedMethod = ref(null)
  const amountPaid = ref(null)

  const gCashName = ref('')
  const gCashNumber = ref('')
  const gCashReference = ref('')

  const bankName = ref('')
  const bankAccount = ref('')
  const bankReference = ref('')

  const reset = () => {
    selectedMethod.value = null
    amountPaid.value = null

    gCashName.value = ''
    gCashNumber.value = ''
    gCashReference.value = ''

    bankName.value = ''
    bankAccount.value = ''
    bankReference.value = ''
  }

  return {
    selectedMethod,
    amountPaid,
    gCashName,
    gCashNumber,
    gCashReference,
    bankName,
    bankAccount,
    bankReference,
    reset
  }
})
```

--- src/stores/tutorBookingDetails.js ---
```
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api/api'

export const useTutorBookingDetailStore = defineStore('tutorBookingDetail', () => {

  const booking = ref(null)
  const isLoading = ref(false)
  const error = ref(null)

  // âœ… These now match backend response structure EXACTLY
  const tuteeProfile = computed(() => booking.value?.tutee || null)
  const sessionInfo = computed(() => booking.value?.session || null)
  const paymentInfo = computed(() => booking.value?.payment || null)

  const bookingId = computed(() => booking.value?.id || null)

  const fetchBookingDetails = async (bookingId) => {
    if (!bookingId) return

    isLoading.value = true
    error.value = null

    try {
      const res = await api.get(`/bookings/${bookingId}/`)
      booking.value = res.data
    } catch (err) {
      console.error('Failed to fetch booking details:', err)
      error.value = err
      booking.value = null
    } finally {
      isLoading.value = false
    }
  }

  const completeSession = async () => {
  const id = booking.value?.id || booking.value?.session?.id

  console.log("Completing booking ID:", id)

  if (!id) {
    console.log("NO ID FOUND")
    return
  }

  try {
    await api.post(`/bookings/${id}/complete/`)
    await fetchBookingDetails(id)
  } catch (err) {
    console.error("Failed to complete session:", err)
    throw err
  }
}


  const confirmPayment = async () => {
    if (!booking.value?.id) return

    try {
      await api.post(`/bookings/confirm/`, {
        booking_id: booking.value.id
      })

      // Refresh data after confirming
      await fetchBookingDetails(booking.value.id)

    } catch (err) {
      console.error('Failed to confirm payment:', err)
      throw err
    }
  }

  const resetStore = () => {
    booking.value = null
    error.value = null
    isLoading.value = false
  }

  return {
    booking,
    isLoading,
    error,
    tuteeProfile,
    sessionInfo,
    paymentInfo,
    bookingId,
    fetchBookingDetails,
    confirmPayment,
    resetStore,
    completeSession,
  }
})
```

--- src/stores/tutorSched.js ---
```
import { defineStore } from 'pinia'
import api from '@/services/api/api'

export const useTutorSchedStore = defineStore('tutorAvailability', {
  state: () => ({
    availabilities: [],
    isLoading: false
  }),

  actions: {

    // ===============================
    // FETCH TEMPLATE SLOTS
    // ===============================
    async fetchAvailability() {
      this.isLoading = true

      try {
        const res = await api.get('/template-availability/')
        this.availabilities = res.data
      } catch (error) {
        console.error('Failed to fetch availability:', error)
      } finally {
        this.isLoading = false
      }
    },

    // ===============================
    // ADD TEMPLATE SLOT
    // ===============================
    async addSlot(slot) {
      try {
        const res = await api.post('/template-availability/', {
          day: slot.day,
          time_slot: slot.time_slot
        })

        this.availabilities.push(res.data)
      } catch (error) {
        console.error('Failed to add slot:', error)
      }
    },

    // ===============================
    // DELETE TEMPLATE SLOT
    // ===============================
    async deleteSlot(id) {
      try {
        await api.delete(`/template-availability/${id}/`)
        this.availabilities = this.availabilities.filter(
          s => s.availability_id !== id
        )
      } catch (error) {
        console.error('Failed to delete slot:', error)
      }
    }
  }
})
```

--- src/views/BookingDetails.vue ---
```
<template>
  <div class="booking-details container py-2">

    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="fw-bold mb-0">Booking Details</h2>
    </div>

    <div v-if="bookingDetailsStore.isLoading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status" />
    </div>

    <div v-else-if="!bookingDetailsStore.booking">
      <div class="alert alert-warning">Booking not found.</div>
    </div>

    <div v-else class="row g-4">

      <div class="col-12 col-md-8">
        <div class="card shadow-sm p-3 d-flex flex-row align-items-stretch h-100 gap-3">
          <img
            v-if="bookingDetailsStore.tuteeProfile?.avatar"
            :src="bookingDetailsStore.tuteeProfile.avatar.replace('150', '300')"
            style="width: 50%; height: 100%; object-fit: cover; border-radius: 10pt;"
            alt="Tutee Avatar"
            />
            

          <div class="flex-grow-1">
            <h3 class="fw-bold mb-2">
              {{ bookingDetailsStore.tuteeProfile?.name || 'N/A' }}
            </h3>
            <p class="text-muted mb-1">
              <strong>Email:</strong> {{ bookingDetailsStore.tuteeProfile?.email || 'N/A' }}
            </p>
            <p class="text-muted mb-1">
              <strong>Course:</strong> {{ bookingDetailsStore.tuteeProfile?.course || 'N/A' }}
            </p>
            <p class="text-muted mb-1">
              <strong>Year Level:</strong> {{ bookingDetailsStore.tuteeProfile?.year_level || 'N/A' }}
            </p>
            <p class="text-muted mb-0">
              <strong>Bio:</strong> {{ bookingDetailsStore.tuteeProfile?.bio || 'N/A' }}
            </p>
          </div>
        </div>
      </div>

      <div class="col-12 col-md-4">
        <div class="card shadow-sm p-3 h-100 d-flex flex-column justify-content-between">
          <div>
            <h5 class="fw-bold mb-3">Payment Summary</h5>

            <div class="row mb-2">
              <div class="col-5 text-muted">Transaction ID</div>
              <div class="col-7 text-end fw-semibold">
                {{ bookingDetailsStore.paymentInfo?.transaction_id || 'N/A' }}
              </div>
            </div>

            <div class="row mb-2">
              <div class="col-5 text-muted">Method</div>
              <div class="col-7 text-end fw-semibold">
                {{ bookingDetailsStore.paymentInfo?.method || 'N/A' }}
              </div>
            </div>

            <div class="row mb-2">
              <div class="col-5 text-muted">Amount Paid</div>
              <div class="col-7 text-end fw-semibold">
                â‚±{{ bookingDetailsStore.paymentInfo?.amount_paid?.toFixed(2) || '0.00' }}
              </div>
            </div>

            <div class="row mb-2">
              <div class="col-5 text-muted">Tutor Earned</div>
              <div class="col-7 text-end fw-semibold">
                â‚±{{ bookingDetailsStore.paymentInfo?.tutor_earned?.toFixed(2) || '0.00' }}
              </div>
            </div>

            <div class="row mb-2">
              <div class="col-5 text-muted">Platform Fee</div>
              <div class="col-7 text-end fw-semibold">
                â‚±{{ bookingDetailsStore.paymentInfo?.platform_fee?.toFixed(2) || '0.00' }}
              </div>
            </div>

            <div
            class="row mb-2"
            v-if="bookingDetailsStore.paymentInfo?.method === 'GCash' || bookingDetailsStore.paymentInfo?.method === 'Bank Transfer'"
            >
                <div class="col-5 text-muted">
                    {{
                    bookingDetailsStore.paymentInfo?.method === 'GCash'
                        ? 'GCash Fee'
                        : 'Bank Fee'
                    }}
                </div>
                <div class="col-7 text-end fw-semibold">
                    â‚±{{ bookingDetailsStore.paymentInfo?.transaction_fee?.toFixed(2) || '0.00' }}
                </div>
            </div>

            <div class="row mb-3">
              <div class="col-5 text-muted">Status</div>
              <div class="col-7 text-end">
                <span
                  class="badge"
                  :class="{
                    'bg-success': bookingDetailsStore.paymentInfo?.status === 'Paid',
                    'bg-warning text-dark': bookingDetailsStore.paymentInfo?.status === 'Pending',
                    'bg-danger': bookingDetailsStore.paymentInfo?.status === 'Failed'
                  }"
                >
                  {{ bookingDetailsStore.paymentInfo?.status || 'N/A' }}
                </span>
              </div>
            </div>
          </div>

          <div class="d-flex justify-content-end">
            <button
              v-if="bookingDetailsStore.sessionInfo?.status === 'Confirmed'"
              class="btn btn-success"
              @click="handleComplete"
            >
              Complete Session
            </button>
          </div>
        </div>
      </div>

      <!-- Session Information (Full Width) -->
      <div class="col-12">
        <div class="card shadow-sm">
          <div class="card-body">
            <h5 class="fw-bold mb-3">Session Information</h5>

            <div class="row text-center fw-semibold mb-2">
              <div class="col">Subject</div>
              <div class="col">Topic</div>
              <div class="col">Date</div>
              <div class="col">Time</div>
              <div class="col">Rating</div>
              <div class="col">Status</div>
            </div>

            <div class="row text-center">
              <div class="col">{{ bookingDetailsStore.sessionInfo?.subject || 'N/A' }}</div>
              <div class="col">{{ bookingDetailsStore.sessionInfo?.topic || 'N/A' }}</div>
              <div class="col">{{ bookingDetailsStore.sessionInfo?.date || 'N/A' }}</div>
              <div class="col">
                {{ bookingDetailsStore.sessionInfo?.start_time || 'N/A' }} â€“
                {{ bookingDetailsStore.sessionInfo?.end_time || 'N/A' }}
              </div>
              <div class="col">{{ bookingDetailsStore.sessionInfo?.rating ?? 'â€”' }}â­</div>
              <div class="col">{{ bookingDetailsStore.sessionInfo?.status || 'N/A' }}</div>
            </div>

          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { onMounted, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import { useTutorBookingDetailStore } from '@/stores/tutorBookingDetails'

const route = useRoute()
const bookingId = route.params.id
const bookingDetailsStore = useTutorBookingDetailStore()
const store = useTutorBookingDetailStore()


const handleComplete = async () => {
  try {
    await bookingDetailsStore.completeSession()
    alert("Session marked as completed.")
  } catch (error) {
    alert(error.response?.data?.error || "Failed to complete session.")
  }
}

onMounted(() => {
    bookingDetailsStore.fetchBookingDetails(route.params.id)
})

onBeforeUnmount(() => {
  bookingDetailsStore.resetStore()
})
</script>

<style scoped>
.card {
  border-radius: 12px;
}

.card-body {
  padding: 1.5rem;
}

.list-group-item {
  border: none;
  padding-left: 0;
  padding-right: 0;
}
</style>
```

--- src/views/Dashboard.vue ---
```
<template>
  <div class="p-4">
    <div class="mb-4">
      <h2 class="fw-bold text-dark">Welcome back, {{ studentName }}!</h2>
      <p class="text-muted">Here's your tutoring overview for today.</p>
    </div>

    <div class="row g-4 mb-5">
      <div class="col-md-6">
        <div class="card border-sb shadow-sm rounded-4 h-100 p-3 d-flex flex-row align-items-center">
          <div class="bg-success bg-opacity-10 p-3 rounded-4 me-3">
            <i class="bi bi-calendar-event text-sb-primary fs-3"></i>
          </div>
          <div>
            <h6 class="text-muted small fw-bold mb-1">Upcoming Sessions</h6>
            <h2 class="fw-bold mb-0">{{ upcomingCount }}</h2>
          </div>
        </div>
      </div>
      <div class="col-md-6">
        <div class="card border-sb shadow-sm rounded-4 h-100 p-3 d-flex flex-row align-items-center">
          <div class="bg-success bg-opacity-10 p-3 rounded-4 me-3">
            <i class="bi bi-book text-sb-primary fs-3"></i>
          </div>
          <div>
            <h6 class="text-muted small fw-bold mb-1">Completed Sessions</h6>
            <h2 class="fw-bold mb-0">{{ completedCount }}</h2>
          </div>
        </div>
      </div>
    </div>

    <div class="row g-4">
      <div class="col-md-6">
        <h5 class="fw-bold mb-3 d-flex align-items-center">
          <i class="bi bi-clock text-sb-primary me-2"></i> Upcoming Sessions
        </h5>

        <div v-if="loading" class="text-muted">Loading upcoming sessions...</div>

        <div v-else>
          <div 
          v-for="session in upcomingSessions"
          :key="session.id"
          @click="viewSessionDetails(session.id)" 
          class="card border-sb shadow-sm rounded-4 mb-3 session-card">
            <div class="card-body d-flex justify-content-between align-items-center">
              <div>
                <h6 class="fw-bold text-dark mb-1">{{ session.subject }}</h6>
                <p class="text-muted small mb-0">with {{ session.tutor }}</p>
              </div>
              <div class="text-end">
                <h6 class="fw-bold text-dark mb-1">{{ session.date }}</h6>
                <p class="text-muted small mb-0">{{session.time}}</p>
              </div>
            </div>
          </div>
        </div>
        

      </div>

      <div class="col-md-6">
        <h5 class="fw-bold mb-3 d-flex align-items-center">
          <i class="bi bi-star text-warning me-2"></i> Recent Sessions
        </h5>

        <div v-if="loading" class="text-muted">Loading completed sessions...</div>

        <div v-else>
          <div 
          v-for="session in completedSessions"
          :key="session.id"
          @click="viewSessionDetails(session.id)" 
          class="card border-sb shadow-sm rounded-4 mb-3 session-card">
            <div class="card-body d-flex justify-content-between align-items-center">
              <div>
                <h6 class="fw-bold text-dark mb-1">{{ session.subject }}</h6>
                <p class="text-muted small mb-0">{{ session.tutor }}</p>
              </div>
              <div class="d-flex gap-2">
                <span class="badge bg-light text-dark border border-sb d-flex align-items-center">
                  <i class="bi bi-star-fill text-dark me-1 small"></i> 5
                </span>
                <span class="badge bg-light text-dark border border-sb d-flex align-items-center">â‚±130</span>
              </div>
            </div>
          </div>
        </div>
        
      </div>
    </div>

    <div class="mt-3">
      <h4 class="fw-bold"
      >Try out these tutors</h4>

      <div class="row g-3">
        <template v-if="loading">
          <div class="col-12 text-muted">
            Loading tutors...
          </div>
        </template>

        <template v-else>
          <div 
            v-for="tutor in recommendedTutors"
            :key="tutor.id"
            class="col-md-4"
          >
            <div 
              class="card border-sb shadow-sm h-100 p-3 tutor-card"
              @click="bookTutor(tutor.id)"
            >
              <div class="card-body">
                <h3>{{ tutor.name }}</h3>
                <p class="text-muted small mb-2">â­ {{ tutor.rating }}</p>
                <p class="small mb-2">
                  Subjects: {{ tutor.subjects?.join(', ') }}
                </p>
                <p class="fw-bold text-sb-primary mb-0">
                  â‚±{{ tutor.hourlyRate }}/hr
                </p>
              </div>
            </div>
          </div>
        </template>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '@/services/api/api' 
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const recommendedTutors = ref([])
const upcomingSessions = ref([])
const completedSessions = ref([])
const loading = ref(false)

const bookTutor = (tutorId) => {
  router.push(`/tutor/${tutorId}`)
}

const fetchSessions = async() => {
  try{
    loading.value = true
   const response = await api.get('dashboard/')

    recommendedTutors.value = response.data.recommendations
    upcomingSessions.value = response.data.upcoming
    completedSessions.value = response.data.completed
  }
  catch(error) {
    console.error('Error loading sessions:', error)
  }
  finally{
    loading.value = false
  }
}

onMounted(() => {
  fetchSessions()
})

const upcomingCount = computed(() => upcomingSessions.value.length)
const completedCount = computed(() => completedSessions.value.length)

const authStore = useAuthStore()

const studentName = computed(() => {
  return authStore.user
    ? authStore.user.fname
    : 'Student'
})

const viewSessionDetails = (sessionId) => {
  // 1. We log the ID to satisfy ESLint and prep for backend integration
  console.log(`Navigating to details for session ID: ${sessionId}`)

  // 2. Route to the schedule page for now
  router.push('/schedule')
}

watch(
  () => route.query.updated,
  () => {
    fetchSessions()
  }
)

const completeSession = async (bookingId) => {
  try {
    await api.post(`bookings/${bookingId}/complete/`)
    alert("Session marked as completed.")

    // Refresh dashboard data
    await loadTutorDashboard()

  } catch (error) {
    console.error(error)
    alert("Failed to complete session.")
  }
}

</script>

<style scoped>
/* Hover effect to make cards feel clickable */
.session-card {
  cursor: pointer;
  transition: all 0.2s ease-in-out;
}
.session-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 15px rgba(0, 137, 90, 0.1) !important;
  border-color: var(--sb-primary) !important;
}
</style>
```

--- src/views/FindTutors.vue ---
```
<template>
    <div class="p-4">
        <div class="mb-4">
            <h2 class="fw-bold text-dark">Find Tutors</h2>
            <p class="text-muted">Browse peer tutors matched to your learning needs.</p>
        </div>

        <form @submit.prevent="searchTutor">
            <div class="row mb-5 g-1 justify-content-center">
            <div class="col-md-2">
                <label class="form-label fw-semibold small">Subject</label>
                <select v-model="initialbookStore.selectedSubject" class="form-select">
                <option disabled value="">Select Subject</option>
                <option
                    v-for="subject in subjects"
                    :key="subject.subject_code"
                    :value="subject.subject_code"
                >
                    {{ subject.subject_name  }}
                </option>
                </select>
            </div>
            <div class="col-md-2">
                <label class="form-label fw-semibold small">Topic</label>
                <select v-model="initialbookStore.selectedTopic" class="form-select border-sb shadow-none py-2">
                    <option value="" disabled>Select Topic</option>
                    <option 
                    v-for="topic in filteredTopics"
                    :key="topic"
                    :value="topic">{{topic}}</option>
                </select>
            </div>
            <div class="col-md-2">
                <label class="form-label fw-semibold small">Mode</label>
                <select v-model="initialbookStore.selectedMode" class="form-select border-sb shadow-none py-2">
                    <option 
                    v-for="mode in modes"
                    :key="mode"
                    :value="mode">{{ mode }}</option>
                </select>
            </div>
            <div class="col-md-2">
                <label class="form-label fw-semibold small">Date</label>
                <input type="date" v-model="initialbookStore.selectedDate" class="form-control border-sb shadow-none" required />
            </div>
            <div class="col" style="flex: 0 0 12.5%; max-width: 12.5%;">
                <label class="form-label fw-semibold small">From</label>
                <input type="time" v-model="initialbookStore.selectedStartTime" class="form-control border-sb shadow-none" required />
            </div>
            <div class="col" style="flex: 0 0 12.5%; max-width: 12.5%;">
                <label class="form-label fw-semibold small">To</label>
                <input type="time" v-model="initialbookStore.selectedEndTime" class="form-control border-sb shadow-none" required />
            </div>
            <div class="col-md-1">
                <label class="form-label fw-semibold small invisible">Search</label>
                <button type="submit" class="btn bg-sb-primary text-white px-3 rounded-3 fw-semibold shadow-sm"
                :disabled="isSubmitting">
                    Search
                </button>
            </div> 
        </div>
        </form>
        

        <div v-if="isLoading" class="text-center py-5">
            <div class="spinner-border text-sb-primary" role="status"></div>
            <p class="text-muted mt-2">Running matching algorithm...</p>
        </div>

        <div v-else class="row g-4">
            <div class="col-md-6" v-for="tutor in matchedTutors" :key="tutor.profile_id">
                <div class="card border-sb shadow-sm rounded-4 h-100">
                    <div class="card-body p-4">
                        <div class="d-flex justify-content-between align-items-start mb-3">
                            <div class="d-flex align-items-center gap-3">
                                <div class="bg-success bg-opacity-10 text-sb-primary fw-bold rounded-circle d-flex align-items-center justify-content-center"
                                    style="width: 48px; height: 48px;">
                                    {{ tutor.initials }}
                                </div>
                                <div>
                                    <h6 class="fw-bold mb-0 text-dark">{{ tutor.name }}</h6>
                                    <p class="text-muted small mb-0">{{ tutor.year_course }}</p>
                                </div>
                            </div>
                            <div class="text-end">
                                <span class="fw-bold text-warning d-flex align-items-center">
                                    <i class="bi bi-star-fill me-1"></i> {{ tutor.rating }}
                                </span>
                            </div>
                        </div>

                        <p class="small text-dark mb-3">{{ tutor.bio }}</p>

                        <div class="d-flex gap-2 mb-4 flex-wrap">
                            <span v-for="subject in tutor.subjects" :key="subject"
                                class="badge bg-light text-dark border border-sb">
                                {{ subject }}
                            </span>
                        </div>

                        <div class="d-flex justify-content-between align-items-center mt-auto">
                            <div class="small">
                                <span class="fw-bold text-dark">â‚±{{ tutor.hourly_rate }}</span><span
                                    class="text-muted">/hr</span>
                                <span class="text-muted ms-2">Â· {{ tutor.total_sessions }} sessions</span>
                            </div>
                            <button 
                                @click="toTutorDetails(tutor)"
                                class="btn bg-sb-primary text-white px-4 rounded-3 fw-semibold shadow-sm"
                                >
                                Book Session
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { useRoute, useRouter } from 'vue-router'
import api from '@/services/api/api'
import { ref, onMounted, watch } from 'vue'

import { useAuthStore } from '@/stores/auth'
import { useInitialBookingPrefsStore } from '@/stores/initialbookingprefs'
import { useBookedSessionStore } from '@/stores/bookedSessionDetails'

const route = useRoute()
const router = useRouter()

const authStore = useAuthStore()
const initialbookStore = useInitialBookingPrefsStore()
const bookedSessionStore = useBookedSessionStore()

const isLoading = ref(true)
const isSubmitting = ref(false)

const matchedTutors = ref([])
const subjects = ref([])

const modes = ['Online', 'Face-to-face']


/*
Reset topic if subject changes
*/
watch(
  () => initialbookStore.selectedSubject,
  () => {
    initialbookStore.selectedTopic = ''
  }
)


/*
CBF Tutor Search
*/
const searchTutor = async () => {

  isSubmitting.value = true
  isLoading.value = true

  try {

    const response = await api.post('/recommend-tutors/', {

      subject: initialbookStore.selectedSubject,
      topic: initialbookStore.selectedTopic,
      preferred_mode: initialbookStore.selectedMode

    })

    matchedTutors.value = response.data.map(tutor => ({

      profile_id: tutor.id,

      initials: tutor.name
        .split(' ')
        .map(n => n[0])
        .join(''),

      name: tutor.name,

      year_course: 'Tutor',

      rating: tutor.rating ?? 5.0,

      bio: 'Peer tutor available.',

      subjects: tutor.subjects ?? [],

      hourly_rate: tutor.hourly_rate ?? 150,

      total_sessions: tutor.total_sessions ?? 0,

      score: tutor.score

    }))

  } catch (error) {

    console.error('CBF search failed:', error)

  } finally {

    isSubmitting.value = false
    isLoading.value = false

  }

}


/*
Navigate to tutor details
*/
const toTutorDetails = (tutor) => {

  bookedSessionStore.bookedSessionTutorID = tutor.profile_id
  bookedSessionStore.bookedSessionTutorName = tutor.name
  bookedSessionStore.bookedSessionSub = initialbookStore.selectedSubject
  bookedSessionStore.bookedSessionTop = initialbookStore.selectedTopic
  bookedSessionStore.bookedSessionMode = initialbookStore.selectedMode

  router.push(`/tutor/${tutor.profile_id}`)
}


/*
Initial page load
*/
onMounted(async () => {

  try {

    const res = await api.get('/subjects/')
    subjects.value = res.data

  } catch (error) {

    console.error("Failed to load subjects", error)

  }

  if (route.query.subject) {
    initialbookStore.selectedSubject = route.query.subject
  }

  if (initialbookStore.selectedSubject) {
    await searchTutor()
  } else {
    isLoading.value = false
  }

})
</script>
```

--- src/views/InitialBooking.vue ---
```
<template>
  <div class="initial-booking-content">
    <div class="mb-4">
      <h2 class="fw-bold text-dark">Book a Session</h2>
      <p class="text-muted">
        Tell us what you need help with, and we'll match you with the right tutor.
      </p>
    </div>

    <div class="card border-sb shadow-sm rounded-4" style="max-width: 600px;">
      <div class="card-body p-4 p-md-5">
        <form @submit.prevent="findTutor">

          <div class="mb-3">
            <label class="form-label fw-semibold small">Subject</label>
            <select v-model="store.selectedSubject" class="form-select border-sb shadow-none" required>
              <option v-for="subject in subjects" :key="subject.subject_code" :value="subject.subject_code">
                {{ subject.subject_name }}
              </option>
            </select>
          </div>

          <div class="mb-3">
            <label class="form-label fw-semibold small">Specific Topic</label>
            <input
              type="text"
              v-model="store.selectedTopic"
              class="form-control border-sb shadow-none"
              placeholder="e.g., Calculus, Thermodynamics"
              required
            />
          </div>

          <div class="row g-3 mb-3">
            <div class="col-md-6">
              <label class="form-label fw-semibold small">Date</label>
              <input
                type="date"
                v-model="store.selectedDate"
                class="form-control border-sb shadow-none"
                required
              />
            </div>

            <div class="col-md-6">
              <label class="form-label fw-semibold small">Preferred Mode</label>
              <select v-model="store.selectedMode" class="form-select border-sb shadow-none" required>
                <option v-for="mode in modes" :key="mode" :value="mode">
                  {{ mode }}
                </option>
              </select>
            </div>
          </div>

          <div class="row g-3 mb-4">
            <div class="col-6">
              <label class="form-label fw-semibold small">Time From</label>
              <input
                type="time"
                v-model="store.selectedStartTime"
                class="form-control border-sb shadow-none"
                required
              />
            </div>

            <div class="col-6">
              <label class="form-label fw-semibold small">Time To</label>
              <input
                type="time"
                v-model="store.selectedEndTime"
                class="form-control border-sb shadow-none"
                required
              />
            </div>
          </div>

          <div class="text-end mt-4">
            <button
              type="submit"
              class="btn bg-sb-primary text-white px-5 py-2 rounded-3 fw-semibold shadow-sm d-inline-flex justify-content-center align-items-center gap-2"
              :disabled="isSubmitting"
            >
              <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-2"></span>
              {{ isSubmitting ? 'Searching...' : 'Find Tutor' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useInitialBookingPrefsStore } from '@/stores/initialbookingprefs'
import api from '@/services/api/api'

const router = useRouter()
const store = useInitialBookingPrefsStore()

const isSubmitting = ref(false)
const subjects = ref([])
const tutors = ref([])

const modes = ['Online', 'Face-to-face']


// Load subjects from backend
onMounted(async () => {

  try {

    const response = await api.get('/subjects/')
    subjects.value = response.data

  } catch (error) {

    console.error("Failed to load subjects", error)

  }

})


// FIND TUTOR (CBF CALL)
const findTutor = async () => {

  isSubmitting.value = true

  try {

    const res = await api.post('/recommend-tutors/', {

      subject: store.selectedSubject,
      topic: store.selectedTopic,
      preferred_mode: store.selectedMode,
      date: store.selectedDate,
      start_time: store.selectedStartTime,
      end_time: store.selectedEndTime

    })

    tutors.value = res.data

    console.log("Recommended tutors:", tutors.value)

    // navigate to tutors page
    router.push({ name: 'tutors' })

  } catch (err) {

    console.error("Tutor recommendation failed", err)

  } finally {

    isSubmitting.value = false

  }

}
</script>
```

--- src/views/LandingPage.vue ---
```
<template>
  <div class="landing-page bg-white min-vh-100 font-inter">
    
    <nav class="navbar navbar-expand-lg bg-white py-3">
      <div class="container">
        <a class="navbar-brand d-flex align-items-center fw-bold fs-4" href="#">
          <i class="bi bi-book text-sb-primary me-2"></i>
          <span class="text-dark">StudyBuddy</span>
        </a>
        <div class="d-flex gap-3 align-items-center">
          <router-link to="/login" class="text-dark fw-semibold text-decoration-none">Log In</router-link>
          <router-link to="/register" class="btn bg-sb-primary text-white px-4 py-2 rounded-pill fw-semibold shadow-sm">
            Get Started
          </router-link>
        </div>
      </div>
    </nav>

    <section class="hero-section py-5 my-5">
      <div class="container">
        <div class="row align-items-center g-5">
          <div class="col-lg-6">
            <span class="badge bg-success bg-opacity-10 text-sb-primary rounded-pill px-3 py-2 mb-4 fw-semibold border border-success border-opacity-25">
              University Peer Tutoring Network
            </span>
            <h1 class="display-3 fw-bold text-dark mb-4" style="line-height: 1.2;">
              Learn Better, <br>
              <span class="text-sb-primary">Together</span>
            </h1>
            <p class="lead text-muted mb-5 pe-lg-5" style="font-size: 1.15rem;">
              Connect with peer tutors matched to your learning needs. Smart recommendations, flexible scheduling, and fair compensation â€” all in one platform.
            </p>
            <div class="d-flex gap-3">
              <router-link to="/register" class="btn bg-sb-primary text-white px-4 py-3 rounded-3 fw-semibold shadow-sm d-flex align-items-center">
                Find a Tutor <i class="bi bi-arrow-right ms-2"></i>
              </router-link>
              <router-link to="/register" class="btn btn-outline-dark px-4 py-3 rounded-3 fw-semibold">
                Become a Tutor
              </router-link>
            </div>
          </div>
          
          <div class="col-lg-6">
            <div class="rounded-4 overflow-hidden shadow-lg border border-sb d-flex align-items-center justify-content-center bg-white" style="height: 400px;">
              <img 
                src="@/assets/hero.png"
                alt="StudyBuddy Peer Tutoring Illustration" 
                class="img-fluid w-100 h-100"
                style="object-fit: contain; padding: 20px;"
              >
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="stats-section border-top border-bottom border-sb py-5 bg-sb-bg">
      <div class="container">
        <div class="row text-center g-4">
          <div class="col-6 col-md-3">
            <h2 class="display-5 fw-bold text-sb-primary mb-1">500+</h2>
            <p class="text-muted fw-medium mb-0">Active Tutors</p>
          </div>
          <div class="col-6 col-md-3">
            <h2 class="display-5 fw-bold text-sb-primary mb-1">2,000+</h2>
            <p class="text-muted fw-medium mb-0">Sessions Completed</p>
          </div>
          <div class="col-6 col-md-3">
            <h2 class="display-5 fw-bold text-sb-primary mb-1">4.8</h2>
            <p class="text-muted fw-medium mb-0">Average Rating</p>
          </div>
          <div class="col-6 col-md-3">
            <h2 class="display-5 fw-bold text-sb-primary mb-1">50+</h2>
            <p class="text-muted fw-medium mb-0">Subjects Covered</p>
          </div>
        </div>
      </div>
    </section>

    <section class="features-section py-5 my-5">
      <div class="container">
        <div class="text-center mb-5 pb-3">
          <h2 class="fw-bold text-dark mb-3">Everything You Need to Succeed</h2>
          <p class="text-muted lead mx-auto" style="max-width: 600px;">
            StudyBuddy combines intelligent matching with practical tools to create the best peer tutoring experience.
          </p>
        </div>

        <div class="row g-4">
          <div class="col-md-6 col-lg-3">
            <div class="card h-100 border-sb shadow-sm rounded-4 p-3 hover-lift">
              <div class="card-body">
                <div class="rounded p-3 bg-success bg-opacity-10 d-inline-block mb-4">
                  <i class="bi bi-people text-sb-primary fs-4"></i>
                </div>
                <h5 class="fw-bold mb-3">Smart Tutor Matching</h5>
                <p class="text-muted small mb-0">
                  Our recommender system pairs you with the best peer tutor based on subject needs, ratings, and compatibility.
                </p>
              </div>
            </div>
          </div>

          <div class="col-md-6 col-lg-3">
            <div class="card h-100 border-sb shadow-sm rounded-4 p-3 hover-lift">
              <div class="card-body">
                <div class="rounded p-3 bg-success bg-opacity-10 d-inline-block mb-4">
                  <i class="bi bi-calendar3 text-sb-primary fs-4"></i>
                </div>
                <h5 class="fw-bold mb-3">Flexible Scheduling</h5>
                <p class="text-muted small mb-0">
                  View tutor availability in real-time and book sessions that fit your schedule with workload balancing.
                </p>
              </div>
            </div>
          </div>

          <div class="col-md-6 col-lg-3">
            <div class="card h-100 border-sb shadow-sm rounded-4 p-3 hover-lift">
              <div class="card-body">
                <div class="rounded p-3 bg-success bg-opacity-10 d-inline-block mb-4">
                  <i class="bi bi-bar-chart text-sb-primary fs-4"></i>
                </div>
                <h5 class="fw-bold mb-3">Earnings & Reports</h5>
                <p class="text-muted small mb-0">
                  Track session history, calculate compensation, and monitor tutoring performance metrics.
                </p>
              </div>
            </div>
          </div>

          <div class="col-md-6 col-lg-3">
            <div class="card h-100 border-sb shadow-sm rounded-4 p-3 hover-lift">
              <div class="card-body">
                <div class="rounded p-3 bg-success bg-opacity-10 d-inline-block mb-4">
                  <i class="bi bi-clock-history text-sb-primary fs-4"></i>
                </div>
                <h5 class="fw-bold mb-3">Workload Balance</h5>
                <p class="text-muted small mb-0">
                  Automatic workload assessment ensures tutors aren't overloaded, maintaining quality support.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="cta-section bg-sb-primary text-white py-5 text-center">
      <div class="container py-5">
        <h2 class="display-6 fw-bold mb-3">Ready to Start Learning?</h2>
        <p class="lead mb-5 opacity-75">
          Join hundreds of students already benefiting from peer tutoring on StudyBuddy.
        </p>
        <router-link to="/register" class="btn btn-light text-sb-primary px-5 py-3 rounded-3 fw-bold shadow-lg fs-5">
          Sign Up Free
        </router-link>
      </div>
    </section>

  </div>
</template>

<style scoped>
/* Ensure the font matches your design exactly */
.font-inter {
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
}

/* Subtle interactive animation for the feature cards */
.hover-lift {
  transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
}
.hover-lift:hover {
  transform: translateY(-5px);
  box-shadow: 0 .5rem 1rem rgba(0,0,0,.1) !important;
}

.bg-sb-bg {
  background-color: var(--sb-bg, #F8F9FA);
}
</style>
```

--- src/views/Login.vue ---
```
<template>
  <div class="min-vh-100 d-flex align-items-center justify-content-center py-5">
    <div class="card border-sb shadow-sm rounded-4" style="max-width: 400px; width: 100%">
      <div class="card-body p-4 p-md-5">
        <div class="text-center mb-4">
          <div
            class="d-inline-flex align-items-center justify-content-center bg-success bg-opacity-10 rounded-3 mb-3"
            style="width: 48px; height: 48px"
          >
            <i class="bi bi-box-arrow-in-right text-sb-primary fs-4"></i>
          </div>
          <h3 class="fw-bold text-dark">Welcome Back</h3>
          <p class="text-muted small">Log in to your StudyBuddy account</p>
        </div>

        <div v-if="loginError" class="alert alert-danger">
          {{ loginError }}
        </div>

        <form @submit.prevent="handleLogin">
          <div class="mb-3">
            <label class="form-label fw-semibold small text-dark">University Email</label>
            <input
              type="email"
              v-model="email"
              class="form-control shadow-none"
              placeholder="you@university.edu"
              required
            />
          </div>

          <div class="mb-4">
            <div class="d-flex justify-content-between align-items-center">
              <label class="form-label fw-semibold small text-dark mb-0">Password</label>
              <a href="#" class="text-sb-primary small text-decoration-none fw-semibold">Forgot?</a>
            </div>
            <input
              type="password"
              v-model="password"
              class="form-control shadow-none mt-2"
              placeholder="â€¢â€¢â€¢â€¢â€¢â€¢â€¢â€¢"
              required
            />
          </div>

          <button
            type="submit"
            class="btn bg-sb-primary text-white w-100 py-2 rounded-3 fw-semibold shadow-sm d-flex justify-content-center align-items-center gap-2"
            :disabled="isSubmitting"
          >
            <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-2"></span>
            {{ isSubmitting ? 'Signing In...' : 'Sign In' }}
          </button>
        </form>

        <div class="text-center mt-4">
          <p class="text-muted small mb-0">
            No account?
            <router-link to="/register" class="text-sb-primary fw-bold text-decoration-none">
              Create one
            </router-link>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const isSubmitting = ref(false)
const loginError = ref('')


const handleLogin = async () => {
  console.log("Login function triggered")
  isSubmitting.value = true
  loginError.value = ''

  try {
    // API_INTEGRATION_POINT: The actual axios call is delegated to the store
    const role = await authStore.login({
      email: email.value,
      password: password.value
    })

    console.log("Role from backend:", role)

    const normalizedRole = role?.toLowerCase()

    console.log("Normalized Role:", normalizedRole)
    // Route to dashboard based on user role
    if (normalizedRole === 'tutor') {
      console.log("Routing to tutor dashboard")
      router.push('/tch-dashboard')
    } 
    else if (normalizedRole === 'tutee') {
       console.log("Routing to student dashboard")
      router.push('/dashboard')
    } 
    else {
       console.log("Routing to fallback")
      router.push('/')
    }

  } catch (error) {
    console.error('Login Error:', error)
    loginError.value = error.response?.data?.error || 'Login failed. Please check your credentials.'
  } finally {
    isSubmitting.value = false
  }
}
</script>
```

--- src/views/PaymentScreenTutee.vue ---
```
<template>
<div class="booking-content container py-2">
    <div class="mb-3">
        <button
            class="btn btn-outline-secondary d-flex align-items-center gap-2"
            @click="backButton"
        >
            <i class="bi bi-arrow-left"></i>
            Back
        </button>
    </div>
    <div class="container py-5">
    <div class="row justify-content-center">
        <div class="col-md-7">
        <div class="card border-sb shadow-sm rounded-4 p-4">

            <div class="card boarder-sb rounded-2 p-1 bg-light">
            <h5>Payment Summary</h5>
            <div v-if="paymentSummary">
                <p><strong>Hours:</strong> {{ paymentSummary.hours }}</p>
                <p><strong>Total:</strong> {{ paymentSummary.total }}</p>
                <p><strong>Subject:</strong> {{ paymentSummary.subject }}</p>
                <p><strong>Tutor:</strong> {{ paymentSummary.tutor }}</p>
            </div>

            <div v-else>
                <p>Loading summary...</p>
            </div>

            </div>

            <div class="paymentOptions">
            <h5>Payment Options</h5>

            <div class="card border-0 rounded-2 p-1 bg-transparent">
                <div class="row g-3">

                <div 
                    v-for="method in paymentMethods"
                    :key="method.id"
                    class="col-4"
                >
                    <button 
                    class="btn btn-outline-sb-primary w-100 d-flex flex-column align-items-center py-3"
                    :class="{ 'btn-sb-primary': paymentStore.selectedMethod === method.id }"
                    @click="chooseMethod(method.id)"
                    >
                    <i :class="`bi ${method.icon} fs-3`"></i>
                    <span class="mt-2 text-center">
                        {{ method.label }}
                    </span>
                    </button>
                </div>

                </div>
            </div>
            </div>

            <div class="card border-sb rounded p-3 mt-3">

            <div v-if="selectedMethodName === 'Cash'">

                <div class="alert alert-info">
                Please prepare exact amount.
                </div>

                <button
                class="btn btn-primary bg-sb-primary w-100"
                style="border-color: #00895A;"
                @click="ConfirmPayment"
                >
                Confirm Cash Payment
                </button>
            </div>

            <div v-else-if="selectedMethodName === 'GCash'">
                <div class="mb-3">
                <label class="form-label">Account Name</label>
                <input
                    type="text"
                    class="form-control"
                    v-model="paymentStore.gCashName"
                    placeholder="Enter GCash name"
                />
                </div>

                <div class="mb-3">
                <label class="form-label">GCash Number</label>
                <input
                    type="tel"
                    class="form-control"
                    v-model="paymentStore.gCashNumber"
                    placeholder="09XXXXXXXXX"
                />
                </div>

                <div class="mb-3">
                <label class="form-label">Reference Number</label>
                <input
                    type="text"
                    class="form-control"
                    v-model="paymentStore.gCashReference"
                    placeholder="Transaction reference"
                />
                </div>

                <button
                class="btn btn-primary bg-sb-primary w-100"
                style="border-color: #00895A;"
                >
                Submit GCash Payment
                </button>
            </div>

            <div v-else-if="selectedMethodName === 'Bank Transfer'">
                <div class="mb-3">
                <label class="form-label">Account Holder Name</label>
                <input
                    type="text"
                    class="form-control"
                    v-model="paymentStore.bankName"
                    placeholder="Enter account name"
                />
                </div>

                <div class="mb-3">
                <label class="form-label">Account Number</label>
                <input
                    type="text"
                    class="form-control"
                    v-model="paymentStore.bankAccount"
                    placeholder="Enter account number"
                />
                </div>

                <div class="mb-3">
                <label class="form-label">Transaction Reference</label>
                <input
                    type="text"
                    class="form-control"
                    v-model="paymentStore.bankReference"
                    placeholder="Reference number"
                />
                </div>

                <button
                class="btn btn-primary bg-sb-primary w-100"
                style="border-color: #00895A;"
                >
                Confirm Payment
                </button>
            </div>

            <div v-else>
                <p class="text-muted text-center">
                Please select a payment method.
                </p>
            </div>

            </div>
            


        </div>
        </div>
    </div>
  </div>
</div>
    
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/services/api/api'
import { usePaymentStore } from '@/stores/tuteePaymentDetails'
import { useBookedSessionStore } from '@/stores/bookedSessionDetails'

const route = useRoute()
const router = useRouter()

const paymentStore = usePaymentStore()
const bookedSessionStore = useBookedSessionStore()

const tutorId = route.params.tutorId

const tutor = ref(null)
const paymentMethods = ref([])

const selectedMethodName = computed(() => {
  const method = paymentMethods.value.find(
    m => m.id === paymentStore.selectedMethod
  )
  return method ? method.label : null
})

// ---------------------------
// PAYMENT SUMMARY
// ---------------------------
const paymentSummary = computed(() => {
  if (!tutor.value) return null

  const hourlyRate = parseFloat(tutor.value.hourly_rate)
  const hours = bookedSessionStore.bookedSessions?.length || 0
  const total = hourlyRate * hours

  return {
    hours,
    total: `â‚±${total.toLocaleString()}`,
    subject: bookedSessionStore.bookedSessionSub,
    tutor: `${tutor.value.fname} ${tutor.value.lname}`
  }
})


// ---------------------------
// NAVIGATION
// ---------------------------
const backButton = () => {
  router.push(`/tutor/${tutorId}`)
  paymentStore.reset()
}


// ---------------------------
// SELECT PAYMENT METHOD
// ---------------------------
const chooseMethod = (methodId) => {
  paymentStore.selectedMethod = methodId
}


// ---------------------------
// LOAD DATA
// ---------------------------
onMounted(async () => {
  try {
    // Load tutor
    const tutorRes = await api.get(`tutors/${tutorId}/`)
    tutor.value = tutorRes.data

    // Load payment methods from backend
    const methodsRes = await api.get('payment-methods/')
    paymentMethods.value = methodsRes.data.map(m => ({
      id: m.id,
      label: m.name,
      icon:
        m.name === 'GCash' ? 'bi-wallet2' :
        m.name === 'Cash' ? 'bi-cash-coin' :
        'bi-credit-card'
    }))

  } catch (error) {
    console.error("Initialization error:", error)
    router.push('/find-tutors')
  }

  // Protect against direct URL access
  if (!bookedSessionStore.bookedSessionSub) {
    alert("No Sessions Selected.")
    router.push('/find-tutors')
  }
})

// ---------------------------
// CONFIRM PAYMENT
// ---------------------------
const ConfirmPayment = async () => {

  if (!paymentStore.selectedMethod) {
    alert("Please select a payment method.")
    return
  }

  try {

    await api.post('bookings/confirm/', {
      tutor_id: tutorId,
      date: bookedSessionStore.bookedSessionDate,
      slots: bookedSessionStore.bookedSessions,
      payment_method: paymentStore.selectedMethod   // real DB method_id
    })

    alert("Booking Confirmed!")

    paymentStore.reset()
    bookedSessionStore.resetStore()

    router.push({
      name: 'dashboard',
      query: { refresh: Date.now() }
    })

  } catch (error) {
    console.error("Payment error:", error.response?.data || error)
    alert(error.response?.data?.error || "Something went wrong.")
  }
}
</script>

<style setup>
.btn-outline-sb-primary {
  color: var(--sb-primary);
  border: 1px solid var(--sb-primary);
  background-color: transparent;
}
.btn-outline-sb-primary:hover {
  background-color: var(--sb-primary);
  color: white;
}
.btn-sb-primary {
  background-color: var(--sb-primary);
  border-color: var(--sb-primary);
  color: white;
}
</style>
```

--- src/views/PreferenceSetup.vue ---
```
<template>

  <!-- NAVBAR -->
  <nav class="navbar navbar-expand-lg bg-white py-3">
    <div class="container">
      <a class="navbar-brand fw-bold fs-4">
        StudyBuddy
      </a>
    </div>
  </nav>

  <div class="container py-5">

    <div class="row justify-content-center">

      <div class="col-md-7">

        <div class="card shadow-sm rounded-4 p-4">

          <!-- PROGRESS -->
          <div class="mb-4">
            <div class="progress" style="height:8px;">
              <div
                class="progress-bar bg-success"
                :style="{ width: progressPercentage + '%' }"
              ></div>
            </div>
          </div>


          <!-- CARD 1 SUBJECTS -->
          <div v-if="currentCard === 0">

            <div class="text-center mb-4">
              <h3 class="fw-bold">What subjects are you interested in?</h3>
              <p class="text-muted">Choose all that apply</p>
            </div>

            <div class="row g-3 mb-4">

              <div
                class="col-6"
                v-for="subject in subjects"
                :key="subject.subject_code"
              >

                <div
                  class="card border rounded-4 p-3 text-center h-100 subject-card"
                  style="cursor:pointer"
                  :class="store.selectedSubjects.includes(subject.subject_code)
                    ? 'border-success bg-success bg-opacity-10'
                    : ''"
                  @click="toggleSubject(subject.subject_code)"
                >

                  <h6 class="fw-bold mb-0">
                    {{ subject.subject_name }}
                  </h6>

                </div>

              </div>

            </div>

            <div class="d-flex justify-content-end">

              <button
                class="btn btn-success px-4"
                :disabled="store.selectedSubjects.length === 0"
                @click="nextCard"
              >
                Continue
              </button>

            </div>

          </div>


          <!-- CARD 2 YEAR LEVEL -->
          <div v-else-if="currentCard === 1">

            <div class="text-center mb-4">
              <h3 class="fw-bold">Select Your Year Level</h3>
              <p class="text-muted">Choose your current academic level</p>
            </div>

            <div class="mb-4">

              <select class="form-select" v-model="yearLevel">

                <option disabled value="">Select Year Level</option>

                <option
                  v-for="level in yearLevels"
                  :key="level.value"
                  :value="level.value"
                >
                  {{ level.label }}
                </option>

              </select>

            </div>

            <div class="d-flex justify-content-end">

              <button
                class="btn btn-success px-4"
                :disabled="!yearLevel"
                @click="nextCard"
              >
                Continue
              </button>

            </div>

          </div>


          <!-- CARD 3 COURSE -->
          <div v-else-if="currentCard === 2">

            <div class="text-center mb-4">
              <h3 class="fw-bold">Select Your Course</h3>
              <p class="text-muted">Choose your academic program</p>
            </div>

            <div class="mb-4">

              <select class="form-select" v-model="selectedCourse">

                <option disabled value="">Select Course</option>

                <option
                  v-for="course in courses"
                  :key="course.course_code"
                  :value="course.course_code"
                >
                  {{ course.course_name }}
                </option>

              </select>

            </div>

            <div class="d-flex justify-content-end">

              <button
                class="btn btn-success px-4"
                :disabled="!selectedCourse || isSubmitting"
                @click="finish"
              >
                {{ isSubmitting ? "Saving..." : "Go to Dashboard" }}
              </button>

            </div>

          </div>

        </div>

      </div>

    </div>

  </div>

</template>

<script setup>

import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { usePreferenceStore } from '@/stores/preferences'
import { useProfileStore } from '@/stores/profile'
import api from '@/services/api/api'

const router = useRouter()
const store = usePreferenceStore()
const profileStore = useProfileStore()

const currentCard = ref(0)
const totalCards = 3
const isSubmitting = ref(false)

const subjects = ref([])
const courses = ref([])

const yearLevel = ref('')
const selectedCourse = ref('')

/* YEAR LEVEL OPTIONS */

const yearLevels = [

  { label: "Grade 1", value: 1 },
  { label: "Grade 2", value: 2 },
  { label: "Grade 3", value: 3 },
  { label: "Grade 4", value: 4 },
  { label: "Grade 5", value: 5 },
  { label: "Grade 6", value: 6 },
  { label: "Grade 7", value: 7 },
  { label: "Grade 8", value: 8 },
  { label: "Grade 9", value: 9 },
  { label: "Grade 10", value: 10 },
  { label: "Grade 11", value: 11 },
  { label: "Grade 12", value: 12 },

  { label: "1st Year College", value: 13 },
  { label: "2nd Year College", value: 14 },
  { label: "3rd Year College", value: 15 },
  { label: "4th Year College", value: 16 }

]

/* LOAD DATA */

onMounted(async () => {

  try {

    const subjectRes = await api.get('subjects/')
    subjects.value = subjectRes.data

    const courseRes = await api.get('courses/')
    courses.value = courseRes.data

  } catch (error) {

    console.error("Failed loading setup data", error)

  }

})

/* SUBJECT TOGGLE */

const toggleSubject = (code) => {

  const index = store.selectedSubjects.indexOf(code)

  if (index > -1) {
    store.selectedSubjects.splice(index, 1)
  } else {
    store.selectedSubjects.push(code)
  }

}

/* NEXT CARD */

const nextCard = () => {

  if (currentCard.value < totalCards - 1) {
    currentCard.value++
  }

}

/* FINISH SETUP */

const finish = async () => {

  isSubmitting.value = true

  try {

    await api.post('profile/setup/', {
      course: selectedCourse.value,
      year_level: yearLevel.value,
      bio: "Student profile"
    })

    await api.post("preferences/", {
       subjects: [...store.selectedSubjects]
    })

    profileStore.profileCompleted = true
    profileStore.loaded = true

    store.resetPreferences()

    router.push('/dashboard')

  } catch (error) {

    console.error("Failed saving preferences", error)
    alert("Could not save preferences")

  } finally {

    isSubmitting.value = false

  }

}

/* PROGRESS BAR */

const progressPercentage = computed(() => {
  return ((currentCard.value + 1) / totalCards) * 100
})

</script>
```

--- src/views/Profile.vue ---
```
<template>
  <div class="profile-content">
    <div class="mb-4">
      <h2 class="fw-bold text-dark">My Profile</h2>
      <p class="text-muted">Manage your personal information and tutoring preferences.</p>
    </div>

    <div class="card border-sb shadow-sm rounded-4" style="max-width: 800px;">
      <div v-if="userRole === 'tutee'" class="card-body p-4 p-md-5">
        
        <div class="d-flex align-items-center mb-4 pb-4 border-bottom border-sb">
          <div class="rounded-circle bg-success bg-opacity-10 text-sb-primary d-flex justify-content-center align-items-center fw-bold fs-3 me-4" style="width: 80px; height: 80px;">
            JD
          </div>
          <div>
            <h5 class="fw-bold mb-1">Juan Dela Cruz</h5>
            <p class="text-muted small mb-2">Student / Tutee</p>
            <button class="btn btn-outline-dark btn-sm rounded-3 fw-semibold px-3">Update Photo</button>
          </div>
        </div>

        <form @submit.prevent="saveProfile">
          <div class="row g-4 mb-4">
            
            <div class="col-md-6">
              <label class="form-label fw-semibold small text-dark">Full Name</label>
              <input type="text" class="form-control border-sb shadow-none" value="Juan Dela Cruz">
            </div>
            
            <div class="col-md-6">
              <label class="form-label fw-semibold small text-dark">University Email</label>
              <input type="email" class="form-control border-sb shadow-none bg-light text-muted" value="juan@university.edu" disabled>
              <div class="form-text small">Email cannot be changed after registration.</div>
            </div>
            
            <div class="col-md-6">
              <label class="form-label fw-semibold small text-dark">Major / Degree Program</label>
              <input type="text" class="form-control border-sb shadow-none" placeholder="e.g., Computer Science">
            </div>
            
            <div class="col-md-6">
              <label class="form-label fw-semibold small text-dark">Year Level</label>
              <select class="form-select border-sb shadow-none">
                <option value="1">1st Year</option>
                <option value="2">2nd Year</option>
                <option value="3">3rd Year</option>
                <option value="4">4th Year</option>
                <option value="5">Graduate</option>
              </select>
            </div>
            
            <div class="col-12">
              <label class="form-label fw-semibold small text-dark">Bio (About Me)</label>
              <textarea class="form-control border-sb shadow-none" rows="4" placeholder="Tell tutors a bit about your learning style or what you usually need help with..."></textarea>
            </div>
            
          </div>

          <div class="text-end mt-2">
            <button type="submit" class="btn bg-sb-primary text-white px-5 py-2 rounded-3 fw-semibold shadow-sm">
              Save Changes
            </button>
          </div>
        </form>

      </div>

      <div v-else  class="card-body p-4 p-md-5">
        
        <div class="d-flex align-items-center mb-4 pb-4 border-bottom border-sb">
          <div class="rounded-circle bg-success bg-opacity-10 text-sb-primary d-flex justify-content-center align-items-center fw-bold fs-3 me-4" style="width: 80px; height: 80px;">
            JD
          </div>
          <div>
            <h5 class="fw-bold mb-1">Juan Dela Cruz</h5>
            <p class="text-muted small mb-2">Student / Tutor</p>
            <button class="btn btn-outline-dark btn-sm rounded-3 fw-semibold px-3">Update Photo</button>
          </div>
        </div>

        <form @submit.prevent="saveProfile">
          <div class="row g-4 mb-4">
            
            <div class="col-md-6">
              <label class="form-label fw-semibold small text-dark">Full Name</label>
              <input type="text" class="form-control border-sb shadow-none" value="Juan Dela Cruz">
            </div>
            
            <div class="col-md-6">
              <label class="form-label fw-semibold small text-dark">University Email</label>
              <input type="email" class="form-control border-sb shadow-none bg-light text-muted" value="juan@university.edu" disabled>
              <div class="form-text small">Email cannot be changed after registration.</div>
            </div>
            
            <div class="col-md-6">
              <label class="form-label fw-semibold small text-dark">Major / Degree Program</label>
              <input type="text" class="form-control border-sb shadow-none" placeholder="e.g., Computer Science">
            </div>
            
            <div class="col-md-6">
              <label class="form-label fw-semibold small text-dark">Year Level</label>
              <select class="form-select border-sb shadow-none">
                <option value="1">1st Year</option>
                <option value="2">2nd Year</option>
                <option value="3">3rd Year</option>
                <option value="4">4th Year</option>
                <option value="5">Graduate</option>
              </select>
            </div>
            
            <div class="col-12 mt-3">

              <div class="d-flex justify-content-between align-items-center mb-3">
                <label class="form-label fw-semibold small text-dark mb-0">
                  Subjects Offered
                </label>
                <button type="button" class="btn btn-outline-dark btn-sm rounded-3 fw-semibold px-3">
                  Edit
                </button>
              </div>

              <div class="d-flex flex-wrap gap-2">
                <span class="badge bg-sb-primary text-white px-3 py-2 rounded-pill">
                  Mathematics
                </span>

                <span class="badge bg-sb-primary text-white px-3 py-2 rounded-pill">
                  Physics
                </span>

                <span class="badge bg-sb-primary text-white px-3 py-2 rounded-pill">
                  Programming
                </span>

                <span class="badge bg-sb-primary text-white px-3 py-2 rounded-pill">
                  Data Structures
                </span>
              </div>

            </div>

            <div class="col-12">
              <label class="form-label fw-semibold small text-dark">Bio (About Me)</label>
              <textarea class="form-control border-sb shadow-none" rows="4" placeholder="Tell tutors a bit about your learning style or what you usually need help with..."></textarea>
            </div>
            
          </div>

          <div class="text-end mt-2">
            <button type="submit" class="btn bg-sb-primary text-white px-5 py-2 rounded-3 fw-semibold shadow-sm">
              Save Changes
            </button>
          </div>
        </form>

      </div>
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore()

const userRole = computed(() => authStore.user?.role?.toLowerCase() || null)

const saveProfile = () => {
  // In a real application, this would trigger an API call to update the database
  alert('Profile updated successfully! (Placeholder logic)')
}
</script>

<style scoped>
.form-control:focus, .form-select:focus {
  border-color: var(--sb-primary);
  box-shadow: 0 0 0 0.25rem rgba(0, 137, 90, 0.25);
}
</style>
```

--- src/views/Register.vue ---
```
<template>
  <div class="min-vh-100 d-flex align-items-center justify-content-center py-5">
    <div class="card border-sb shadow-sm rounded-4" style="max-width: 450px; width: 100%;">
      <div class="card-body p-4 p-md-5">
        <div class="text-center mb-4">
          <div class="d-inline-flex align-items-center justify-content-center bg-success bg-opacity-10 rounded-3 mb-3" style="width: 48px; height: 48px;">
            <i class="bi bi-book text-sb-primary fs-4"></i>
          </div>
          <h3 class="fw-bold text-dark">Create Account</h3>
          <p class="text-muted small">Join the StudyBuddy network</p>
        </div>

        <div v-if="generalError" class="alert alert-danger">
          {{ generalError }}
        </div>

        <form @submit.prevent="handleRegister">
          <div class="mb-3">
            <label class="form-label fw-semibold small text-dark">First Name</label>
            <div class="input-group">
              <span class="input-group-text bg-white border-end-0 text-muted"><i class="bi bi-person"></i></span>
              <input type="text" v-model="store.newUserFname" class="form-control border-start-0 ps-0 shadow-none" placeholder="Juan Dela Cruz" required>
            </div>
          </div>

          <div class="mb-3">
            <label class="form-label fw-semibold small text-dark">Middle Name</label>
            <div class="input-group">
              <span class="input-group-text bg-white border-end-0 text-muted"><i class="bi bi-person"></i></span>
              <input type="text" v-model="store.newUserMname" class="form-control border-start-0 ps-0 shadow-none" placeholder="Juan Dela Cruz" required>
            </div>
          </div>

          <div class="mb-3">
            <label class="form-label fw-semibold small text-dark">Last Name</label>
            <div class="input-group">
              <span class="input-group-text bg-white border-end-0 text-muted"><i class="bi bi-person"></i></span>
              <input type="text" v-model="store.newUserLname" class="form-control border-start-0 ps-0 shadow-none" placeholder="Juan Dela Cruz" required>
            </div>
          </div>

          <div class="mb-3">
            <label class="form-label fw-semibold small text-dark">University Email</label>
            <div class="input-group">
              <span class="input-group-text bg-white border-end-0 text-muted"><i class="bi bi-envelope"></i></span>
              <input type="email" v-model="store.newUserEmail" class="form-control border-start-0 ps-0 shadow-none" placeholder="you@university.edu" required>
            </div>
            <div v-if="emailError" class="text-danger small mt-1">{{ emailError }}</div>
          </div>

          <div class="mb-3">
            <label class="form-label fw-semibold small text-dark">Institution</label>
            <select v-model="store.selectedInstitutionId" class="form-select shadow-none" required>
              <option value="" disabled>Select your institution</option>
              <option
                v-for="institution in institutions"
                :key="institution.id"
                :value="String(institution.id)"
              >
                {{ institution.institution_name }} ({{ institution.school_email_domain }})
              </option>
            </select>
            <div v-if="selectedInstitutionDomain" class="form-text small">
              Allowed email domain: {{ selectedInstitutionDomain }}
            </div>
            <div v-if="institutionError" class="text-danger small mt-1">{{ institutionError }}</div>
          </div>

          <div class="mb-3">
            <label class="form-label fw-semibold small text-dark">Password</label>
            <div class="input-group">
              <span class="input-group-text bg-white border-end-0 text-muted"><i class="bi bi-lock"></i></span>
              <input type="password" v-model="store.newUserPassword" class="form-control border-start-0 ps-0 shadow-none" placeholder="â€¢â€¢â€¢â€¢â€¢â€¢â€¢â€¢" required>
            </div>
          </div>

          <div class="mb-4">
            <label class="form-label fw-semibold small text-dark">I want to</label>
            <select v-model="store.newUserType" class="form-select shadow-none" required>
              <option value="" disabled selected>Select your role</option>
              <option value="Tutee">Find a Tutor (Student)</option>
              <option value="Tutor">Become a Tutor</option>
            </select>
          </div>

          <button type="submit" class="btn bg-sb-primary text-white w-100 py-2 rounded-3 fw-semibold shadow-sm d-flex justify-content-center align-items-center gap-2" :disabled="isSubmitting">
            <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-2"></span>
            {{ isSubmitting ? 'Processing...' : 'Create Account' }}
            <i v-if="!isSubmitting" class="bi bi-arrow-right"></i>
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useRegistrationInfoStore } from '@/stores/registrationinfo'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'

const router = useRouter()
const store = useRegistrationInfoStore()
const authStore = useAuthStore()

const isSubmitting = ref(false)
const institutions = ref([])

const generalError = ref('')
const emailError = ref('')
const institutionError = ref('')

const selectedInstitution = computed(() => {
  return institutions.value.find(
    (institution) => String(institution.id) === String(store.selectedInstitutionId)
  ) || null
})

const selectedInstitutionDomain = computed(() => {
  return selectedInstitution.value?.school_email_domain || ''
})

const emailDomainMatchesInstitution = computed(() => {
  if (!store.newUserEmail || !selectedInstitutionDomain.value) {
    return true
  }

  const parts = store.newUserEmail.split('@')

  if (parts.length !== 2) {
    return false
  }

  return parts[1].trim().toLowerCase() === selectedInstitutionDomain.value.toLowerCase()
})

const loadInstitutions = async () => {
  try {
    const response = await axios.get('http://localhost:8000/api/partner-institutions/')
    institutions.value = response.data
  } catch (error) {
    console.error('Failed to load partner institutions:', error)
    generalError.value = 'Unable to load partner institutions right now. Please try again later.'
  }
}

const handleRegister = async () => {

  generalError.value = ''
  emailError.value = ''
  institutionError.value = ''

  // ðŸ”¹ Basic validation
  if (!store.newUserFname ||
      !store.newUserLname ||
      !store.newUserEmail ||
      !store.newUserPassword ||
      !store.selectedInstitutionId) {

    generalError.value = "Please fill in all required fields."
    return
  }

  // ðŸ”¹ Role validation
  if (!store.newUserType) {
    generalError.value = "Please select your role."
    return
  }

  if (!emailDomainMatchesInstitution.value) {
    institutionError.value = 'Your email domain does not match the selected institution. Please check and try again.'
    return
  }

  isSubmitting.value = true

  try {

    const role = store.newUserType

    // ðŸ”¹ REGISTER USER
    await axios.post('http://localhost:8000/api/register/', {
      fname: store.newUserFname,
      mname: store.newUserMname,
      lname: store.newUserLname,
      email: store.newUserEmail,
      password: store.newUserPassword,
      role: role,
      institution_id: store.selectedInstitutionId
    })

    // ðŸ”¹ AUTO LOGIN
    await authStore.login({
      email: store.newUserEmail,
      password: store.newUserPassword
    })

    // ðŸ”¹ ROLE BASED REDIRECT
    if (role === 'Tutor') {
      router.push('/tutor-setup')
    } else {
      router.push('/preferencesetup')
    }

  } catch (error) {

    console.error('Registration Error:', error)

    if (error.response) {

      const data = error.response.data

      const message = data.error || data.detail || "Registration failed. Please try again."

      if (message.toLowerCase().includes('email')) {
        emailError.value = message
      } else if (message.toLowerCase().includes('institution')) {
        institutionError.value = message
      } else {
        generalError.value = message
      }

    }

    else if (error.request) {
      generalError.value = "Server not responding. Please try again later."
    }

    else {
      generalError.value = "An unexpected error occurred."
    }

  } finally {
    isSubmitting.value = false
  }
}

onMounted(() => {
  loadInstitutions()
})
</script>
```

--- src/views/Schedule.vue ---
```
<template>
  <div class="schedule-content">
    <div class="mb-4">
      <h2 class="fw-bold text-dark">My Schedule</h2>
      <p class="text-muted">Manage your availability for tutoring sessions.</p>
    </div>

    <div class="card border-sb border-1 shadow-sm rounded-4">
      <div class="card-body p-4 p-md-5">
        
        <h4 class="fw-bold mb-4 d-flex align-items-center">
          <i class="bi bi-calendar-check text-sb-primary me-3"></i> Weekly Availability
        </h4>

        <div class="d-flex flex-column gap-3">
          
          <div 
            v-for="day in weeklySchedule" 
            :key="day.name" 
            class="card border-sb rounded-4 shadow-none"
          >
            <div class="card-body p-4">
              <h6 class="fw-bold mb-3">{{ day.name }}</h6>
              
              <div class="d-flex flex-wrap gap-3">
                <div 
                  v-for="slot in day.slots" 
                  :key="slot.id"
                  class="time-slot-pill d-flex align-items-center justify-content-between border border-sb rounded-pill px-3 py-2 bg-white"
                >
                  
                  <div class="d-flex align-items-center text-muted" style="font-size: 0.9rem;">
                    <i class="bi bi-clock me-2"></i>
                    <span>{{ slot.time }}</span>
                  </div>

                  <div class="d-flex align-items-center gap-2 ms-4">
                    <div class="form-check form-switch mb-0 custom-switch-wrapper">
                      <input 
                        class="form-check-input custom-switch shadow-none cursor-pointer" 
                        type="checkbox" 
                        role="switch" 
                        v-model="slot.isOpen"
                        @change="handleScheduleChange(day.name, slot)"
                      >
                    </div>
                    <span 
                      class="badge rounded-pill px-3 py-1 fw-normal" 
                      :class="slot.isOpen ? 'bg-sb-primary text-white' : 'bg-light text-muted border border-sb'"
                    >
                      {{ slot.isOpen ? 'Open' : 'Closed' }}
                    </span>
                  </div>

                </div>
              </div>
            </div>
          </div>

        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// Data-driven state: This mimics what your backend API will eventually send
const weeklySchedule = ref([
  {
    name: 'Monday',
    slots: [
      { id: 'm1', time: '9:00 â€“ 12:00', isOpen: true },
      { id: 'm2', time: '14:00 â€“ 17:00', isOpen: false }
    ]
  },
  {
    name: 'Tuesday',
    slots: [
      { id: 't1', time: '10:00 â€“ 13:00', isOpen: true },
      { id: 't2', time: '14:00 â€“ 17:00', isOpen: true }
    ]
  },
  {
    name: 'Wednesday',
    slots: [
      { id: 'w1', time: '9:00 â€“ 12:00', isOpen: false },
      { id: 'w2', time: '14:00 â€“ 17:00', isOpen: true }
    ]
  },
  {
    name: 'Thursday',
    slots: [
      { id: 'th1', time: '9:00 â€“ 12:00', isOpen: true },
      { id: 'th2', time: '14:00 â€“ 17:00', isOpen: false }
    ]
  },
  {
    name: 'Friday',
    slots: [
      { id: 'f1', time: '9:00 â€“ 12:00', isOpen: true },
      { id: 'f2', time: '14:00 â€“ 17:00', isOpen: true }
    ]
  }
])

// Strategic foundation: Prepare for your API logic
const handleScheduleChange = (dayName, slot) => {
  // In the future, this is where you trigger an Axios/Fetch request to update the database
  console.log(`Updated workload capacity: ${dayName} at ${slot.time} is now ${slot.isOpen ? 'Open' : 'Closed'}`);
}
</script>

<style scoped>
/* Force the pill containers to a consistent minimum width matching the design */
.time-slot-pill {
  min-width: 260px;
}

/* Make the toggle pointer act like a clickable button */
.cursor-pointer {
  cursor: pointer;
}

/* Customizing Bootstrap's default blue switch to your brand's green */
.custom-switch-wrapper .form-check-input {
  width: 2.5em;
  height: 1.25em;
}

.custom-switch-wrapper .form-check-input:checked {
  background-color: var(--sb-primary);
  border-color: var(--sb-primary);
}

.custom-switch-wrapper .form-check-input:focus {
  border-color: rgba(0, 137, 90, 0.25);
  box-shadow: 0 0 0 0.25rem rgba(0, 137, 90, 0.25);
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='-4 -4 8 8'%3e%3ccircle r='3' fill='rgba%280, 0, 0, 0.25%29'/%3e%3c/svg%3e");
}

.custom-switch-wrapper .form-check-input:checked:focus {
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='-4 -4 8 8'%3e%3ccircle r='3' fill='%23fff'/%3e%3c/svg%3e");
}
</style>
```

--- src/views/SessionsReports.vue ---
```
<template>
  <div class="reports-content">
    <div class="mb-4">
      <h2 class="fw-bold text-dark">Sessions & Reports</h2>
      <p class="text-muted">Track your tutoring history, earnings, and performance.</p>
    </div>

    <div class="row g-4 mb-5">
      <div class="col-md-3">
        <div class="card border-sb shadow-sm h-100 rounded-4">
          <div class="card-body d-flex flex-column justify-content-center text-center py-4">
            <div class="d-flex align-items-center justify-content-center mb-2 gap-2">
              <div class="rounded-circle bg-success bg-opacity-10 text-sb-primary d-flex justify-content-center align-items-center" style="width: 32px; height: 32px;">
                <i class="bi bi-calendar-event"></i>
              </div>
              <span class="text-muted small fw-semibold">Total Sessions</span>
            </div>
            <h3 class="fw-bold mb-0">{{ totalSessions }}</h3>
          </div>
        </div>
      </div>
      
      <div class="col-md-3">
        <div class="card border-sb shadow-sm h-100 rounded-4">
          <div class="card-body d-flex flex-column justify-content-center text-center py-4">
            <div class="d-flex align-items-center justify-content-center mb-2 gap-2">
               <div class="rounded-circle bg-success bg-opacity-10 text-sb-primary d-flex justify-content-center align-items-center" style="width: 32px; height: 32px;">
                <i class="bi bi-currency-dollar"></i>
              </div>
              <span class="text-muted small fw-semibold">Total Earnings</span>
            </div>
            <h3 class="fw-bold mb-0">{{ totalEarnings }}</h3>
          </div>
        </div>
      </div>

      <div class="col-md-3">
        <div class="card border-sb shadow-sm h-100 rounded-4">
          <div class="card-body d-flex flex-column justify-content-center text-center py-4">
             <div class="d-flex align-items-center justify-content-center mb-2 gap-2">
               <div class="rounded-circle bg-warning bg-opacity-10 text-warning d-flex justify-content-center align-items-center" style="width: 32px; height: 32px;">
                <i class="bi bi-star"></i>
              </div>
              <span class="text-muted small fw-semibold">Avg Rating</span>
            </div>
            <h3 class="fw-bold mb-0">{{ averageRating }}</h3>
          </div>
        </div>
      </div>

      <div class="col-md-3">
        <div class="card border-sb shadow-sm h-100 rounded-4">
          <div class="card-body d-flex flex-column justify-content-center text-center py-4">
            <div class="d-flex align-items-center justify-content-center mb-2 gap-2">
               <div class="rounded-circle bg-info bg-opacity-10 text-info d-flex justify-content-center align-items-center" style="width: 32px; height: 32px;">
                <i class="bi bi-graph-up-arrow"></i>
              </div>
              <span class="text-muted small fw-semibold">Hours Tutored</span>
            </div>
            <h3 class="fw-bold mb-0">{{totalHours.toFixed(1)}}h</h3>
          </div>
        </div>
      </div>
    </div>

    <div class="card border-sb border-1 shadow-sm rounded-4">
      <div class="card-body p-4 p-md-5">
        
        <h4 class="fw-bold mb-4 d-flex align-items-center">
          <i class="bi bi-file-earmark-text text-sb-primary me-3"></i> Session History
        </h4>

        <div class="d-flex gap-2 mb-4 bg-light p-2 rounded-3 d-inline-flex border border-sb">
          <button 
            v-for="filter in filters" 
            :key="filter.value"
            @click="currentFilter = filter.value"
            class="btn rounded-pill px-3 py-1 fw-semibold text-muted shadow-none transition-all"
            :class="currentFilter === filter.value ? 'bg-white text-dark shadow-sm' : 'btn-light'"
          >
            {{ filter.label }}
          </button>
        </div>

        <div class="table-responsive">
          <table class="table table-hover align-middle mb-0">
            <thead>
              <tr class="text-muted small align-bottom" style="border-bottom: 2px solid var(--sb-card-border);">
                <th class="fw-semibold pb-3">Subject</th>
                <th class="fw-semibold pb-3">Tutor</th>
                <th class="fw-semibold pb-3">Date</th>
                <th class="fw-semibold pb-3">Duration</th>
                <th class="fw-semibold pb-3">Status</th>
                <th class="fw-semibold pb-3">Rating</th>
                <th class="fw-semibold pb-3">Earnings</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr 
              v-for="session in filteredSessions" 
              :key="session.id" 
              style="border-bottom: 1px solid var(--sb-card-border);"
              class="session-row">
                <td class="py-3 fw-bold">{{ session.subject }}</td>
                <td class="py-3">{{ session.tutor }}</td>
                <td class="py-3">{{ session.date }}</td>
                <td class="py-3">{{ session.startTime }} - {{ session.endTime }}</td>
                <td class="py-3">
                  <span class="badge rounded-pill px-3 py-1 fw-normal" :class="getStatusClass(session.status)">
                    {{ session.status }}
                  </span>
                </td>
                <td class="py-3">
                  <span v-if="session.rating" class="d-flex align-items-center text-warning fw-bold small">
                    <i class="bi bi-star-fill me-1"></i> {{ session.rating }}
                  </span>
                  <span v-else class="text-muted">â€”</span>
                </td>
                <td class="py-3 fw-bold">
                  {{ session.earnings ? 'â‚±' + session.earnings : 'â€”' }}
                </td>
                <td class="py-3 text-end action-cell">
                  <button 
                    class="btn btn-sm bg-sb-primary text-white"
                    @click="goToDetails(session.id)"
                  >
                    View Details
                  </button>
                </td>
              </tr>
              
              <tr v-if="filteredSessions.length === 0">
                <td colspan="7" class="text-center py-5 text-muted">
                  No sessions found for this category.
                </td>
              </tr>
            </tbody>
          </table>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useSessionsStore } from '@/stores/completedSessions'
import { useRouter } from 'vue-router'

const router = useRouter()
const sessionStore = useSessionsStore()
const currentFilter = ref('All')

const filters = computed(() => [
  { 
    label: `All (${sessionStore.sessions.length})`, 
    value: 'All' 
  },
  { 
    label: `Completed (${sessionStore.completedSessions.length})`, 
    value: 'completed' 
  },
  { 
    label: `Upcoming (${sessionStore.upcomingSessions.length})`, 
    value: 'upcoming' 
  },
  { 
    label: `Cancelled (${sessionStore.cancelledSessions.length})`, 
    value: 'cancelled' 
  }
])

onMounted(() => {
  sessionStore.fetchSessions()
})

const goToDetails = (sessionId) => {
  router.push(`/booking-details/${sessionId}`)
}

const totalSessions = computed(() =>
  sessionStore.sessions.length
)

const totalEarnings = computed(() =>
  sessionStore.completedSessions
    .reduce((sum, s) => sum + (s.earnings || 0), 0)
)

const averageRating = computed(() => {
  const rated = sessionStore.completedSessions
    .filter(s => s.rating)

  if (!rated.length) return 0

  return (
    rated.reduce((sum, s) => sum + s.rating, 0) /
    rated.length
  ).toFixed(1)
})

const totalHours = computed(() =>
  sessionStore.completedSessions
    .reduce((sum, s) => {
      const start = new Date(`1970-01-01T${s.startTime}`)
      const end = new Date(`1970-01-01T${s.endTime}`)
      return sum + (end - start)
    }, 0) / (1000 * 60 * 60)
)

const filteredSessions = computed(() => {
  switch (currentFilter.value) {
    case 'completed':
      return sessionStore.completedSessions
    case 'upcoming':
      return sessionStore.upcomingSessions
    case 'cancelled':
      return sessionStore.cancelledSessions
    default:
      return sessionStore.sessions
  }
})

const getStatusClass = (status) => {
  switch (status?.toLowerCase()) {
    case 'upcoming':
      return 'bg-warning bg-opacity-25 text-dark' // Soft orange
    case 'completed':
      return 'bg-sb-primary text-white' // Solid Green
    case 'cancelled':
      return 'bg-danger text-white' // Solid Red
    default:
      return 'bg-secondary text-white'
  }
}
</script>

<style scoped>
/* Smooth transition for the filter pill buttons */
.transition-all {
  transition: all 0.2s ease-in-out;
}

/* Ensure the table looks completely clean, removing default Bootstrap borders on the sides */
.table > :not(caption) > * > * {
  border-bottom-width: 0px;
}

.session-row {
  position: relative;
}
</style>
```

--- src/views/TestApi.vue ---
```
<template>
  <div style="padding: 40px;">
    <h1>Test API Connection</h1>

    <input v-model="newMessage" placeholder="Enter message" />
    <button @click="sendMessage">Send</button>

    <hr />

    <button @click="loadMessages">Load Messages</button>

    <ul v-if="messages.length">
      <li v-for="msg in messages" :key="msg.id">
        {{ msg.message }}
      </li>
    </ul>

    <p v-else>No messages yet.</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const messages = ref([])
const newMessage = ref('')

const loadMessages = async () => {
  const response = await fetch('http://127.0.0.1:8000/api/test/')
  const data = await response.json()
  messages.value = data
}

const sendMessage = async () => {
  await fetch('http://127.0.0.1:8000/api/test/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      message: newMessage.value
    })
  })

  newMessage.value = ''
  loadMessages()
}
</script>
```

--- src/views/TuteeProfile.vue ---
```
<template>
  <div class="profile-content">
    <div class="mb-4">
      <h2 class="fw-bold text-dark">My Profile</h2>
      <p class="text-muted">Manage your personal information and tutoring preferences.</p>
    </div>

    <div class="card border-sb shadow-sm rounded-4" style="max-width: 800px;">
      <div class="card-body p-4 p-md-5">
        
        <!-- PROFILE HEADER -->
        <div class="d-flex align-items-center mb-4 pb-4 border-bottom border-sb">
          <div
            class="rounded-circle bg-success bg-opacity-10 text-sb-primary d-flex justify-content-center align-items-center fw-bold fs-3 me-4"
            style="width: 80px; height: 80px;"
          >
            {{ initials }}
          </div>

          <div>
            <h5 class="fw-bold mb-1">
              {{ profile.fname }} {{ profile.lname }}
            </h5>
            <p class="text-muted small mb-2">Student / Tutee</p>
            <button class="btn btn-outline-dark btn-sm rounded-3 fw-semibold px-3">
              Update Photo
            </button>
          </div>
        </div>

        <form @submit.prevent="saveProfile">

          <div class="row g-4 mb-4">

            <!-- FIRST NAME -->
            <div class="col-md-4">
              <label class="form-label fw-semibold small text-dark">First Name</label>
              <input
                type="text"
                v-model="profile.fname"
                class="form-control border-sb shadow-none"
              >
            </div>

            <!-- MIDDLE NAME -->
            <div class="col-md-4">
              <label class="form-label fw-semibold small text-dark">Middle Name</label>
              <input
                type="text"
                v-model="profile.mname"
                class="form-control border-sb shadow-none"
              >
            </div>

            <!-- LAST NAME -->
            <div class="col-md-4">
              <label class="form-label fw-semibold small text-dark">Last Name</label>
              <input
                type="text"
                v-model="profile.lname"
                class="form-control border-sb shadow-none"
              >
            </div>

            <!-- EMAIL -->
            <div class="col-md-6">
              <label class="form-label fw-semibold small text-dark">University Email</label>
              <input
                type="email"
                v-model="profile.email"
                class="form-control border-sb shadow-none bg-light text-muted"
                disabled
              >
              <div class="form-text small">
                Email cannot be changed after registration.
              </div>
            </div>

            <!-- COURSE -->
            <div class="col-md-6">
              <label class="form-label fw-semibold">Course</label>

              <select v-model="profile.course" class="form-select">

                <option value="">Select Course</option>

                <option
                  v-for="course in courses"
                  :key="course.course_code"
                  :value="course.course_code"
                >
                  {{ course.course_name }}
                </option>

              </select>
            </div>

            <div class="col-md-6">
              <label class="form-label fw-semibold">Preferred Subjects</label>

              <select
                v-model="profile.subjects"
                class="form-select"
                multiple
              >

                <option
                  v-for="subject in subjects"
                  :key="subject.subject_code"
                  :value="subject.subject_code"
                >
                  {{ subject.subject_name }}
                </option>

              </select>

            </div>

            <!-- YEAR LEVEL -->
            <div class="col-md-6">
              <label class="form-label fw-semibold">Year Level</label>

              <select v-model="profile.year_level" class="form-select">

                <option value="">Select Year Level</option>

                <option
                  v-for="level in yearLevels"
                  :key="level.value"
                  :value="level.value"
                >
                  {{ level.label }}
                </option>

              </select>
            </div>

            <!-- BIO -->
            <div class="col-12">
              <label class="form-label fw-semibold small text-dark">
                Bio (About Me)
              </label>

              <textarea
                v-model="profile.bio"
                class="form-control border-sb shadow-none"
                rows="4"
                placeholder="Tell tutors a bit about your learning style or what you usually need help with..."
              ></textarea>
            </div>

          </div>

          <div class="text-end mt-2">
            <button
              type="submit"
              class="btn bg-sb-primary text-white px-5 py-2 rounded-3 fw-semibold shadow-sm"
            >
              Save Changes
            </button>
          </div>

        </form>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api/api'

const profile = ref({
  fname: '',
  lname: '',
  email: '',
  course: '',
  year_level: '',
  bio: ''
})

const courses = ref([])

/*
-----------------------------
LOAD PROFILE DATA
-----------------------------
*/
const loadProfile = async () => {
  try {
    const res = await api.get('/tutee/profile/')
    profile.value = res.data
  } catch (err) {
    console.error("Failed to load profile", err)
  }
}

const yearLevels = [

  { label: "Grade 1", value: 1 },
  { label: "Grade 2", value: 2 },
  { label: "Grade 3", value: 3 },
  { label: "Grade 4", value: 4 },
  { label: "Grade 5", value: 5 },
  { label: "Grade 6", value: 6 },
  { label: "Grade 7", value: 7 },
  { label: "Grade 8", value: 8 },
  { label: "Grade 9", value: 9 },
  { label: "Grade 10", value: 10 },
  { label: "Grade 11", value: 11 },
  { label: "Grade 12", value: 12 },

  { label: "1st Year College", value: 13 },
  { label: "2nd Year College", value: 14 },
  { label: "3rd Year College", value: 15 },
  { label: "4th Year College", value: 16 }

]


const subjects = ref([])

const loadSubjects = async () => {

  const res = await api.get('subjects/')

  subjects.value = res.data

}
/*
-----------------------------
LOAD COURSES FOR DROPDOWN
-----------------------------
*/
const loadCourses = async () => {
  try {

    const res = await api.get('courses/')

    console.log("Courses loaded:", res.data)

    courses.value = res.data

  } catch (err) {
    console.error("Failed to load courses", err)
  }
}

import { computed } from 'vue'

const initials = computed(() => {

  const first = profile.value?.fname?.charAt(0) || ''
  const last = profile.value?.lname?.charAt(0) || ''

  return (first + last).toUpperCase()

})
/*
-----------------------------
SAVE PROFILE
-----------------------------
*/
const saveProfile = async () => {
  try {

    await api.put('/tutee/profile/update/', profile.value)

    alert("Profile updated successfully")

  } catch (err) {
    console.error(err)
    alert("Failed to update profile")
  }
}

onMounted(() => {
  loadProfile()
  loadCourses()
  loadSubjects()
})
</script>
```

--- src/views/TutorDashboard.vue ---
```
<template>
  <div class="p-4">

    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="fw-bold text-dark">Teaching Hub</h2>

      <router-link
        to="/tch-availability"
        class="btn bg-sb-primary text-white rounded-3 px-4 fw-semibold shadow-sm"
      >
        Set Schedule
      </router-link>
    </div>


    <!-- Stats Cards -->
    <div class="row g-4 mb-4">

      <div class="col-md-4">
        <div class="card border-sb rounded-4 p-4 shadow-sm h-100">
          <p class="text-muted small fw-bold mb-2">TOTAL SESSIONS</p>
          <h2 class="fw-bold mb-0 text-dark">{{ totalSessions }}</h2>
        </div>
      </div>

      <div class="col-md-4">
        <div class="card border-sb rounded-4 p-4 shadow-sm h-100">
          <p class="text-muted small fw-bold mb-2">AVG RATING</p>
          <h2 class="fw-bold mb-0 text-dark d-flex align-items-center">
            {{ avgRating }}
            <i class="bi bi-star-fill text-warning fs-4 ms-2"></i>
          </h2>
        </div>
      </div>

      <div class="col-md-4">
        <div
          class="card border-0 rounded-4 p-4 shadow-sm h-100"
          style="background-color: var(--sb-dark);"
        >
          <p class="text-white-50 small fw-bold mb-2">EARNINGS</p>
          <h2 class="fw-bold text-white mb-0">â‚±{{ earnings }}</h2>
        </div>
      </div>

    </div>


    <!-- Upcoming Bookings -->
    <div class="card border-sb rounded-4 shadow-sm">

      <div class="card-body p-4">

        <h6 class="fw-bold text-dark mb-4">Upcoming Bookings</h6>

        <!-- No bookings -->
        <div v-if="upcomingBookings.length === 0" class="text-muted text-center py-4">
          No upcoming sessions yet.
        </div>

        <!-- Table -->
        <div v-else class="table-responsive">

          <table class="table align-middle mb-0">

            <thead>
              <tr class="small fw-bold text-muted">
                <th class="border-bottom-0 pb-3">STUDENT</th>
                <th class="border-bottom-0 pb-3">SUBJECT</th>
                <th class="border-bottom-0 pb-3">DATE</th>
                <th class="border-bottom-0 pb-3">STATUS</th>
                <th class="border-bottom-0 pb-3"></th>
              </tr>
            </thead>

            <tbody>

              <tr
                v-for="booking in upcomingBookings"
                :key="booking.id"
                style="border-top: 1px solid var(--sb-card-border);"
              >

                <!-- Student -->
                <td class="py-3 text-dark">
                  {{ booking.student }}
                </td>

                <!-- Subject -->
                <td class="py-3">
                  <span class="badge bg-light text-dark border border-sb px-2 py-1">
                    {{ booking.subject || 'General' }}
                  </span>
                </td>

                <!-- Date -->
                <td class="py-3 text-dark">
                  {{ new Date(booking.date).toLocaleDateString() }}
                </td>

                <!-- Status -->
                <td class="py-3">

                  <span
                    class="badge px-3 py-1 rounded-pill"
                    :class="{
                      'bg-warning bg-opacity-10 text-warning border border-warning':
                        booking.status === 'Pending',

                      'bg-success bg-opacity-10 text-success border border-success':
                        booking.status === 'Confirmed',

                      'bg-secondary bg-opacity-10 text-secondary border border-secondary':
                        booking.status === 'Completed'
                    }"
                  >
                    {{ booking.status }}
                  </span>

                </td>

                <!-- Action -->
                <td class="py-3 text-end">

                  <button
                    class="btn btn-success btn-sm"
                    @click="goToBookingDetails(booking.id)"
                  >
                    View Details
                  </button>

                </td>

              </tr>

            </tbody>

          </table>

        </div>

      </div>

    </div>

  </div>
</template>


<script setup>
import { useRouter } from 'vue-router'
import { ref, onMounted } from 'vue'
import api from '@/services/api/api'

const router = useRouter()

const totalSessions = ref(0)
const avgRating = ref(0)
const earnings = ref(0)
const upcomingBookings = ref([])




const goToBookingDetails = (id) => {
  router.push({
    name: 'booking-details',
    params: { id }
  })
}

const loadTutorDashboard = async () => {

  try {

    const response = await api.get('tutor-dashboard/')

    totalSessions.value = response.data.total_sessions
    avgRating.value = response.data.rating_average
    earnings.value = response.data.total_earnings

    // âœ… just assign what backend sends
    upcomingBookings.value = response.data.upcoming_bookings || []

  } catch (error) {

    console.error("Failed to load tutor dashboard:", error)

  }

}

onMounted(loadTutorDashboard)
</script>
```

--- src/views/TutorDetails.vue ---
Summary only because this file exceeds 300 lines (321 lines).

Vue single-file component for the tutee's tutor-booking detail screen.
- Renders tutor profile info, subject badges, hourly rate, bio, and a week-view schedule table.
- Reads oute.params.id as the tutor id.
- Uses selectedSessions and ookedSessionDetails Pinia stores.
- Calls GET tutors/:id/ to load tutor details.
- Calls GET tutors/:id/availability/?date=YYYY-MM-DD to load bookable slots for the selected date.
- Lets the user pick a date and select one or more slots.
- Enforces booking constraints in the client: slots must be on the same date and must form consecutive one-hour blocks.
- On booking, stores the chosen slots/tutor metadata in Pinia and routes to /payment-tutee/:tutorId.
- Includes scoped styles for slot states (vailable, ooked, selected) and card media.

--- src/views/TutorPaymentScreen.vue ---
```
<template>
  <div class="p-4">
    <h2 class="fw-bold mb-4">Payment Verification</h2>

    <div class="card border-sb rounded-4 shadow-sm overflow-hidden">
      <div class="table-responsive">
        <table class="table table-hover align-middle mb-0">
          <thead class="bg-light">
            <tr>
              <th class="ps-4">Tutee</th>
              <th>Amount</th>
              <th>Status</th>
              <th class="text-end pe-4">Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="pay in payments" :key="pay.id">
              <td class="ps-4 fw-semibold">{{ pay.name }}</td>
              <td class="fw-bold">â‚±{{ pay.amount }}</td>
              <td><span class="badge bg-warning-subtle text-warning border border-warning">Pending</span></td>
              <td class="text-end pe-4">
                <button @click="verify(pay.id)" class="btn btn-sm bg-sb-primary text-white px-3 fw-bold">Verify Paid</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
const payments = ref([
  { id: 1, name: 'Lia Salinas', amount: 250 },
  { id: 2, name: 'Reggie Cruz', amount: 500 }
])
const verify = (id) => {
  payments.value = payments.value.filter(p => p.id !== id)
  alert('Payment verified! Booking finalized.')
}
</script>
```

--- src/views/TutorPreferenceSetup.vue ---
```
<template>
  <div class="min-vh-100 bg-light py-5">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-md-7 col-lg-6">
          <div class="card border-0 shadow-sm rounded-4">
            <div class="card-body p-4 p-md-5">
              <div class="text-center mb-4">
                <h3 class="fw-bold text-dark">Tutor Profile Setup</h3>
                <p class="text-muted">Set your teaching preferences to start matching.</p>
              </div>

              <form @submit.prevent="handleCompleteSetup">
                <div class="mb-4">
                  <label class="form-label fw-bold small text-muted">TEACHING LEVEL</label>
                  <select v-model="form.teaching_level" class="form-select border-sb shadow-none" required>
                    <option value="" disabled>Select level</option>
                    <option value="Elementary">Elementary</option>
                    <option value="High School">High School</option>
                    <option value="College">College</option>
                  </select>
                </div>

                <div class="mb-4">
                  <label class="form-label fw-bold small text-muted d-block">MODALITY</label>
                  <div class="form-check form-switch mb-2">
                    <input class="form-check-input" type="checkbox" v-model="form.can_online" id="on">
                    <label class="form-check-label" for="on">Online Sessions</label>
                  </div>
                  <div class="form-check form-switch">
                    <input class="form-check-input" type="checkbox" v-model="form.can_f2f" id="f2f">
                    <label class="form-check-label" for="f2f">Face-to-Face Sessions</label>
                  </div>
                </div>

                <div class="mb-5">
                  <label class="form-label fw-bold small text-muted">HOURLY RATE (PHP)</label>
                  <input type="number" v-model="form.hourly_rate" class="form-control border-sb shadow-none" placeholder="â‚± 0.00" required>
                </div>

                <button type="submit" class="btn bg-sb-primary text-white w-100 py-3 rounded-3 fw-bold shadow-sm">
                  Complete Profile
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useProfileStore } from '@/stores/profile'
import api from '@/services/api/api'

const router = useRouter()
const profileStore = useProfileStore()

const form = ref({
  teaching_level: '',
  can_online: true,
  can_f2f: false,
  hourly_rate: null
})


/* LOAD EXISTING TUTOR DATA */
onMounted(async () => {

  try {

    const response = await api.get('/tutor-dashboard/')

    const tutor = response.data

    form.value.teaching_level = tutor.teaching_level
    form.value.can_online = tutor.can_online
    form.value.can_f2f = tutor.can_f2f
    form.value.hourly_rate = tutor.hourly_rate

  } catch (error) {

    console.log("New tutor setup")

  }

})


/* SUBMIT PROFILE SETUP */
const handleCompleteSetup = async () => {

  try {

    await api.post('/tutor/setup/', form.value)

    // update profile guard state
    profileStore.profileCompleted = true

    router.push({ name: 'tch-dashboard' })

  } catch (error) {

    console.error("Failed to save tutor profile", error)
    alert("Could not save tutor profile.")

  }

}
</script>
```

--- src/views/TutorProfile.vue ---
```
<template>
<div class="profile-content">

  <div class="mb-4">
    <h2 class="fw-bold text-dark">My Profile</h2>
    <p class="text-muted">Manage your tutoring information.</p>
  </div>

  <div class="card border-sb shadow-sm rounded-4">
  <div class="card-body p-4 p-md-5">

  <!-- Avatar -->
  <div class="d-flex align-items-center mb-4 pb-4 border-bottom">
    <div
      class="rounded-circle bg-success bg-opacity-10 d-flex justify-content-center align-items-center fw-bold fs-3 me-4"
      style="width:80px;height:80px"
    >
      {{ initials }}
    </div>

    <div>
      <h5 class="fw-bold mb-1">{{ profile.fullName }}</h5>
      <p class="text-muted small mb-2">Tutor</p>
    </div>
  </div>

<form @submit.prevent="saveProfile">

<div class="row g-4">

<!-- NAME -->
<div class="col-md-6">
<label class="form-label fw-semibold small">Full Name</label>
<input v-model="profile.fullName" class="form-control">
</div>

<!-- EMAIL -->
<div class="col-md-6">
<label class="form-label fw-semibold small">Email</label>
<input :value="profile.email" disabled class="form-control bg-light">
</div>

<!-- COURSE -->
<div class="col-md-6">
<label class="form-label fw-semibold small">Course</label>

<select v-model="profile.course" class="form-select">

<option value="">Select Course</option>

<option
  v-for="c in courses"
  :key="c.course_code"
  :value="c.course_code"
>
  {{ c.course_code }} - {{ c.course_name }}
</option>

</select>
</div>

<!-- YEAR LEVEL -->
<div class="col-md-6">
<label class="form-label fw-semibold small">Year Level</label>

<select v-model.number="profile.year_level" class="form-select">

<option value="">Select Level</option>

<option
  v-for="y in yearLevels"
  :key="y.value"
  :value="y.value"
>
  {{ y.label }}
</option>

</select>
</div>

<!-- HOURLY RATE -->
<div class="col-md-6">
<label class="form-label fw-semibold small">Hourly Rate</label>
<input type="number" v-model="profile.hourly_rate" class="form-control">
</div>

<!-- TEACHING LEVEL -->
<div class="col-md-6">
<label class="form-label fw-semibold small">Teaching Level</label>
<input v-model="profile.teaching_level" class="form-control">
</div>

<!-- SESSION MODE -->
<div class="col-md-6">

<label class="form-label fw-semibold small">Session Mode</label>

<div class="form-check">
<input type="checkbox" v-model="profile.can_online" class="form-check-input">
<label class="form-check-label">Online</label>
</div>

<div class="form-check">
<input type="checkbox" v-model="profile.can_f2f" class="form-check-input">
<label class="form-check-label">Face-to-Face</label>
</div>

</div>

<!-- SUBJECTS -->
<div class="col-12">

<label class="form-label fw-semibold small">Subjects</label>

<div class="d-flex flex-wrap gap-2 mb-3">

<span
v-for="s in profile.subjects"
:key="s.subject_code"
class="badge bg-sb-primary px-3 py-2"
>

{{ s.subject_name }}

<button
type="button"
class="btn-close btn-close-white ms-2"
style="font-size:10px"
@click="removeSubject(s.subject_code)"
></button>

</span>

</div>

<div class="d-flex gap-2">

<select v-model="newSubject" class="form-select">

<option value="">Select subject</option>

<option
v-for="s in allSubjects"
:key="s.subject_code"
:value="s.subject_code"
>
{{ s.subject_name }}
</option>

</select>

<button
type="button"
class="btn btn-outline-dark"
@click="addSubject"
>
Add
</button>

</div>

</div>

<!-- BIO -->
<div class="col-12">

<label class="form-label fw-semibold small">Bio</label>

<textarea
v-model="profile.bio"
rows="4"
class="form-control"
></textarea>

</div>

</div>

<div class="text-end mt-4">
<button class="btn bg-sb-primary text-white px-4">
Save Changes
</button>
</div>

</form>

</div>
</div>
</div>
</template>

<script setup>

import { ref, computed, onMounted } from 'vue'
import api from '@/services/api/api'

const profile = ref({
  fullName: '',
  email: '',
  course: '',
  year_level: null,
  subjects: [],
  bio: '',
  hourly_rate: '',
  teaching_level: '',
  can_online: true,
  can_f2f: false
})

const courses = ref([])
const allSubjects = ref([])
const newSubject = ref('')

/* YEAR LEVELS */
const yearLevels = [
  { label: "Grade 1", value: 1 },
  { label: "Grade 2", value: 2 },
  { label: "Grade 3", value: 3 },
  { label: "Grade 4", value: 4 },
  { label: "Grade 5", value: 5 },
  { label: "Grade 6", value: 6 },
  { label: "Grade 7", value: 7 },
  { label: "Grade 8", value: 8 },
  { label: "Grade 9", value: 9 },
  { label: "Grade 10", value: 10 },
  { label: "Grade 11", value: 11 },
  { label: "Grade 12", value: 12 },
  { label: "1st Year College", value: 13 },
  { label: "2nd Year College", value: 14 },
  { label: "3rd Year College", value: 15 },
  { label: "4th Year College", value: 16 }
]

/* INITIALS */
const initials = computed(() => {

  if (!profile.value.fullName) return ''

  return profile.value.fullName
    .split(' ')
    .map(n => n[0])
    .join('')

})

/* LOAD PROFILE */
const loadProfile = async () => {

  try {

    const res = await api.get('/tutor/profile/')
    const data = res.data

    profile.value.fullName = `${data.fname} ${data.lname}`
    profile.value.email = data.email
    profile.value.course = data.course
    profile.value.year_level = data.year_level
    profile.value.bio = data.bio

    profile.value.hourly_rate = data.hourly_rate
    profile.value.teaching_level = data.teaching_level
    profile.value.can_online = data.can_online
    profile.value.can_f2f = data.can_f2f

    const subjectRes = await api.get('/tutor/subjects/')
    profile.value.subjects = subjectRes.data

  } catch (err) {

    console.error("Failed to load tutor profile:", err)

  }

}

/* LOAD SUBJECTS */
const loadSubjects = async () => {

  const res = await api.get('/subjects/')
  allSubjects.value = res.data

}

/* LOAD COURSES */
const loadCourses = async () => {

  const res = await api.get('/courses/')
  courses.value = res.data

}

/* ADD SUBJECT */
const addSubject = async () => {

  if (!newSubject.value) return

  await api.post('/tutor/subjects/add/', {
    subject_code: newSubject.value
  })

  newSubject.value = ''
  await loadProfile()

}

/* REMOVE SUBJECT */
const removeSubject = async (code) => {

  await api.delete(`/tutor/subjects/remove/${code}/`)
  await loadProfile()

}

/* SAVE PROFILE */
const saveProfile = async () => {

  const names = profile.value.fullName.split(' ')

  const tuteePayload = {
    fname: names[0],
    lname: names.slice(1).join(' '),
    course: profile.value.course,
    year_level: profile.value.year_level,
    bio: profile.value.bio
  }

  const tutorPayload = {
    hourly_rate: profile.value.hourly_rate,
    teaching_level: profile.value.teaching_level,
    can_online: profile.value.can_online,
    can_f2f: profile.value.can_f2f
  }

  try {

    // Update profile (UserProfile)
    await api.put('/tutee/profile/update/', tuteePayload)

    // Update tutor info (Tutor model)
    await api.put('/tutor/update/', tutorPayload)

    alert("Profile Updated")

  } catch (err) {

    console.error("Profile update failed:", err)

  }

}

/* MOUNT */
onMounted(() => {

  loadProfile()
  loadSubjects()
  loadCourses()

})

</script>
```

--- src/views/TutorRequestedSessions.vue ---
```
<template>
  <div class="p-1">

    <div class="d-flex mb-4 justify-content-between align-items-center">
        <div>
        <h2 class="fw-bold mb-1">Requested Sessions</h2>
        <p class="text-muted mb-0">
            Manage pending session requests.
        </p>
        </div>

        <div style="width: 200px;">
          <input
            type="date"
            v-model="selectedDate"
            class="form-control"
          />
        </div>
    </div>


    <div v-if="filteredSessions.length === 0" class="text-center text-muted py-5">
        No pending session requests found.
    </div>
    
    <div v-else>
    
        <div
          v-for="session in filteredSessions"
          :key="session.id"
          class="card border mb-2 rounded-4 shadow-sm request-card"
        >
          <div class="card-body py-3">

            <div class="row align-items-center text-center text-md-start">

              <div class="col-md">
                <small class="text-muted">Tutee</small>
                <div class="fw-semibold">
                  {{ session.tuteeName }}
                </div>
              </div>

              <div class="col-md">
                <small class="text-muted">Subject</small>
                <div class="fw-semibold">
                  {{ session.subject }}
                </div>
              </div>

              <div class="col-md">
                <small class="text-muted">Topic</small>
                <div class="fw-semibold">
                  {{ session.topic || 'â€”' }}
                </div>
              </div>

              <div class="col-md">
                <small class="text-muted">Date</small>
                <div class="fw-semibold">
                  {{ session.date }}
                </div>
              </div>

              <div class="col-md">
                <small class="text-muted">Start Time</small>
                <div class="fw-semibold">
                  {{ session.startTime }}
                </div>
              </div>

              <div class="col-md">
                <small class="text-muted">End Time</small>
                <div class="fw-semibold">
                  {{ session.endTime }}
                </div>
              </div>

              <!-- Action Column -->
              <div class="col-md text-md-end mt-3 mt-md-0">
                <div class="d-grid gap-2">

                <button
                  class="btn btn-sm btn-success"
                  :disabled="confirmingId === session.id"
                  @click="confirmSession(session.id)"
                >
                  {{ confirmingId === session.id ? "Confirming..." : "Confirm" }}
                </button>

                  <button
                    class="btn btn-sm btn-danger"
                    :disabled="rejectingId === session.id"
                    @click="rejectSession(session.id)"
                  >
                    {{ rejectingId === session.id ? "Rejecting..." : "Reject" }}
                  </button>

                </div>
              </div>

            </div>

          </div>
        </div>
        
    </div>

      

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useSessionsStore } from '@/stores/completedSessions'

const confirmingId = ref(null)
const rejectingId = ref(null)
const sessionStore = useSessionsStore()

const selectedDate = ref('')

onMounted(() => {
  sessionStore.fetchSessions()
})

const confirmSession = async (id) => {
  confirmingId.value = id
  await sessionStore.approveSession(id)
  confirmingId.value = null
}

const rejectSession = async (id) => {
  rejectingId.value = id
  await sessionStore.rejectSession(id)
  rejectingId.value = null
}

const filteredSessions = computed(() => {
  let sessions = sessionStore.requestedSessions

  if (selectedDate.value) {
    sessions = sessions.filter(session =>
      session.date === selectedDate.value
    )
  }

  return sessions
})
</script>

<style scoped>
.session-card {
  cursor: pointer;
  transition: all 0.2s ease;
}

.session-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 18px rgba(0,0,0,0.08);
}
</style>
```

--- src/views/TutorSchedule.vue ---
Summary only because this file exceeds 300 lines (310 lines).

Vue single-file component for a tutor's recurring weekly availability template.
- Displays weekly slots grouped by day in a table.
- Uses the 	utorSched Pinia store for loading, creating, and deleting availability entries.
- Supports selecting a slot for deletion.
- Provides a modal form to add slots by day plus start/end time.
- Expands a time range into one-hour slots and submits each missing slot individually through the store.
- Validates required fields, end-after-start, and full-hour boundaries before saving.
- Refreshes availability after add/delete operations.
- Includes scoped modal and slot styling.

Binary/non-text files present in the project and not expanded in this section:
- backend/media/profile_pics/sql.jpg
- backend/media/profile_pics/sql_5tVye1Y.jpg
- public/favicon.ico
- src/assets/hero.png
- src/assets/logo.svg
- src/views/drive-download-20260305T061413Z-3-001.zip

## 5. Database / Data Models

Model declarations and migration files:

--- backend/studybuddy/models.py ---
```
from django.db import models
from django.contrib.auth.models import User ### allows the use of auth user model for authentication and user management


# Create your models here.

class Strand(models.Model):

    strand_code = models.CharField(max_length=10, primary_key=True)
    strand_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.strand_code} - {self.strand_name}"
    
class Course(models.Model):

    course_code = models.CharField(max_length=20, primary_key=True)
    course_name = models.CharField(max_length=100)

    strand = models.ForeignKey(
        Strand,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.course_code} - {self.course_name}"


class PartnerInstitution(models.Model):
    institution_name = models.CharField(max_length=255)
    school_email_domain = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    contact_person = models.CharField(max_length=255, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['institution_name']

    def __str__(self):
        return f"{self.institution_name} ({self.school_email_domain})"



class UserProfile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    fname = models.CharField(max_length=100)
    mname = models.CharField(max_length=100, blank=True)
    lname = models.CharField(max_length=100)

    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    year_level = models.IntegerField(null=True, blank=True)

    bio = models.TextField(blank=True, null=True)

    profile_completed = models.BooleanField(default=False)

    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        blank=True,
        null=True
    )

    institution = models.ForeignKey(
        PartnerInstitution,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    is_domain_exempt = models.BooleanField(default=False)

    ROLE_CHOICES = [
        ('Tutee', 'Tutee'),
        ('Tutor', 'Tutor'),
        ('Admin', 'Admin'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.fname} {self.lname}"
    
#TUTOR TABLE
class Tutor(models.Model):

    profile = models.OneToOneField(
        UserProfile,
        on_delete=models.CASCADE,
        primary_key=True
    )

    # Tutor setup fields (filled later)
    teaching_level = models.CharField(max_length=100, null=True, blank=True)

    can_online = models.BooleanField(default=True)
    can_f2f = models.BooleanField(default=False)

    rating_average = models.FloatField(default=0)

    hourly_rate = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True
    )

    total_sessions = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Tutor: {self.profile.fname} {self.profile.lname}"

#Subjects Table 
class Subjects(models.Model):
    subject_code = models.CharField(max_length=20, primary_key=True)
    subject_name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.subject_code} - {self.subject_name}"
    
#Tutor Subjects Table

class TutorSubjects(models.Model):
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subjects, on_delete=models.CASCADE)
    
    expertise_level = models.IntegerField()  # e.g., Beginner, Intermediate, Advanced

    def __str__(self):
        return f"{self.tutor.profile.fname} {self.tutor.profile.lname} - {self.subject.subject_code}"


class TutorAvailability(models.Model):

    DAY_CHOICES = [
        ('Mon', 'Monday'),
        ('Tue', 'Tuesday'),
        ('Wed', 'Wednesday'),
        ('Thu', 'Thursday'),
        ('Fri', 'Friday'),
        ('Sat', 'Saturday'),
        ('Sun', 'Sunday'),
    ]

    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    day = models.CharField(max_length=3, choices=DAY_CHOICES)
    time_slot = models.TimeField()
    is_active = models.BooleanField(default=False)   # tutor toggles this
    is_booked = models.BooleanField(default=False)   # system controls this

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('tutor', 'day', 'time_slot')

    def __str__(self):
        return f"{self.tutor.profile.fname} - {self.day} {self.time_slot}"
    
class Booking(models.Model):

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    student = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="student_bookings"
    )

    tutor = models.ForeignKey(
        Tutor,
        on_delete=models.CASCADE,
        related_name="tutor_bookings"
    )

    availability = models.ForeignKey(
        TutorAvailability,
        on_delete=models.CASCADE,
        related_name="bookings"
    )

    session_date = models.DateField()

    session_mode = models.CharField(
        max_length=10,
        choices=[('Online', 'Online'), ('F2F', 'Face-to-Face')]
    )

    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default="Pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('availability', 'session_date')

class PaymentMethod(models.Model):

    METHOD_CODES = [
        ('CASH', 'Cash'),
        ('GCASH', 'GCash'),
        ('BANK', 'Bank Transfer'),
    ]

    method_id = models.AutoField(primary_key=True)

    code = models.CharField(             
        max_length=20,
        choices=METHOD_CODES,
        unique=True,
    )

    method_name = models.CharField(max_length=50)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.method_name} ({self.code})"

class Payment(models.Model):

    PAYMENT_STATUS = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Failed', 'Failed'),
        ('Refunded', 'Refunded'),
    ]

    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        related_name="payment"
    )

    method = models.ForeignKey(        # âœ… FK to PAYMENT_METHODS
        PaymentMethod,
        on_delete=models.SET_NULL,
        null=True,
        related_name="payments"
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    payment_status = models.CharField(
        max_length=10,
        choices=PAYMENT_STATUS,
        default='Pending'
    )

    transaction_reference = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    paid_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for Booking {self.booking.id} - {self.payment_status}"
    
class Rating(models.Model):

    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        related_name="rating"
    )

    student = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE
    )

    tutor = models.ForeignKey(
        Tutor,
        on_delete=models.CASCADE,
        related_name="ratings"
    )

    rating_score = models.IntegerField()  # 1â€“5

    comment = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.rating_score} â­ for {self.tutor.profile.fname}"
    
class Preference(models.Model):

    MODE_CHOICES = [
        ('Online', 'Online'),
        ('F2F', 'Face-to-Face'),
    ]

    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE)

    subjects = models.ManyToManyField(Subjects)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Preferences for {self.user.fname}"
```

--- backend/studybuddy/migrations/__init__.py ---
```
(empty file)
```

--- backend/studybuddy/migrations/0001_initial.py ---
```
# Generated by Django 6.0.2 on 2026-02-23 14:05

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='user',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('password', models.CharField(max_length=255)),
                ('role', models.CharField(max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
```

--- backend/studybuddy/migrations/0002_userprofile_delete_user.py ---
```
# Generated by Django 6.0.2 on 2026-02-23 16:09

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fname', models.CharField(max_length=100)),
                ('mname', models.CharField(blank=True, max_length=100)),
                ('lname', models.CharField(max_length=100)),
                ('course', models.CharField(blank=True, max_length=100)),
                ('year_level', models.IntegerField(blank=True, null=True)),
                ('role', models.CharField(max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.DeleteModel(
            name='user',
        ),
    ]
```

--- backend/studybuddy/migrations/0003_tutor_alter_userprofile_role.py ---
```
# Generated by Django 6.0.2 on 2026-02-24 21:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0002_userprofile_delete_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tutor',
            fields=[
                ('profile', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='studybuddy.userprofile')),
                ('teaching_level', models.CharField(max_length=100)),
                ('can_online', models.BooleanField(default=True)),
                ('can_f2f', models.BooleanField(default=False)),
                ('rating_average', models.FloatField(default=0)),
                ('hourly_rate', models.DecimalField(decimal_places=2, max_digits=8)),
                ('total_sessions', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='role',
            field=models.CharField(choices=[('Tutee', 'Tutee'), ('Tutor', 'Tutor'), ('Admin', 'Admin')], max_length=20),
        ),
    ]
```

--- backend/studybuddy/migrations/0004_subjects.py ---
```
# Generated by Django 6.0.2 on 2026-02-24 21:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0003_tutor_alter_userprofile_role'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subjects',
            fields=[
                ('subject_code', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('subject_name', models.CharField(max_length=100)),
                ('department', models.CharField(max_length=100)),
            ],
        ),
    ]
```

--- backend/studybuddy/migrations/0005_tutorsubjects.py ---
```
# Generated by Django 6.0.2 on 2026-02-25 14:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0004_subjects'),
    ]

    operations = [
        migrations.CreateModel(
            name='TutorSubjects',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('expertise_level', models.IntegerField()),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='studybuddy.subjects')),
                ('tutor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='studybuddy.tutor')),
            ],
        ),
    ]
```

--- backend/studybuddy/migrations/0006_tutoravailability.py ---
```
# Generated by Django 6.0.2 on 2026-02-25 14:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0005_tutorsubjects'),
    ]

    operations = [
        migrations.CreateModel(
            name='TutorAvailability',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day_of_week', models.CharField(choices=[('Mon', 'Monday'), ('Tue', 'Tuesday'), ('Wed', 'Wednesday'), ('Thu', 'Thursday'), ('Fri', 'Friday'), ('Sat', 'Saturday'), ('Sun', 'Sunday')], max_length=3)),
                ('time_slot', models.TimeField()),
                ('is_active', models.BooleanField(default=False)),
                ('is_booked', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('tutor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='availabilities', to='studybuddy.tutor')),
            ],
            options={
                'unique_together': {('tutor', 'day_of_week', 'time_slot')},
            },
        ),
    ]
```

--- backend/studybuddy/migrations/0007_booking.py ---
```
# Generated by Django 6.0.2 on 2026-02-25 15:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0006_tutoravailability'),
    ]

    operations = [
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_date', models.DateField()),
                ('session_mode', models.CharField(choices=[('Online', 'Online'), ('F2F', 'Face-to-Face')], max_length=10)),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Confirmed', 'Confirmed'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled')], default='Pending', max_length=15)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('availability', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='studybuddy.tutoravailability')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_bookings', to='studybuddy.userprofile')),
                ('tutor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tutor_bookings', to='studybuddy.tutor')),
            ],
        ),
    ]
```

--- backend/studybuddy/migrations/0008_alter_booking_availability_payment.py ---
```
# Generated by Django 6.0.2 on 2026-02-25 15:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0007_booking'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='availability',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='studybuddy.tutoravailability'),
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('payment_status', models.CharField(choices=[('Pending', 'Pending'), ('Paid', 'Paid'), ('Failed', 'Failed'), ('Refunded', 'Refunded')], default='Pending', max_length=10)),
                ('transaction_reference', models.CharField(blank=True, max_length=100, null=True)),
                ('paid_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('booking', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='payment', to='studybuddy.booking')),
            ],
        ),
    ]
```

--- backend/studybuddy/migrations/0009_rating.py ---
```
# Generated by Django 6.0.2 on 2026-02-25 18:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0008_alter_booking_availability_payment'),
    ]

    operations = [
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating_score', models.IntegerField()),
                ('comment', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('booking', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='rating', to='studybuddy.booking')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='studybuddy.userprofile')),
                ('tutor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ratings', to='studybuddy.tutor')),
            ],
        ),
    ]
```

--- backend/studybuddy/migrations/0010_userprofile_bio_userprofile_profile_picture.py ---
```
# Generated by Django 6.0.2 on 2026-02-27 19:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0009_rating'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='bio',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='profile_picture',
            field=models.ImageField(blank=True, null=True, upload_to='profile_pics/'),
        ),
    ]
```

--- backend/studybuddy/migrations/0011_tutoravailability_day.py ---
```
# Generated by Django 6.0.2 on 2026-02-27 20:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0010_userprofile_bio_userprofile_profile_picture'),
    ]

    operations = [
        migrations.AddField(
            model_name='tutoravailability',
            name='day',
            field=models.CharField(choices=[('Mon', 'Monday'), ('Tue', 'Tuesday'), ('Wed', 'Wednesday'), ('Thu', 'Thursday'), ('Fri', 'Friday'), ('Sat', 'Saturday'), ('Sun', 'Sunday')], default='Mon', max_length=3),
            preserve_default=False,
        ),
    ]
```

--- backend/studybuddy/migrations/0012_alter_tutoravailability_tutor.py ---
```
# Generated by Django 6.0.2 on 2026-02-27 20:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0011_tutoravailability_day'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tutoravailability',
            name='tutor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='studybuddy.tutor'),
        ),
    ]
```

--- backend/studybuddy/migrations/0013_alter_tutoravailability_unique_together_and_more.py ---
```
# Generated by Django 6.0.2 on 2026-02-28 20:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0012_alter_tutoravailability_tutor'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='tutoravailability',
            unique_together={('tutor', 'day', 'time_slot')},
        ),
        migrations.AlterField(
            model_name='booking',
            name='availability',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to='studybuddy.tutoravailability'),
        ),
        migrations.AlterUniqueTogether(
            name='booking',
            unique_together={('availability', 'session_date')},
        ),
        migrations.RemoveField(
            model_name='tutoravailability',
            name='day_of_week',
        ),
    ]
```

--- backend/studybuddy/migrations/0014_paymentmethod_payment_method.py ---
```
# Generated by Django 6.0.2 on 2026-03-03 13:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0013_alter_tutoravailability_unique_together_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentMethod',
            fields=[
                ('method_id', models.AutoField(primary_key=True, serialize=False)),
                ('method_name', models.CharField(max_length=50)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AddField(
            model_name='payment',
            name='method',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='payments', to='studybuddy.paymentmethod'),
        ),
    ]
```

--- backend/studybuddy/migrations/0015_paymentmethod_code.py ---
```
# Generated by Django 6.0.2 on 2026-03-03 13:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0014_paymentmethod_payment_method'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentmethod',
            name='code',
            field=models.CharField(blank=True, choices=[('CASH', 'Cash'), ('GCASH', 'GCash'), ('BANK', 'Bank Transfer')], max_length=20, null=True, unique=True),
        ),
    ]
```

--- backend/studybuddy/migrations/0016_alter_paymentmethod_code.py ---
```
# Generated by Django 6.0.2 on 2026-03-03 13:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0015_paymentmethod_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymentmethod',
            name='code',
            field=models.CharField(choices=[('CASH', 'Cash'), ('GCASH', 'GCash'), ('BANK', 'Bank Transfer')], max_length=20, unique=True),
        ),
    ]
```

--- backend/studybuddy/migrations/0017_userprofile_profile_completed.py ---
```
# Generated by Django 6.0.2 on 2026-03-04 08:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0016_alter_paymentmethod_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='profile_completed',
            field=models.BooleanField(default=False),
        ),
    ]
```

--- backend/studybuddy/migrations/0018_preference.py ---
```
# Generated by Django 6.0.2 on 2026-03-04 09:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0017_userprofile_profile_completed'),
    ]

    operations = [
        migrations.CreateModel(
            name='Preference',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('preferred_mode', models.CharField(choices=[('Online', 'Online'), ('F2F', 'Face-to-Face')], max_length=10)),
                ('hourly_budget', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('subjects', models.ManyToManyField(to='studybuddy.subjects')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='studybuddy.userprofile')),
            ],
        ),
    ]
```

--- backend/studybuddy/migrations/0019_alter_tutor_hourly_rate_alter_tutor_teaching_level.py ---
```
# Generated by Django 6.0.2 on 2026-03-04 10:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0018_preference'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tutor',
            name='hourly_rate',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True),
        ),
        migrations.AlterField(
            model_name='tutor',
            name='teaching_level',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
```

--- backend/studybuddy/migrations/0020_course_strand_alter_userprofile_course_course_strand.py ---
```
# Generated by Django 6.0.2 on 2026-03-04 15:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0019_alter_tutor_hourly_rate_alter_tutor_teaching_level'),
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('course_code', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('course_name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Strand',
            fields=[
                ('strand_code', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('strand_name', models.CharField(max_length=100)),
            ],
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='course',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='studybuddy.course'),
        ),
        migrations.AddField(
            model_name='course',
            name='strand',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='studybuddy.strand'),
        ),
    ]
```

--- backend/studybuddy/migrations/0021_remove_preference_hourly_budget_and_more.py ---
```
# Generated by Django 6.0.2 on 2026-03-05 09:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0020_course_strand_alter_userprofile_course_course_strand'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='preference',
            name='hourly_budget',
        ),
        migrations.RemoveField(
            model_name='preference',
            name='preferred_mode',
        ),
    ]
```

--- backend/studybuddy/migrations/0022_partnerinstitution_userprofile_institution_and_more.py ---
```
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0021_remove_preference_hourly_budget_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='PartnerInstitution',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('institution_name', models.CharField(max_length=255)),
                ('school_email_domain', models.CharField(max_length=255, unique=True)),
                ('is_active', models.BooleanField(default=True)),
                ('contact_person', models.CharField(blank=True, max_length=255)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['institution_name'],
            },
        ),
        migrations.AddField(
            model_name='userprofile',
            name='institution',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='studybuddy.partnerinstitution'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='is_domain_exempt',
            field=models.BooleanField(default=False),
        ),
    ]
```

--- backend/testapp/migrations/__init__.py ---
```
(empty file)
```

--- backend/testapp/migrations/0001_initial.py ---
```
# Generated by Django 6.0.2 on 2026-02-19 15:58

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TestMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
```

## 6. API / Interface Contract

No OpenAPI/Swagger/Postman contract was found. The following interface list is inferred from the router and Django URL/view modules.

Frontend routes (`src/router/index.js`)
- / -> LandingPage
- /login -> Login
- /register -> Register
- /preferencesetup -> PreferenceSetup (auth)
- /dashboard -> Dashboard (auth, role=Tutee)
- /tutee-profile -> TuteeProfile (auth, role=Tutee)
- /tutors -> FindTutors (auth, role=Tutee)
- /book -> InitialBooking (auth, role=Tutee)
- /tutor/:id -> TutorDetails (auth, role=Tutee)
- /payment-tutee/:tutorId -> PaymentScreenTutee (auth, role=Tutee)
- /tutor-setup -> TutorPreferenceSetup (auth)
- /tch-dashboard -> TutorDashboard (auth, role=Tutor)
- /tutor-profile -> TutorProfile (auth, role=Tutor)
- /tch-availability -> TutorSchedule (auth, role=Tutor)
- /tch-payments -> TutorPaymentScreen (auth, role=Tutor)
- /tch-requestedSessions -> TutorRequestedSessions (auth, role=Tutor)
- /booking-details/:id -> BookingDetails (auth, role=Tutor)
- /schedule -> Schedule (auth)
- /reports -> SessionsReports (auth)
- /profile -> Profile (auth)

Backend base routing
- `backend/backend/urls.py` mounts Django admin at `/admin/` and the studybuddy API at `/api/`.

Backend API endpoints (`backend/studybuddy/urls.py` + `backend/studybuddy/views.py`)
- GET `/api/partner-institutions/` -> list active partner institutions.
- POST `/api/register/` -> register a user. Inputs inferred: `email`, `password`, `fname`, `mname`, `lname`, `role`, `institution_id`. Returns success/error JSON.
- POST `/api/login/` -> log in with `email`, `password`. Returns JWT token payload plus user/profile metadata.
- POST `/api/token/refresh/` -> SimpleJWT access-token refresh.
- GET `/api/profile/status/` -> authenticated profile-completion status.
- POST `/api/preferences/` -> authenticated preference save. Inputs inferred: `subjects`.
- GET `/api/dashboard/` -> authenticated tutee dashboard payload.
- GET `/api/tutee/profile/` -> authenticated tutee profile payload.
- PUT or POST? `/api/tutee/profile/update/` -> wired to `update_tutee_profile`; the view itself is annotated `PUT`. Inputs inferred: `fname`, `mname`, `lname`, `course`, `year_level`, `bio`, `subjects`.
- GET `/api/tutor/profile/` -> authenticated tutor profile payload.
- GET `/api/tutor/subjects/` -> authenticated tutor subject list.
- POST `/api/tutor/subjects/add/` -> add tutor subject. Inputs inferred: `subject_code`.
- DELETE `/api/tutor/subjects/remove/<subject_code>/` -> remove tutor subject.
- GET `/api/search-tutors/?subject=<code>` -> serialized tutor search results.
- GET `/api/subjects/` -> subject list.
- GET `/api/courses/` -> course list.
- GET `/api/tutor-dashboard/` -> authenticated tutor dashboard payload.
- GET `/api/tutors/<profile_id>/` -> tutor detail payload.
- GET `/api/tutors/<tutor_id>/availability/?date=YYYY-MM-DD` -> tutor availability for booking.
- POST `/api/profile/setup/` -> authenticated profile setup. Inputs inferred: `course`, `year_level`, `bio`.
- PUT or POST? `/api/tutor/update/` -> wired to `update_tutor_profile`; the view itself is annotated `PUT`. Inputs inferred: `hourly_rate`, `teaching_level`, `can_online`, `can_f2f`.
- GET `/api/bookings/` -> booking collection for the current user.
- GET `/api/bookings/<booking_id>/` -> booking detail payload.
- GET `/api/payment-methods/` -> payment method list.
- POST `/api/bookings/confirm/` -> confirm payment and create bookings. Inputs inferred: `tutor_id`, `slots`, `payment_method`.
- GET `/api/template-availability/` -> authenticated tutor recurring-slot template.
- POST `/api/template-availability/` -> create recurring slot. Inputs inferred: `day`, `time_slot`.
- GET `/api/template-availability/<pk>/` -> same view with slot id parameter.
- DELETE `/api/template-availability/<pk>/` -> delete recurring slot by id.
- POST `/api/bookings/<booking_id>/complete/` -> mark booking complete.
- POST `/api/bookings/<booking_id>/approve/` -> approve a pending booking.
- POST `/api/bookings/<booking_id>/reject/` -> reject/remove a pending booking.
- POST `/api/tutor/setup/` -> tutor setup payload. Inputs inferred: `teaching_level`, `can_online`, `can_f2f`, `hourly_rate`.
- POST `/api/recommend-tutors/` -> recommendation query. Inputs inferred: `subject`, `preferred_mode`. Returns recommender output data.

Other interface code found
- `backend/testapp/urls.py` defines `/test/` for `test_api`, but this URLconf is not mounted by `backend/backend/urls.py`.
- `backend/testapp/views.py::test_api` supports `GET` (list `TestMessage` rows) and `POST` (create a `message`).
- `src/services/api/api.js` exports a configured Axios instance with auth-token attachment and refresh-token retry behavior.

## 7. Known Issues / TODOs

Comment scan results
- No `TODO`, `FIXME`, `HACK`, or `BUG` markers were found in authored project files (`.git/`, `node_modules/`, and `backend/venv/` excluded from the scan).

Known bugs / unfinished / noteworthy issues observed during dump assembly
- `src/services/api/search-tutors.js` exists but is an empty file (0 lines), which suggests unfinished or abandoned API helper work.
- Frontend env/config mismatch: `.env` defines `VITE_API_BASE_URL=http://localhost:8000/api/v1`, but `src/services/api/api.js` hardcodes `http://127.0.0.1:8000/api/` and does not read the env variable.
- `backend/{` is a stray zero-byte file with an unusual name.
- `backend/.env` contains live-looking database credentials and raw `psql` restore commands committed in plain text; this is a security and handoff hygiene risk.
- `backend/testapp` is present but not mounted into the main Django URL configuration, so its test endpoint is effectively unreachable in the current app wiring.

## 8. Recent Changes

Last 10 git commit messages (`git log --oneline -10`):
```text
5346bd2 Merge origin/main into ryan/LatestWorking
ec92348 FixedTutorDetails ready to merge now
3e07727 Edited the tutor details page (#52)
148efa2 Merge origin/main into ryan/LatestWorking
74e4db7 added Notifcations, Hansdhake, statuses
7a17c57 Fix tutor search routing from initial booking (#51)
89544ab fix: restore tutor search routing
6e2fec1 Merge pull request #50 from llariesalinas/feature/data-seeding
068de3b Added the data seeding process and backend, front end changes
55e7454 Merge origin/main into ryan/LatestWorking
```

Latest handoff notes as of 2026-04-11:
- `src/views/TutorDetails.vue` was reconciled against the newer `origin/main` changes from commit `3e07727`, then re-merged cleanly in `5346bd2`.
- The current Tutor Details page now uses the updated sidebar layout: `Tutor Stats` plus a `Subjects Taught` accordion instead of the older payment summary / payment method cards.
- Tutor profile actions now include the favorite toggle again, using `favorites/add/` and `favorites/remove/<tutorID>/` from the frontend page logic.
- Booking confirmation in `TutorDetails.vue` currently posts `payment_method: 1` along with `tutor_id` and `slots`.
- The `ryan/LatestWorking` branch has already been pushed after conflict resolution and is intended to open / update a pull request into `main`.

### Addendum: Schedule And Availability Updates After This Dump

- Tutor sidebar schedule navigation now routes tutors to `/tch-availability` instead of the shared `/schedule` page. The duplicate `Set Schedule` button was also removed from the tutor dashboard header, so schedule management now lives in the sidebar only.
- `src/views/TutorSchedule.vue` was updated from a plain recurring-slot editor into a week-based schedule manager:
  - visible week columns now show calendar dates
  - week arrows are limited to the currently viewed month only
  - day cards no longer dim/disable adjacent-week dates that appear in the visible week
- A new one-off blocked-date / blocked-slot exception layer was added on top of recurring tutor availability.
  - New backend model: `TutorAvailabilityOverride`
  - New migration: `backend/studybuddy/migrations/0026_tutoravailabilityoverride.py`
  - Purpose: allow tutors to mark either a full specific date or specific recurring slots on a specific date as unavailable without editing the weekly template itself
- New backend API support for tutor date overrides:
  - `GET/POST /api/availability-overrides/`
  - `DELETE /api/availability-overrides/<override_id>/`
- Booking availability and booking creation were updated so blocked overrides are enforced:
  - tutor availability responses now mark overridden date/slot entries as unavailable
  - booking creation rejects slots blocked by a date override
  - pending requests do not auto-cancel; tutors are expected to handle them manually in Requested Sessions
  - confirmed/completed bookings prevent creating conflicting overrides
- Frontend tutor schedule state now tracks both recurring template slots and date overrides in `src/stores/tutorSched.js`.
- Operational note: the blocked-date feature requires migration `0026_tutoravailabilityoverride` to be applied. If the UI appears unable to block dates, run:
  - `python manage.py migrate studybuddy`
- Environment note: `backend/.env` currently includes raw `psql ...` command lines in addition to `KEY=value` entries. `python-dotenv` warns on startup because those command lines are not valid dotenv syntax, but Django still starts normally.

### Addendum: New System Features Confirmed On 2026-04-14

- Booking and session lifecycle is now more granular than the earlier handoff dump.
  - Backend booking statuses now include `Pending`, `Confirmed`, `Awaiting Payment Verification`, `Completed`, `Cancelled`, and `Rejected`.
  - Frontend tutee/tutor views normalize those into UX-facing states such as `Upcoming`, `Ongoing`, `Payment Required`, `Awaiting Verification`, and `Completed`.
  - Multi-slot sessions are grouped through `session_group_id`, while booking attempts can also be tied together through `booking_request_id` (see migrations `0030`, `0031`, `0032` and current booking store logic).

- Post-session payment verification flow is now implemented end-to-end.
  - Tutees can submit payment proof through `POST /api/bookings/<booking_id>/submit-payment/`.
  - Tutors can review payment details and mark the session complete through `POST /api/bookings/<booking_id>/complete/`.
  - Tutor booking detail screens now expose transaction id, payment method label, amount paid, tutor earnings context, and uploaded receipt image.
  - Current UI files for this flow include `src/views/PaymentScreenTutee.vue`, `src/views/PostSessionPaymentView.vue`, `src/views/TuteeSessionDetailsFlow.vue`, and `src/views/TutorBookingDetailsFlow.vue`.

- Notifications are now a first-class feature.
  - Backend endpoints: `GET /api/notifications/` and `POST /api/notifications/<notification_id>/read/`.
  - Notifications are created for booking requests, accepted bookings, rejected bookings, payment submissions awaiting review, and completed sessions.
  - Frontend polling-based notification bell UI is implemented in `src/components/NotificationBell.vue` with Pinia state in `src/stores/notifications.js`.

- Ratings and review surfacing were added.
  - Tutees can submit ratings through `POST /api/bookings/<booking_id>/rating/`.
  - The frontend now tracks unrated completed sessions and can prompt the user with a stacked modal (`src/components/RatingStackModal.vue`).
  - Tutors now support `pinned_review`, `response_time`, `response_time_label`, and `total_sessions`.
  - Tutor detail/profile serializers expose pinned review data and tutor subject descriptions.

- Tutor profile management is significantly richer than the original dump.
  - Tutors can manage subjects through `GET /api/tutor/subjects/`, `POST /api/tutor/subjects/add/`, `PUT/PATCH /api/tutor/subjects/update/<subject_code>/`, and `DELETE /api/tutor/subjects/remove/<subject_code>/`.
  - `TutorSubjects` now includes a `description` field (migration `0033_tutorsubjects_description.py`), and the profile UI uses expandable subject cards for syllabus/approach notes.
  - Tutor profile editing now includes hourly rate, response time, teaching level, session mode toggles, subject selection, and pinned review selection.

- Tutor discovery and recommendations were expanded.
  - Dashboard recommendations are now loaded into the tutee dashboard and shown in a paginated “Try out these tutors” panel.
  - Find Tutors now supports subject, session mode, date, start/end time, and budget filtering with the new `BudgetRangeSlider` component.
  - The tutor search/store flow was refactored so filtered results and booking preferences are preserved between the initial booking page and tutor search page.
  - Recommendation-related backend endpoint remains `POST /api/recommend-tutors/`, while the dashboard also returns recommendation data consumed by `src/stores/completedSessions.js`.

- Dashboard and reports now reflect the newer booking model.
  - Tutee dashboard session stats distinguish pending, upcoming, completed, rejected, and cancelled sessions.
  - Session stores now merge grouped half-hour bookings into one displayed session block for dashboard and detail views.
  - Tutor requested sessions and tutor/tutee report views were updated to understand payment-verification and rejected-session states.

- Data seeding was updated for the newer schema.
  - `backend/studybuddy/management/commands/seed_data.py` now includes newer booking/payment compatibility work plus tutee/tutor confirmation fields needed to avoid integrity errors.

- Working tree note as of 2026-04-14:
  - `src/views/Dashboard.vue` has additional uncommitted refinements that convert the old “today” schedule into a navigable weekly schedule with overlapping-card lane layout.
  - `src/stores/completedSessions.js` has an uncommitted recommendation response fix using `response.data.recommendations || []`.
  - `src/views/TutorDetails.vue` has an uncommitted UI enhancement that visually highlights the current day column in the booking calendar.


```

--- README.md ---
```
# ðŸ“š StudyBuddy: Peer Academic Tutoring Network

## Overview

StudyBuddy is a localized, web-based peer academic tutoring and knowledge-sharing network designed BY university students FOR university students.

### Core Objectives

- **Smart Matching:** A recommender system utilizing content-based and collaborative filtering to match tutees with compatible peer tutors based on subject expertise.
- **Flexible Scheduling:** A dynamic availability module that assesses assigned workloads and prevents tutor burnout.
- **Compensation Tracking:** A module calculating payments based on session completion.
- **Performance Reporting:** Comprehensive tracking of session history, earnings records, and tutoring metrics.
---

## ðŸ›  Tech Stack

- **Frontend Framework:** Vue 3 (Composition API)
- **Styling & UI:** Bootstrap 5 & Custom CSS Variables
- **Routing:** Vue Router
- **Build Tool:** Vite

---

## ðŸš€ Project Setup for Team Members

### 1. Prerequisites

Ensure you have [Node.js](https://nodejs.org/) installed on your machine.

### 2. Installation

Clone the repository and install the required dependencies (Vue, Bootstrap, etc.):

```bash
# Clone the repository
git clone <insert-your-repo-link-here>

# Navigate into the project directory
cd studybuddy-ui

# Install all dependencies
npm install
```
```

--- src/App.vue ---
```
<template>
  <div v-if="isPublicRoute" class="public-layout">
    <router-view />
  </div>

  <div v-else class="d-flex vh-100 overflow-hidden">
    <aside class="sidebar d-flex flex-column text-white p-3 shadow-sm" style="width: 250px; background-color: var(--sb-dark);">
      <div class="d-flex align-items-center mb-5 mt-3 px-2">
        <i class="bi bi-book text-sb-primary fs-4 me-2"></i>
        <h4 class="mb-0 fw-bold">StudyBuddy</h4>
      </div>

      <ul class="nav nav-pills flex-column mb-auto">
        <li class="nav-item mb-2">
          <router-link :to="userRole === 'tutor' ? '/tch-dashboard' : '/dashboard'" class="nav-link text-white opacity-75 d-flex align-items-center" active-class="active-nav">
            <i class="bi bi-grid-1x2 me-3"></i> Dashboard
          </router-link>
        </li>

        <li class="nav-item mb-2" v-if="userRole === 'tutee'">
          <router-link to="/tutors" class="nav-link text-white opacity-75 d-flex align-items-center" active-class="active-nav">
            <i class="bi bi-search me-3"></i> Find Tutors
          </router-link>
        </li>

        <li class="nav-item mb-2">
          <router-link to="/schedule" class="nav-link text-white opacity-75 d-flex align-items-center" active-class="active-nav">
            <i class="bi bi-calendar3 me-3"></i> Schedule
          </router-link>
        </li>

        <li class="nav-item mb-2" v-if="userRole === 'tutor'">
          <router-link to="/reports" class="nav-link text-white opacity-75 d-flex align-items-center" active-class="active-nav">
            <i class="bi bi-file-earmark-text me-3"></i> Sessions & Reports
          </router-link>
        </li>
      </ul>
    </aside>

    <main class="flex-grow-1 overflow-auto p-5" style="background-color: var(--sb-bg);">
      <header class="d-flex justify-content-between align-items-center mb-3 pb-3 border-bottom border-sb">
          <div>
            </div>
          <div class="d-flex gap-3 align-items-center">
            <router-link v-if="userRole === 'tutee'" to="/book" class="btn bg-sb-primary text-white px-4 py-2 rounded-3 fw-semibold shadow-sm">
              Book Session
            </router-link>

            <router-link v-if="userRole === 'tutor'" to="/tch-requestedSessions" class="btn bg-sb-primary text-white px-4 py-2 rounded-3 fw-semibold shadow-sm">
              Manage Pending Sessions
            </router-link>

            <div class="profileDropdown">
              <button 
              class="btn text-sb-primary fs-3 ms-2 transition-all hover-lift"
              @click="toggleDropdown"
              >
                <i class="bi bi-person-circle"></i>
              </button>
              <ul v-if="isOpen" class="dropdown-menu show position-absolute end-0 mt-2 me-2">
                <li>
                  <div class="dropdown-item" @click="goToProfile">
                    Manage your account
                  </div>
                </li>
                <li><hr class="dropdown-divider"></li>
                <li><button class="btn btn-success dropdown-item text-danger text-center px-4"
                            @click="logout">
                      Log-out
                    </button>
                </li>
              </ul>
            </div>
          </div>
        </header>
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth' // Import auth store
import router from './router'

const route = useRoute()
const authStore = useAuthStore()
const isOpen = ref(false)

const toggleDropdown = () => {
  isOpen.value = !isOpen.value
}

const manageAccount = () => {
  setTimeout(() => {
    router.push('/profile')
  }, 500)
}

const logout = () => {

  authStore.logout()
  router.push('/login') // Redirect to login after logout

  router.push
}

const goToProfile = () => {

  if (userRole.value === 'tutee') {
    router.push('/tutee-profile')
  }

  if (userRole.value === 'tutor') {
    router.push('/tutor-profile')
  }

  isOpen.value = false
}

const hideSessionButton = computed(() => {
  const hiddenPages = [
    'book',
    'tutors',
    'tutor-details',
    'payment',
    'tch-dashboard',
    'tutorpreferencesetup',
    'tch-availability',
    'tch-availability',
    'tch-payments',
    'tch-requestedSessions',
    'booking-details'
  ]
  return !hiddenPages.includes(route.name)
})

const hideReqSessionsButton = computed(() => {
  const hiddenPages = [
    'book',
    'tutors',
    'tutor-details',
    'paymentTutee',
    'preferencesetup',
    'dashboard',
    'tch-requestedSessions'
  ]
  return !hiddenPages.includes(route.name)
})

const isPublicRoute = computed(() => {
  return ['home', 'login', 'register', 'preferencesetup', 'tutorpreferencesetup'].includes(route.name)
})

// Get the role from the store to control the sidebar links
const userRole = computed(() => authStore.user?.role?.toLowerCase() || null)
</script>

<style>
/* Global styles */
:root {
  --sb-dark: #0A1916;
  --sb-primary: #00895A; /* Your exact Figma Green */
  --sb-primary-hover: #00704A; /* Slightly darker for button hovers */
  --sb-bg: #F8F9FA;
  --sb-card-border: #EAEAEA;
}

body {
  background-color: var(--sb-bg);
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
}

/* --- Brand Color Utility Classes --- */
.text-sb-primary {
  color: var(--sb-primary) !important;
}

.bg-sb-primary {
  background-color: var(--sb-primary) !important;
}

.border-sb {
  border-color: var(--sb-card-border) !important;
}

/* Button Hover State */
.btn.bg-sb-primary:hover {
  background-color: var(--sb-primary-hover) !important;
  color: #ffffff !important;
}

/* --- Sidebar Navigation Styles --- */
.active-nav {
  background-color: rgba(0, 137, 90, 0.1) !important;
  color: var(--sb-primary) !important;
  font-weight: 600;
  border-radius: 8px;
  opacity: 1 !important;
}
.nav-link:hover {
  opacity: 1 !important;
}
</style>
```

--- src/assets/base.css ---
```
/* color palette from <https://github.com/vuejs/theme> */
:root {
  --vt-c-white: #ffffff;
  --vt-c-white-soft: #f8f8f8;
  --vt-c-white-mute: #f2f2f2;

  --vt-c-black: #181818;
  --vt-c-black-soft: #222222;
  --vt-c-black-mute: #282828;

  --vt-c-indigo: #2c3e50;

  --vt-c-divider-light-1: rgba(60, 60, 60, 0.29);
  --vt-c-divider-light-2: rgba(60, 60, 60, 0.12);
  --vt-c-divider-dark-1: rgba(84, 84, 84, 0.65);
  --vt-c-divider-dark-2: rgba(84, 84, 84, 0.48);

  --vt-c-text-light-1: var(--vt-c-indigo);
  --vt-c-text-light-2: rgba(60, 60, 60, 0.66);
  --vt-c-text-dark-1: var(--vt-c-white);
  --vt-c-text-dark-2: rgba(235, 235, 235, 0.64);
}

/* semantic color variables for this project */
:root {
  --color-background: var(--vt-c-white);
  --color-background-soft: var(--vt-c-white-soft);
  --color-background-mute: var(--vt-c-white-mute);

  --color-border: var(--vt-c-divider-light-2);
  --color-border-hover: var(--vt-c-divider-light-1);

  --color-heading: var(--vt-c-text-light-1);
  --color-text: var(--vt-c-text-light-1);

  --section-gap: 160px;
}

@media (prefers-color-scheme: dark) {
  :root {
    --color-background: var(--vt-c-black);
    --color-background-soft: var(--vt-c-black-soft);
    --color-background-mute: var(--vt-c-black-mute);

    --color-border: var(--vt-c-divider-dark-2);
    --color-border-hover: var(--vt-c-divider-dark-1);

    --color-heading: var(--vt-c-text-dark-1);
    --color-text: var(--vt-c-text-dark-2);
  }
}

*,
*::before,
*::after {
  box-sizing: border-box;
  margin: 0;
  font-weight: normal;
}

body {
  min-height: 100vh;
  color: var(--color-text);
  background: var(--color-background);
  transition:
    color 0.5s,
    background-color 0.5s;
  line-height: 1.6;
  font-family:
    Inter,
    -apple-system,
    BlinkMacSystemFont,
    'Segoe UI',
    Roboto,
    Oxygen,
    Ubuntu,
    Cantarell,
    'Fira Sans',
    'Droid Sans',
    'Helvetica Neue',
    sans-serif;
  font-size: 15px;
  text-rendering: optimizeLegibility;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
```

--- src/assets/main.css ---
```
:root {
  --sb-dark: #0A1916;      /* Sidebar background */
  --sb-primary: #00895A;   /* Primary green (buttons, icons, active text) */
  --sb-bg: #F8F9FA;        /* Main background */
  --sb-card-border: #EAEAEA;
}

body {
  background-color: var(--sb-bg);
  font-family: 'Inter', system-ui, -apple-system, sans-serif; /* Standard modern font */
}

/* Custom Utilities to extend Bootstrap */
.text-sb-primary { color: var(--sb-primary) !important; }
.bg-sb-primary { background-color: var(--sb-primary) !important; }
.border-sb { border-color: var(--sb-card-border) !important; }
```

--- src/components/HelloWorld.vue ---
```
<script setup>
defineProps({
  msg: {
    type: String,
    required: true,
  },
})
</script>

<template>
  <div class="greetings">
    <h1 class="green">{{ msg }}</h1>
    <h3>
      Youâ€™ve successfully created a project with
      <a href="https://vite.dev/" target="_blank" rel="noopener">Vite</a> +
      <a href="https://vuejs.org/" target="_blank" rel="noopener">Vue 3</a>.
    </h3>
  </div>
</template>

<style scoped>
h1 {
  font-weight: 500;
  font-size: 2.6rem;
  position: relative;
  top: -10px;
}

h3 {
  font-size: 1.2rem;
}

.greetings h1,
.greetings h3 {
  text-align: center;
}

@media (min-width: 1024px) {
  .greetings h1,
  .greetings h3 {
    text-align: left;
  }
}
</style>
```

--- src/components/icons/IconCommunity.vue ---
```
<template>
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor">
    <path
      d="M15 4a1 1 0 1 0 0 2V4zm0 11v-1a1 1 0 0 0-1 1h1zm0 4l-.707.707A1 1 0 0 0 16 19h-1zm-4-4l.707-.707A1 1 0 0 0 11 14v1zm-4.707-1.293a1 1 0 0 0-1.414 1.414l1.414-1.414zm-.707.707l-.707-.707.707.707zM9 11v-1a1 1 0 0 0-.707.293L9 11zm-4 0h1a1 1 0 0 0-1-1v1zm0 4H4a1 1 0 0 0 1.707.707L5 15zm10-9h2V4h-2v2zm2 0a1 1 0 0 1 1 1h2a3 3 0 0 0-3-3v2zm1 1v6h2V7h-2zm0 6a1 1 0 0 1-1 1v2a3 3 0 0 0 3-3h-2zm-1 1h-2v2h2v-2zm-3 1v4h2v-4h-2zm1.707 3.293l-4-4-1.414 1.414 4 4 1.414-1.414zM11 14H7v2h4v-2zm-4 0c-.276 0-.525-.111-.707-.293l-1.414 1.414C5.42 15.663 6.172 16 7 16v-2zm-.707 1.121l3.414-3.414-1.414-1.414-3.414 3.414 1.414 1.414zM9 12h4v-2H9v2zm4 0a3 3 0 0 0 3-3h-2a1 1 0 0 1-1 1v2zm3-3V3h-2v6h2zm0-6a3 3 0 0 0-3-3v2a1 1 0 0 1 1 1h2zm-3-3H3v2h10V0zM3 0a3 3 0 0 0-3 3h2a1 1 0 0 1 1-1V0zM0 3v6h2V3H0zm0 6a3 3 0 0 0 3 3v-2a1 1 0 0 1-1-1H0zm3 3h2v-2H3v2zm1-1v4h2v-4H4zm1.707 4.707l.586-.586-1.414-1.414-.586.586 1.414 1.414z"
    />
  </svg>
</template>
```

--- src/components/icons/IconDocumentation.vue ---
```
<template>
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="17" fill="currentColor">
    <path
      d="M11 2.253a1 1 0 1 0-2 0h2zm-2 13a1 1 0 1 0 2 0H9zm.447-12.167a1 1 0 1 0 1.107-1.666L9.447 3.086zM1 2.253L.447 1.42A1 1 0 0 0 0 2.253h1zm0 13H0a1 1 0 0 0 1.553.833L1 15.253zm8.447.833a1 1 0 1 0 1.107-1.666l-1.107 1.666zm0-14.666a1 1 0 1 0 1.107 1.666L9.447 1.42zM19 2.253h1a1 1 0 0 0-.447-.833L19 2.253zm0 13l-.553.833A1 1 0 0 0 20 15.253h-1zm-9.553-.833a1 1 0 1 0 1.107 1.666L9.447 14.42zM9 2.253v13h2v-13H9zm1.553-.833C9.203.523 7.42 0 5.5 0v2c1.572 0 2.961.431 3.947 1.086l1.107-1.666zM5.5 0C3.58 0 1.797.523.447 1.42l1.107 1.666C2.539 2.431 3.928 2 5.5 2V0zM0 2.253v13h2v-13H0zm1.553 13.833C2.539 15.431 3.928 15 5.5 15v-2c-1.92 0-3.703.523-5.053 1.42l1.107 1.666zM5.5 15c1.572 0 2.961.431 3.947 1.086l1.107-1.666C9.203 13.523 7.42 13 5.5 13v2zm5.053-11.914C11.539 2.431 12.928 2 14.5 2V0c-1.92 0-3.703.523-5.053 1.42l1.107 1.666zM14.5 2c1.573 0 2.961.431 3.947 1.086l1.107-1.666C18.203.523 16.421 0 14.5 0v2zm3.5.253v13h2v-13h-2zm1.553 12.167C18.203 13.523 16.421 13 14.5 13v2c1.573 0 2.961.431 3.947 1.086l1.107-1.666zM14.5 13c-1.92 0-3.703.523-5.053 1.42l1.107 1.666C11.539 15.431 12.928 15 14.5 15v-2z"
    />
  </svg>
</template>
```

--- src/components/icons/IconEcosystem.vue ---
```
<template>
  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="20" fill="currentColor">
    <path
      d="M11.447 8.894a1 1 0 1 0-.894-1.789l.894 1.789zm-2.894-.789a1 1 0 1 0 .894 1.789l-.894-1.789zm0 1.789a1 1 0 1 0 .894-1.789l-.894 1.789zM7.447 7.106a1 1 0 1 0-.894 1.789l.894-1.789zM10 9a1 1 0 1 0-2 0h2zm-2 2.5a1 1 0 1 0 2 0H8zm9.447-5.606a1 1 0 1 0-.894-1.789l.894 1.789zm-2.894-.789a1 1 0 1 0 .894 1.789l-.894-1.789zm2 .789a1 1 0 1 0 .894-1.789l-.894 1.789zm-1.106-2.789a1 1 0 1 0-.894 1.789l.894-1.789zM18 5a1 1 0 1 0-2 0h2zm-2 2.5a1 1 0 1 0 2 0h-2zm-5.447-4.606a1 1 0 1 0 .894-1.789l-.894 1.789zM9 1l.447-.894a1 1 0 0 0-.894 0L9 1zm-2.447.106a1 1 0 1 0 .894 1.789l-.894-1.789zm-6 3a1 1 0 1 0 .894 1.789L.553 4.106zm2.894.789a1 1 0 1 0-.894-1.789l.894 1.789zm-2-.789a1 1 0 1 0-.894 1.789l.894-1.789zm1.106 2.789a1 1 0 1 0 .894-1.789l-.894 1.789zM2 5a1 1 0 1 0-2 0h2zM0 7.5a1 1 0 1 0 2 0H0zm8.553 12.394a1 1 0 1 0 .894-1.789l-.894 1.789zm-1.106-2.789a1 1 0 1 0-.894 1.789l.894-1.789zm1.106 1a1 1 0 1 0 .894 1.789l-.894-1.789zm2.894.789a1 1 0 1 0-.894-1.789l.894 1.789zM8 19a1 1 0 1 0 2 0H8zm2-2.5a1 1 0 1 0-2 0h2zm-7.447.394a1 1 0 1 0 .894-1.789l-.894 1.789zM1 15H0a1 1 0 0 0 .553.894L1 15zm1-2.5a1 1 0 1 0-2 0h2zm12.553 2.606a1 1 0 1 0 .894 1.789l-.894-1.789zM17 15l.447.894A1 1 0 0 0 18 15h-1zm1-2.5a1 1 0 1 0-2 0h2zm-7.447-5.394l-2 1 .894 1.789 2-1-.894-1.789zm-1.106 1l-2-1-.894 1.789 2 1 .894-1.789zM8 9v2.5h2V9H8zm8.553-4.894l-2 1 .894 1.789 2-1-.894-1.789zm.894 0l-2-1-.894 1.789 2 1 .894-1.789zM16 5v2.5h2V5h-2zm-4.553-3.894l-2-1-.894 1.789 2 1 .894-1.789zm-2.894-1l-2 1 .894 1.789 2-1L8.553.106zM1.447 5.894l2-1-.894-1.789-2 1 .894 1.789zm-.894 0l2 1 .894-1.789-2-1-.894 1.789zM0 5v2.5h2V5H0zm9.447 13.106l-2-1-.894 1.789 2 1 .894-1.789zm0 1.789l2-1-.894-1.789-2 1 .894 1.789zM10 19v-2.5H8V19h2zm-6.553-3.894l-2-1-.894 1.789 2 1 .894-1.789zM2 15v-2.5H0V15h2zm13.447 1.894l2-1-.894-1.789-2 1 .894 1.789zM18 15v-2.5h-2V15h2z"
    />
  </svg>
</template>
```

--- src/components/icons/IconSupport.vue ---
```
<template>
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor">
    <path
      d="M10 3.22l-.61-.6a5.5 5.5 0 0 0-7.666.105 5.5 5.5 0 0 0-.114 7.665L10 18.78l8.39-8.4a5.5 5.5 0 0 0-.114-7.665 5.5 5.5 0 0 0-7.666-.105l-.61.61z"
    />
  </svg>
</template>
```

--- src/components/icons/IconTooling.vue ---
```
<!-- This icon is from <https://github.com/Templarian/MaterialDesign>, distributed under Apache 2.0 (https://www.apache.org/licenses/LICENSE-2.0) license-->
<template>
  <svg
    xmlns="http://www.w3.org/2000/svg"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    aria-hidden="true"
    role="img"
    class="iconify iconify--mdi"
    width="24"
    height="24"
    preserveAspectRatio="xMidYMid meet"
    viewBox="0 0 24 24"
  >
    <path
      d="M20 18v-4h-3v1h-2v-1H9v1H7v-1H4v4h16M6.33 8l-1.74 4H7v-1h2v1h6v-1h2v1h2.41l-1.74-4H6.33M9 5v1h6V5H9m12.84 7.61c.1.22.16.48.16.8V18c0 .53-.21 1-.6 1.41c-.4.4-.85.59-1.4.59H4c-.55 0-1-.19-1.4-.59C2.21 19 2 18.53 2 18v-4.59c0-.32.06-.58.16-.8L4.5 7.22C4.84 6.41 5.45 6 6.33 6H7V5c0-.55.18-1 .57-1.41C7.96 3.2 8.44 3 9 3h6c.56 0 1.04.2 1.43.59c.39.41.57.86.57 1.41v1h.67c.88 0 1.49.41 1.83 1.22l2.34 5.39z"
      fill="currentColor"
    ></path>
  </svg>
</template>
```

--- src/components/TheWelcome.vue ---
```
<script setup>
import WelcomeItem from './WelcomeItem.vue'
import DocumentationIcon from './icons/IconDocumentation.vue'
import ToolingIcon from './icons/IconTooling.vue'
import EcosystemIcon from './icons/IconEcosystem.vue'
import CommunityIcon from './icons/IconCommunity.vue'
import SupportIcon from './icons/IconSupport.vue'

const openReadmeInEditor = () => fetch('/__open-in-editor?file=README.md')
</script>

<template>
  <WelcomeItem>
    <template #icon>
      <DocumentationIcon />
    </template>
    <template #heading>Documentation</template>

    Vueâ€™s
    <a href="https://vuejs.org/" target="_blank" rel="noopener">official documentation</a>
    provides you with all information you need to get started.
  </WelcomeItem>

  <WelcomeItem>
    <template #icon>
      <ToolingIcon />
    </template>
    <template #heading>Tooling</template>

    This project is served and bundled with
    <a href="https://vite.dev/guide/features.html" target="_blank" rel="noopener">Vite</a>. The
    recommended IDE setup is
    <a href="https://code.visualstudio.com/" target="_blank" rel="noopener">VSCode</a>
    +
    <a href="https://github.com/vuejs/language-tools" target="_blank" rel="noopener"
      >Vue - Official</a
    >. If you need to test your components and web pages, check out
    <a href="https://vitest.dev/" target="_blank" rel="noopener">Vitest</a>
    and
    <a href="https://www.cypress.io/" target="_blank" rel="noopener">Cypress</a>
    /
    <a href="https://playwright.dev/" target="_blank" rel="noopener">Playwright</a>.

    <br />

    More instructions are available in
    <a href="javascript:void(0)" @click="openReadmeInEditor"><code>README.md</code></a
    >.
  </WelcomeItem>

  <WelcomeItem>
    <template #icon>
      <EcosystemIcon />
    </template>
    <template #heading>Ecosystem</template>

    Get official tools and libraries for your project:
    <a href="https://pinia.vuejs.org/" target="_blank" rel="noopener">Pinia</a>,
    <a href="https://router.vuejs.org/" target="_blank" rel="noopener">Vue Router</a>,
    <a href="https://test-utils.vuejs.org/" target="_blank" rel="noopener">Vue Test Utils</a>, and
    <a href="https://github.com/vuejs/devtools" target="_blank" rel="noopener">Vue Dev Tools</a>. If
    you need more resources, we suggest paying
    <a href="https://github.com/vuejs/awesome-vue" target="_blank" rel="noopener">Awesome Vue</a>
    a visit.
  </WelcomeItem>

  <WelcomeItem>
    <template #icon>
      <CommunityIcon />
    </template>
    <template #heading>Community</template>

    Got stuck? Ask your question on
    <a href="https://chat.vuejs.org" target="_blank" rel="noopener">Vue Land</a>
    (our official Discord server), or
    <a href="https://stackoverflow.com/questions/tagged/vue.js" target="_blank" rel="noopener"
      >StackOverflow</a
    >. You should also follow the official
    <a href="https://bsky.app/profile/vuejs.org" target="_blank" rel="noopener">@vuejs.org</a>
    Bluesky account or the
    <a href="https://x.com/vuejs" target="_blank" rel="noopener">@vuejs</a>
    X account for latest news in the Vue world.
  </WelcomeItem>

  <WelcomeItem>
    <template #icon>
      <SupportIcon />
    </template>
    <template #heading>Support Vue</template>

    As an independent project, Vue relies on community backing for its sustainability. You can help
    us by
    <a href="https://vuejs.org/sponsor/" target="_blank" rel="noopener">becoming a sponsor</a>.
  </WelcomeItem>
</template>
```

--- src/components/WelcomeItem.vue ---
```
<template>
  <div class="item">
    <i>
      <slot name="icon"></slot>
    </i>
    <div class="details">
      <h3>
        <slot name="heading"></slot>
      </h3>
      <slot></slot>
    </div>
  </div>
</template>

<style scoped>
.item {
  margin-top: 2rem;
  display: flex;
  position: relative;
}

.details {
  flex: 1;
  margin-left: 1rem;
}

i {
  display: flex;
  place-items: center;
  place-content: center;
  width: 32px;
  height: 32px;
  color: var(--color-text);
}

h3 {
  font-size: 1.2rem;
  font-weight: 500;
  margin-bottom: 0.4rem;
  color: var(--color-heading);
}

@media (min-width: 1024px) {
  .item {
    margin-top: 0;
    padding: 0.4rem 0 1rem calc(var(--section-gap) / 2);
  }

  i {
    top: calc(50% - 25px);
    left: -26px;
    position: absolute;
    border: 1px solid var(--color-border);
    background: var(--color-background);
    border-radius: 8px;
    width: 50px;
    height: 50px;
  }

  .item:before {
    content: ' ';
    border-left: 1px solid var(--color-border);
    position: absolute;
    left: 0;
    bottom: calc(50% + 25px);
    height: calc(50% - 25px);
  }

  .item:after {
    content: ' ';
    border-left: 1px solid var(--color-border);
    position: absolute;
    left: 0;
    top: calc(50% + 25px);
    height: calc(50% - 25px);
  }

  .item:first-of-type:before {
    display: none;
  }

  .item:last-of-type:after {
    display: none;
  }
}
</style>
```

--- src/main.js ---
```
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import { useAuthStore } from '@/stores/auth' // 1. Import the store

// 1. Import Bootstrap CSS
import 'bootstrap/dist/css/bootstrap.min.css'
// 2. Import Bootstrap Icons
import 'bootstrap-icons/font/bootstrap-icons.css'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// 2. Initialize Auth state to load the token into Axios
const authStore = useAuthStore()
authStore.initializeAuth()

app.mount('#app')

// 3. Import Bootstrap JS at the end so it loads after the DOM
import 'bootstrap/dist/js/bootstrap.bundle.min.js'
```

--- src/router/index.js ---
```
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useProfileStore } from '@/stores/profile'

import Dashboard from '@/views/Dashboard.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [

    // ---------- PUBLIC ROUTES ----------
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/LandingPage.vue')
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/Login.vue')
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/Register.vue')
    },

    // ---------- STUDENT ROUTES ----------
    {
      path: '/preferencesetup',
      name: 'preferencesetup',
      component: () => import('@/views/PreferenceSetup.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: Dashboard,
      meta: { requiresAuth: true, role: 'Tutee' }
    },
    {
      path: '/tutee-profile',
      name: 'tutee-profile',
      component: () => import('@/views/TuteeProfile.vue'),
      meta: { requiresAuth: true, role: 'Tutee' }
    },
    {
      path: '/tutors',
      name: 'tutors',
      component: () => import('@/views/FindTutors.vue'),
      meta: { requiresAuth: true, role: 'Tutee' }
    },
    {
      path: '/book',
      name: 'book',
      component: () => import('@/views/InitialBooking.vue'),
      meta: { requiresAuth: true, role: 'Tutee' }
    },
    {
      path: '/tutor/:id',
      name: 'tutor-details',
      component: () => import('@/views/TutorDetails.vue'),
      meta: { requiresAuth: true, role: 'Tutee' }
    },
    {
      path: '/payment-tutee/:tutorId',
      name: 'PaymentTutee',
      component: () => import('@/views/PaymentScreenTutee.vue'),
      props: true,
      meta: { requiresAuth: true, role: 'Tutee' }
    },

    // ---------- TUTOR ROUTES ----------
    {
      path: '/tutor-setup',
      name: 'tutorpreferencesetup',
      component: () => import('@/views/TutorPreferenceSetup.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/tch-dashboard',
      name: 'tch-dashboard',
      component: () => import('@/views/TutorDashboard.vue'),
      meta: { requiresAuth: true, role: 'Tutor' }
    },
    {
      path: '/tutor-profile',
      name: 'tutor-profile',
      component: () => import('@/views/TutorProfile.vue'),
      meta: { requiresAuth: true, role: 'Tutor' }
    },
    {
      path: '/tch-availability',
      name: 'tch-availability',
      component: () => import('@/views/TutorSchedule.vue'),
      meta: { requiresAuth: true, role: 'Tutor' }
    },
    {
      path: '/tch-payments',
      name: 'tch-payments',
      component: () => import('@/views/TutorPaymentScreen.vue'),
      meta: { requiresAuth: true, role: 'Tutor' }
    },
    {
      path: '/tch-requestedSessions',
      name: 'tch-requestedSessions',
      component: () => import('@/views/TutorRequestedSessions.vue'),
      meta: { requiresAuth: true, role: 'Tutor' }
    },
    {
      path: '/booking-details/:id',
      name: 'booking-details',
      component: () => import('@/views/BookingDetails.vue'),
      meta: { requiresAuth: true, role: 'Tutor' }
    },

    // ---------- SHARED ROUTES ----------
    {
      path: '/schedule',
      name: 'schedule',
      component: () => import('@/views/Schedule.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/reports',
      name: 'reports',
      component: () => import('@/views/SessionsReports.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('@/views/Profile.vue'),
      meta: { requiresAuth: true }
    }

  ]
})

/*
  GLOBAL NAVIGATION GUARD
*/
router.beforeEach(async (to, from, next) => {

  const authStore = useAuthStore()
  const profileStore = useProfileStore()
  const normalizedUserRole = authStore.userRole?.toLowerCase?.() || null
  const normalizedRouteRole = to.meta.role?.toLowerCase?.() || null

  // 1ï¸âƒ£ Protect routes requiring authentication
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return next('/login')
  }

  if (authStore.isAuthenticated) {

    // Ensure token exists
    if (!authStore.token) {
      return next('/login')
    }

    // 2ï¸âƒ£ Load profile status
    if (!profileStore.loaded) {
      try {
        await profileStore.checkProfileStatus()
      } catch (error) {

        console.error("Profile check failed:", error)

        authStore.logout()
        return next('/login')
      }
    }

    // 3ï¸âƒ£ Profile completion guard
    if (!profileStore.profileCompleted) {

      const role = normalizedUserRole

      if (to.path === '/preferencesetup' || to.path === '/tutor-setup') {
        return next()
      }

      if (role === 'tutor') {
        return next('/tutor-setup')
      }

      return next('/preferencesetup')
    }

    // 4ï¸âƒ£ Role protection
    if (normalizedRouteRole && normalizedUserRole !== normalizedRouteRole) {

      if (normalizedUserRole === 'tutor') {
        return next('/tch-dashboard')
      }

      if (normalizedUserRole === 'tutee') {
        return next('/dashboard')
      }

      return next('/')
    }

  }

  next()

})

export default router
```

--- src/services/api/api.js ---
```
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'

const API_BASE_URL = 'http://127.0.0.1:8000/api/'

const api = axios.create({
  baseURL: API_BASE_URL,
})

let refreshPromise = null

const refreshAccessToken = async () => {
  if (!refreshPromise) {
    const authStore = useAuthStore()

    refreshPromise = authStore
      .refreshAccessToken()
      .finally(() => {
        refreshPromise = null
      })
  }

  return refreshPromise
}

api.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    const token = authStore.token || localStorage.getItem('access_token')

    if (token) {
      config.headers = config.headers ?? {}
      config.headers.Authorization = `Bearer ${token}`
    }

    return config
  },
  (error) => Promise.reject(error)
)

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (
      error.response &&
      error.response.status === 401 &&
      originalRequest &&
      !originalRequest._retry &&
      !originalRequest.url?.includes('token/refresh/')
    ) {
      originalRequest._retry = true

      try {
        const newAccessToken = await refreshAccessToken()

        originalRequest.headers = originalRequest.headers ?? {}
        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`

        return api(originalRequest)
      } catch (refreshError) {
        const authStore = useAuthStore()
        authStore.logout()
        router.push('/login')

        return Promise.reject(refreshError)
      }
    }

    if (error.response && error.response.status === 401) {
      const authStore = useAuthStore()
      authStore.logout()
      router.push('/login')
    }

    return Promise.reject(error)
  }
)

export default api
```

--- src/services/api/registerapi.js ---
```
import axios from 'axios'

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/',
})

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default api

export const registerUser = async (store) => {
  return await axios.post(`${API_URL}/register/`, {
    email: store.newUserEmail,
    password: store.newUserPassword,
    fname: store.newUserFname,
    mname: store.newUserMname,
    lname: store.newUserLname,
    role: store.newUserType
  })
}
```

--- src/services/api/search-tutors.js ---
```
(empty file)
```

--- src/services/auth/idleSession.js ---
```
const IDLE_LOGOUT_MS = 10 * 60 * 1000

const ACTIVITY_EVENTS = [
  'mousemove',
  'mousedown',
  'keydown',
  'scroll',
  'touchstart',
  'click'
]

let idleTimeoutId = null
let timeoutCallback = null
let listenersAttached = false

const clearIdleTimeout = () => {
  if (idleTimeoutId !== null && typeof window !== 'undefined') {
    window.clearTimeout(idleTimeoutId)
    idleTimeoutId = null
  }
}

const resetIdleTimer = () => {
  if (typeof window === 'undefined' || !timeoutCallback) {
    return
  }

  clearIdleTimeout()

  idleTimeoutId = window.setTimeout(() => {
    timeoutCallback?.()
  }, IDLE_LOGOUT_MS)
}

const handleUserActivity = () => {
  resetIdleTimer()
}

const attachActivityListeners = () => {
  if (typeof window === 'undefined' || listenersAttached) {
    return
  }

  ACTIVITY_EVENTS.forEach((eventName) => {
    window.addEventListener(eventName, handleUserActivity, true)
  })

  listenersAttached = true
}

const detachActivityListeners = () => {
  if (typeof window === 'undefined' || !listenersAttached) {
    return
  }

  ACTIVITY_EVENTS.forEach((eventName) => {
    window.removeEventListener(eventName, handleUserActivity, true)
  })

  listenersAttached = false
}

export const startIdleSessionTracking = (onTimeout) => {
  timeoutCallback = onTimeout

  attachActivityListeners()
  resetIdleTimer()
}

export const stopIdleSessionTracking = () => {
  clearIdleTimeout()
  detachActivityListeners()
  timeoutCallback = null
}

export { IDLE_LOGOUT_MS }
```

--- src/stores/auth.js ---
```
import axios from 'axios'
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api/api'
import { useProfileStore } from '@/stores/profile'
import {
  startIdleSessionTracking,
  stopIdleSessionTracking
} from '@/services/auth/idleSession'

const API_BASE_URL = 'http://127.0.0.1:8000/api/'
const ACCESS_REFRESH_INTERVAL_MS = 4 * 60 * 1000

let refreshIntervalId = null

export const useAuthStore = defineStore('auth', () => {
  const profileStore = useProfileStore()

  const normalizeRole = (role) => {
    if (!role) {
      return null
    }

    return String(role).toLowerCase()
  }

  const handleIdleLogout = () => {
    logout()

    if (typeof window !== 'undefined' && window.location.pathname !== '/login') {
      window.location.replace('/login')
    }
  }

  const token = ref(localStorage.getItem('access_token') || null)
  const refreshToken = ref(localStorage.getItem('refresh_token') || null)
  const user = ref(null)

  const isAuthenticated = computed(() => !!token.value)
  const userRole = computed(() => user.value?.role || null)

  const setTokens = ({ accessToken, refreshTokenValue }) => {
    token.value = accessToken
    refreshToken.value = refreshTokenValue

    localStorage.setItem('access_token', accessToken)
    localStorage.setItem('refresh_token', refreshTokenValue)
  }

  const updateAccessToken = (accessToken) => {
    token.value = accessToken
    localStorage.setItem('access_token', accessToken)
  }

  const stopAccessTokenRefresh = () => {
    if (refreshIntervalId !== null && typeof window !== 'undefined') {
      window.clearInterval(refreshIntervalId)
      refreshIntervalId = null
    }
  }

  const refreshAccessToken = async () => {
    const storedRefreshToken = refreshToken.value || localStorage.getItem('refresh_token')

    if (!storedRefreshToken) {
      throw new Error('No refresh token available.')
    }

    const response = await axios.post(`${API_BASE_URL}token/refresh/`, {
      refresh: storedRefreshToken
    })

    const newAccessToken = response.data.access

    if (!newAccessToken) {
      throw new Error('No access token returned from refresh endpoint.')
    }

    updateAccessToken(newAccessToken)
    return newAccessToken
  }

  const startAccessTokenRefresh = () => {
    stopAccessTokenRefresh()

    if (typeof window === 'undefined' || !refreshToken.value) {
      return
    }

    refreshIntervalId = window.setInterval(async () => {
      try {
        await refreshAccessToken()
      } catch {
        logout()

        if (window.location.pathname !== '/login') {
          window.location.replace('/login')
        }
      }
    }, ACCESS_REFRESH_INTERVAL_MS)
  }

  const startSessionTracking = () => {
    startIdleSessionTracking(handleIdleLogout)
    startAccessTokenRefresh()
  }

  const login = async (credentials) => {
    const response = await api.post('login/', credentials)

    const receivedToken = response.data.access
    const receivedRefreshToken = response.data.refresh

    if (!receivedToken || !receivedRefreshToken) {
      throw new Error('Missing authentication token(s) from server.')
    }

    setTokens({
      accessToken: receivedToken,
      refreshTokenValue: receivedRefreshToken
    })

    user.value = {
      email: response.data.email,
      role: normalizeRole(response.data.role),
      id: response.data.user_id,
      fname: response.data.fname,
      lname: response.data.lname
    }

    localStorage.setItem('user_role', normalizeRole(response.data.role))
    profileStore.resetProfileState()

    startSessionTracking()

    return response.data.role
  }

  const logout = () => {
    stopIdleSessionTracking()
    stopAccessTokenRefresh()

    token.value = null
    refreshToken.value = null
    user.value = null
    profileStore.resetProfileState()

    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user_role')
  }

  const initializeAuth = () => {
    const storedToken = localStorage.getItem('access_token')
    const storedRefreshToken = localStorage.getItem('refresh_token')
    const storedRole = localStorage.getItem('user_role')

    if (storedToken && storedRefreshToken) {
      token.value = storedToken
      refreshToken.value = storedRefreshToken
      startSessionTracking()
    }

    if (storedRole) {
      user.value = {
        role: normalizeRole(storedRole)
      }
    }
  }

  return {
    token,
    refreshToken,
    user,
    userRole,
    isAuthenticated,
    setTokens,
    updateAccessToken,
    refreshAccessToken,
    login,
    logout,
    initializeAuth
  }
})
```

--- src/stores/bookedSessionDetails.js ---
```
import { ref } from "vue";
import { defineStore } from "pinia";

export const useBookedSessionStore = defineStore('bookedSessionDetails', () => {

    const bookedSessionTutorID = ref(null)
    const bookedSessionTutorName = ref('')
    const bookedSessionSub = ref('')
    const bookedSessionTop = ref('')
    const bookedSessionMode = ref('')
    const bookedSessionDate = ref(null)
    const bookedSessions = ref([])

    const resetStore = () => {
        bookedSessionTutorID.value = null
        bookedSessionTutorName.value = ''
        bookedSessionSub.value = ''
        bookedSessionTop.value = ''
        bookedSessionMode.value = ''
        bookedSessionDate.value = null
        bookedSessions.value = []
    }

    return {
        bookedSessionTutorID,
        bookedSessionTutorName,
        bookedSessionSub,
        bookedSessionTop,
        bookedSessionMode,
        bookedSessionDate,
        bookedSessions,
        resetStore
    }
})
```

--- src/stores/completedSessions.js ---
```
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api/api'

export const useSessionsStore = defineStore('sessions', () => {

  const sessions = ref([])
  const loading = ref(false)
  const error = ref(null)

  const fetchSessions = async () => {
    loading.value = true
    error.value = null

    try {
      const response = await api.get('/bookings/')
      sessions.value = response.data
    } catch (err) {
      error.value = 'Failed to load sessions.'
    } finally {
      loading.value = false
    }
  }

  

  const normalizeStatus = (status) =>
    status?.toLowerCase() || ''

  const completedSessions = computed(() =>
    sessions.value
      .filter(s => normalizeStatus(s.status) === 'completed')
      .sort((a, b) => new Date(b.date) - new Date(a.date))
  )

  const upcomingSessions = computed(() =>
    sessions.value
      .filter(s => normalizeStatus(s.status) === 'confirmed')
      .sort((a, b) => new Date(a.date) - new Date(b.date))
  )

  const cancelledSessions = computed(() =>
    sessions.value
      .filter(s => normalizeStatus(s.status) === 'cancelled')
      .sort((a, b) => new Date(b.date) - new Date(a.date))
  )

  const requestedSessions = computed(() =>
  sessions.value
    .filter(s => normalizeStatus(s.status) === 'pending')
    .sort((a, b) => new Date(a.date) - new Date(b.date))
  )

  const approveSession = async (id) => {
  await api.post(`/bookings/${id}/approve/`)

  const session = sessions.value.find(s => s.id === id)
  if (session) {
    session.status = "Confirmed"
  }

  }

  const rejectSession = async (id) => {
  await api.post(`/bookings/${id}/reject/`)

  const session = sessions.value.find(s => s.id === id)
  if (session) {
    session.status = "Cancelled"
  }
  } 

  return {
    sessions,
    loading,
    error,
    fetchSessions,
    completedSessions,
    upcomingSessions,
    cancelledSessions,
    requestedSessions,
    approveSession,
    rejectSession
  }
})
```

--- src/stores/counter.js ---
```
import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export const useCounterStore = defineStore('counter', () => {
  const count = ref(0)
  const doubleCount = computed(() => count.value * 2)
  function increment() {
    count.value++
  }

  return { count, doubleCount, increment }
})
```

--- src/stores/initialbookingprefs.js ---
```
import { defineStore } from 'pinia';
import { ref } from 'vue'

export const useInitialBookingPrefsStore = defineStore('initialBookingPrefs', () => {
    const selectedSubject = ref('')
    const selectedTopic = ref('')
    const selectedDate = ref(null)
    const selectedMode = ref('')
    const selectedStartTime = ref(null)
    const selectedEndTime = ref(null)

    const resetPreferences = () => {
        selectedSubject.value = ''
        selectedTopic.value = ''
        selectedDate.value = null
        selectedMode.value = ''
        selectedStartTime.value = null
        selectedEndTime.value = null
    }

    return {
      selectedSubject,
      selectedTopic,
      selectedDate,
      selectedMode,
      selectedStartTime,
      selectedEndTime,
      resetPreferences
    }
})
```

--- src/stores/preferences.js ---
```
import { defineStore } from 'pinia';
import {ref} from 'vue'

export const usePreferenceStore = defineStore('preferences', () => {
    const selectedSubjects = ref([])
    const selectedLevel = ref(null)
    const selectedTime = ref(null)

    const resetPreferences = () => {
        selectedSubjects.value = []
        selectedLevel.value = null
        selectedTime.value = null
    }
    return {selectedSubjects, selectedLevel, selectedTime, resetPreferences}
})
```

--- src/stores/profile.js ---
```
import { defineStore } from 'pinia'
import api from '@/services/api/api'

export const useProfileStore = defineStore('profile', {

  state: () => ({
    profileCompleted: false,
    loaded: false
  }),

  actions: {
    resetProfileState() {
      this.profileCompleted = false
      this.loaded = false
    },

    async checkProfileStatus() {

      const res = await api.get('/profile/status/')

      this.profileCompleted = res.data.profile_completed
      this.loaded = true

      return res.data
    }

  }

})
```

--- src/stores/registrationinfo.js ---
```
import { ref } from "vue";
import { defineStore } from "pinia";

export const useRegistrationInfoStore= defineStore('newUserInfo', () => {
    const newUserFname = ref('')
    const newUserMname = ref('')
    const newUserLname = ref('')
    const newUserEmail = ref('')
    const newUserPassword = ref('')
    const newUserType = ref('')
    const selectedInstitutionId = ref('')

    return {
        newUserFname, 
        newUserMname, 
        newUserLname, 
        newUserEmail, 
        newUserPassword, 
        newUserType,
        selectedInstitutionId}
})
```

--- src/stores/selectedSessions.js ---
```
import { defineStore } from 'pinia';
import {ref} from 'vue'

export const useBookingPrefsStore = defineStore ('bookingPrefs', () => {
    const bookedSessions = ref([])

    const addBookings = (slots) => {
        bookedSessions.value = slots
    }

    return {bookedSessions, addBookings}
})
```

--- src/stores/tuteePaymentDetails.js ---
```
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const usePaymentStore = defineStore('payment', () => {

  const selectedMethod = ref(null)
  const amountPaid = ref(null)

  const gCashName = ref('')
  const gCashNumber = ref('')
  const gCashReference = ref('')

  const bankName = ref('')
  const bankAccount = ref('')
  const bankReference = ref('')

  const reset = () => {
    selectedMethod.value = null
    amountPaid.value = null

    gCashName.value = ''
    gCashNumber.value = ''
    gCashReference.value = ''

    bankName.value = ''
    bankAccount.value = ''
    bankReference.value = ''
  }

  return {
    selectedMethod,
    amountPaid,
    gCashName,
    gCashNumber,
    gCashReference,
    bankName,
    bankAccount,
    bankReference,
    reset
  }
})
```

--- src/stores/tutorBookingDetails.js ---
```
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api/api'

export const useTutorBookingDetailStore = defineStore('tutorBookingDetail', () => {

  const booking = ref(null)
  const isLoading = ref(false)
  const error = ref(null)

  // âœ… These now match backend response structure EXACTLY
  const tuteeProfile = computed(() => booking.value?.tutee || null)
  const sessionInfo = computed(() => booking.value?.session || null)
  const paymentInfo = computed(() => booking.value?.payment || null)

  const bookingId = computed(() => booking.value?.id || null)

  const fetchBookingDetails = async (bookingId) => {
    if (!bookingId) return

    isLoading.value = true
    error.value = null

    try {
      const res = await api.get(`/bookings/${bookingId}/`)
      booking.value = res.data
    } catch (err) {
      console.error('Failed to fetch booking details:', err)
      error.value = err
      booking.value = null
    } finally {
      isLoading.value = false
    }
  }

  const completeSession = async () => {
  const id = booking.value?.id || booking.value?.session?.id

  console.log("Completing booking ID:", id)

  if (!id) {
    console.log("NO ID FOUND")
    return
  }

  try {
    await api.post(`/bookings/${id}/complete/`)
    await fetchBookingDetails(id)
  } catch (err) {
    console.error("Failed to complete session:", err)
    throw err
  }
}


  const confirmPayment = async () => {
    if (!booking.value?.id) return

    try {
      await api.post(`/bookings/confirm/`, {
        booking_id: booking.value.id
      })

      // Refresh data after confirming
      await fetchBookingDetails(booking.value.id)

    } catch (err) {
      console.error('Failed to confirm payment:', err)
      throw err
    }
  }

  const resetStore = () => {
    booking.value = null
    error.value = null
    isLoading.value = false
  }

  return {
    booking,
    isLoading,
    error,
    tuteeProfile,
    sessionInfo,
    paymentInfo,
    bookingId,
    fetchBookingDetails,
    confirmPayment,
    resetStore,
    completeSession,
  }
})
```

--- src/stores/tutorSched.js ---
```
import { defineStore } from 'pinia'
import api from '@/services/api/api'

export const useTutorSchedStore = defineStore('tutorAvailability', {
  state: () => ({
    availabilities: [],
    isLoading: false
  }),

  actions: {

    // ===============================
    // FETCH TEMPLATE SLOTS
    // ===============================
    async fetchAvailability() {
      this.isLoading = true

      try {
        const res = await api.get('/template-availability/')
        this.availabilities = res.data
      } catch (error) {
        console.error('Failed to fetch availability:', error)
      } finally {
        this.isLoading = false
      }
    },

    // ===============================
    // ADD TEMPLATE SLOT
    // ===============================
    async addSlot(slot) {
      try {
        const res = await api.post('/template-availability/', {
          day: slot.day,
          time_slot: slot.time_slot
        })

        this.availabilities.push(res.data)
      } catch (error) {
        console.error('Failed to add slot:', error)
      }
    },

    // ===============================
    // DELETE TEMPLATE SLOT
    // ===============================
    async deleteSlot(id) {
      try {
        await api.delete(`/template-availability/${id}/`)
        this.availabilities = this.availabilities.filter(
          s => s.availability_id !== id
        )
      } catch (error) {
        console.error('Failed to delete slot:', error)
      }
    }
  }
})
```

--- src/views/BookingDetails.vue ---
```
<template>
  <div class="booking-details container py-2">

    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="fw-bold mb-0">Booking Details</h2>
    </div>

    <div v-if="bookingDetailsStore.isLoading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status" />
    </div>

    <div v-else-if="!bookingDetailsStore.booking">
      <div class="alert alert-warning">Booking not found.</div>
    </div>

    <div v-else class="row g-4">

      <div class="col-12 col-md-8">
        <div class="card shadow-sm p-3 d-flex flex-row align-items-stretch h-100 gap-3">
          <img
            v-if="bookingDetailsStore.tuteeProfile?.avatar"
            :src="bookingDetailsStore.tuteeProfile.avatar.replace('150', '300')"
            style="width: 50%; height: 100%; object-fit: cover; border-radius: 10pt;"
            alt="Tutee Avatar"
            />
            

          <div class="flex-grow-1">
            <h3 class="fw-bold mb-2">
              {{ bookingDetailsStore.tuteeProfile?.name || 'N/A' }}
            </h3>
            <p class="text-muted mb-1">
              <strong>Email:</strong> {{ bookingDetailsStore.tuteeProfile?.email || 'N/A' }}
            </p>
            <p class="text-muted mb-1">
              <strong>Course:</strong> {{ bookingDetailsStore.tuteeProfile?.course || 'N/A' }}
            </p>
            <p class="text-muted mb-1">
              <strong>Year Level:</strong> {{ bookingDetailsStore.tuteeProfile?.year_level || 'N/A' }}
            </p>
            <p class="text-muted mb-0">
              <strong>Bio:</strong> {{ bookingDetailsStore.tuteeProfile?.bio || 'N/A' }}
            </p>
          </div>
        </div>
      </div>

      <div class="col-12 col-md-4">
        <div class="card shadow-sm p-3 h-100 d-flex flex-column justify-content-between">
          <div>
            <h5 class="fw-bold mb-3">Payment Summary</h5>

            <div class="row mb-2">
              <div class="col-5 text-muted">Transaction ID</div>
              <div class="col-7 text-end fw-semibold">
                {{ bookingDetailsStore.paymentInfo?.transaction_id || 'N/A' }}
              </div>
            </div>

            <div class="row mb-2">
              <div class="col-5 text-muted">Method</div>
              <div class="col-7 text-end fw-semibold">
                {{ bookingDetailsStore.paymentInfo?.method || 'N/A' }}
              </div>
            </div>

            <div class="row mb-2">
              <div class="col-5 text-muted">Amount Paid</div>
              <div class="col-7 text-end fw-semibold">
                â‚±{{ bookingDetailsStore.paymentInfo?.amount_paid?.toFixed(2) || '0.00' }}
              </div>
            </div>

            <div class="row mb-2">
              <div class="col-5 text-muted">Tutor Earned</div>
              <div class="col-7 text-end fw-semibold">
                â‚±{{ bookingDetailsStore.paymentInfo?.tutor_earned?.toFixed(2) || '0.00' }}
              </div>
            </div>

            <div class="row mb-2">
              <div class="col-5 text-muted">Platform Fee</div>
              <div class="col-7 text-end fw-semibold">
                â‚±{{ bookingDetailsStore.paymentInfo?.platform_fee?.toFixed(2) || '0.00' }}
              </div>
            </div>

            <div
            class="row mb-2"
            v-if="bookingDetailsStore.paymentInfo?.method === 'GCash' || bookingDetailsStore.paymentInfo?.method === 'Bank Transfer'"
            >
                <div class="col-5 text-muted">
                    {{
                    bookingDetailsStore.paymentInfo?.method === 'GCash'
                        ? 'GCash Fee'
                        : 'Bank Fee'
                    }}
                </div>
                <div class="col-7 text-end fw-semibold">
                    â‚±{{ bookingDetailsStore.paymentInfo?.transaction_fee?.toFixed(2) || '0.00' }}
                </div>
            </div>

            <div class="row mb-3">
              <div class="col-5 text-muted">Status</div>
              <div class="col-7 text-end">
                <span
                  class="badge"
                  :class="{
                    'bg-success': bookingDetailsStore.paymentInfo?.status === 'Paid',
                    'bg-warning text-dark': bookingDetailsStore.paymentInfo?.status === 'Pending',
                    'bg-danger': bookingDetailsStore.paymentInfo?.status === 'Failed'
                  }"
                >
                  {{ bookingDetailsStore.paymentInfo?.status || 'N/A' }}
                </span>
              </div>
            </div>
          </div>

          <div class="d-flex justify-content-end">
            <button
              v-if="bookingDetailsStore.sessionInfo?.status === 'Confirmed'"
              class="btn btn-success"
              @click="handleComplete"
            >
              Complete Session
            </button>
          </div>
        </div>
      </div>

      <!-- Session Information (Full Width) -->
      <div class="col-12">
        <div class="card shadow-sm">
          <div class="card-body">
            <h5 class="fw-bold mb-3">Session Information</h5>

            <div class="row text-center fw-semibold mb-2">
              <div class="col">Subject</div>
              <div class="col">Topic</div>
              <div class="col">Date</div>
              <div class="col">Time</div>
              <div class="col">Rating</div>
              <div class="col">Status</div>
            </div>

            <div class="row text-center">
              <div class="col">{{ bookingDetailsStore.sessionInfo?.subject || 'N/A' }}</div>
              <div class="col">{{ bookingDetailsStore.sessionInfo?.topic || 'N/A' }}</div>
              <div class="col">{{ bookingDetailsStore.sessionInfo?.date || 'N/A' }}</div>
              <div class="col">
                {{ bookingDetailsStore.sessionInfo?.start_time || 'N/A' }} â€“
                {{ bookingDetailsStore.sessionInfo?.end_time || 'N/A' }}
              </div>
              <div class="col">{{ bookingDetailsStore.sessionInfo?.rating ?? 'â€”' }}â­</div>
              <div class="col">{{ bookingDetailsStore.sessionInfo?.status || 'N/A' }}</div>
            </div>

          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { onMounted, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import { useTutorBookingDetailStore } from '@/stores/tutorBookingDetails'

const route = useRoute()
const bookingId = route.params.id
const bookingDetailsStore = useTutorBookingDetailStore()
const store = useTutorBookingDetailStore()


const handleComplete = async () => {
  try {
    await bookingDetailsStore.completeSession()
    alert("Session marked as completed.")
  } catch (error) {
    alert(error.response?.data?.error || "Failed to complete session.")
  }
}

onMounted(() => {
    bookingDetailsStore.fetchBookingDetails(route.params.id)
})

onBeforeUnmount(() => {
  bookingDetailsStore.resetStore()
})
</script>

<style scoped>
.card {
  border-radius: 12px;
}

.card-body {
  padding: 1.5rem;
}

.list-group-item {
  border: none;
  padding-left: 0;
  padding-right: 0;
}
</style>
```

--- src/views/Dashboard.vue ---
```
<template>
  <div class="p-4">
    <div class="mb-4">
      <h2 class="fw-bold text-dark">Welcome back, {{ studentName }}!</h2>
      <p class="text-muted">Here's your tutoring overview for today.</p>
    </div>

    <div class="row g-4 mb-5">
      <div class="col-md-6">
        <div class="card border-sb shadow-sm rounded-4 h-100 p-3 d-flex flex-row align-items-center">
          <div class="bg-success bg-opacity-10 p-3 rounded-4 me-3">
            <i class="bi bi-calendar-event text-sb-primary fs-3"></i>
          </div>
          <div>
            <h6 class="text-muted small fw-bold mb-1">Upcoming Sessions</h6>
            <h2 class="fw-bold mb-0">{{ upcomingCount }}</h2>
          </div>
        </div>
      </div>
      <div class="col-md-6">
        <div class="card border-sb shadow-sm rounded-4 h-100 p-3 d-flex flex-row align-items-center">
          <div class="bg-success bg-opacity-10 p-3 rounded-4 me-3">
            <i class="bi bi-book text-sb-primary fs-3"></i>
          </div>
          <div>
            <h6 class="text-muted small fw-bold mb-1">Completed Sessions</h6>
            <h2 class="fw-bold mb-0">{{ completedCount }}</h2>
          </div>
        </div>
      </div>
    </div>

    <div class="row g-4">
      <div class="col-md-6">
        <h5 class="fw-bold mb-3 d-flex align-items-center">
          <i class="bi bi-clock text-sb-primary me-2"></i> Upcoming Sessions
        </h5>

        <div v-if="loading" class="text-muted">Loading upcoming sessions...</div>

        <div v-else>
          <div 
          v-for="session in upcomingSessions"
          :key="session.id"
          @click="viewSessionDetails(session.id)" 
          class="card border-sb shadow-sm rounded-4 mb-3 session-card">
            <div class="card-body d-flex justify-content-between align-items-center">
              <div>
                <h6 class="fw-bold text-dark mb-1">{{ session.subject }}</h6>
                <p class="text-muted small mb-0">with {{ session.tutor }}</p>
              </div>
              <div class="text-end">
                <h6 class="fw-bold text-dark mb-1">{{ session.date }}</h6>
                <p class="text-muted small mb-0">{{session.time}}</p>
              </div>
            </div>
          </div>
        </div>
        

      </div>

      <div class="col-md-6">
        <h5 class="fw-bold mb-3 d-flex align-items-center">
          <i class="bi bi-star text-warning me-2"></i> Recent Sessions
        </h5>

        <div v-if="loading" class="text-muted">Loading completed sessions...</div>

        <div v-else>
          <div 
          v-for="session in completedSessions"
          :key="session.id"
          @click="viewSessionDetails(session.id)" 
          class="card border-sb shadow-sm rounded-4 mb-3 session-card">
            <div class="card-body d-flex justify-content-between align-items-center">
              <div>
                <h6 class="fw-bold text-dark mb-1">{{ session.subject }}</h6>
                <p class="text-muted small mb-0">{{ session.tutor }}</p>
              </div>
              <div class="d-flex gap-2">
                <span class="badge bg-light text-dark border border-sb d-flex align-items-center">
                  <i class="bi bi-star-fill text-dark me-1 small"></i> 5
                </span>
                <span class="badge bg-light text-dark border border-sb d-flex align-items-center">â‚±130</span>
              </div>
            </div>
          </div>
        </div>
        
      </div>
    </div>

    <div class="mt-3">
      <h4 class="fw-bold"
      >Try out these tutors</h4>

      <div class="row g-3">
        <template v-if="loading">
          <div class="col-12 text-muted">
            Loading tutors...
          </div>
        </template>

        <template v-else>
          <div 
            v-for="tutor in recommendedTutors"
            :key="tutor.id"
            class="col-md-4"
          >
            <div 
              class="card border-sb shadow-sm h-100 p-3 tutor-card"
              @click="bookTutor(tutor.id)"
            >
              <div class="card-body">
                <h3>{{ tutor.name }}</h3>
                <p class="text-muted small mb-2">â­ {{ tutor.rating }}</p>
                <p class="small mb-2">
                  Subjects: {{ tutor.subjects?.join(', ') }}
                </p>
                <p class="fw-bold text-sb-primary mb-0">
                  â‚±{{ tutor.hourlyRate }}/hr
                </p>
              </div>
            </div>
          </div>
        </template>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '@/services/api/api' 
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const recommendedTutors = ref([])
const upcomingSessions = ref([])
const completedSessions = ref([])
const loading = ref(false)

const bookTutor = (tutorId) => {
  router.push(`/tutor/${tutorId}`)
}

const fetchSessions = async() => {
  try{
    loading.value = true
   const response = await api.get('dashboard/')

    recommendedTutors.value = response.data.recommendations
    upcomingSessions.value = response.data.upcoming
    completedSessions.value = response.data.completed
  }
  catch(error) {
    console.error('Error loading sessions:', error)
  }
  finally{
    loading.value = false
  }
}

onMounted(() => {
  fetchSessions()
})

const upcomingCount = computed(() => upcomingSessions.value.length)
const completedCount = computed(() => completedSessions.value.length)

const authStore = useAuthStore()

const studentName = computed(() => {
  return authStore.user
    ? authStore.user.fname
    : 'Student'
})

const viewSessionDetails = (sessionId) => {
  // 1. We log the ID to satisfy ESLint and prep for backend integration
  console.log(`Navigating to details for session ID: ${sessionId}`)

  // 2. Route to the schedule page for now
  router.push('/schedule')
}

watch(
  () => route.query.updated,
  () => {
    fetchSessions()
  }
)

const completeSession = async (bookingId) => {
  try {
    await api.post(`bookings/${bookingId}/complete/`)
    alert("Session marked as completed.")

    // Refresh dashboard data
    await loadTutorDashboard()

  } catch (error) {
    console.error(error)
    alert("Failed to complete session.")
  }
}

</script>

<style scoped>
/* Hover effect to make cards feel clickable */
.session-card {
  cursor: pointer;
  transition: all 0.2s ease-in-out;
}
.session-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 15px rgba(0, 137, 90, 0.1) !important;
  border-color: var(--sb-primary) !important;
}
</style>
```

--- src/views/FindTutors.vue ---
```
<template>
    <div class="p-4">
        <div class="mb-4">
            <h2 class="fw-bold text-dark">Find Tutors</h2>
            <p class="text-muted">Browse peer tutors matched to your learning needs.</p>
        </div>

        <form @submit.prevent="searchTutor">
            <div class="row mb-5 g-1 justify-content-center">
            <div class="col-md-2">
                <label class="form-label fw-semibold small">Subject</label>
                <select v-model="initialbookStore.selectedSubject" class="form-select">
                <option disabled value="">Select Subject</option>
                <option
                    v-for="subject in subjects"
                    :key="subject.subject_code"
                    :value="subject.subject_code"
                >
                    {{ subject.subject_name  }}
                </option>
                </select>
            </div>
            <div class="col-md-2">
                <label class="form-label fw-semibold small">Topic</label>
                <select v-model="initialbookStore.selectedTopic" class="form-select border-sb shadow-none py-2">
                    <option value="" disabled>Select Topic</option>
                    <option 
                    v-for="topic in filteredTopics"
                    :key="topic"
                    :value="topic">{{topic}}</option>
                </select>
            </div>
            <div class="col-md-2">
                <label class="form-label fw-semibold small">Mode</label>
                <select v-model="initialbookStore.selectedMode" class="form-select border-sb shadow-none py-2">
                    <option 
                    v-for="mode in modes"
                    :key="mode"
                    :value="mode">{{ mode }}</option>
                </select>
            </div>
            <div class="col-md-2">
                <label class="form-label fw-semibold small">Date</label>
                <input type="date" v-model="initialbookStore.selectedDate" class="form-control border-sb shadow-none" required />
            </div>
            <div class="col" style="flex: 0 0 12.5%; max-width: 12.5%;">
                <label class="form-label fw-semibold small">From</label>
                <input type="time" v-model="initialbookStore.selectedStartTime" class="form-control border-sb shadow-none" required />
            </div>
            <div class="col" style="flex: 0 0 12.5%; max-width: 12.5%;">
                <label class="form-label fw-semibold small">To</label>
                <input type="time" v-model="initialbookStore.selectedEndTime" class="form-control border-sb shadow-none" required />
            </div>
            <div class="col-md-1">
                <label class="form-label fw-semibold small invisible">Search</label>
                <button type="submit" class="btn bg-sb-primary text-white px-3 rounded-3 fw-semibold shadow-sm"
                :disabled="isSubmitting">
                    Search
                </button>
            </div> 
        </div>
        </form>
        

        <div v-if="isLoading" class="text-center py-5">
            <div class="spinner-border text-sb-primary" role="status"></div>
            <p class="text-muted mt-2">Running matching algorithm...</p>
        </div>

        <div v-else class="row g-4">
            <div class="col-md-6" v-for="tutor in matchedTutors" :key="tutor.profile_id">
                <div class="card border-sb shadow-sm rounded-4 h-100">
                    <div class="card-body p-4">
                        <div class="d-flex justify-content-between align-items-start mb-3">
                            <div class="d-flex align-items-center gap-3">
                                <div class="bg-success bg-opacity-10 text-sb-primary fw-bold rounded-circle d-flex align-items-center justify-content-center"
                                    style="width: 48px; height: 48px;">
                                    {{ tutor.initials }}
                                </div>
                                <div>
                                    <h6 class="fw-bold mb-0 text-dark">{{ tutor.name }}</h6>
                                    <p class="text-muted small mb-0">{{ tutor.year_course }}</p>
                                </div>
                            </div>
                            <div class="text-end">
                                <span class="fw-bold text-warning d-flex align-items-center">
                                    <i class="bi bi-star-fill me-1"></i> {{ tutor.rating }}
                                </span>
                            </div>
                        </div>

                        <p class="small text-dark mb-3">{{ tutor.bio }}</p>

                        <div class="d-flex gap-2 mb-4 flex-wrap">
                            <span v-for="subject in tutor.subjects" :key="subject"
                                class="badge bg-light text-dark border border-sb">
                                {{ subject }}
                            </span>
                        </div>

                        <div class="d-flex justify-content-between align-items-center mt-auto">
                            <div class="small">
                                <span class="fw-bold text-dark">â‚±{{ tutor.hourly_rate }}</span><span
                                    class="text-muted">/hr</span>
                                <span class="text-muted ms-2">Â· {{ tutor.total_sessions }} sessions</span>
                            </div>
                            <button 
                                @click="toTutorDetails(tutor)"
                                class="btn bg-sb-primary text-white px-4 rounded-3 fw-semibold shadow-sm"
                                >
                                Book Session
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { useRoute, useRouter } from 'vue-router'
import api from '@/services/api/api'
import { ref, onMounted, watch } from 'vue'

import { useAuthStore } from '@/stores/auth'
import { useInitialBookingPrefsStore } from '@/stores/initialbookingprefs'
import { useBookedSessionStore } from '@/stores/bookedSessionDetails'

const route = useRoute()
const router = useRouter()

const authStore = useAuthStore()
const initialbookStore = useInitialBookingPrefsStore()
const bookedSessionStore = useBookedSessionStore()

const isLoading = ref(true)
const isSubmitting = ref(false)

const matchedTutors = ref([])
const subjects = ref([])

const modes = ['Online', 'Face-to-face']


/*
Reset topic if subject changes
*/
watch(
  () => initialbookStore.selectedSubject,
  () => {
    initialbookStore.selectedTopic = ''
  }
)


/*
CBF Tutor Search
*/
const searchTutor = async () => {

  isSubmitting.value = true
  isLoading.value = true

  try {

    const response = await api.post('/recommend-tutors/', {

      subject: initialbookStore.selectedSubject,
      topic: initialbookStore.selectedTopic,
      preferred_mode: initialbookStore.selectedMode

    })

    matchedTutors.value = response.data.map(tutor => ({

      profile_id: tutor.id,

      initials: tutor.name
        .split(' ')
        .map(n => n[0])
        .join(''),

      name: tutor.name,

      year_course: 'Tutor',

      rating: tutor.rating ?? 5.0,

      bio: 'Peer tutor available.',

      subjects: tutor.subjects ?? [],

      hourly_rate: tutor.hourly_rate ?? 150,

      total_sessions: tutor.total_sessions ?? 0,

      score: tutor.score

    }))

  } catch (error) {

    console.error('CBF search failed:', error)

  } finally {

    isSubmitting.value = false
    isLoading.value = false

  }

}


/*
Navigate to tutor details
*/
const toTutorDetails = (tutor) => {

  bookedSessionStore.bookedSessionTutorID = tutor.profile_id
  bookedSessionStore.bookedSessionTutorName = tutor.name
  bookedSessionStore.bookedSessionSub = initialbookStore.selectedSubject
  bookedSessionStore.bookedSessionTop = initialbookStore.selectedTopic
  bookedSessionStore.bookedSessionMode = initialbookStore.selectedMode

  router.push(`/tutor/${tutor.profile_id}`)
}


/*
Initial page load
*/
onMounted(async () => {

  try {

    const res = await api.get('/subjects/')
    subjects.value = res.data

  } catch (error) {

    console.error("Failed to load subjects", error)

  }

  if (route.query.subject) {
    initialbookStore.selectedSubject = route.query.subject
  }

  if (initialbookStore.selectedSubject) {
    await searchTutor()
  } else {
    isLoading.value = false
  }

})
</script>
```

--- src/views/InitialBooking.vue ---
```
<template>
  <div class="initial-booking-content">
    <div class="mb-4">
      <h2 class="fw-bold text-dark">Book a Session</h2>
      <p class="text-muted">
        Tell us what you need help with, and we'll match you with the right tutor.
      </p>
    </div>

    <div class="card border-sb shadow-sm rounded-4" style="max-width: 600px;">
      <div class="card-body p-4 p-md-5">
        <form @submit.prevent="findTutor">

          <div class="mb-3">
            <label class="form-label fw-semibold small">Subject</label>
            <select v-model="store.selectedSubject" class="form-select border-sb shadow-none" required>
              <option v-for="subject in subjects" :key="subject.subject_code" :value="subject.subject_code">
                {{ subject.subject_name }}
              </option>
            </select>
          </div>

          <div class="mb-3">
            <label class="form-label fw-semibold small">Specific Topic</label>
            <input
              type="text"
              v-model="store.selectedTopic"
              class="form-control border-sb shadow-none"
              placeholder="e.g., Calculus, Thermodynamics"
              required
            />
          </div>

          <div class="row g-3 mb-3">
            <div class="col-md-6">
              <label class="form-label fw-semibold small">Date</label>
              <input
                type="date"
                v-model="store.selectedDate"
                class="form-control border-sb shadow-none"
                required
              />
            </div>

            <div class="col-md-6">
              <label class="form-label fw-semibold small">Preferred Mode</label>
              <select v-model="store.selectedMode" class="form-select border-sb shadow-none" required>
                <option v-for="mode in modes" :key="mode" :value="mode">
                  {{ mode }}
                </option>
              </select>
            </div>
          </div>

          <div class="row g-3 mb-4">
            <div class="col-6">
              <label class="form-label fw-semibold small">Time From</label>
              <input
                type="time"
                v-model="store.selectedStartTime"
                class="form-control border-sb shadow-none"
                required
              />
            </div>

            <div class="col-6">
              <label class="form-label fw-semibold small">Time To</label>
              <input
                type="time"
                v-model="store.selectedEndTime"
                class="form-control border-sb shadow-none"
                required
              />
            </div>
          </div>

          <div class="text-end mt-4">
            <button
              type="submit"
              class="btn bg-sb-primary text-white px-5 py-2 rounded-3 fw-semibold shadow-sm d-inline-flex justify-content-center align-items-center gap-2"
              :disabled="isSubmitting"
            >
              <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-2"></span>
              {{ isSubmitting ? 'Searching...' : 'Find Tutor' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useInitialBookingPrefsStore } from '@/stores/initialbookingprefs'
import api from '@/services/api/api'

const router = useRouter()
const store = useInitialBookingPrefsStore()

const isSubmitting = ref(false)
const subjects = ref([])
const tutors = ref([])

const modes = ['Online', 'Face-to-face']


// Load subjects from backend
onMounted(async () => {

  try {

    const response = await api.get('/subjects/')
    subjects.value = response.data

  } catch (error) {

    console.error("Failed to load subjects", error)

  }

})


// FIND TUTOR (CBF CALL)
const findTutor = async () => {

  isSubmitting.value = true

  try {

    const res = await api.post('/recommend-tutors/', {

      subject: store.selectedSubject,
      topic: store.selectedTopic,
      preferred_mode: store.selectedMode,
      date: store.selectedDate,
      start_time: store.selectedStartTime,
      end_time: store.selectedEndTime

    })

    tutors.value = res.data

    console.log("Recommended tutors:", tutors.value)

    // navigate to tutors page
    router.push({ name: 'tutors' })

  } catch (err) {

    console.error("Tutor recommendation failed", err)

  } finally {

    isSubmitting.value = false

  }

}
</script>
```

--- src/views/LandingPage.vue ---
```
<template>
  <div class="landing-page bg-white min-vh-100 font-inter">
    
    <nav class="navbar navbar-expand-lg bg-white py-3">
      <div class="container">
        <a class="navbar-brand d-flex align-items-center fw-bold fs-4" href="#">
          <i class="bi bi-book text-sb-primary me-2"></i>
          <span class="text-dark">StudyBuddy</span>
        </a>
        <div class="d-flex gap-3 align-items-center">
          <router-link to="/login" class="text-dark fw-semibold text-decoration-none">Log In</router-link>
          <router-link to="/register" class="btn bg-sb-primary text-white px-4 py-2 rounded-pill fw-semibold shadow-sm">
            Get Started
          </router-link>
        </div>
      </div>
    </nav>

    <section class="hero-section py-5 my-5">
      <div class="container">
        <div class="row align-items-center g-5">
          <div class="col-lg-6">
            <span class="badge bg-success bg-opacity-10 text-sb-primary rounded-pill px-3 py-2 mb-4 fw-semibold border border-success border-opacity-25">
              University Peer Tutoring Network
            </span>
            <h1 class="display-3 fw-bold text-dark mb-4" style="line-height: 1.2;">
              Learn Better, <br>
              <span class="text-sb-primary">Together</span>
            </h1>
            <p class="lead text-muted mb-5 pe-lg-5" style="font-size: 1.15rem;">
              Connect with peer tutors matched to your learning needs. Smart recommendations, flexible scheduling, and fair compensation â€” all in one platform.
            </p>
            <div class="d-flex gap-3">
              <router-link to="/register" class="btn bg-sb-primary text-white px-4 py-3 rounded-3 fw-semibold shadow-sm d-flex align-items-center">
                Find a Tutor <i class="bi bi-arrow-right ms-2"></i>
              </router-link>
              <router-link to="/register" class="btn btn-outline-dark px-4 py-3 rounded-3 fw-semibold">
                Become a Tutor
              </router-link>
            </div>
          </div>
          
          <div class="col-lg-6">
            <div class="rounded-4 overflow-hidden shadow-lg border border-sb d-flex align-items-center justify-content-center bg-white" style="height: 400px;">
              <img 
                src="@/assets/hero.png"
                alt="StudyBuddy Peer Tutoring Illustration" 
                class="img-fluid w-100 h-100"
                style="object-fit: contain; padding: 20px;"
              >
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="stats-section border-top border-bottom border-sb py-5 bg-sb-bg">
      <div class="container">
        <div class="row text-center g-4">
          <div class="col-6 col-md-3">
            <h2 class="display-5 fw-bold text-sb-primary mb-1">500+</h2>
            <p class="text-muted fw-medium mb-0">Active Tutors</p>
          </div>
          <div class="col-6 col-md-3">
            <h2 class="display-5 fw-bold text-sb-primary mb-1">2,000+</h2>
            <p class="text-muted fw-medium mb-0">Sessions Completed</p>
          </div>
          <div class="col-6 col-md-3">
            <h2 class="display-5 fw-bold text-sb-primary mb-1">4.8</h2>
            <p class="text-muted fw-medium mb-0">Average Rating</p>
          </div>
          <div class="col-6 col-md-3">
            <h2 class="display-5 fw-bold text-sb-primary mb-1">50+</h2>
            <p class="text-muted fw-medium mb-0">Subjects Covered</p>
          </div>
        </div>
      </div>
    </section>

    <section class="features-section py-5 my-5">
      <div class="container">
        <div class="text-center mb-5 pb-3">
          <h2 class="fw-bold text-dark mb-3">Everything You Need to Succeed</h2>
          <p class="text-muted lead mx-auto" style="max-width: 600px;">
            StudyBuddy combines intelligent matching with practical tools to create the best peer tutoring experience.
          </p>
        </div>

        <div class="row g-4">
          <div class="col-md-6 col-lg-3">
            <div class="card h-100 border-sb shadow-sm rounded-4 p-3 hover-lift">
              <div class="card-body">
                <div class="rounded p-3 bg-success bg-opacity-10 d-inline-block mb-4">
                  <i class="bi bi-people text-sb-primary fs-4"></i>
                </div>
                <h5 class="fw-bold mb-3">Smart Tutor Matching</h5>
                <p class="text-muted small mb-0">
                  Our recommender system pairs you with the best peer tutor based on subject needs, ratings, and compatibility.
                </p>
              </div>
            </div>
          </div>

          <div class="col-md-6 col-lg-3">
            <div class="card h-100 border-sb shadow-sm rounded-4 p-3 hover-lift">
              <div class="card-body">
                <div class="rounded p-3 bg-success bg-opacity-10 d-inline-block mb-4">
                  <i class="bi bi-calendar3 text-sb-primary fs-4"></i>
                </div>
                <h5 class="fw-bold mb-3">Flexible Scheduling</h5>
                <p class="text-muted small mb-0">
                  View tutor availability in real-time and book sessions that fit your schedule with workload balancing.
                </p>
              </div>
            </div>
          </div>

          <div class="col-md-6 col-lg-3">
            <div class="card h-100 border-sb shadow-sm rounded-4 p-3 hover-lift">
              <div class="card-body">
                <div class="rounded p-3 bg-success bg-opacity-10 d-inline-block mb-4">
                  <i class="bi bi-bar-chart text-sb-primary fs-4"></i>
                </div>
                <h5 class="fw-bold mb-3">Earnings & Reports</h5>
                <p class="text-muted small mb-0">
                  Track session history, calculate compensation, and monitor tutoring performance metrics.
                </p>
              </div>
            </div>
          </div>

          <div class="col-md-6 col-lg-3">
            <div class="card h-100 border-sb shadow-sm rounded-4 p-3 hover-lift">
              <div class="card-body">
                <div class="rounded p-3 bg-success bg-opacity-10 d-inline-block mb-4">
                  <i class="bi bi-clock-history text-sb-primary fs-4"></i>
                </div>
                <h5 class="fw-bold mb-3">Workload Balance</h5>
                <p class="text-muted small mb-0">
                  Automatic workload assessment ensures tutors aren't overloaded, maintaining quality support.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="cta-section bg-sb-primary text-white py-5 text-center">
      <div class="container py-5">
        <h2 class="display-6 fw-bold mb-3">Ready to Start Learning?</h2>
        <p class="lead mb-5 opacity-75">
          Join hundreds of students already benefiting from peer tutoring on StudyBuddy.
        </p>
        <router-link to="/register" class="btn btn-light text-sb-primary px-5 py-3 rounded-3 fw-bold shadow-lg fs-5">
          Sign Up Free
        </router-link>
      </div>
    </section>

  </div>
</template>

<style scoped>
/* Ensure the font matches your design exactly */
.font-inter {
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
}

/* Subtle interactive animation for the feature cards */
.hover-lift {
  transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
}
.hover-lift:hover {
  transform: translateY(-5px);
  box-shadow: 0 .5rem 1rem rgba(0,0,0,.1) !important;
}

.bg-sb-bg {
  background-color: var(--sb-bg, #F8F9FA);
}
</style>
```

--- src/views/Login.vue ---
```
<template>
  <div class="min-vh-100 d-flex align-items-center justify-content-center py-5">
    <div class="card border-sb shadow-sm rounded-4" style="max-width: 400px; width: 100%">
      <div class="card-body p-4 p-md-5">
        <div class="text-center mb-4">
          <div
            class="d-inline-flex align-items-center justify-content-center bg-success bg-opacity-10 rounded-3 mb-3"
            style="width: 48px; height: 48px"
          >
            <i class="bi bi-box-arrow-in-right text-sb-primary fs-4"></i>
          </div>
          <h3 class="fw-bold text-dark">Welcome Back</h3>
          <p class="text-muted small">Log in to your StudyBuddy account</p>
        </div>

        <div v-if="loginError" class="alert alert-danger">
          {{ loginError }}
        </div>

        <form @submit.prevent="handleLogin">
          <div class="mb-3">
            <label class="form-label fw-semibold small text-dark">University Email</label>
            <input
              type="email"
              v-model="email"
              class="form-control shadow-none"
              placeholder="you@university.edu"
              required
            />
          </div>

          <div class="mb-4">
            <div class="d-flex justify-content-between align-items-center">
              <label class="form-label fw-semibold small text-dark mb-0">Password</label>
              <a href="#" class="text-sb-primary small text-decoration-none fw-semibold">Forgot?</a>
            </div>
            <input
              type="password"
              v-model="password"
              class="form-control shadow-none mt-2"
              placeholder="â€¢â€¢â€¢â€¢â€¢â€¢â€¢â€¢"
              required
            />
          </div>

          <button
            type="submit"
            class="btn bg-sb-primary text-white w-100 py-2 rounded-3 fw-semibold shadow-sm d-flex justify-content-center align-items-center gap-2"
            :disabled="isSubmitting"
          >
            <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-2"></span>
            {{ isSubmitting ? 'Signing In...' : 'Sign In' }}
          </button>
        </form>

        <div class="text-center mt-4">
          <p class="text-muted small mb-0">
            No account?
            <router-link to="/register" class="text-sb-primary fw-bold text-decoration-none">
              Create one
            </router-link>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const isSubmitting = ref(false)
const loginError = ref('')


const handleLogin = async () => {
  console.log("Login function triggered")
  isSubmitting.value = true
  loginError.value = ''

  try {
    // API_INTEGRATION_POINT: The actual axios call is delegated to the store
    const role = await authStore.login({
      email: email.value,
      password: password.value
    })

    console.log("Role from backend:", role)

    const normalizedRole = role?.toLowerCase()

    console.log("Normalized Role:", normalizedRole)
    // Route to dashboard based on user role
    if (normalizedRole === 'tutor') {
      console.log("Routing to tutor dashboard")
      router.push('/tch-dashboard')
    } 
    else if (normalizedRole === 'tutee') {
       console.log("Routing to student dashboard")
      router.push('/dashboard')
    } 
    else {
       console.log("Routing to fallback")
      router.push('/')
    }

  } catch (error) {
    console.error('Login Error:', error)
    loginError.value = error.response?.data?.error || 'Login failed. Please check your credentials.'
  } finally {
    isSubmitting.value = false
  }
}
</script>
```

--- src/views/PaymentScreenTutee.vue ---
```
<template>
<div class="booking-content container py-2">
    <div class="mb-3">
        <button
            class="btn btn-outline-secondary d-flex align-items-center gap-2"
            @click="backButton"
        >
            <i class="bi bi-arrow-left"></i>
            Back
        </button>
    </div>
    <div class="container py-5">
    <div class="row justify-content-center">
        <div class="col-md-7">
        <div class="card border-sb shadow-sm rounded-4 p-4">

            <div class="card boarder-sb rounded-2 p-1 bg-light">
            <h5>Payment Summary</h5>
            <div v-if="paymentSummary">
                <p><strong>Hours:</strong> {{ paymentSummary.hours }}</p>
                <p><strong>Total:</strong> {{ paymentSummary.total }}</p>
                <p><strong>Subject:</strong> {{ paymentSummary.subject }}</p>
                <p><strong>Tutor:</strong> {{ paymentSummary.tutor }}</p>
            </div>

            <div v-else>
                <p>Loading summary...</p>
            </div>

            </div>

            <div class="paymentOptions">
            <h5>Payment Options</h5>

            <div class="card border-0 rounded-2 p-1 bg-transparent">
                <div class="row g-3">

                <div 
                    v-for="method in paymentMethods"
                    :key="method.id"
                    class="col-4"
                >
                    <button 
                    class="btn btn-outline-sb-primary w-100 d-flex flex-column align-items-center py-3"
                    :class="{ 'btn-sb-primary': paymentStore.selectedMethod === method.id }"
                    @click="chooseMethod(method.id)"
                    >
                    <i :class="`bi ${method.icon} fs-3`"></i>
                    <span class="mt-2 text-center">
                        {{ method.label }}
                    </span>
                    </button>
                </div>

                </div>
            </div>
            </div>

            <div class="card border-sb rounded p-3 mt-3">

            <div v-if="selectedMethodName === 'Cash'">

                <div class="alert alert-info">
                Please prepare exact amount.
                </div>

                <button
                class="btn btn-primary bg-sb-primary w-100"
                style="border-color: #00895A;"
                @click="ConfirmPayment"
                >
                Confirm Cash Payment
                </button>
            </div>

            <div v-else-if="selectedMethodName === 'GCash'">
                <div class="mb-3">
                <label class="form-label">Account Name</label>
                <input
                    type="text"
                    class="form-control"
                    v-model="paymentStore.gCashName"
                    placeholder="Enter GCash name"
                />
                </div>

                <div class="mb-3">
                <label class="form-label">GCash Number</label>
                <input
                    type="tel"
                    class="form-control"
                    v-model="paymentStore.gCashNumber"
                    placeholder="09XXXXXXXXX"
                />
                </div>

                <div class="mb-3">
                <label class="form-label">Reference Number</label>
                <input
                    type="text"
                    class="form-control"
                    v-model="paymentStore.gCashReference"
                    placeholder="Transaction reference"
                />
                </div>

                <button
                class="btn btn-primary bg-sb-primary w-100"
                style="border-color: #00895A;"
                >
                Submit GCash Payment
                </button>
            </div>

            <div v-else-if="selectedMethodName === 'Bank Transfer'">
                <div class="mb-3">
                <label class="form-label">Account Holder Name</label>
                <input
                    type="text"
                    class="form-control"
                    v-model="paymentStore.bankName"
                    placeholder="Enter account name"
                />
                </div>

                <div class="mb-3">
                <label class="form-label">Account Number</label>
                <input
                    type="text"
                    class="form-control"
                    v-model="paymentStore.bankAccount"
                    placeholder="Enter account number"
                />
                </div>

                <div class="mb-3">
                <label class="form-label">Transaction Reference</label>
                <input
                    type="text"
                    class="form-control"
                    v-model="paymentStore.bankReference"
                    placeholder="Reference number"
                />
                </div>

                <button
                class="btn btn-primary bg-sb-primary w-100"
                style="border-color: #00895A;"
                >
                Confirm Payment
                </button>
            </div>

            <div v-else>
                <p class="text-muted text-center">
                Please select a payment method.
                </p>
            </div>

            </div>
            


        </div>
        </div>
    </div>
  </div>
</div>
    
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/services/api/api'
import { usePaymentStore } from '@/stores/tuteePaymentDetails'
import { useBookedSessionStore } from '@/stores/bookedSessionDetails'

const route = useRoute()
const router = useRouter()

const paymentStore = usePaymentStore()
const bookedSessionStore = useBookedSessionStore()

const tutorId = route.params.tutorId

const tutor = ref(null)
const paymentMethods = ref([])

const selectedMethodName = computed(() => {
  const method = paymentMethods.value.find(
    m => m.id === paymentStore.selectedMethod
  )
  return method ? method.label : null
})

// ---------------------------
// PAYMENT SUMMARY
// ---------------------------
const paymentSummary = computed(() => {
  if (!tutor.value) return null

  const hourlyRate = parseFloat(tutor.value.hourly_rate)
  const hours = bookedSessionStore.bookedSessions?.length || 0
  const total = hourlyRate * hours

  return {
    hours,
    total: `â‚±${total.toLocaleString()}`,
    subject: bookedSessionStore.bookedSessionSub,
    tutor: `${tutor.value.fname} ${tutor.value.lname}`
  }
})


// ---------------------------
// NAVIGATION
// ---------------------------
const backButton = () => {
  router.push(`/tutor/${tutorId}`)
  paymentStore.reset()
}


// ---------------------------
// SELECT PAYMENT METHOD
// ---------------------------
const chooseMethod = (methodId) => {
  paymentStore.selectedMethod = methodId
}


// ---------------------------
// LOAD DATA
// ---------------------------
onMounted(async () => {
  try {
    // Load tutor
    const tutorRes = await api.get(`tutors/${tutorId}/`)
    tutor.value = tutorRes.data

    // Load payment methods from backend
    const methodsRes = await api.get('payment-methods/')
    paymentMethods.value = methodsRes.data.map(m => ({
      id: m.id,
      label: m.name,
      icon:
        m.name === 'GCash' ? 'bi-wallet2' :
        m.name === 'Cash' ? 'bi-cash-coin' :
        'bi-credit-card'
    }))

  } catch (error) {
    console.error("Initialization error:", error)
    router.push('/find-tutors')
  }

  // Protect against direct URL access
  if (!bookedSessionStore.bookedSessionSub) {
    alert("No Sessions Selected.")
    router.push('/find-tutors')
  }
})

// ---------------------------
// CONFIRM PAYMENT
// ---------------------------
const ConfirmPayment = async () => {

  if (!paymentStore.selectedMethod) {
    alert("Please select a payment method.")
    return
  }

  try {

    await api.post('bookings/confirm/', {
      tutor_id: tutorId,
      date: bookedSessionStore.bookedSessionDate,
      slots: bookedSessionStore.bookedSessions,
      payment_method: paymentStore.selectedMethod   // real DB method_id
    })

    alert("Booking Confirmed!")

    paymentStore.reset()
    bookedSessionStore.resetStore()

    router.push({
      name: 'dashboard',
      query: { refresh: Date.now() }
    })

  } catch (error) {
    console.error("Payment error:", error.response?.data || error)
    alert(error.response?.data?.error || "Something went wrong.")
  }
}
</script>

<style setup>
.btn-outline-sb-primary {
  color: var(--sb-primary);
  border: 1px solid var(--sb-primary);
  background-color: transparent;
}
.btn-outline-sb-primary:hover {
  background-color: var(--sb-primary);
  color: white;
}
.btn-sb-primary {
  background-color: var(--sb-primary);
  border-color: var(--sb-primary);
  color: white;
}
</style>
```

--- src/views/PreferenceSetup.vue ---
```
<template>

  <!-- NAVBAR -->
  <nav class="navbar navbar-expand-lg bg-white py-3">
    <div class="container">
      <a class="navbar-brand fw-bold fs-4">
        StudyBuddy
      </a>
    </div>
  </nav>

  <div class="container py-5">

    <div class="row justify-content-center">

      <div class="col-md-7">

        <div class="card shadow-sm rounded-4 p-4">

          <!-- PROGRESS -->
          <div class="mb-4">
            <div class="progress" style="height:8px;">
              <div
                class="progress-bar bg-success"
                :style="{ width: progressPercentage + '%' }"
              ></div>
            </div>
          </div>


          <!-- CARD 1 SUBJECTS -->
          <div v-if="currentCard === 0">

            <div class="text-center mb-4">
              <h3 class="fw-bold">What subjects are you interested in?</h3>
              <p class="text-muted">Choose all that apply</p>
            </div>

            <div class="row g-3 mb-4">

              <div
                class="col-6"
                v-for="subject in subjects"
                :key="subject.subject_code"
              >

                <div
                  class="card border rounded-4 p-3 text-center h-100 subject-card"
                  style="cursor:pointer"
                  :class="store.selectedSubjects.includes(subject.subject_code)
                    ? 'border-success bg-success bg-opacity-10'
                    : ''"
                  @click="toggleSubject(subject.subject_code)"
                >

                  <h6 class="fw-bold mb-0">
                    {{ subject.subject_name }}
                  </h6>

                </div>

              </div>

            </div>

            <div class="d-flex justify-content-end">

              <button
                class="btn btn-success px-4"
                :disabled="store.selectedSubjects.length === 0"
                @click="nextCard"
              >
                Continue
              </button>

            </div>

          </div>


          <!-- CARD 2 YEAR LEVEL -->
          <div v-else-if="currentCard === 1">

            <div class="text-center mb-4">
              <h3 class="fw-bold">Select Your Year Level</h3>
              <p class="text-muted">Choose your current academic level</p>
            </div>

            <div class="mb-4">

              <select class="form-select" v-model="yearLevel">

                <option disabled value="">Select Year Level</option>

                <option
                  v-for="level in yearLevels"
                  :key="level.value"
                  :value="level.value"
                >
                  {{ level.label }}
                </option>

              </select>

            </div>

            <div class="d-flex justify-content-end">

              <button
                class="btn btn-success px-4"
                :disabled="!yearLevel"
                @click="nextCard"
              >
                Continue
              </button>

            </div>

          </div>


          <!-- CARD 3 COURSE -->
          <div v-else-if="currentCard === 2">

            <div class="text-center mb-4">
              <h3 class="fw-bold">Select Your Course</h3>
              <p class="text-muted">Choose your academic program</p>
            </div>

            <div class="mb-4">

              <select class="form-select" v-model="selectedCourse">

                <option disabled value="">Select Course</option>

                <option
                  v-for="course in courses"
                  :key="course.course_code"
                  :value="course.course_code"
                >
                  {{ course.course_name }}
                </option>

              </select>

            </div>

            <div class="d-flex justify-content-end">

              <button
                class="btn btn-success px-4"
                :disabled="!selectedCourse || isSubmitting"
                @click="finish"
              >
                {{ isSubmitting ? "Saving..." : "Go to Dashboard" }}
              </button>

            </div>

          </div>

        </div>

      </div>

    </div>

  </div>

</template>

<script setup>

import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { usePreferenceStore } from '@/stores/preferences'
import { useProfileStore } from '@/stores/profile'
import api from '@/services/api/api'

const router = useRouter()
const store = usePreferenceStore()
const profileStore = useProfileStore()

const currentCard = ref(0)
const totalCards = 3
const isSubmitting = ref(false)

const subjects = ref([])
const courses = ref([])

const yearLevel = ref('')
const selectedCourse = ref('')

/* YEAR LEVEL OPTIONS */

const yearLevels = [

  { label: "Grade 1", value: 1 },
  { label: "Grade 2", value: 2 },
  { label: "Grade 3", value: 3 },
  { label: "Grade 4", value: 4 },
  { label: "Grade 5", value: 5 },
  { label: "Grade 6", value: 6 },
  { label: "Grade 7", value: 7 },
  { label: "Grade 8", value: 8 },
  { label: "Grade 9", value: 9 },
  { label: "Grade 10", value: 10 },
  { label: "Grade 11", value: 11 },
  { label: "Grade 12", value: 12 },

  { label: "1st Year College", value: 13 },
  { label: "2nd Year College", value: 14 },
  { label: "3rd Year College", value: 15 },
  { label: "4th Year College", value: 16 }

]

/* LOAD DATA */

onMounted(async () => {

  try {

    const subjectRes = await api.get('subjects/')
    subjects.value = subjectRes.data

    const courseRes = await api.get('courses/')
    courses.value = courseRes.data

  } catch (error) {

    console.error("Failed loading setup data", error)

  }

})

/* SUBJECT TOGGLE */

const toggleSubject = (code) => {

  const index = store.selectedSubjects.indexOf(code)

  if (index > -1) {
    store.selectedSubjects.splice(index, 1)
  } else {
    store.selectedSubjects.push(code)
  }

}

/* NEXT CARD */

const nextCard = () => {

  if (currentCard.value < totalCards - 1) {
    currentCard.value++
  }

}

/* FINISH SETUP */

const finish = async () => {

  isSubmitting.value = true

  try {

    await api.post('profile/setup/', {
      course: selectedCourse.value,
      year_level: yearLevel.value,
      bio: "Student profile"
    })

    await api.post("preferences/", {
       subjects: [...store.selectedSubjects]
    })

    profileStore.profileCompleted = true
    profileStore.loaded = true

    store.resetPreferences()

    router.push('/dashboard')

  } catch (error) {

    console.error("Failed saving preferences", error)
    alert("Could not save preferences")

  } finally {

    isSubmitting.value = false

  }

}

/* PROGRESS BAR */

const progressPercentage = computed(() => {
  return ((currentCard.value + 1) / totalCards) * 100
})

</script>
```

--- src/views/Profile.vue ---
```
<template>
  <div class="profile-content">
    <div class="mb-4">
      <h2 class="fw-bold text-dark">My Profile</h2>
      <p class="text-muted">Manage your personal information and tutoring preferences.</p>
    </div>

    <div class="card border-sb shadow-sm rounded-4" style="max-width: 800px;">
      <div v-if="userRole === 'tutee'" class="card-body p-4 p-md-5">
        
        <div class="d-flex align-items-center mb-4 pb-4 border-bottom border-sb">
          <div class="rounded-circle bg-success bg-opacity-10 text-sb-primary d-flex justify-content-center align-items-center fw-bold fs-3 me-4" style="width: 80px; height: 80px;">
            JD
          </div>
          <div>
            <h5 class="fw-bold mb-1">Juan Dela Cruz</h5>
            <p class="text-muted small mb-2">Student / Tutee</p>
            <button class="btn btn-outline-dark btn-sm rounded-3 fw-semibold px-3">Update Photo</button>
          </div>
        </div>

        <form @submit.prevent="saveProfile">
          <div class="row g-4 mb-4">
            
            <div class="col-md-6">
              <label class="form-label fw-semibold small text-dark">Full Name</label>
              <input type="text" class="form-control border-sb shadow-none" value="Juan Dela Cruz">
            </div>
            
            <div class="col-md-6">
              <label class="form-label fw-semibold small text-dark">University Email</label>
              <input type="email" class="form-control border-sb shadow-none bg-light text-muted" value="juan@university.edu" disabled>
              <div class="form-text small">Email cannot be changed after registration.</div>
            </div>
            
            <div class="col-md-6">
              <label class="form-label fw-semibold small text-dark">Major / Degree Program</label>
              <input type="text" class="form-control border-sb shadow-none" placeholder="e.g., Computer Science">
            </div>
            
            <div class="col-md-6">
              <label class="form-label fw-semibold small text-dark">Year Level</label>
              <select class="form-select border-sb shadow-none">
                <option value="1">1st Year</option>
                <option value="2">2nd Year</option>
                <option value="3">3rd Year</option>
                <option value="4">4th Year</option>
                <option value="5">Graduate</option>
              </select>
            </div>
            
            <div class="col-12">
              <label class="form-label fw-semibold small text-dark">Bio (About Me)</label>
              <textarea class="form-control border-sb shadow-none" rows="4" placeholder="Tell tutors a bit about your learning style or what you usually need help with..."></textarea>
            </div>
            
          </div>

          <div class="text-end mt-2">
            <button type="submit" class="btn bg-sb-primary text-white px-5 py-2 rounded-3 fw-semibold shadow-sm">
              Save Changes
            </button>
          </div>
        </form>

      </div>

      <div v-else  class="card-body p-4 p-md-5">
        
        <div class="d-flex align-items-center mb-4 pb-4 border-bottom border-sb">
          <div class="rounded-circle bg-success bg-opacity-10 text-sb-primary d-flex justify-content-center align-items-center fw-bold fs-3 me-4" style="width: 80px; height: 80px;">
            JD
          </div>
          <div>
            <h5 class="fw-bold mb-1">Juan Dela Cruz</h5>
            <p class="text-muted small mb-2">Student / Tutor</p>
            <button class="btn btn-outline-dark btn-sm rounded-3 fw-semibold px-3">Update Photo</button>
          </div>
        </div>

        <form @submit.prevent="saveProfile">
          <div class="row g-4 mb-4">
            
            <div class="col-md-6">
              <label class="form-label fw-semibold small text-dark">Full Name</label>
              <input type="text" class="form-control border-sb shadow-none" value="Juan Dela Cruz">
            </div>
            
            <div class="col-md-6">
              <label class="form-label fw-semibold small text-dark">University Email</label>
              <input type="email" class="form-control border-sb shadow-none bg-light text-muted" value="juan@university.edu" disabled>
              <div class="form-text small">Email cannot be changed after registration.</div>
            </div>
            
            <div class="col-md-6">
              <label class="form-label fw-semibold small text-dark">Major / Degree Program</label>
              <input type="text" class="form-control border-sb shadow-none" placeholder="e.g., Computer Science">
            </div>
            
            <div class="col-md-6">
              <label class="form-label fw-semibold small text-dark">Year Level</label>
              <select class="form-select border-sb shadow-none">
                <option value="1">1st Year</option>
                <option value="2">2nd Year</option>
                <option value="3">3rd Year</option>
                <option value="4">4th Year</option>
                <option value="5">Graduate</option>
              </select>
            </div>
            
            <div class="col-12 mt-3">

              <div class="d-flex justify-content-between align-items-center mb-3">
                <label class="form-label fw-semibold small text-dark mb-0">
                  Subjects Offered
                </label>
                <button type="button" class="btn btn-outline-dark btn-sm rounded-3 fw-semibold px-3">
                  Edit
                </button>
              </div>

              <div class="d-flex flex-wrap gap-2">
                <span class="badge bg-sb-primary text-white px-3 py-2 rounded-pill">
                  Mathematics
                </span>

                <span class="badge bg-sb-primary text-white px-3 py-2 rounded-pill">
                  Physics
                </span>

                <span class="badge bg-sb-primary text-white px-3 py-2 rounded-pill">
                  Programming
                </span>

                <span class="badge bg-sb-primary text-white px-3 py-2 rounded-pill">
                  Data Structures
                </span>
              </div>

            </div>

            <div class="col-12">
              <label class="form-label fw-semibold small text-dark">Bio (About Me)</label>
              <textarea class="form-control border-sb shadow-none" rows="4" placeholder="Tell tutors a bit about your learning style or what you usually need help with..."></textarea>
            </div>
            
          </div>

          <div class="text-end mt-2">
            <button type="submit" class="btn bg-sb-primary text-white px-5 py-2 rounded-3 fw-semibold shadow-sm">
              Save Changes
            </button>
          </div>
        </form>

      </div>
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore()

const userRole = computed(() => authStore.user?.role?.toLowerCase() || null)

const saveProfile = () => {
  // In a real application, this would trigger an API call to update the database
  alert('Profile updated successfully! (Placeholder logic)')
}
</script>

<style scoped>
.form-control:focus, .form-select:focus {
  border-color: var(--sb-primary);
  box-shadow: 0 0 0 0.25rem rgba(0, 137, 90, 0.25);
}
</style>
```

--- src/views/Register.vue ---
```
<template>
  <div class="min-vh-100 d-flex align-items-center justify-content-center py-5">
    <div class="card border-sb shadow-sm rounded-4" style="max-width: 450px; width: 100%;">
      <div class="card-body p-4 p-md-5">
        <div class="text-center mb-4">
          <div class="d-inline-flex align-items-center justify-content-center bg-success bg-opacity-10 rounded-3 mb-3" style="width: 48px; height: 48px;">
            <i class="bi bi-book text-sb-primary fs-4"></i>
          </div>
          <h3 class="fw-bold text-dark">Create Account</h3>
          <p class="text-muted small">Join the StudyBuddy network</p>
        </div>

        <div v-if="generalError" class="alert alert-danger">
          {{ generalError }}
        </div>

        <form @submit.prevent="handleRegister">
          <div class="mb-3">
            <label class="form-label fw-semibold small text-dark">First Name</label>
            <div class="input-group">
              <span class="input-group-text bg-white border-end-0 text-muted"><i class="bi bi-person"></i></span>
              <input type="text" v-model="store.newUserFname" class="form-control border-start-0 ps-0 shadow-none" placeholder="Juan Dela Cruz" required>
            </div>
          </div>

          <div class="mb-3">
            <label class="form-label fw-semibold small text-dark">Middle Name</label>
            <div class="input-group">
              <span class="input-group-text bg-white border-end-0 text-muted"><i class="bi bi-person"></i></span>
              <input type="text" v-model="store.newUserMname" class="form-control border-start-0 ps-0 shadow-none" placeholder="Juan Dela Cruz" required>
            </div>
          </div>

          <div class="mb-3">
            <label class="form-label fw-semibold small text-dark">Last Name</label>
            <div class="input-group">
              <span class="input-group-text bg-white border-end-0 text-muted"><i class="bi bi-person"></i></span>
              <input type="text" v-model="store.newUserLname" class="form-control border-start-0 ps-0 shadow-none" placeholder="Juan Dela Cruz" required>
            </div>
          </div>

          <div class="mb-3">
            <label class="form-label fw-semibold small text-dark">University Email</label>
            <div class="input-group">
              <span class="input-group-text bg-white border-end-0 text-muted"><i class="bi bi-envelope"></i></span>
              <input type="email" v-model="store.newUserEmail" class="form-control border-start-0 ps-0 shadow-none" placeholder="you@university.edu" required>
            </div>
            <div v-if="emailError" class="text-danger small mt-1">{{ emailError }}</div>
          </div>

          <div class="mb-3">
            <label class="form-label fw-semibold small text-dark">Institution</label>
            <select v-model="store.selectedInstitutionId" class="form-select shadow-none" required>
              <option value="" disabled>Select your institution</option>
              <option
                v-for="institution in institutions"
                :key="institution.id"
                :value="String(institution.id)"
              >
                {{ institution.institution_name }} ({{ institution.school_email_domain }})
              </option>
            </select>
            <div v-if="selectedInstitutionDomain" class="form-text small">
              Allowed email domain: {{ selectedInstitutionDomain }}
            </div>
            <div v-if="institutionError" class="text-danger small mt-1">{{ institutionError }}</div>
          </div>

          <div class="mb-3">
            <label class="form-label fw-semibold small text-dark">Password</label>
            <div class="input-group">
              <span class="input-group-text bg-white border-end-0 text-muted"><i class="bi bi-lock"></i></span>
              <input type="password" v-model="store.newUserPassword" class="form-control border-start-0 ps-0 shadow-none" placeholder="â€¢â€¢â€¢â€¢â€¢â€¢â€¢â€¢" required>
            </div>
          </div>

          <div class="mb-4">
            <label class="form-label fw-semibold small text-dark">I want to</label>
            <select v-model="store.newUserType" class="form-select shadow-none" required>
              <option value="" disabled selected>Select your role</option>
              <option value="Tutee">Find a Tutor (Student)</option>
              <option value="Tutor">Become a Tutor</option>
            </select>
          </div>

          <button type="submit" class="btn bg-sb-primary text-white w-100 py-2 rounded-3 fw-semibold shadow-sm d-flex justify-content-center align-items-center gap-2" :disabled="isSubmitting">
            <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-2"></span>
            {{ isSubmitting ? 'Processing...' : 'Create Account' }}
            <i v-if="!isSubmitting" class="bi bi-arrow-right"></i>
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useRegistrationInfoStore } from '@/stores/registrationinfo'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'

const router = useRouter()
const store = useRegistrationInfoStore()
const authStore = useAuthStore()

const isSubmitting = ref(false)
const institutions = ref([])

const generalError = ref('')
const emailError = ref('')
const institutionError = ref('')

const selectedInstitution = computed(() => {
  return institutions.value.find(
    (institution) => String(institution.id) === String(store.selectedInstitutionId)
  ) || null
})

const selectedInstitutionDomain = computed(() => {
  return selectedInstitution.value?.school_email_domain || ''
})

const emailDomainMatchesInstitution = computed(() => {
  if (!store.newUserEmail || !selectedInstitutionDomain.value) {
    return true
  }

  const parts = store.newUserEmail.split('@')

  if (parts.length !== 2) {
    return false
  }

  return parts[1].trim().toLowerCase() === selectedInstitutionDomain.value.toLowerCase()
})

const loadInstitutions = async () => {
  try {
    const response = await axios.get('http://localhost:8000/api/partner-institutions/')
    institutions.value = response.data
  } catch (error) {
    console.error('Failed to load partner institutions:', error)
    generalError.value = 'Unable to load partner institutions right now. Please try again later.'
  }
}

const handleRegister = async () => {

  generalError.value = ''
  emailError.value = ''
  institutionError.value = ''

  // ðŸ”¹ Basic validation
  if (!store.newUserFname ||
      !store.newUserLname ||
      !store.newUserEmail ||
      !store.newUserPassword ||
      !store.selectedInstitutionId) {

    generalError.value = "Please fill in all required fields."
    return
  }

  // ðŸ”¹ Role validation
  if (!store.newUserType) {
    generalError.value = "Please select your role."
    return
  }

  if (!emailDomainMatchesInstitution.value) {
    institutionError.value = 'Your email domain does not match the selected institution. Please check and try again.'
    return
  }

  isSubmitting.value = true

  try {

    const role = store.newUserType

    // ðŸ”¹ REGISTER USER
    await axios.post('http://localhost:8000/api/register/', {
      fname: store.newUserFname,
      mname: store.newUserMname,
      lname: store.newUserLname,
      email: store.newUserEmail,
      password: store.newUserPassword,
      role: role,
      institution_id: store.selectedInstitutionId
    })

    // ðŸ”¹ AUTO LOGIN
    await authStore.login({
      email: store.newUserEmail,
      password: store.newUserPassword
    })

    // ðŸ”¹ ROLE BASED REDIRECT
    if (role === 'Tutor') {
      router.push('/tutor-setup')
    } else {
      router.push('/preferencesetup')
    }

  } catch (error) {

    console.error('Registration Error:', error)

    if (error.response) {

      const data = error.response.data

      const message = data.error || data.detail || "Registration failed. Please try again."

      if (message.toLowerCase().includes('email')) {
        emailError.value = message
      } else if (message.toLowerCase().includes('institution')) {
        institutionError.value = message
      } else {
        generalError.value = message
      }

    }

    else if (error.request) {
      generalError.value = "Server not responding. Please try again later."
    }

    else {
      generalError.value = "An unexpected error occurred."
    }

  } finally {
    isSubmitting.value = false
  }
}

onMounted(() => {
  loadInstitutions()
})
</script>
```

--- src/views/Schedule.vue ---
```
<template>
  <div class="schedule-content">
    <div class="mb-4">
      <h2 class="fw-bold text-dark">My Schedule</h2>
      <p class="text-muted">Manage your availability for tutoring sessions.</p>
    </div>

    <div class="card border-sb border-1 shadow-sm rounded-4">
      <div class="card-body p-4 p-md-5">
        
        <h4 class="fw-bold mb-4 d-flex align-items-center">
          <i class="bi bi-calendar-check text-sb-primary me-3"></i> Weekly Availability
        </h4>

        <div class="d-flex flex-column gap-3">
          
          <div 
            v-for="day in weeklySchedule" 
            :key="day.name" 
            class="card border-sb rounded-4 shadow-none"
          >
            <div class="card-body p-4">
              <h6 class="fw-bold mb-3">{{ day.name }}</h6>
              
              <div class="d-flex flex-wrap gap-3">
                <div 
                  v-for="slot in day.slots" 
                  :key="slot.id"
                  class="time-slot-pill d-flex align-items-center justify-content-between border border-sb rounded-pill px-3 py-2 bg-white"
                >
                  
                  <div class="d-flex align-items-center text-muted" style="font-size: 0.9rem;">
                    <i class="bi bi-clock me-2"></i>
                    <span>{{ slot.time }}</span>
                  </div>

                  <div class="d-flex align-items-center gap-2 ms-4">
                    <div class="form-check form-switch mb-0 custom-switch-wrapper">
                      <input 
                        class="form-check-input custom-switch shadow-none cursor-pointer" 
                        type="checkbox" 
                        role="switch" 
                        v-model="slot.isOpen"
                        @change="handleScheduleChange(day.name, slot)"
                      >
                    </div>
                    <span 
                      class="badge rounded-pill px-3 py-1 fw-normal" 
                      :class="slot.isOpen ? 'bg-sb-primary text-white' : 'bg-light text-muted border border-sb'"
                    >
                      {{ slot.isOpen ? 'Open' : 'Closed' }}
                    </span>
                  </div>

                </div>
              </div>
            </div>
          </div>

        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// Data-driven state: This mimics what your backend API will eventually send
const weeklySchedule = ref([
  {
    name: 'Monday',
    slots: [
      { id: 'm1', time: '9:00 â€“ 12:00', isOpen: true },
      { id: 'm2', time: '14:00 â€“ 17:00', isOpen: false }
    ]
  },
  {
    name: 'Tuesday',
    slots: [
      { id: 't1', time: '10:00 â€“ 13:00', isOpen: true },
      { id: 't2', time: '14:00 â€“ 17:00', isOpen: true }
    ]
  },
  {
    name: 'Wednesday',
    slots: [
      { id: 'w1', time: '9:00 â€“ 12:00', isOpen: false },
      { id: 'w2', time: '14:00 â€“ 17:00', isOpen: true }
    ]
  },
  {
    name: 'Thursday',
    slots: [
      { id: 'th1', time: '9:00 â€“ 12:00', isOpen: true },
      { id: 'th2', time: '14:00 â€“ 17:00', isOpen: false }
    ]
  },
  {
    name: 'Friday',
    slots: [
      { id: 'f1', time: '9:00 â€“ 12:00', isOpen: true },
      { id: 'f2', time: '14:00 â€“ 17:00', isOpen: true }
    ]
  }
])

// Strategic foundation: Prepare for your API logic
const handleScheduleChange = (dayName, slot) => {
  // In the future, this is where you trigger an Axios/Fetch request to update the database
  console.log(`Updated workload capacity: ${dayName} at ${slot.time} is now ${slot.isOpen ? 'Open' : 'Closed'}`);
}
</script>

<style scoped>
/* Force the pill containers to a consistent minimum width matching the design */
.time-slot-pill {
  min-width: 260px;
}

/* Make the toggle pointer act like a clickable button */
.cursor-pointer {
  cursor: pointer;
}

/* Customizing Bootstrap's default blue switch to your brand's green */
.custom-switch-wrapper .form-check-input {
  width: 2.5em;
  height: 1.25em;
}

.custom-switch-wrapper .form-check-input:checked {
  background-color: var(--sb-primary);
  border-color: var(--sb-primary);
}

.custom-switch-wrapper .form-check-input:focus {
  border-color: rgba(0, 137, 90, 0.25);
  box-shadow: 0 0 0 0.25rem rgba(0, 137, 90, 0.25);
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='-4 -4 8 8'%3e%3ccircle r='3' fill='rgba%280, 0, 0, 0.25%29'/%3e%3c/svg%3e");
}

.custom-switch-wrapper .form-check-input:checked:focus {
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='-4 -4 8 8'%3e%3ccircle r='3' fill='%23fff'/%3e%3c/svg%3e");
}
</style>
```

--- src/views/SessionsReports.vue ---
```
<template>
  <div class="reports-content">
    <div class="mb-4">
      <h2 class="fw-bold text-dark">Sessions & Reports</h2>
      <p class="text-muted">Track your tutoring history, earnings, and performance.</p>
    </div>

    <div class="row g-4 mb-5">
      <div class="col-md-3">
        <div class="card border-sb shadow-sm h-100 rounded-4">
          <div class="card-body d-flex flex-column justify-content-center text-center py-4">
            <div class="d-flex align-items-center justify-content-center mb-2 gap-2">
              <div class="rounded-circle bg-success bg-opacity-10 text-sb-primary d-flex justify-content-center align-items-center" style="width: 32px; height: 32px;">
                <i class="bi bi-calendar-event"></i>
              </div>
              <span class="text-muted small fw-semibold">Total Sessions</span>
            </div>
            <h3 class="fw-bold mb-0">{{ totalSessions }}</h3>
          </div>
        </div>
      </div>
      
      <div class="col-md-3">
        <div class="card border-sb shadow-sm h-100 rounded-4">
          <div class="card-body d-flex flex-column justify-content-center text-center py-4">
            <div class="d-flex align-items-center justify-content-center mb-2 gap-2">
               <div class="rounded-circle bg-success bg-opacity-10 text-sb-primary d-flex justify-content-center align-items-center" style="width: 32px; height: 32px;">
                <i class="bi bi-currency-dollar"></i>
              </div>
              <span class="text-muted small fw-semibold">Total Earnings</span>
            </div>
            <h3 class="fw-bold mb-0">{{ totalEarnings }}</h3>
          </div>
        </div>
      </div>

      <div class="col-md-3">
        <div class="card border-sb shadow-sm h-100 rounded-4">
          <div class="card-body d-flex flex-column justify-content-center text-center py-4">
             <div class="d-flex align-items-center justify-content-center mb-2 gap-2">
               <div class="rounded-circle bg-warning bg-opacity-10 text-warning d-flex justify-content-center align-items-center" style="width: 32px; height: 32px;">
                <i class="bi bi-star"></i>
              </div>
              <span class="text-muted small fw-semibold">Avg Rating</span>
            </div>
            <h3 class="fw-bold mb-0">{{ averageRating }}</h3>
          </div>
        </div>
      </div>

      <div class="col-md-3">
        <div class="card border-sb shadow-sm h-100 rounded-4">
          <div class="card-body d-flex flex-column justify-content-center text-center py-4">
            <div class="d-flex align-items-center justify-content-center mb-2 gap-2">
               <div class="rounded-circle bg-info bg-opacity-10 text-info d-flex justify-content-center align-items-center" style="width: 32px; height: 32px;">
                <i class="bi bi-graph-up-arrow"></i>
              </div>
              <span class="text-muted small fw-semibold">Hours Tutored</span>
            </div>
            <h3 class="fw-bold mb-0">{{totalHours.toFixed(1)}}h</h3>
          </div>
        </div>
      </div>
    </div>

    <div class="card border-sb border-1 shadow-sm rounded-4">
      <div class="card-body p-4 p-md-5">
        
        <h4 class="fw-bold mb-4 d-flex align-items-center">
          <i class="bi bi-file-earmark-text text-sb-primary me-3"></i> Session History
        </h4>

        <div class="d-flex gap-2 mb-4 bg-light p-2 rounded-3 d-inline-flex border border-sb">
          <button 
            v-for="filter in filters" 
            :key="filter.value"
            @click="currentFilter = filter.value"
            class="btn rounded-pill px-3 py-1 fw-semibold text-muted shadow-none transition-all"
            :class="currentFilter === filter.value ? 'bg-white text-dark shadow-sm' : 'btn-light'"
          >
            {{ filter.label }}
          </button>
        </div>

        <div class="table-responsive">
          <table class="table table-hover align-middle mb-0">
            <thead>
              <tr class="text-muted small align-bottom" style="border-bottom: 2px solid var(--sb-card-border);">
                <th class="fw-semibold pb-3">Subject</th>
                <th class="fw-semibold pb-3">Tutor</th>
                <th class="fw-semibold pb-3">Date</th>
                <th class="fw-semibold pb-3">Duration</th>
                <th class="fw-semibold pb-3">Status</th>
                <th class="fw-semibold pb-3">Rating</th>
                <th class="fw-semibold pb-3">Earnings</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr 
              v-for="session in filteredSessions" 
              :key="session.id" 
              style="border-bottom: 1px solid var(--sb-card-border);"
              class="session-row">
                <td class="py-3 fw-bold">{{ session.subject }}</td>
                <td class="py-3">{{ session.tutor }}</td>
                <td class="py-3">{{ session.date }}</td>
                <td class="py-3">{{ session.startTime }} - {{ session.endTime }}</td>
                <td class="py-3">
                  <span class="badge rounded-pill px-3 py-1 fw-normal" :class="getStatusClass(session.status)">
                    {{ session.status }}
                  </span>
                </td>
                <td class="py-3">
                  <span v-if="session.rating" class="d-flex align-items-center text-warning fw-bold small">
                    <i class="bi bi-star-fill me-1"></i> {{ session.rating }}
                  </span>
                  <span v-else class="text-muted">â€”</span>
                </td>
                <td class="py-3 fw-bold">
                  {{ session.earnings ? 'â‚±' + session.earnings : 'â€”' }}
                </td>
                <td class="py-3 text-end action-cell">
                  <button 
                    class="btn btn-sm bg-sb-primary text-white"
                    @click="goToDetails(session.id)"
                  >
                    View Details
                  </button>
                </td>
              </tr>
              
              <tr v-if="filteredSessions.length === 0">
                <td colspan="7" class="text-center py-5 text-muted">
                  No sessions found for this category.
                </td>
              </tr>
            </tbody>
          </table>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useSessionsStore } from '@/stores/completedSessions'
import { useRouter } from 'vue-router'

const router = useRouter()
const sessionStore = useSessionsStore()
const currentFilter = ref('All')

const filters = computed(() => [
  { 
    label: `All (${sessionStore.sessions.length})`, 
    value: 'All' 
  },
  { 
    label: `Completed (${sessionStore.completedSessions.length})`, 
    value: 'completed' 
  },
  { 
    label: `Upcoming (${sessionStore.upcomingSessions.length})`, 
    value: 'upcoming' 
  },
  { 
    label: `Cancelled (${sessionStore.cancelledSessions.length})`, 
    value: 'cancelled' 
  }
])

onMounted(() => {
  sessionStore.fetchSessions()
})

const goToDetails = (sessionId) => {
  router.push(`/booking-details/${sessionId}`)
}

const totalSessions = computed(() =>
  sessionStore.sessions.length
)

const totalEarnings = computed(() =>
  sessionStore.completedSessions
    .reduce((sum, s) => sum + (s.earnings || 0), 0)
)

const averageRating = computed(() => {
  const rated = sessionStore.completedSessions
    .filter(s => s.rating)

  if (!rated.length) return 0

  return (
    rated.reduce((sum, s) => sum + s.rating, 0) /
    rated.length
  ).toFixed(1)
})

const totalHours = computed(() =>
  sessionStore.completedSessions
    .reduce((sum, s) => {
      const start = new Date(`1970-01-01T${s.startTime}`)
      const end = new Date(`1970-01-01T${s.endTime}`)
      return sum + (end - start)
    }, 0) / (1000 * 60 * 60)
)

const filteredSessions = computed(() => {
  switch (currentFilter.value) {
    case 'completed':
      return sessionStore.completedSessions
    case 'upcoming':
      return sessionStore.upcomingSessions
    case 'cancelled':
      return sessionStore.cancelledSessions
    default:
      return sessionStore.sessions
  }
})

const getStatusClass = (status) => {
  switch (status?.toLowerCase()) {
    case 'upcoming':
      return 'bg-warning bg-opacity-25 text-dark' // Soft orange
    case 'completed':
      return 'bg-sb-primary text-white' // Solid Green
    case 'cancelled':
      return 'bg-danger text-white' // Solid Red
    default:
      return 'bg-secondary text-white'
  }
}
</script>

<style scoped>
/* Smooth transition for the filter pill buttons */
.transition-all {
  transition: all 0.2s ease-in-out;
}

/* Ensure the table looks completely clean, removing default Bootstrap borders on the sides */
.table > :not(caption) > * > * {
  border-bottom-width: 0px;
}

.session-row {
  position: relative;
}
</style>
```

--- src/views/TestApi.vue ---
```
<template>
  <div style="padding: 40px;">
    <h1>Test API Connection</h1>

    <input v-model="newMessage" placeholder="Enter message" />
    <button @click="sendMessage">Send</button>

    <hr />

    <button @click="loadMessages">Load Messages</button>

    <ul v-if="messages.length">
      <li v-for="msg in messages" :key="msg.id">
        {{ msg.message }}
      </li>
    </ul>

    <p v-else>No messages yet.</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const messages = ref([])
const newMessage = ref('')

const loadMessages = async () => {
  const response = await fetch('http://127.0.0.1:8000/api/test/')
  const data = await response.json()
  messages.value = data
}

const sendMessage = async () => {
  await fetch('http://127.0.0.1:8000/api/test/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      message: newMessage.value
    })
  })

  newMessage.value = ''
  loadMessages()
}
</script>
```

--- src/views/TuteeProfile.vue ---
```
<template>
  <div class="profile-content">
    <div class="mb-4">
      <h2 class="fw-bold text-dark">My Profile</h2>
      <p class="text-muted">Manage your personal information and tutoring preferences.</p>
    </div>

    <div class="card border-sb shadow-sm rounded-4" style="max-width: 800px;">
      <div class="card-body p-4 p-md-5">
        
        <!-- PROFILE HEADER -->
        <div class="d-flex align-items-center mb-4 pb-4 border-bottom border-sb">
          <div
            class="rounded-circle bg-success bg-opacity-10 text-sb-primary d-flex justify-content-center align-items-center fw-bold fs-3 me-4"
            style="width: 80px; height: 80px;"
          >
            {{ initials }}
          </div>

          <div>
            <h5 class="fw-bold mb-1">
              {{ profile.fname }} {{ profile.lname }}
            </h5>
            <p class="text-muted small mb-2">Student / Tutee</p>
            <button class="btn btn-outline-dark btn-sm rounded-3 fw-semibold px-3">
              Update Photo
            </button>
          </div>
        </div>

        <form @submit.prevent="saveProfile">

          <div class="row g-4 mb-4">

            <!-- FIRST NAME -->
            <div class="col-md-4">
              <label class="form-label fw-semibold small text-dark">First Name</label>
              <input
                type="text"
                v-model="profile.fname"
                class="form-control border-sb shadow-none"
              >
            </div>

            <!-- MIDDLE NAME -->
            <div class="col-md-4">
              <label class="form-label fw-semibold small text-dark">Middle Name</label>
              <input
                type="text"
                v-model="profile.mname"
                class="form-control border-sb shadow-none"
              >
            </div>

            <!-- LAST NAME -->
            <div class="col-md-4">
              <label class="form-label fw-semibold small text-dark">Last Name</label>
              <input
                type="text"
                v-model="profile.lname"
                class="form-control border-sb shadow-none"
              >
            </div>

            <!-- EMAIL -->
            <div class="col-md-6">
              <label class="form-label fw-semibold small text-dark">University Email</label>
              <input
                type="email"
                v-model="profile.email"
                class="form-control border-sb shadow-none bg-light text-muted"
                disabled
              >
              <div class="form-text small">
                Email cannot be changed after registration.
              </div>
            </div>

            <!-- COURSE -->
            <div class="col-md-6">
              <label class="form-label fw-semibold">Course</label>

              <select v-model="profile.course" class="form-select">

                <option value="">Select Course</option>

                <option
                  v-for="course in courses"
                  :key="course.course_code"
                  :value="course.course_code"
                >
                  {{ course.course_name }}
                </option>

              </select>
            </div>

            <div class="col-md-6">
              <label class="form-label fw-semibold">Preferred Subjects</label>

              <select
                v-model="profile.subjects"
                class="form-select"
                multiple
              >

                <option
                  v-for="subject in subjects"
                  :key="subject.subject_code"
                  :value="subject.subject_code"
                >
                  {{ subject.subject_name }}
                </option>

              </select>

            </div>

            <!-- YEAR LEVEL -->
            <div class="col-md-6">
              <label class="form-label fw-semibold">Year Level</label>

              <select v-model="profile.year_level" class="form-select">

                <option value="">Select Year Level</option>

                <option
                  v-for="level in yearLevels"
                  :key="level.value"
                  :value="level.value"
                >
                  {{ level.label }}
                </option>

              </select>
            </div>

            <!-- BIO -->
            <div class="col-12">
              <label class="form-label fw-semibold small text-dark">
                Bio (About Me)
              </label>

              <textarea
                v-model="profile.bio"
                class="form-control border-sb shadow-none"
                rows="4"
                placeholder="Tell tutors a bit about your learning style or what you usually need help with..."
              ></textarea>
            </div>

          </div>

          <div class="text-end mt-2">
            <button
              type="submit"
              class="btn bg-sb-primary text-white px-5 py-2 rounded-3 fw-semibold shadow-sm"
            >
              Save Changes
            </button>
          </div>

        </form>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api/api'

const profile = ref({
  fname: '',
  lname: '',
  email: '',
  course: '',
  year_level: '',
  bio: ''
})

const courses = ref([])

/*
-----------------------------
LOAD PROFILE DATA
-----------------------------
*/
const loadProfile = async () => {
  try {
    const res = await api.get('/tutee/profile/')
    profile.value = res.data
  } catch (err) {
    console.error("Failed to load profile", err)
  }
}

const yearLevels = [

  { label: "Grade 1", value: 1 },
  { label: "Grade 2", value: 2 },
  { label: "Grade 3", value: 3 },
  { label: "Grade 4", value: 4 },
  { label: "Grade 5", value: 5 },
  { label: "Grade 6", value: 6 },
  { label: "Grade 7", value: 7 },
  { label: "Grade 8", value: 8 },
  { label: "Grade 9", value: 9 },
  { label: "Grade 10", value: 10 },
  { label: "Grade 11", value: 11 },
  { label: "Grade 12", value: 12 },

  { label: "1st Year College", value: 13 },
  { label: "2nd Year College", value: 14 },
  { label: "3rd Year College", value: 15 },
  { label: "4th Year College", value: 16 }

]


const subjects = ref([])

const loadSubjects = async () => {

  const res = await api.get('subjects/')

  subjects.value = res.data

}
/*
-----------------------------
LOAD COURSES FOR DROPDOWN
-----------------------------
*/
const loadCourses = async () => {
  try {

    const res = await api.get('courses/')

    console.log("Courses loaded:", res.data)

    courses.value = res.data

  } catch (err) {
    console.error("Failed to load courses", err)
  }
}

import { computed } from 'vue'

const initials = computed(() => {

  const first = profile.value?.fname?.charAt(0) || ''
  const last = profile.value?.lname?.charAt(0) || ''

  return (first + last).toUpperCase()

})
/*
-----------------------------
SAVE PROFILE
-----------------------------
*/
const saveProfile = async () => {
  try {

    await api.put('/tutee/profile/update/', profile.value)

    alert("Profile updated successfully")

  } catch (err) {
    console.error(err)
    alert("Failed to update profile")
  }
}

onMounted(() => {
  loadProfile()
  loadCourses()
  loadSubjects()
})
</script>
```

--- src/views/TutorDashboard.vue ---
```
<template>
  <div class="p-4">

    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="fw-bold text-dark">Teaching Hub</h2>

      <router-link
        to="/tch-availability"
        class="btn bg-sb-primary text-white rounded-3 px-4 fw-semibold shadow-sm"
      >
        Set Schedule
      </router-link>
    </div>


    <!-- Stats Cards -->
    <div class="row g-4 mb-4">

      <div class="col-md-4">
        <div class="card border-sb rounded-4 p-4 shadow-sm h-100">
          <p class="text-muted small fw-bold mb-2">TOTAL SESSIONS</p>
          <h2 class="fw-bold mb-0 text-dark">{{ totalSessions }}</h2>
        </div>
      </div>

      <div class="col-md-4">
        <div class="card border-sb rounded-4 p-4 shadow-sm h-100">
          <p class="text-muted small fw-bold mb-2">AVG RATING</p>
          <h2 class="fw-bold mb-0 text-dark d-flex align-items-center">
            {{ avgRating }}
            <i class="bi bi-star-fill text-warning fs-4 ms-2"></i>
          </h2>
        </div>
      </div>

      <div class="col-md-4">
        <div
          class="card border-0 rounded-4 p-4 shadow-sm h-100"
          style="background-color: var(--sb-dark);"
        >
          <p class="text-white-50 small fw-bold mb-2">EARNINGS</p>
          <h2 class="fw-bold text-white mb-0">â‚±{{ earnings }}</h2>
        </div>
      </div>

    </div>


    <!-- Upcoming Bookings -->
    <div class="card border-sb rounded-4 shadow-sm">

      <div class="card-body p-4">

        <h6 class="fw-bold text-dark mb-4">Upcoming Bookings</h6>

        <!-- No bookings -->
        <div v-if="upcomingBookings.length === 0" class="text-muted text-center py-4">
          No upcoming sessions yet.
        </div>

        <!-- Table -->
        <div v-else class="table-responsive">

          <table class="table align-middle mb-0">

            <thead>
              <tr class="small fw-bold text-muted">
                <th class="border-bottom-0 pb-3">STUDENT</th>
                <th class="border-bottom-0 pb-3">SUBJECT</th>
                <th class="border-bottom-0 pb-3">DATE</th>
                <th class="border-bottom-0 pb-3">STATUS</th>
                <th class="border-bottom-0 pb-3"></th>
              </tr>
            </thead>

            <tbody>

              <tr
                v-for="booking in upcomingBookings"
                :key="booking.id"
                style="border-top: 1px solid var(--sb-card-border);"
              >

                <!-- Student -->
                <td class="py-3 text-dark">
                  {{ booking.student }}
                </td>

                <!-- Subject -->
                <td class="py-3">
                  <span class="badge bg-light text-dark border border-sb px-2 py-1">
                    {{ booking.subject || 'General' }}
                  </span>
                </td>

                <!-- Date -->
                <td class="py-3 text-dark">
                  {{ new Date(booking.date).toLocaleDateString() }}
                </td>

                <!-- Status -->
                <td class="py-3">

                  <span
                    class="badge px-3 py-1 rounded-pill"
                    :class="{
                      'bg-warning bg-opacity-10 text-warning border border-warning':
                        booking.status === 'Pending',

                      'bg-success bg-opacity-10 text-success border border-success':
                        booking.status === 'Confirmed',

                      'bg-secondary bg-opacity-10 text-secondary border border-secondary':
                        booking.status === 'Completed'
                    }"
                  >
                    {{ booking.status }}
                  </span>

                </td>

                <!-- Action -->
                <td class="py-3 text-end">

                  <button
                    class="btn btn-success btn-sm"
                    @click="goToBookingDetails(booking.id)"
                  >
                    View Details
                  </button>

                </td>

              </tr>

            </tbody>

          </table>

        </div>

      </div>

    </div>

  </div>
</template>


<script setup>
import { useRouter } from 'vue-router'
import { ref, onMounted } from 'vue'
import api from '@/services/api/api'

const router = useRouter()

const totalSessions = ref(0)
const avgRating = ref(0)
const earnings = ref(0)
const upcomingBookings = ref([])




const goToBookingDetails = (id) => {
  router.push({
    name: 'booking-details',
    params: { id }
  })
}

const loadTutorDashboard = async () => {

  try {

    const response = await api.get('tutor-dashboard/')

    totalSessions.value = response.data.total_sessions
    avgRating.value = response.data.rating_average
    earnings.value = response.data.total_earnings

    // âœ… just assign what backend sends
    upcomingBookings.value = response.data.upcoming_bookings || []

  } catch (error) {

    console.error("Failed to load tutor dashboard:", error)

  }

}

onMounted(loadTutorDashboard)
</script>
```

--- src/views/TutorDetails.vue ---
Summary only because this file exceeds 300 lines (321 lines).

Vue single-file component for the tutee's tutor-booking detail screen.
- Renders tutor profile info, subject badges, hourly rate, bio, and a week-view schedule table.
- Reads oute.params.id as the tutor id.
- Uses selectedSessions and ookedSessionDetails Pinia stores.
- Calls GET tutors/:id/ to load tutor details.
- Calls GET tutors/:id/availability/?date=YYYY-MM-DD to load bookable slots for the selected date.
- Lets the user pick a date and select one or more slots.
- Enforces booking constraints in the client: slots must be on the same date and must form consecutive one-hour blocks.
- On booking, stores the chosen slots/tutor metadata in Pinia and routes to /payment-tutee/:tutorId.
- Includes scoped styles for slot states (vailable, ooked, selected) and card media.

--- src/views/TutorPaymentScreen.vue ---
```
<template>
  <div class="p-4">
    <h2 class="fw-bold mb-4">Payment Verification</h2>

    <div class="card border-sb rounded-4 shadow-sm overflow-hidden">
      <div class="table-responsive">
        <table class="table table-hover align-middle mb-0">
          <thead class="bg-light">
            <tr>
              <th class="ps-4">Tutee</th>
              <th>Amount</th>
              <th>Status</th>
              <th class="text-end pe-4">Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="pay in payments" :key="pay.id">
              <td class="ps-4 fw-semibold">{{ pay.name }}</td>
              <td class="fw-bold">â‚±{{ pay.amount }}</td>
              <td><span class="badge bg-warning-subtle text-warning border border-warning">Pending</span></td>
              <td class="text-end pe-4">
                <button @click="verify(pay.id)" class="btn btn-sm bg-sb-primary text-white px-3 fw-bold">Verify Paid</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
const payments = ref([
  { id: 1, name: 'Lia Salinas', amount: 250 },
  { id: 2, name: 'Reggie Cruz', amount: 500 }
])
const verify = (id) => {
  payments.value = payments.value.filter(p => p.id !== id)
  alert('Payment verified! Booking finalized.')
}
</script>
```

--- src/views/TutorPreferenceSetup.vue ---
```
<template>
  <div class="min-vh-100 bg-light py-5">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-md-7 col-lg-6">
          <div class="card border-0 shadow-sm rounded-4">
            <div class="card-body p-4 p-md-5">
              <div class="text-center mb-4">
                <h3 class="fw-bold text-dark">Tutor Profile Setup</h3>
                <p class="text-muted">Set your teaching preferences to start matching.</p>
              </div>

              <form @submit.prevent="handleCompleteSetup">
                <div class="mb-4">
                  <label class="form-label fw-bold small text-muted">TEACHING LEVEL</label>
                  <select v-model="form.teaching_level" class="form-select border-sb shadow-none" required>
                    <option value="" disabled>Select level</option>
                    <option value="Elementary">Elementary</option>
                    <option value="High School">High School</option>
                    <option value="College">College</option>
                  </select>
                </div>

                <div class="mb-4">
                  <label class="form-label fw-bold small text-muted d-block">MODALITY</label>
                  <div class="form-check form-switch mb-2">
                    <input class="form-check-input" type="checkbox" v-model="form.can_online" id="on">
                    <label class="form-check-label" for="on">Online Sessions</label>
                  </div>
                  <div class="form-check form-switch">
                    <input class="form-check-input" type="checkbox" v-model="form.can_f2f" id="f2f">
                    <label class="form-check-label" for="f2f">Face-to-Face Sessions</label>
                  </div>
                </div>

                <div class="mb-5">
                  <label class="form-label fw-bold small text-muted">HOURLY RATE (PHP)</label>
                  <input type="number" v-model="form.hourly_rate" class="form-control border-sb shadow-none" placeholder="â‚± 0.00" required>
                </div>

                <button type="submit" class="btn bg-sb-primary text-white w-100 py-3 rounded-3 fw-bold shadow-sm">
                  Complete Profile
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useProfileStore } from '@/stores/profile'
import api from '@/services/api/api'

const router = useRouter()
const profileStore = useProfileStore()

const form = ref({
  teaching_level: '',
  can_online: true,
  can_f2f: false,
  hourly_rate: null
})


/* LOAD EXISTING TUTOR DATA */
onMounted(async () => {

  try {

    const response = await api.get('/tutor-dashboard/')

    const tutor = response.data

    form.value.teaching_level = tutor.teaching_level
    form.value.can_online = tutor.can_online
    form.value.can_f2f = tutor.can_f2f
    form.value.hourly_rate = tutor.hourly_rate

  } catch (error) {

    console.log("New tutor setup")

  }

})


/* SUBMIT PROFILE SETUP */
const handleCompleteSetup = async () => {

  try {

    await api.post('/tutor/setup/', form.value)

    // update profile guard state
    profileStore.profileCompleted = true

    router.push({ name: 'tch-dashboard' })

  } catch (error) {

    console.error("Failed to save tutor profile", error)
    alert("Could not save tutor profile.")

  }

}
</script>
```

--- src/views/TutorProfile.vue ---
```
<template>
<div class="profile-content">

  <div class="mb-4">
    <h2 class="fw-bold text-dark">My Profile</h2>
    <p class="text-muted">Manage your tutoring information.</p>
  </div>

  <div class="card border-sb shadow-sm rounded-4">
  <div class="card-body p-4 p-md-5">

  <!-- Avatar -->
  <div class="d-flex align-items-center mb-4 pb-4 border-bottom">
    <div
      class="rounded-circle bg-success bg-opacity-10 d-flex justify-content-center align-items-center fw-bold fs-3 me-4"
      style="width:80px;height:80px"
    >
      {{ initials }}
    </div>

    <div>
      <h5 class="fw-bold mb-1">{{ profile.fullName }}</h5>
      <p class="text-muted small mb-2">Tutor</p>
    </div>
  </div>

<form @submit.prevent="saveProfile">

<div class="row g-4">

<!-- NAME -->
<div class="col-md-6">
<label class="form-label fw-semibold small">Full Name</label>
<input v-model="profile.fullName" class="form-control">
</div>

<!-- EMAIL -->
<div class="col-md-6">
<label class="form-label fw-semibold small">Email</label>
<input :value="profile.email" disabled class="form-control bg-light">
</div>

<!-- COURSE -->
<div class="col-md-6">
<label class="form-label fw-semibold small">Course</label>

<select v-model="profile.course" class="form-select">

<option value="">Select Course</option>

<option
  v-for="c in courses"
  :key="c.course_code"
  :value="c.course_code"
>
  {{ c.course_code }} - {{ c.course_name }}
</option>

</select>
</div>

<!-- YEAR LEVEL -->
<div class="col-md-6">
<label class="form-label fw-semibold small">Year Level</label>

<select v-model.number="profile.year_level" class="form-select">

<option value="">Select Level</option>

<option
  v-for="y in yearLevels"
  :key="y.value"
  :value="y.value"
>
  {{ y.label }}
</option>

</select>
</div>

<!-- HOURLY RATE -->
<div class="col-md-6">
<label class="form-label fw-semibold small">Hourly Rate</label>
<input type="number" v-model="profile.hourly_rate" class="form-control">
</div>

<!-- TEACHING LEVEL -->
<div class="col-md-6">
<label class="form-label fw-semibold small">Teaching Level</label>
<input v-model="profile.teaching_level" class="form-control">
</div>

<!-- SESSION MODE -->
<div class="col-md-6">

<label class="form-label fw-semibold small">Session Mode</label>

<div class="form-check">
<input type="checkbox" v-model="profile.can_online" class="form-check-input">
<label class="form-check-label">Online</label>
</div>

<div class="form-check">
<input type="checkbox" v-model="profile.can_f2f" class="form-check-input">
<label class="form-check-label">Face-to-Face</label>
</div>

</div>

<!-- SUBJECTS -->
<div class="col-12">

<label class="form-label fw-semibold small">Subjects</label>

<div class="d-flex flex-wrap gap-2 mb-3">

<span
v-for="s in profile.subjects"
:key="s.subject_code"
class="badge bg-sb-primary px-3 py-2"
>

{{ s.subject_name }}

<button
type="button"
class="btn-close btn-close-white ms-2"
style="font-size:10px"
@click="removeSubject(s.subject_code)"
></button>

</span>

</div>

<div class="d-flex gap-2">

<select v-model="newSubject" class="form-select">

<option value="">Select subject</option>

<option
v-for="s in allSubjects"
:key="s.subject_code"
:value="s.subject_code"
>
{{ s.subject_name }}
</option>

</select>

<button
type="button"
class="btn btn-outline-dark"
@click="addSubject"
>
Add
</button>

</div>

</div>

<!-- BIO -->
<div class="col-12">

<label class="form-label fw-semibold small">Bio</label>

<textarea
v-model="profile.bio"
rows="4"
class="form-control"
></textarea>

</div>

</div>

<div class="text-end mt-4">
<button class="btn bg-sb-primary text-white px-4">
Save Changes
</button>
</div>

</form>

</div>
</div>
</div>
</template>

<script setup>

import { ref, computed, onMounted } from 'vue'
import api from '@/services/api/api'

const profile = ref({
  fullName: '',
  email: '',
  course: '',
  year_level: null,
  subjects: [],
  bio: '',
  hourly_rate: '',
  teaching_level: '',
  can_online: true,
  can_f2f: false
})

const courses = ref([])
const allSubjects = ref([])
const newSubject = ref('')

/* YEAR LEVELS */
const yearLevels = [
  { label: "Grade 1", value: 1 },
  { label: "Grade 2", value: 2 },
  { label: "Grade 3", value: 3 },
  { label: "Grade 4", value: 4 },
  { label: "Grade 5", value: 5 },
  { label: "Grade 6", value: 6 },
  { label: "Grade 7", value: 7 },
  { label: "Grade 8", value: 8 },
  { label: "Grade 9", value: 9 },
  { label: "Grade 10", value: 10 },
  { label: "Grade 11", value: 11 },
  { label: "Grade 12", value: 12 },
  { label: "1st Year College", value: 13 },
  { label: "2nd Year College", value: 14 },
  { label: "3rd Year College", value: 15 },
  { label: "4th Year College", value: 16 }
]

/* INITIALS */
const initials = computed(() => {

  if (!profile.value.fullName) return ''

  return profile.value.fullName
    .split(' ')
    .map(n => n[0])
    .join('')

})

/* LOAD PROFILE */
const loadProfile = async () => {

  try {

    const res = await api.get('/tutor/profile/')
    const data = res.data

    profile.value.fullName = `${data.fname} ${data.lname}`
    profile.value.email = data.email
    profile.value.course = data.course
    profile.value.year_level = data.year_level
    profile.value.bio = data.bio

    profile.value.hourly_rate = data.hourly_rate
    profile.value.teaching_level = data.teaching_level
    profile.value.can_online = data.can_online
    profile.value.can_f2f = data.can_f2f

    const subjectRes = await api.get('/tutor/subjects/')
    profile.value.subjects = subjectRes.data

  } catch (err) {

    console.error("Failed to load tutor profile:", err)

  }

}

/* LOAD SUBJECTS */
const loadSubjects = async () => {

  const res = await api.get('/subjects/')
  allSubjects.value = res.data

}

/* LOAD COURSES */
const loadCourses = async () => {

  const res = await api.get('/courses/')
  courses.value = res.data

}

/* ADD SUBJECT */
const addSubject = async () => {

  if (!newSubject.value) return

  await api.post('/tutor/subjects/add/', {
    subject_code: newSubject.value
  })

  newSubject.value = ''
  await loadProfile()

}

/* REMOVE SUBJECT */
const removeSubject = async (code) => {

  await api.delete(`/tutor/subjects/remove/${code}/`)
  await loadProfile()

}

/* SAVE PROFILE */
const saveProfile = async () => {

  const names = profile.value.fullName.split(' ')

  const tuteePayload = {
    fname: names[0],
    lname: names.slice(1).join(' '),
    course: profile.value.course,
    year_level: profile.value.year_level,
    bio: profile.value.bio
  }

  const tutorPayload = {
    hourly_rate: profile.value.hourly_rate,
    teaching_level: profile.value.teaching_level,
    can_online: profile.value.can_online,
    can_f2f: profile.value.can_f2f
  }

  try {

    // Update profile (UserProfile)
    await api.put('/tutee/profile/update/', tuteePayload)

    // Update tutor info (Tutor model)
    await api.put('/tutor/update/', tutorPayload)

    alert("Profile Updated")

  } catch (err) {

    console.error("Profile update failed:", err)

  }

}

/* MOUNT */
onMounted(() => {

  loadProfile()
  loadSubjects()
  loadCourses()

})

</script>
```

--- src/views/TutorRequestedSessions.vue ---
```
<template>
  <div class="p-1">

    <div class="d-flex mb-4 justify-content-between align-items-center">
        <div>
        <h2 class="fw-bold mb-1">Requested Sessions</h2>
        <p class="text-muted mb-0">
            Manage pending session requests.
        </p>
        </div>

        <div style="width: 200px;">
          <input
            type="date"
            v-model="selectedDate"
            class="form-control"
          />
        </div>
    </div>


    <div v-if="filteredSessions.length === 0" class="text-center text-muted py-5">
        No pending session requests found.
    </div>
    
    <div v-else>
    
        <div
          v-for="session in filteredSessions"
          :key="session.id"
          class="card border mb-2 rounded-4 shadow-sm request-card"
        >
          <div class="card-body py-3">

            <div class="row align-items-center text-center text-md-start">

              <div class="col-md">
                <small class="text-muted">Tutee</small>
                <div class="fw-semibold">
                  {{ session.tuteeName }}
                </div>
              </div>

              <div class="col-md">
                <small class="text-muted">Subject</small>
                <div class="fw-semibold">
                  {{ session.subject }}
                </div>
              </div>

              <div class="col-md">
                <small class="text-muted">Topic</small>
                <div class="fw-semibold">
                  {{ session.topic || 'â€”' }}
                </div>
              </div>

              <div class="col-md">
                <small class="text-muted">Date</small>
                <div class="fw-semibold">
                  {{ session.date }}
                </div>
              </div>

              <div class="col-md">
                <small class="text-muted">Start Time</small>
                <div class="fw-semibold">
                  {{ session.startTime }}
                </div>
              </div>

              <div class="col-md">
                <small class="text-muted">End Time</small>
                <div class="fw-semibold">
                  {{ session.endTime }}
                </div>
              </div>

              <!-- Action Column -->
              <div class="col-md text-md-end mt-3 mt-md-0">
                <div class="d-grid gap-2">

                <button
                  class="btn btn-sm btn-success"
                  :disabled="confirmingId === session.id"
                  @click="confirmSession(session.id)"
                >
                  {{ confirmingId === session.id ? "Confirming..." : "Confirm" }}
                </button>

                  <button
                    class="btn btn-sm btn-danger"
                    :disabled="rejectingId === session.id"
                    @click="rejectSession(session.id)"
                  >
                    {{ rejectingId === session.id ? "Rejecting..." : "Reject" }}
                  </button>

                </div>
              </div>

            </div>

          </div>
        </div>
        
    </div>

      

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useSessionsStore } from '@/stores/completedSessions'

const confirmingId = ref(null)
const rejectingId = ref(null)
const sessionStore = useSessionsStore()

const selectedDate = ref('')

onMounted(() => {
  sessionStore.fetchSessions()
})

const confirmSession = async (id) => {
  confirmingId.value = id
  await sessionStore.approveSession(id)
  confirmingId.value = null
}

const rejectSession = async (id) => {
  rejectingId.value = id
  await sessionStore.rejectSession(id)
  rejectingId.value = null
}

const filteredSessions = computed(() => {
  let sessions = sessionStore.requestedSessions

  if (selectedDate.value) {
    sessions = sessions.filter(session =>
      session.date === selectedDate.value
    )
  }

  return sessions
})
</script>

<style scoped>
.session-card {
  cursor: pointer;
  transition: all 0.2s ease;
}

.session-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 18px rgba(0,0,0,0.08);
}
</style>
```

--- src/views/TutorSchedule.vue ---
Summary only because this file exceeds 300 lines (310 lines).

Vue single-file component for a tutor's recurring weekly availability template.
- Displays weekly slots grouped by day in a table.
- Uses the 	utorSched Pinia store for loading, creating, and deleting availability entries.
- Supports selecting a slot for deletion.
- Provides a modal form to add slots by day plus start/end time.
- Expands a time range into one-hour slots and submits each missing slot individually through the store.
- Validates required fields, end-after-start, and full-hour boundaries before saving.
- Refreshes availability after add/delete operations.
- Includes scoped modal and slot styling.

Binary/non-text files present in the project and not expanded in this section:
- backend/media/profile_pics/sql.jpg
- backend/media/profile_pics/sql_5tVye1Y.jpg
- public/favicon.ico
- src/assets/hero.png
- src/assets/logo.svg
- src/views/drive-download-20260305T061413Z-3-001.zip

## 5. Database / Data Models

Model declarations and migration files:

--- backend/studybuddy/models.py ---
```
from django.db import models
from django.contrib.auth.models import User ### allows the use of auth user model for authentication and user management


# Create your models here.

class Strand(models.Model):

    strand_code = models.CharField(max_length=10, primary_key=True)
    strand_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.strand_code} - {self.strand_name}"
    
class Course(models.Model):

    course_code = models.CharField(max_length=20, primary_key=True)
    course_name = models.CharField(max_length=100)

    strand = models.ForeignKey(
        Strand,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.course_code} - {self.course_name}"


class PartnerInstitution(models.Model):
    institution_name = models.CharField(max_length=255)
    school_email_domain = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    contact_person = models.CharField(max_length=255, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['institution_name']

    def __str__(self):
        return f"{self.institution_name} ({self.school_email_domain})"



class UserProfile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    fname = models.CharField(max_length=100)
    mname = models.CharField(max_length=100, blank=True)
    lname = models.CharField(max_length=100)

    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    year_level = models.IntegerField(null=True, blank=True)

    bio = models.TextField(blank=True, null=True)

    profile_completed = models.BooleanField(default=False)

    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        blank=True,
        null=True
    )

    institution = models.ForeignKey(
        PartnerInstitution,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    is_domain_exempt = models.BooleanField(default=False)

    ROLE_CHOICES = [
        ('Tutee', 'Tutee'),
        ('Tutor', 'Tutor'),
        ('Admin', 'Admin'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.fname} {self.lname}"
    
#TUTOR TABLE
class Tutor(models.Model):

    profile = models.OneToOneField(
        UserProfile,
        on_delete=models.CASCADE,
        primary_key=True
    )

    # Tutor setup fields (filled later)
    teaching_level = models.CharField(max_length=100, null=True, blank=True)

    can_online = models.BooleanField(default=True)
    can_f2f = models.BooleanField(default=False)

    rating_average = models.FloatField(default=0)

    hourly_rate = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True
    )

    total_sessions = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Tutor: {self.profile.fname} {self.profile.lname}"

#Subjects Table 
class Subjects(models.Model):
    subject_code = models.CharField(max_length=20, primary_key=True)
    subject_name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.subject_code} - {self.subject_name}"
    
#Tutor Subjects Table

class TutorSubjects(models.Model):
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subjects, on_delete=models.CASCADE)
    
    expertise_level = models.IntegerField()  # e.g., Beginner, Intermediate, Advanced

    def __str__(self):
        return f"{self.tutor.profile.fname} {self.tutor.profile.lname} - {self.subject.subject_code}"


class TutorAvailability(models.Model):

    DAY_CHOICES = [
        ('Mon', 'Monday'),
        ('Tue', 'Tuesday'),
        ('Wed', 'Wednesday'),
        ('Thu', 'Thursday'),
        ('Fri', 'Friday'),
        ('Sat', 'Saturday'),
        ('Sun', 'Sunday'),
    ]

    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    day = models.CharField(max_length=3, choices=DAY_CHOICES)
    time_slot = models.TimeField()
    is_active = models.BooleanField(default=False)   # tutor toggles this
    is_booked = models.BooleanField(default=False)   # system controls this

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('tutor', 'day', 'time_slot')

    def __str__(self):
        return f"{self.tutor.profile.fname} - {self.day} {self.time_slot}"
    
class Booking(models.Model):

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    student = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="student_bookings"
    )

    tutor = models.ForeignKey(
        Tutor,
        on_delete=models.CASCADE,
        related_name="tutor_bookings"
    )

    availability = models.ForeignKey(
        TutorAvailability,
        on_delete=models.CASCADE,
        related_name="bookings"
    )

    session_date = models.DateField()

    session_mode = models.CharField(
        max_length=10,
        choices=[('Online', 'Online'), ('F2F', 'Face-to-Face')]
    )

    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default="Pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('availability', 'session_date')

class PaymentMethod(models.Model):

    METHOD_CODES = [
        ('CASH', 'Cash'),
        ('GCASH', 'GCash'),
        ('BANK', 'Bank Transfer'),
    ]

    method_id = models.AutoField(primary_key=True)

    code = models.CharField(             
        max_length=20,
        choices=METHOD_CODES,
        unique=True,
    )

    method_name = models.CharField(max_length=50)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.method_name} ({self.code})"

class Payment(models.Model):

    PAYMENT_STATUS = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Failed', 'Failed'),
        ('Refunded', 'Refunded'),
    ]

    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        related_name="payment"
    )

    method = models.ForeignKey(        # âœ… FK to PAYMENT_METHODS
        PaymentMethod,
        on_delete=models.SET_NULL,
        null=True,
        related_name="payments"
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    payment_status = models.CharField(
        max_length=10,
        choices=PAYMENT_STATUS,
        default='Pending'
    )

    transaction_reference = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    paid_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for Booking {self.booking.id} - {self.payment_status}"
    
class Rating(models.Model):

    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        related_name="rating"
    )

    student = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE
    )

    tutor = models.ForeignKey(
        Tutor,
        on_delete=models.CASCADE,
        related_name="ratings"
    )

    rating_score = models.IntegerField()  # 1â€“5

    comment = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.rating_score} â­ for {self.tutor.profile.fname}"
    
class Preference(models.Model):

    MODE_CHOICES = [
        ('Online', 'Online'),
        ('F2F', 'Face-to-Face'),
    ]

    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE)

    subjects = models.ManyToManyField(Subjects)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Preferences for {self.user.fname}"
```

--- backend/studybuddy/migrations/__init__.py ---
```
(empty file)
```

--- backend/studybuddy/migrations/0001_initial.py ---
```
# Generated by Django 6.0.2 on 2026-02-23 14:05

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='user',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('password', models.CharField(max_length=255)),
                ('role', models.CharField(max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
```

--- backend/studybuddy/migrations/0002_userprofile_delete_user.py ---
```
# Generated by Django 6.0.2 on 2026-02-23 16:09

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fname', models.CharField(max_length=100)),
                ('mname', models.CharField(blank=True, max_length=100)),
                ('lname', models.CharField(max_length=100)),
                ('course', models.CharField(blank=True, max_length=100)),
                ('year_level', models.IntegerField(blank=True, null=True)),
                ('role', models.CharField(max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.DeleteModel(
            name='user',
        ),
    ]
```

--- backend/studybuddy/migrations/0003_tutor_alter_userprofile_role.py ---
```
# Generated by Django 6.0.2 on 2026-02-24 21:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0002_userprofile_delete_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tutor',
            fields=[
                ('profile', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='studybuddy.userprofile')),
                ('teaching_level', models.CharField(max_length=100)),
                ('can_online', models.BooleanField(default=True)),
                ('can_f2f', models.BooleanField(default=False)),
                ('rating_average', models.FloatField(default=0)),
                ('hourly_rate', models.DecimalField(decimal_places=2, max_digits=8)),
                ('total_sessions', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='role',
            field=models.CharField(choices=[('Tutee', 'Tutee'), ('Tutor', 'Tutor'), ('Admin', 'Admin')], max_length=20),
        ),
    ]
```

--- backend/studybuddy/migrations/0004_subjects.py ---
```
# Generated by Django 6.0.2 on 2026-02-24 21:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0003_tutor_alter_userprofile_role'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subjects',
            fields=[
                ('subject_code', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('subject_name', models.CharField(max_length=100)),
                ('department', models.CharField(max_length=100)),
            ],
        ),
    ]
```

--- backend/studybuddy/migrations/0005_tutorsubjects.py ---
```
# Generated by Django 6.0.2 on 2026-02-25 14:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0004_subjects'),
    ]

    operations = [
        migrations.CreateModel(
            name='TutorSubjects',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('expertise_level', models.IntegerField()),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='studybuddy.subjects')),
                ('tutor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='studybuddy.tutor')),
            ],
        ),
    ]
```

--- backend/studybuddy/migrations/0006_tutoravailability.py ---
```
# Generated by Django 6.0.2 on 2026-02-25 14:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0005_tutorsubjects'),
    ]

    operations = [
        migrations.CreateModel(
            name='TutorAvailability',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day_of_week', models.CharField(choices=[('Mon', 'Monday'), ('Tue', 'Tuesday'), ('Wed', 'Wednesday'), ('Thu', 'Thursday'), ('Fri', 'Friday'), ('Sat', 'Saturday'), ('Sun', 'Sunday')], max_length=3)),
                ('time_slot', models.TimeField()),
                ('is_active', models.BooleanField(default=False)),
                ('is_booked', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('tutor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='availabilities', to='studybuddy.tutor')),
            ],
            options={
                'unique_together': {('tutor', 'day_of_week', 'time_slot')},
            },
        ),
    ]
```

--- backend/studybuddy/migrations/0007_booking.py ---
```
# Generated by Django 6.0.2 on 2026-02-25 15:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0006_tutoravailability'),
    ]

    operations = [
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_date', models.DateField()),
                ('session_mode', models.CharField(choices=[('Online', 'Online'), ('F2F', 'Face-to-Face')], max_length=10)),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Confirmed', 'Confirmed'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled')], default='Pending', max_length=15)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('availability', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='studybuddy.tutoravailability')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_bookings', to='studybuddy.userprofile')),
                ('tutor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tutor_bookings', to='studybuddy.tutor')),
            ],
        ),
    ]
```

--- backend/studybuddy/migrations/0008_alter_booking_availability_payment.py ---
```
# Generated by Django 6.0.2 on 2026-02-25 15:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0007_booking'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='availability',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='studybuddy.tutoravailability'),
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('payment_status', models.CharField(choices=[('Pending', 'Pending'), ('Paid', 'Paid'), ('Failed', 'Failed'), ('Refunded', 'Refunded')], default='Pending', max_length=10)),
                ('transaction_reference', models.CharField(blank=True, max_length=100, null=True)),
                ('paid_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('booking', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='payment', to='studybuddy.booking')),
            ],
        ),
    ]
```

--- backend/studybuddy/migrations/0009_rating.py ---
```
# Generated by Django 6.0.2 on 2026-02-25 18:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0008_alter_booking_availability_payment'),
    ]

    operations = [
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating_score', models.IntegerField()),
                ('comment', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('booking', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='rating', to='studybuddy.booking')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='studybuddy.userprofile')),
                ('tutor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ratings', to='studybuddy.tutor')),
            ],
        ),
    ]
```

--- backend/studybuddy/migrations/0010_userprofile_bio_userprofile_profile_picture.py ---
```
# Generated by Django 6.0.2 on 2026-02-27 19:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0009_rating'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='bio',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='profile_picture',
            field=models.ImageField(blank=True, null=True, upload_to='profile_pics/'),
        ),
    ]
```

--- backend/studybuddy/migrations/0011_tutoravailability_day.py ---
```
# Generated by Django 6.0.2 on 2026-02-27 20:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0010_userprofile_bio_userprofile_profile_picture'),
    ]

    operations = [
        migrations.AddField(
            model_name='tutoravailability',
            name='day',
            field=models.CharField(choices=[('Mon', 'Monday'), ('Tue', 'Tuesday'), ('Wed', 'Wednesday'), ('Thu', 'Thursday'), ('Fri', 'Friday'), ('Sat', 'Saturday'), ('Sun', 'Sunday')], default='Mon', max_length=3),
            preserve_default=False,
        ),
    ]
```

--- backend/studybuddy/migrations/0012_alter_tutoravailability_tutor.py ---
```
# Generated by Django 6.0.2 on 2026-02-27 20:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0011_tutoravailability_day'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tutoravailability',
            name='tutor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='studybuddy.tutor'),
        ),
    ]
```

--- backend/studybuddy/migrations/0013_alter_tutoravailability_unique_together_and_more.py ---
```
# Generated by Django 6.0.2 on 2026-02-28 20:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0012_alter_tutoravailability_tutor'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='tutoravailability',
            unique_together={('tutor', 'day', 'time_slot')},
        ),
        migrations.AlterField(
            model_name='booking',
            name='availability',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to='studybuddy.tutoravailability'),
        ),
        migrations.AlterUniqueTogether(
            name='booking',
            unique_together={('availability', 'session_date')},
        ),
        migrations.RemoveField(
            model_name='tutoravailability',
            name='day_of_week',
        ),
    ]
```

--- backend/studybuddy/migrations/0014_paymentmethod_payment_method.py ---
```
# Generated by Django 6.0.2 on 2026-03-03 13:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0013_alter_tutoravailability_unique_together_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentMethod',
            fields=[
                ('method_id', models.AutoField(primary_key=True, serialize=False)),
                ('method_name', models.CharField(max_length=50)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AddField(
            model_name='payment',
            name='method',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='payments', to='studybuddy.paymentmethod'),
        ),
    ]
```

--- backend/studybuddy/migrations/0015_paymentmethod_code.py ---
```
# Generated by Django 6.0.2 on 2026-03-03 13:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0014_paymentmethod_payment_method'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentmethod',
            name='code',
            field=models.CharField(blank=True, choices=[('CASH', 'Cash'), ('GCASH', 'GCash'), ('BANK', 'Bank Transfer')], max_length=20, null=True, unique=True),
        ),
    ]
```

--- backend/studybuddy/migrations/0016_alter_paymentmethod_code.py ---
```
# Generated by Django 6.0.2 on 2026-03-03 13:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0015_paymentmethod_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymentmethod',
            name='code',
            field=models.CharField(choices=[('CASH', 'Cash'), ('GCASH', 'GCash'), ('BANK', 'Bank Transfer')], max_length=20, unique=True),
        ),
    ]
```

--- backend/studybuddy/migrations/0017_userprofile_profile_completed.py ---
```
# Generated by Django 6.0.2 on 2026-03-04 08:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0016_alter_paymentmethod_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='profile_completed',
            field=models.BooleanField(default=False),
        ),
    ]
```

--- backend/studybuddy/migrations/0018_preference.py ---
```
# Generated by Django 6.0.2 on 2026-03-04 09:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0017_userprofile_profile_completed'),
    ]

    operations = [
        migrations.CreateModel(
            name='Preference',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('preferred_mode', models.CharField(choices=[('Online', 'Online'), ('F2F', 'Face-to-Face')], max_length=10)),
                ('hourly_budget', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('subjects', models.ManyToManyField(to='studybuddy.subjects')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='studybuddy.userprofile')),
            ],
        ),
    ]
```

--- backend/studybuddy/migrations/0019_alter_tutor_hourly_rate_alter_tutor_teaching_level.py ---
```
# Generated by Django 6.0.2 on 2026-03-04 10:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0018_preference'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tutor',
            name='hourly_rate',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True),
        ),
        migrations.AlterField(
            model_name='tutor',
            name='teaching_level',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
```

--- backend/studybuddy/migrations/0020_course_strand_alter_userprofile_course_course_strand.py ---
```
# Generated by Django 6.0.2 on 2026-03-04 15:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0019_alter_tutor_hourly_rate_alter_tutor_teaching_level'),
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('course_code', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('course_name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Strand',
            fields=[
                ('strand_code', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('strand_name', models.CharField(max_length=100)),
            ],
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='course',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='studybuddy.course'),
        ),
        migrations.AddField(
            model_name='course',
            name='strand',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='studybuddy.strand'),
        ),
    ]
```

--- backend/studybuddy/migrations/0021_remove_preference_hourly_budget_and_more.py ---
```
# Generated by Django 6.0.2 on 2026-03-05 09:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0020_course_strand_alter_userprofile_course_course_strand'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='preference',
            name='hourly_budget',
        ),
        migrations.RemoveField(
            model_name='preference',
            name='preferred_mode',
        ),
    ]
```

--- backend/studybuddy/migrations/0022_partnerinstitution_userprofile_institution_and_more.py ---
```
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0021_remove_preference_hourly_budget_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='PartnerInstitution',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('institution_name', models.CharField(max_length=255)),
                ('school_email_domain', models.CharField(max_length=255, unique=True)),
                ('is_active', models.BooleanField(default=True)),
                ('contact_person', models.CharField(blank=True, max_length=255)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['institution_name'],
            },
        ),
        migrations.AddField(
            model_name='userprofile',
            name='institution',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='studybuddy.partnerinstitution'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='is_domain_exempt',
            field=models.BooleanField(default=False),
        ),
    ]
```

--- backend/testapp/migrations/__init__.py ---
```
(empty file)
```

--- backend/testapp/migrations/0001_initial.py ---
```
# Generated by Django 6.0.2 on 2026-02-19 15:58

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TestMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
```

## 6. API / Interface Contract

No OpenAPI/Swagger/Postman contract was found. The following interface list is inferred from the router and Django URL/view modules.

Frontend routes (`src/router/index.js`)
- / -> LandingPage
- /login -> Login
- /register -> Register
- /preferencesetup -> PreferenceSetup (auth)
- /dashboard -> Dashboard (auth, role=Tutee)
- /tutee-profile -> TuteeProfile (auth, role=Tutee)
- /tutors -> FindTutors (auth, role=Tutee)
- /book -> InitialBooking (auth, role=Tutee)
- /tutor/:id -> TutorDetails (auth, role=Tutee)
- /payment-tutee/:tutorId -> PaymentScreenTutee (auth, role=Tutee)
- /tutor-setup -> TutorPreferenceSetup (auth)
- /tch-dashboard -> TutorDashboard (auth, role=Tutor)
- /tutor-profile -> TutorProfile (auth, role=Tutor)
- /tch-availability -> TutorSchedule (auth, role=Tutor)
- /tch-payments -> TutorPaymentScreen (auth, role=Tutor)
- /tch-requestedSessions -> TutorRequestedSessions (auth, role=Tutor)
- /booking-details/:id -> BookingDetails (auth, role=Tutor)
- /schedule -> Schedule (auth)
- /reports -> SessionsReports (auth)
- /profile -> Profile (auth)

Backend base routing
- `backend/backend/urls.py` mounts Django admin at `/admin/` and the studybuddy API at `/api/`.

Backend API endpoints (`backend/studybuddy/urls.py` + `backend/studybuddy/views.py`)
- GET `/api/partner-institutions/` -> list active partner institutions.
- POST `/api/register/` -> register a user. Inputs inferred: `email`, `password`, `fname`, `mname`, `lname`, `role`, `institution_id`. Returns success/error JSON.
- POST `/api/login/` -> log in with `email`, `password`. Returns JWT token payload plus user/profile metadata.
- POST `/api/token/refresh/` -> SimpleJWT access-token refresh.
- GET `/api/profile/status/` -> authenticated profile-completion status.
- POST `/api/preferences/` -> authenticated preference save. Inputs inferred: `subjects`.
- GET `/api/dashboard/` -> authenticated tutee dashboard payload.
- GET `/api/tutee/profile/` -> authenticated tutee profile payload.
- PUT or POST? `/api/tutee/profile/update/` -> wired to `update_tutee_profile`; the view itself is annotated `PUT`. Inputs inferred: `fname`, `mname`, `lname`, `course`, `year_level`, `bio`, `subjects`.
- GET `/api/tutor/profile/` -> authenticated tutor profile payload.
- GET `/api/tutor/subjects/` -> authenticated tutor subject list.
- POST `/api/tutor/subjects/add/` -> add tutor subject. Inputs inferred: `subject_code`.
- DELETE `/api/tutor/subjects/remove/<subject_code>/` -> remove tutor subject.
- GET `/api/search-tutors/?subject=<code>` -> serialized tutor search results.
- GET `/api/subjects/` -> subject list.
- GET `/api/courses/` -> course list.
- GET `/api/tutor-dashboard/` -> authenticated tutor dashboard payload.
- GET `/api/tutors/<profile_id>/` -> tutor detail payload.
- GET `/api/tutors/<tutor_id>/availability/?date=YYYY-MM-DD` -> tutor availability for booking.
- POST `/api/profile/setup/` -> authenticated profile setup. Inputs inferred: `course`, `year_level`, `bio`.
- PUT or POST? `/api/tutor/update/` -> wired to `update_tutor_profile`; the view itself is annotated `PUT`. Inputs inferred: `hourly_rate`, `teaching_level`, `can_online`, `can_f2f`.
- GET `/api/bookings/` -> booking collection for the current user.
- GET `/api/bookings/<booking_id>/` -> booking detail payload.
- GET `/api/payment-methods/` -> payment method list.
- POST `/api/bookings/confirm/` -> confirm payment and create bookings. Inputs inferred: `tutor_id`, `slots`, `payment_method`.
- GET `/api/template-availability/` -> authenticated tutor recurring-slot template.
- POST `/api/template-availability/` -> create recurring slot. Inputs inferred: `day`, `time_slot`.
- GET `/api/template-availability/<pk>/` -> same view with slot id parameter.
- DELETE `/api/template-availability/<pk>/` -> delete recurring slot by id.
- POST `/api/bookings/<booking_id>/complete/` -> mark booking complete.
- POST `/api/bookings/<booking_id>/approve/` -> approve a pending booking.
- POST `/api/bookings/<booking_id>/reject/` -> reject/remove a pending booking.
- POST `/api/tutor/setup/` -> tutor setup payload. Inputs inferred: `teaching_level`, `can_online`, `can_f2f`, `hourly_rate`.
- POST `/api/recommend-tutors/` -> recommendation query. Inputs inferred: `subject`, `preferred_mode`. Returns recommender output data.

Other interface code found
- `backend/testapp/urls.py` defines `/test/` for `test_api`, but this URLconf is not mounted by `backend/backend/urls.py`.
- `backend/testapp/views.py::test_api` supports `GET` (list `TestMessage` rows) and `POST` (create a `message`).
- `src/services/api/api.js` exports a configured Axios instance with auth-token attachment and refresh-token retry behavior.

## 7. Known Issues / TODOs

Comment scan results
- No `TODO`, `FIXME`, `HACK`, or `BUG` markers were found in authored project files (`.git/`, `node_modules/`, and `backend/venv/` excluded from the scan).

Known bugs / unfinished / noteworthy issues observed during dump assembly
- `src/services/api/search-tutors.js` exists but is an empty file (0 lines), which suggests unfinished or abandoned API helper work.
- Frontend env/config mismatch: `.env` defines `VITE_API_BASE_URL=http://localhost:8000/api/v1`, but `src/services/api/api.js` hardcodes `http://127.0.0.1:8000/api/` and does not read the env variable.
- `backend/{` is a stray zero-byte file with an unusual name.
- `backend/.env` contains live-looking database credentials and raw `psql` restore commands committed in plain text; this is a security and handoff hygiene risk.
- `backend/testapp` is present but not mounted into the main Django URL configuration, so its test endpoint is effectively unreachable in the current app wiring.

## 8. Recent Changes

Last 10 git commit messages (`git log --oneline -10`):
```text
3a7a2d2 Fixed Loading of Tutor and Tutee pages
e524f20 fix remaining conflict markers
0c58d2f added institutional verification
e1027fb  fixed backend conflicts
06f9324 Fixed the tokens and logout timers for backend and frontend
53d3d82 After Yes
576a503 After Midtem Checkpoint
b977330 working CBF
eac9011 Before Doing any Progress adding database seeds
fc17641 Merge branch 'main' into ryan/LatestWorking
```


