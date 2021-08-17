from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers
from django_comments.models import Comment
from taggit.models import Tag
from taggit.serializers import TagListSerializerField, TaggitSerializer
from core.models import Answer, Question
from users.serializers import UserListSerializer
from core.utils import is_owner, update_votes

__all__ = [
    'CommentListSerializer', 'CommentCreateSerializer',  'CommentEditSerializer',
    'AnswerListSerializer', 'AnswerListSerializer', 'AnswerCreateSerializer',
    'QuestionListSerializer',
    'QuestionCreateSerializer', 'QuestionDetailSerializer', 'TagListSerializer',
    'CountedTagsSerializer', 'QuestionVoteSerializer', 'AnswerVoteSerializer'
]


class CommentListSerializer(serializers.ModelSerializer):
    user = UserListSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'comment', 'submit_date', 'user']


class CommentCreateSerializer(serializers.ModelSerializer):
    object_type = serializers.CharField(write_only=True)

    class Meta:
        model = Comment
        fields = ['comment', 'object_type', 'object_pk']

    def create(self, validated_data):
        object_type = validated_data.pop('object_type')
        validated_data['content_type'] = ContentType.objects.get(model=object_type)
        validated_data['user'] = self.context['request'].user
        validated_data['site_id'] = settings.SITE_ID
        comment = super(CommentCreateSerializer, self).create(validated_data)
        return comment


class CommentEditSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ['comment']


class AnswerListSerializer(serializers.ModelSerializer):
    comment_set = CommentListSerializer(many=True, read_only=True, source='comments')
    upvoted = serializers.SerializerMethodField()
    downvoted = serializers.SerializerMethodField()

    class Meta:
        model = Answer
        fields = [
            'id', 'content', 'user', 'timestamp', 'total_votes',
            'accepted', 'upvoted', 'downvoted', 'comment_set'
        ]

    def get_upvoted(self, instance):
        user = self.context['request'].user
        user_voted = instance.votes.filter(value=True, user=user).exists()
        return True if user_voted else False

    def get_downvoted(self, instance):
        user = self.context['request'].user
        user_voted = instance.votes.filter(value=False, user=user).exists()
        return True if user_voted else False


class AnswerCreateSerializer(serializers.ModelSerializer):
    question = serializers.PrimaryKeyRelatedField(queryset=Question.objects.all())

    class Meta:
        model = Answer
        fields = ['question', 'content']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        answer = super(AnswerCreateSerializer, self).create(validated_data)
        return answer


class QuestionListSerializer(TaggitSerializer, serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='core:question-detail')
    tags = TagListSerializerField()
    user = UserListSerializer(read_only=True)

    class Meta:
        model = Question
        fields = [
            'url', 'title', 'content', 'total_votes', 'count_answers',
            'has_answer', 'tags', 'timestamp', 'user',
        ]


class QuestionCreateSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField()

    class Meta:
        model = Question
        fields = ['title', 'content', 'tags']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        question = super(QuestionCreateSerializer, self).create(validated_data)
        return question


class QuestionDetailSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='core:question-detail')
    answer_set = AnswerListSerializer(many=True, read_only=True)
    comment_set = CommentListSerializer(many=True, read_only=True, source='comments')
    tags = TagListSerializerField()
    user = UserListSerializer(read_only=True)
    upvoted = serializers.SerializerMethodField()
    downvoted = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = [
            'url', 'id', 'title', 'slug', 'content', 'total_votes',
            'upvoted', 'downvoted', 'count_answers', 'has_answer',
            'timestamp', 'user', 'tags', 'comment_set', 'answer_set'
        ]

    def get_upvoted(self, instance):
        user = self.context['request'].user
        user_voted = instance.votes.filter(value=True, user=user).exists()
        return True if user_voted else False

    def get_downvoted(self, instance):
        user = self.context['request'].user
        user_voted = instance.votes.filter(value=False, user=user).exists()
        return True if user_voted else False


class TagListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ['name', 'slug']


class CountedTagsSerializer(serializers.Serializer):
    name = serializers.SerializerMethodField()
    count = serializers.SerializerMethodField()

    def get_name(self, obj):
        return obj[0]

    def get_count(self, obj):
        return obj[1]


class QuestionVoteSerializer(serializers.Serializer):
    value = serializers.BooleanField(write_only=True)

    def validate(self, attrs):
        user = self.context.get('user')
        question_id = self.context.get('question_id')
        question = Question.objects.get(id=question_id)
        if is_owner(question, user):
            raise serializers.ValidationError(
                {'detail': "You can't vote your own question."}
            )
        attrs['user'] = user
        attrs['question'] = question
        return attrs

    def create(self, validated_data):
        question = validated_data['question']
        user = validated_data['user']
        value = validated_data['value']
        update_votes(question, user, value)
        return question.votes


class AnswerVoteSerializer(serializers.Serializer):
    value = serializers.BooleanField(write_only=True)

    def validate(self, attrs):
        user = self.context.get('user')
        answer_id = self.context.get('answer_id')
        answer = Answer.objects.get(id=answer_id)
        if is_owner(answer, user):
            raise serializers.ValidationError(
                {'detail': "You can't vote your own answer."}
            )
        attrs['user'] = user
        attrs['answer'] = answer
        return attrs

    def create(self, validated_data):
        answer = validated_data['answer']
        user = validated_data['user']
        value = validated_data['value']
        update_votes(answer, user, value)
        return answer.votes