import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question


def create_question(question_text, days):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionModelTests(TestCase):

    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions whose pub_date
        is within the last day.
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)

    def test_can_vote_within_publish_and_end_date(self):
        """can_vote of Questions within voting period returns True. False otherwise."""
        pub_time = timezone.now() - datetime.timedelta(days=1)
        end_time1 = timezone.now() + datetime.timedelta(days=1)
        question = Question(pub_date=pub_time, end_date=end_time1)
        self.assertIs(question.can_vote(), True)

    def test_can_vote_after_end_date(self):
        """If end_date has passed then voting is not allowed."""
        pub_time = timezone.now() - datetime.timedelta(days=2)
        end_time1 = timezone.now() - datetime.timedelta(days=1)
        question = Question(pub_date=pub_time, end_date=end_time1)
        self.assertIs(question.can_vote(), False)

    def test_can_vote_without_end_date(self):
        """If published date has passed without end_date then voting is allowed."""
        pub_time = timezone.now() - datetime.timedelta(days=1)
        question = Question(pub_date=pub_time)
        self.assertIs(question.can_vote(), True)

    def test_can_vote_with_pub_date_in_future(self):
        """If pub_date is in the future then voting is not allowed."""
        pub_time = timezone.now() + datetime.timedelta(days=1)
        question = Question(pub_date=pub_time)
        self.assertIs(question.can_vote(), False)

    def test_can_vote_with_current_time_as_end_date(self):
        """If end_date is exactly the current time, voting is not allowed."""
        pub_time = timezone.now() + datetime.timedelta(days=1)
        end_time = timezone.now()
        question = Question(pub_date=pub_time, end_date=end_time)
        self.assertIs(question.can_vote(), False)

    def test_can_vote_with_current_time_as_pub_date(self):
        """If pub_date is exactly the current time, voting is allowed."""
        pub_time = timezone.now()
        end_time = timezone.now() + datetime.timedelta(days=1)
        question = Question(pub_date=pub_time, end_date=end_time)
        self.assertIs(question.can_vote(), True)


class QuestionIndexViewTests(TestCase):

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
        question = create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question],
        )

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
        question = create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question],
        )

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        question1 = create_question(question_text="Past question 1.", days=-30)
        question2 = create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question2, question1],
        )


class QuestionDetailViewTests(TestCase):

    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_question = create_question(question_text='Future question.', days=5)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(question_text='Past Question.', days=-5)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)


class QuestionResultsViewTests(TestCase):

    def test_voting_count(self):
        """Test that the app count and displays the correct amount of votes for each choice."""
        question1 = create_question(question_text="test question 1.", days=-1)
        c1 = question1.choice_set.create(choice_text='Yes', votes=1)
        c2 = question1.choice_set.create(choice_text='No', votes=0)
        response = self.client.get(reverse('polls:results', args=(question1.id,)))
        yes_count = response.context.dicts[3]['question'].choice_set.get(pk=1).votes
        no_count = response.context.dicts[3]['question'].choice_set.get(pk=2).votes
        self.assertEqual(yes_count, 1)
        self.assertEqual(no_count, 0)
