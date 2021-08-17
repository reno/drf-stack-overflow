from django.urls import path
from rest_framework import routers
from core import views

app_name = 'core'

router = routers.DefaultRouter()
router.register('questions', views.NewestQuestionListView, basename='question')
router.register('tags', views.TagListView)

urlpatterns = [
    path(
        'questions/unaswered/',
        views.UnasweredQuestionListView.as_view({'get': 'list'}),
        name='unaswered-questions'
    ),
    path(
        'questions/most-voted/',
        views.MostVotedQuestionListView.as_view({'get': 'list'}),
        name='most-voted-questions'
    ),
    path(
        'questions/tagged/<str:tag>/',
        views.QuestionTaggedListView.as_view({'get': 'list'}),
        name='tagged-questions'
    ),
    path(
        'questions/<int:pk>/',
        views.QuestionDetailView.as_view(
            {
                'get': 'retrieve',
                'put': 'update',
                'delete': 'destroy'
            }
        ),
        name='question-detail'
    ),
    path(
        'answers/',
        views.AnswerCreateView.as_view({'post': 'create'}),
        name='propose-answer'
    ),
    path(
        'tags/popular/',
        views.PopularTagListView.as_view({'get': 'list'}),
        name='popular-tags'
    ),
    path('comments/', views.CommentCreateView.as_view({'post': 'create'}), name='comment-create'),
    path(
        'comments/<int:pk>/',
        views.CommentEditView.as_view({'put': 'update', 'delete': 'destroy'}),
        name='comment-delete'
    ),
    path(
        'questions/<int:pk>/votes/',
        views.QuestionVoteView.as_view({'post': 'create', 'delete': 'destroy'}),
        name='question-vote'
    ),
    path(
        'answers/<int:pk>/votes/',
        views.AnswerVoteView.as_view({'post': 'create', 'delete': 'destroy'}),
        name='answer-vote'
    ),
    path('answers/<int:pk>/accept/', views.AcceptAnswerView.as_view(), name='accept-answer'),
    path('answers/<int:pk>/undo-accept/', views.UndoAcceptAnswerView.as_view(), name='undo-accept-answer'),
]

urlpatterns += router.urls
