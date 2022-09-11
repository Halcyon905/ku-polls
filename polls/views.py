from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic
from .models import Question, Choice
from django.utils import timezone
from django.contrib import messages


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """Return 5 last published questions. Not including ones set to publish in the future."""
        return Question.objects.filter(pub_date__lte=timezone.localtime()).order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.localtime())

    def get(self, request, pk):
        """
        Return detail page if can_vote method returns True. If not then redirect to results page.
        """
        question = get_object_or_404(Question, pk=pk)
        if question.can_vote():
            return render(request, 'polls/detail.html', {'question': question})
        elif question.is_published():
            messages.error(request, 'Voting period is closed for this question.')
            return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
        messages.error(request, 'Access to question denied.')
        return HttpResponseRedirect(reverse('polls:index'))


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'

    def get(self, request, pk):
        """
        Return result page if can_vote method returns True. If not then redirect to results page.
        """
        question = get_object_or_404(Question, pk=pk)
        if question.is_published():
            return render(request, 'polls/results.html', {'question': question})
        messages.error(request, 'Access to question denied.')
        return HttpResponseRedirect(reverse('polls:index'))


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
