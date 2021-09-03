from django.shortcuts import render
from . import models
import markdown
from django.db.models import Count
from django.db.models.functions import ExtractMonth, ExtractYear
from django.conf import settings


# Create your views here.

def home(request):
    year_month_count = models.Article.objects.annotate(year=ExtractYear('create_time'),
                                                       month=ExtractMonth('create_time')) \
        .values('year', 'month').order_by('year', 'month').annotate(count=Count('id'))
    print(year_month_count)
    year_count = {}
    for i in year_month_count:
        if i.get('year') not in year_count:
            year_count[i.get('year')] = i.get('count')
        else:
            year_count[i.get('year')] += i.get('count')
    print(year_count)

    return render(request, 'home.html', context={'year_month_count': year_month_count,
                                                 'year_count': year_count})


def article(request, id):
    obj = models.Article.objects.filter(id=id).first()
    context = markdown.markdown(obj.context)

    return render(request, 'article.html', context={'context': context, 'title': obj.title})
