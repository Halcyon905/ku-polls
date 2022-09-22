"""This module contains the tests for the polls.models."""
import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question, Vote
from django.contrib.auth.models import User


def create_question(question_text, days=0, end=1):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time1 = timezone.localtime() + datetime.timedelta(days=days)
    # plus milliseconds for more consistent tests
    time2 = timezone.localtime() + datetime.timedelta(days=days + end,
                                                      milliseconds=50)
    return Question.objects.create(question_text=question_text,
                                   pub_date=time1,
                                   end_date=time2)


class QuestionModelTests(TestCase):

    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        time = timezone.localtime() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is older than 1 day.
        """
        time = timezone.localtime() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions whose pub_date
        is within the last day.
        """
        time = timezone.localtime() - datetime.timedelta(hours=23,
                                                         minutes=59,
                                                         seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)

    def test_can_vote_within_publish_and_end_date(self):
        """
        can_vote of Questions within voting period returns True.
        False otherwise.
        """
        question = create_question(question_text="test question 1.",
                                   days=-1, end=2)
        self.assertIs(question.can_vote(), True)

    def test_can_vote_after_end_date(self):
        """If pub_date and end_date has passed then voting is not allowed."""
        question = create_question(question_text="test question 1.",
                                   days=-2)
        self.assertIs(question.can_vote(), False)

    def test_can_vote_without_end_date(self):
        """
        If published date has passed without end_date then voting is allowed.
        """
        pub_time = timezone.localtime() - datetime.timedelta(1)
        question = Question(question_text="test question 1.",
                            pub_date=pub_time)
        self.assertIs(question.can_vote(), True)

    def test_can_vote_with_pub_date_in_future(self):
        """If pub_date is in the future then voting is not allowed."""
        question = create_question(question_text="test question 1.",
                                   days=1)
        self.assertIs(question.can_vote(), False)

    def test_can_vote_with_current_time_as_end_date(self):
        """If end_date is exactly the current time, voting is not allowed."""
        question = create_question(question_text="test question 1.",
                                   days=-1)
        self.assertIs(question.can_vote(), True)

    def test_can_vote_with_current_time_as_pub_date(self):
        """If pub_date is exactly the current time, voting is allowed."""
        question = create_question(question_text="test question 1.")
        self.assertIs(question.can_vote(), True)


class QuestionIndexViewTests(TestCase):

    def setUp(self) -> None:
        """Setup before running tests."""
        self.user = User.objects.create(username='test_person')
        self.user.set_password('12345')
        self.user.save()
        self.logged_in = self.client.login(username='test_person',
                                           password='12345')

    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        """
        Questions with a pub_date in the past are displayed on the
        index page.
        """
        question = create_question(question_text="Past question.",
                                   days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question],
        )

    def test_anyone_can_see_polls_list(self):
        """Users can see the polls list without logging in."""
        self.client.logout()
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)

    def test_future_question(self):
        """
        Questions with a pub_date in the future aren't displayed on
        the index page.
        """
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        are displayed.
        """
        question = create_question(question_text="Past question.",
                                   days=-30)
        create_question(question_text="Future question.",
                        days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question],
        )

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        question1 = create_question(question_text="Past question 1.",
                                    days=-30)
        question2 = create_question(question_text="Past question 2.",
                                    days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question2, question1],
        )


class QuestionDetailViewTests(TestCase):

    def setUp(self) -> None:
        """Setup before running tests."""
        self.user = User.objects.create(username='test_person')
        self.user.set_password('12345')
        self.user.save()
        self.logged_in = self.client.login(username='test_person',
                                           password='12345')

    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 302 not found.
        """
        future_question = create_question(question_text='Future question.',
                                          days=5)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the
        past displays the question's text.
        """
        past_question = create_question(question_text='Past Question.',
                                        days=-5, end=10)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

    def test_closed_voting_period_question(self):
        """
        If both pub_date and end_date has passed
        then redirect to results page.
        """
        past_question = create_question(question_text='Past Question.',
                                        days=-5)
        response = self.client.get(reverse('polls:detail',
                                           args=(past_question.id,)))
        self.assertEqual(response.status_code, 302)


class QuestionResultsViewTests(TestCase):

    def setUp(self) -> None:
        """Setup before running tests."""
        self.user = User.objects.create(username='test_person')
        self.user.set_password('12345')
        self.user.save()
        self.logged_in = self.client.login(username='test_person',
                                           password='12345')

    def test_voting_count(self):
        """
        Test that the app count and displays
        the correct amount of votes for each choice.
        """
        question1 = create_question(question_text="test question 1.",
                                    days=-1, end=5)
        c1 = question1.choice_set.create(choice_text='Yes')
        Vote.objects.create(choice=c1, user=self.user)
        self.assertEqual(1, c1.votes())

    def test_future_pub_date_question(self):
        """
        Access to results of unpublished questions
        should be redirected to index page.
        """
        question1 = create_question(question_text="test question 1.",
                                    days=5)
        response = self.client.get(reverse('polls:results',
                                           args=(question1.id,)))
        self.assertEqual(response.status_code, 302)

    def test_anyone_can_see_result(self):
        """Anyone can see the results page of a question."""
        self.client.logout()
        question1 = create_question(question_text="test question 1.",
                                    days=-1)
        response = self.client.get(reverse('polls:results',
                                           args=(question1.id,)))
        self.assertEqual(response.status_code, 200)


class QuestionVoteViewTest(TestCase):

    def setUp(self) -> None:
        """Setup before running tests."""
        self.user = User.objects.create(username='test_person')
        self.user.set_password('12345')
        self.user.save()
        self.logged_in = self.client.login(username='test_person',
                                           password='12345')

    def test_only_authenticated_users_can_vote(self):
        """
        Only authenticated users can vote.
        If not they are redirected.
        """
        question1 = create_question("test_question1", days=-2)
        response = self.client.post(reverse('polls:vote',
                                            args=(question1.id,)))
        self.assertEqual(response.status_code, 200)
        self.client.logout()
        response = self.client.post(reverse('polls:vote',
                                            args=(question1.id,)))
        self.assertEqual(response.status_code, 302)

    def test_one_person_one_vote(self):
        """One user can vote once per question."""
        question1 = create_question("test_question1", days=-2)
        c1 = question1.choice_set.create(choice_text="yes")
        c2 = question1.choice_set.create(choice_text="no")
        self.client.post(reverse('polls:vote', args=(question1.id,)),
                         {'choice': c1.id})
        selected = Vote.objects.get(user=self.user,
                                    choice__in=question1.choice_set.all())
        self.assertEqual(selected.choice, c1)
        self.assertEqual(Vote.objects.all().count(), 1)
        self.client.post(reverse('polls:vote', args=(question1.id,)),
                         {'choice': c2.id})
        selected = Vote.objects.get(user=self.user,
                                    choice__in=question1.choice_set.all())
        self.assertEqual(selected.choice, c2)
        self.assertEqual(Vote.objects.all().count(), 1)
