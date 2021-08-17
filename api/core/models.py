from collections import Counter
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Count
from django.utils.translation import ugettext_lazy as _
from django_comments.models import Comment
from slugify import slugify
from taggit.managers import TaggableManager
from markdownx.models import MarkdownxField


class Vote(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    value = models.BooleanField(default=True)
    content_type = models.ForeignKey(
        ContentType,
        blank=True,
        null=True,
        related_name='votes_on',
        on_delete=models.CASCADE,
    )
    object_id = models.PositiveIntegerField(blank=True, null=True)
    vote = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = _('Vote')
        verbose_name_plural = _('Votes')
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'content_type', 'object_id'], name='unique vote')
        ]


class QuestionQuerySet(models.query.QuerySet):

    def get_most_voted(self):
        return self.order_by('total_votes')

    def get_unanswered(self):
        return self.filter(has_answer=False)

    def get_tagged(self, tag):
        return self.filter(tags__name=tag)

    def get_counted_tags(self):
        tag_dict = {}
        query = self.all().annotate(tagged=Count('tags')).filter(tags__gt=0)
        for question in query:
            for tag in question.tags.names():
                if tag not in tag_dict:
                    tag_dict[tag] = 1
                else: # pragma: no cover
                    tag_dict[tag] += 1
        return sorted(tag_dict.items(), key=lambda item: item[1])



class Question(models.Model):
    OPEN = 'O'
    CLOSED = 'C'
    DRAFT = 'D'
    STATUS = ((OPEN, _('Open')), (CLOSED, _('Closed')), (DRAFT, _('Draft')))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, unique=True, blank=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(max_length=80, null=True, blank=True)
    status = models.CharField(max_length=1, choices=STATUS, default=DRAFT)
    content = MarkdownxField()
    has_answer = models.BooleanField(default=False)
    total_votes = models.IntegerField(default=0)
    votes = GenericRelation(Vote)
    comments = GenericRelation(Comment, object_id_field='object_pk')
    tags = TaggableManager()
    objects = QuestionQuerySet.as_manager()

    class Meta:
        ordering = ['-timestamp']
        verbose_name = _('Question')
        verbose_name_plural = _('Questions')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(
                self.title, lowercase=True, max_length=80
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def count_answers(self):
        return Answer.objects.filter(question=self).count()

    def count_votes(self):
        dic = Counter(self.votes.values_list('value', flat=True))
        Question.objects.filter(id=self.id).update(total_votes=dic[True] - dic[False])
        self.refresh_from_db()


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = MarkdownxField()
    total_votes = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)
    votes = GenericRelation(Vote)
    comments = GenericRelation(Comment, object_id_field='object_pk')

    class Meta:
        ordering = ['-accepted', '-timestamp']
        verbose_name = _('Answer')
        verbose_name_plural = _('Answers')

    def __str__(self):
        return self.content

    def count_votes(self):
        dic = Counter(self.votes.values_list('value', flat=True))
        Answer.objects.filter(id=self.id).update(
            total_votes=dic[True] - dic[False]
        )
        self.refresh_from_db()

    def accept_answer(self):
        answer_set = Answer.objects.filter(question=self.question)
        answer_set.update(accepted=False)
        self.accepted = True
        self.save()
        self.question.has_answer = True
        self.question.save()

    def undo_accept_answer(self):
        answer_set = Answer.objects.filter(question=self.question)
        answer_set.update(accepted=False)
        self.question.has_answer = False
        self.question.save()