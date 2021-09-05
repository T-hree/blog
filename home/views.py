import time

from django.shortcuts import render
from . import models
import markdown
from django.db.models import Count
from django.db.models.functions import ExtractMonth, ExtractYear
from django.conf import settings
from django.core.cache import cache
from django_redis import get_redis_connection


# Create your views here.
def home(request):
    return render(request, 'home.html')


def archive(request):
    start = time.time()

    year_month_count = models.Article.objects.annotate(year=ExtractYear('create_time'),
                                                       month=ExtractMonth('create_time')) \
        .values('year', 'month').order_by('year', 'month').annotate(count=Count('id')).order_by('-month')

    obj_list = {}
    for year_month in year_month_count:
        year = year_month.get('year')
        month = year_month.get('month')
        count = year_month.get('count')
        articles = models.Article.objects.filter(create_time__year=year, create_time__month=month)
        if year not in obj_list:
            obj_list[year] = {'count': count, 'month': {}}
        else:
            obj_list[year]['count'] += count
        obj_list[year]['month'][month] = {'count': count, 'article_list': articles}

    print(time.time() - start)
    return render(request, 'archive.html', context={'obj_list': obj_list})


def article(request, id):
    obj = models.Article.objects.filter(id=id).first()
    con = get_redis_connection("default")
    con.hincrby('test', id, 1)
    md = markdown.Markdown(extensions=['markdown.extensions.extra', 'markdown.extensions.codehilite'])
    context = md.convert(obj.context)
    num = con.hget('test', id).decode()

    return render(request, 'article.html', locals())
