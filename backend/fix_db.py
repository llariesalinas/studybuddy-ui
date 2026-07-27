import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()
from django.db import connection

sql = """
ALTER TABLE studybuddy_tuteeapplication ADD COLUMN reason_to_tutor text NOT NULL DEFAULT '';
"""
with connection.cursor() as cursor:
    try:
        cursor.execute(sql)
        print("Column added successfully.")
    except Exception as e:
        print("Error:", e)
