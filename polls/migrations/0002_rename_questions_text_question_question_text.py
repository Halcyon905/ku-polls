# Generated by Django 4.1 on 2022-09-01 14:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("polls", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="question", old_name="questions_text", new_name="question_text",
        ),
    ]
