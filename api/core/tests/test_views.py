import json
import os
from django.contrib.auth import get_user_model
from django_comments.models import Comment
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory
from core.models import Answer, Question, Vote


class ViewsTestCase(APITestCase):

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


class NewestQuestionListViewTestCase(ViewsTestCase):

    def test_get_serializer_class(self):
        pass


class QuestionTaggedListViewTestCase(ViewsTestCase):

    def test_list(self):
        pass


class PopularTagListViewTestCase(ViewsTestCase):

    def test_list(self):
        pass


class QuestionVoteViewTestCase(ViewsTestCase):

    def test_get_serializer_class(self):
        pass

    def test_create(self):
        pass

    def test_destroy(self):
        pass


class AnswerVoteViewTestCase(ViewsTestCase):

    def test_get_serializer_class(self):
        pass

    def test_create(self):
        pass

    def test_destroy(self):
        pass
