import json
import os
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIRequestFactory
from django_comments.models import Comment
from core.models import Question, Answer
from core.serializers import *
from core.utils import update_votes


class SerializerTestCase(TestCase):

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


class CommentCreateSerializerTestCase(SerializerTestCase):

    def test_create(self):
        url = reverse('core:comment-create')
        factory = APIRequestFactory()
        request = factory.get(url)
        request.user = self.user
        serializer = CommentCreateSerializer(
            data={
                'comment': 'Test comment',
                'object_type': 'question',
                'object_pk': self.question.id
            },
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.create(serializer.validated_data)
        self.assertTrue(Comment.objects.exists())


class AnswerListSerializerTestCase(SerializerTestCase):

    def setUp(self):
        super().setUp()
        url = reverse('core:question-detail', args=[self.question.id])
        factory = APIRequestFactory()
        self.request = factory.get(url)

    def test_get_upvoted(self):
        self.request.user = self.user
        serializer = AnswerListSerializer(context={'request': self.request})
        self.assertFalse(serializer.get_upvoted(self.answer))
        update_votes(self.answer, self.other_user, True)
        self.request.user = self.other_user
        serializer = AnswerListSerializer(context={'request': self.request})
        self.assertTrue(serializer.get_upvoted(self.answer))

    def test_get_downvoted(self):
        self.request.user = self.user
        serializer = AnswerListSerializer(context={'request': self.request})
        self.assertFalse(serializer.get_downvoted(self.answer))
        update_votes(self.answer, self.other_user, False)
        self.request.user = self.other_user
        serializer = AnswerListSerializer(context={'request': self.request})
        self.assertTrue(serializer.get_downvoted(self.answer))


class AnswerCreateSerializerTestCase(SerializerTestCase):

    def setUp(self):
        super().setUp()
        url = reverse('users:list')
        factory = APIRequestFactory()
        self.request = factory.get(url)

    def test_create(self):
        pass


class QuestionCreateSerializer(SerializerTestCase):

    def setUp(self):
        super().setUp()
        url = reverse('users:list')
        factory = APIRequestFactory()
        self.request = factory.get(url)

    def test_create(self):
        pass


class QuestionDetailSerializerTestCase(SerializerTestCase):

    def setUp(self):
        super().setUp()
        url = reverse('core:question-detail', args=[self.question.id])
        factory = APIRequestFactory()
        self.request = factory.get(url)

    def test_get_upvoted(self):
        self.request.user = self.user
        serializer = QuestionDetailSerializer(context={'request': self.request})
        self.assertFalse(serializer.get_upvoted(self.answer))
        update_votes(self.answer, self.other_user, True)
        self.request.user = self.other_user
        serializer = QuestionDetailSerializer(context={'request': self.request})
        self.assertTrue(serializer.get_upvoted(self.answer))

    def test_get_downvoted(self):
        self.request.user = self.user
        serializer = QuestionDetailSerializer(context={'request': self.request})
        self.assertFalse(serializer.get_downvoted(self.answer))
        update_votes(self.answer, self.other_user, False)
        self.request.user = self.other_user
        serializer = QuestionDetailSerializer(context={'request': self.request})
        self.assertTrue(serializer.get_downvoted(self.answer))


class QuestionVoteSerializerTestCase(SerializerTestCase):

    def test_validate(self):
        pass

    def test_create(self):
        pass

class AnswerVoteSerializerTestCase(SerializerTestCase):

    def test_validate(self):
        pass

    def test_create(self):
        pass

