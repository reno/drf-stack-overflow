from django.contrib.contenttypes.models import ContentType
from rest_framework import mixins, permissions, status, views, viewsets
from rest_framework.response import Response
from django_comments.models import Comment
from taggit.models import Tag
from core.models import Question, Answer, Vote
from core.permissions import OwnerOrReadOnly, IsOriginalPoster
from core.serializers import *


class NewestQuestionListView(mixins.CreateModelMixin, mixins.ListModelMixin,
                             viewsets.GenericViewSet):
    queryset = Question.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'list':
            return QuestionListSerializer
        elif self.action == 'create':
            return QuestionCreateSerializer


class UnasweredQuestionListView(viewsets.ReadOnlyModelViewSet):
    queryset = Question.objects.get_unanswered()
    serializer_class = QuestionListSerializer


class MostVotedQuestionListView(viewsets.ReadOnlyModelViewSet):
    queryset = Question.objects.get_most_voted()
    serializer_class = QuestionListSerializer


class QuestionTaggedListView(viewsets.ReadOnlyModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionListSerializer

    def list(self, request, tag):
        queryset = Question.objects.get_tagged(tag)
        serializer = QuestionListSerializer(
            queryset,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)


class QuestionDetailView(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionDetailSerializer
    permission_classes = [OwnerOrReadOnly]


class AnswerCreateView(viewsets.ModelViewSet):
    queryset = Answer.objects.all()
    serializer_class = AnswerCreateSerializer


class TagListView(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.order_by('name')
    serializer_class = TagListSerializer


class PopularTagListView(viewsets.ViewSet):

    def list(self, request):
        counted_tags = Question.objects.get_counted_tags()
        serializer = CountedTagsSerializer(counted_tags, many=True)
        return Response(serializer.data)


class QuestionVoteView(viewsets.ModelViewSet):
    queryset = Vote.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return QuestionVoteSerializer

    def create(self, request, *args, **kwargs):
        question_id = kwargs.get('pk')
        content_type = ContentType.objects.get(model='question')
        serializer = self.get_serializer(
            data=request.data,
            context={
                'content_type': content_type,
                'question_id': question_id,
                'user': request.user,
            }
        )
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def destroy(self, request, *args, **kwargs):
        user = request.user
        question_id = kwargs.get('pk')
        vote = Vote.objects.filter(user=user, object_id=question_id)
        vote.delete()
        question = Question.objects.get(id=question_id)
        question.count_votes()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AnswerVoteView(viewsets.ModelViewSet):
    queryset = Vote.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return AnswerVoteSerializer

    def create(self, request, *args, **kwargs):
        answer_id = kwargs.get('pk')
        serializer = self.get_serializer(
            data=request.data,
            context={
                'answer_id': answer_id,
                'user': request.user,
            }
        )
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def destroy(self, request, *args, **kwargs):
        user = request.user
        answer_id = kwargs.get('pk')
        vote = Vote.objects.filter(user=user, object_id=answer_id)
        vote.delete()
        answer = Answer.objects.get(id=answer_id)
        answer.count_votes()
        print(answer.total_votes)
        return Response(status=status.HTTP_204_NO_CONTENT)


class AcceptAnswerView(views.APIView):
    permission_classes = [IsOriginalPoster]

    def put(self, request, pk):
        answer = Answer.objects.get(pk=pk)
        answer.accept_answer()
        return Response({'status': 'true'}, status=status.HTTP_200_OK)


class UndoAcceptAnswerView(views.APIView):
    permission_classes = [IsOriginalPoster]

    def put(self, request, pk):
        answer = Answer.objects.get(pk=pk)
        answer.undo_accept_answer()
        return Response({'status': 'false'}, status=status.HTTP_200_OK)


class CommentCreateView(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentCreateSerializer
    permission_classes = [permissions.IsAuthenticated]


class CommentEditView(mixins.DestroyModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = Comment.objects.all()
    permission_classes = [OwnerOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'update':
            return CommentEditSerializer