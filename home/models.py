from django.db import models
from mdeditor.fields import MDTextField
from utils.models import BaseModel


# Create your models here.


class Article(BaseModel.Base):
    title = models.CharField(max_length=32, verbose_name='标题')
    context = MDTextField(verbose_name='内容')

    def __str__(self):
        return self.title

    def day(self):
        return self.create_time.day

    # class Meta:
    #     db_table = '文章'

