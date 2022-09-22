"""This module contains the views of each page of the application."""
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views import generic
from .models import Question, Choice, Vote
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required


class IndexView(generic.ListView):
    """Index page of application."""

    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """
        Return 5 last published questions. Not including
        ones set to publish in the future.
        """
        return Question.objects.filter(
            pub_date__lte=timezone.localtime()).order_by('-pub_date')[:5]

    def get(self, request):
        """Return HttpResponse object contain the index page."""
        if request.user.is_anonymous:
            return render(request,
                          'polls/index.html',
                          context={"latest_question_list": self.get_queryset(),
                                   "username": "Not currently logged in."})
        return render(request,
                      'polls/index.html',
                      context={"latest_question_list": self.get_queryset(),
                               "username": "Logged in as "
                                           + request.user.username})


class DetailView(generic.DetailView):
    """Detail page of application."""

    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """Excludes any questions that aren't published yet."""
        return Question.objects.filter(pub_date__lte=timezone.localtime())

    def get(self, request, pk):
        """Return different pages in accordance to can_vote and is_published.

        Return detail page if can_vote method returns True. If not then but
        question is published redirect to results page. If question not
        yet published, redirect to index page.
        """
        if request.user.is_anonymous:
            return redirect(to='http://127.0.0.1:8000/accounts/login')
        user = request.user
        try:
            question = Question.objects.get(pk=pk)
        except (KeyError, Question.DoesNotExist):
            messages.error(request, 'Access to question denied.')
            return HttpResponseRedirect(reverse('polls:index'))
        if question.can_vote():
            try:
                vote_info = \
                    Vote.objects.get(user=user,
                                     choice__in=question.choice_set.all())
                check = vote_info.choice.choice_text
            except Vote.DoesNotExist:
                check = ''
            return render(request, 'polls/detail.html', {'question': question,
                                                         'check': check})
        elif question.is_published():
            messages.error(request,
                           'Voting period is closed for this question.')
            return HttpResponseRedirect(reverse('polls:results',
                                                args=(question.id,)))
        messages.error(request, 'Access to question denied.')
        return HttpResponseRedirect(reverse('polls:index'))


class ResultsView(generic.DetailView):
    """Result page of the application."""

    model = Question
    template_name = 'polls/results.html'

    def get(self, request, pk):
        """
        Return result page if can_vote method returns True.
        If not then redirect to results page.
        """
        try:
            question = Question.objects.get(pk=pk)
        except (KeyError, Question.DoesNotExist):
            messages.error(request, 'Access to question denied.')
            return HttpResponseRedirect(reverse('polls:index'))
        if question.is_published():
            return render(request, 'polls/results.html',
                          {'question': question})
        messages.error(request, 'Access to question denied.')
        return HttpResponseRedirect(reverse('polls:index'))


@login_required
def vote(request, question_id):
    """Add vote to choice of the current question."""
    question = get_object_or_404(Question, pk=question_id)
    user = request.user
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        # check if user has voted in question before
        try:
            vote_info = Vote.objects.get(user=user,
                                         choice__in=question.choice_set.all())
            vote_info.choice = selected_choice
            vote_info.save()
        except Vote.DoesNotExist:
            Vote.objects.create(choice=selected_choice, user=user).save()
        return HttpResponseRedirect(reverse('polls:results',
                                            args=(question.id,)))
