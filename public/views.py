from django.shortcuts import render

# Create your views here.
# 导入必须的模块
from django.http import HttpResponse
import redis

html = '''<!DOCTYPE html>
<html lang="zh-CN">
  <head><link href="https://cdn.jsdelivr.net/npm/bootstrap@3.3.7/dist/css/bootstrap.min.css" rel="stylesheet"></head>
  <div class="col-md-3"></div><div class="col-md-6">%s</div><div class="col-md-3"></div>
'''

def redis_info(request):
    r = redis.Redis(host="127.0.0.1", port=6379)
    data = r.info()
    msg = ""
    for i,j in data.items():
        msg += '<tr><td >%s</td><td>%s</td></tr>' % (i, j)
    table ='<div><table class="table table-bordered">%s</table></div>' % msg
    return HttpResponse(html % table)
