import json
import os
from django.contrib.auth import get_user_model
from django.test import TestCase
from core.models import Question, Answer


class ModelsTestCase(TestCase):

    def setUp(self):
        User = get_user_model()
        base_dir = os.path.dirname(__file__)
        file_path = os.path.join(base_dir, 'data.json')
        with open(file_path) as file:
            data = json.load(file)
        user_data = data.get('user_data')
        self.user = User.objects.create_user(**user_data)
        other_user_data = data.get('other_user_data')
        self.other_user = User.objects.create_user(**other_user_data)
        question_data = data.get('question_data')
        question_data['user'] = self.user
        self.question = Question.objects.create(**question_data)
        self.question.tags.add('test1')
        other_question_data = data.get('other_question_data')
        other_question_data['user'] = self.user
        self.other_question = Question.objects.create(**other_question_data)
        self.other_question.tags.add('test2')
        answer_data = data.get('answer_data')
        answer_data['question'] = self.question
        answer_data['user'] = self.user
        self.answer = Answer.objects.create(**answer_data)
        self.question.has_answer = True
        other_answer_data = data.get('other_answer_data')
        other_answer_data['question'] = self.question
        other_answer_data['user'] = self.user
        self.other_answer = Answer.objects.create(**other_answer_data)


class QuestionTestCase(ModelsTestCase):

    def test_type(self):
        self.assertTrue(isinstance(self.question, Question))

    def test_str(self):
        self.assertEqual(self.question.__str__(), self.question.title)

    def test_count_answers(self):
        self.assertEqual(self.question.count_answers, 2)
        self.assertEqual(self.other_question.count_answers, 0)

    def test_count_votes(self):
        self.question.votes.update_or_create(
            user=self.other_user, defaults={'value': True}
        )
        self.question.count_votes()
        self.assertEqual(self.question.total_votes, 1)
        self.assertEqual(self.other_question.total_votes, 0)


class QuestionQuerySetTestCase(ModelsTestCase):

    def test_get_most_voted(self):
        self.question.votes.update_or_create(
            user=self.other_user, defaults={'value': True}
        )
        self.assertEqual(Question.objects.get_most_voted()[0], self.question)

    def test_get_unanswered(self):
        self.assertEqual(Question.objects.get_unanswered().first(), self.other_question)

    def test_get_tagged(self):
        self.assertEqual(Question.objects.get_tagged('test1').first(), self.question)

    def test_get_counted_tags(self):
        counted_tags = {'test1': 1, 'test2': 1}
        self.assertEqual(Question.objects.get_counted_tags(), list(counted_tags.items()))


class AnswerTestCase(ModelsTestCase):

    def test_type(self):
        self.assertTrue(isinstance(self.answer, Answer))

    def test_str(self):
        self.assertEqual(self.answer.__str__(), self.answer.content)

    def test_count_votes(self):
        self.answer.votes.update_or_create(
            user=self.other_user, defaults={'value': True}
        )
        self.answer.count_votes()
        self.assertEqual(self.answer.total_votes, 1)

    def test_accept_answer(self):
        self.other_answer.accept_answer()
        self.answer.refresh_from_db()
        self.assertFalse(self.answer.accepted)
        self.assertTrue(self.other_answer.accepted)

    def test_undo_accept_answer(self):
        self.answer.undo_accept_answer()
        self.answer.refresh_from_db()
        self.assertFalse(self.answer.accepted)