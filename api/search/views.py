from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic import ListView

from taggit.models import Tag
from core.models import Question


class SearchListView(LoginRequiredMixin, ListView):
    """CBV to contain all the search results"""

    model = Question
    template_name = "search/search_results.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        query = self.request.GET.get("query")
        context["active"] = "questions"
        context["hide_search"] = True
        context["tags_list"] = Tag.objects.filter(name=query)
        context["questions_list"] = Question.objects.filter(
            Q(title__icontains=query)
            | Q(content__icontains=query)
            | Q(tags__name__icontains=query)
        ).distinct()
        context["users_list"] = (
            get_user_model()
            .objects.filter(Q(username__icontains=query) | Q(name__icontains=query))
            .distinct()
        )
        context["questions_count"] = context["questions_list"].count()
        context["users_count"] = context["users_list"].count()
        context["tags_count"] = context["tags_list"].count()
        context["total_results"] = (
            context["questions_count"]
            + context["users_count"]
            + context["tags_count"]
        )
        return context


# For autocomplete suggestions
@login_required
def get_suggestions(request):
    # Convert users, articles, questions objects into list to be
    # represented as a single list.
    query = request.GET.get("term", "")
    users = list(
        get_user_model().objects.filter(
            Q(username__icontains=query) | Q(name__icontains=query)
        )
    )
    questions = list(
        Question.objects.filter(
            Q(title__icontains=query)
            | Q(content__icontains=query)
            | Q(tags__name__icontains=query)
        )
    )
    # Add all the retrieved users, articles, questions to data_retrieved
    # list.
    data_retrieved = users
    data_retrieved.extend(questions)
    results = []
    for data in data_retrieved:
        data_json = {}
        if isinstance(data, get_user_model()):
            data_json["id"] = data.id
            data_json["label"] = data.username
            data_json["value"] = data.username

        if isinstance(data, Question):
            data_json["id"] = data.id
            data_json["label"] = data.title
            data_json["value"] = data.title

        results.append(data_json)

    return JsonResponse(results, safe=False)
