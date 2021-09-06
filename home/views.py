import time

from django.shortcuts import render
from . import models
import markdown
from django.db.models import Count
from django.db.models.functions import ExtractMonth, ExtractYear
from django.conf import settings
from django_redis import get_redis_connection


# Create your views here.
def home(request):
    return render(request, 'home.html')


def archive(request):
    start = time.time()
    # year_month_count = models.Article.objects.annotate(year=ExtractYear('create_time'),
    #                                                    month=ExtractMonth('create_time')) \
    #     .values('year', 'month').order_by('-year', '-month').annotate(count=Count('id'))
    article_list = models.Article.objects.all().values('id', 'title', 'create_time').order_by('-create_time')
    obj_list = {}
    for i in article_list:
        year = i.get('create_time').year
        month = i.get('create_time').month
        day = i.get('create_time').day
        i['day'] = day
        if year not in obj_list:
            obj_list[year] = {
                'count': 1,
                'month': {
                    month: {
                        'count': 1,
                        'articles': [i]
                    }
                }
            }
        else:
            obj_list[year]['count'] += 1
            if month not in obj_list[year]['month']:
                obj_list[year]['month'][month] = {
                    'count': 1,
                    'articles': [i]
                }
            else:
                obj_list[year]['month'][month]['count'] += 1
                obj_list[year]['month'][month]['articles'].append(i)
    print(time.time() - start)
    return render(request, 'archive.html', context={'obj_list': obj_list})  # 模板渲染较慢


def article(request, id):
    obj = models.Article.objects.filter(id=id).first()
    con = get_redis_connection("default")
    con.hincrby('test', id, 1)
    # 修改 Markdown 语法渲染
    md = markdown.Markdown(
        extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
            'markdown.extensions.toc',
        ]
    )
    context = md.convert(obj.context)
    num = con.hget('test', id).decode()
    return render(request, 'article.html', locals())
