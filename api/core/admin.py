from django.contrib import admin
from core.models import Answer, Question, Vote


class AnswerInline(admin.StackedInline):
    model = Answer
    extra = 0


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'user', 'timestamp', 'status', 'has_answer', 'total_votes'
    ]
    search_fields = ['title', 'content', 'user']
    list_filter = ['status', 'has_answer', 'tags']
    inlines = [AnswerInline]

