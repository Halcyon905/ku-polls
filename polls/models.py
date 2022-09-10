import datetime
from django.db import models
from django.utils import timezone
from django.contrib import admin


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    end_date = models.DateTimeField('date ending', null=True, default=None)

    def __str__(self):
        """Return readable string"""
        return self.question_text

    @admin.display(
        boolean=True,
        ordering='pub_date',
        description='Published recently?',
    )
    def can_vote(self):
        """Return boolean whether voting is allowed."""
        now = timezone.localtime()
        if self.end_date is None:
            return self.pub_date <= now
        return self.pub_date <= now <= self.end_date

    def is_published(self):
        """Return boolean whether the question was published."""
        now = timezone.localtime()
        return self.pub_date <= now

    def was_published_recently(self):
        """Return boolean whether it was published recently."""
        now = timezone.localtime()
        return (now - datetime.timedelta(days=1)) <= self.pub_date <= now


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        """Return readable string"""
        return self.choice_text
