from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import UserForm, News, NewsForm
from django.contrib.auth import (authenticate,
    REDIRECT_FIELD_NAME, get_user_model,login,
    logout , update_session_auth_hash,
)
import pymongo
from bson.objectid import ObjectId
from django.contrib import auth
from django.contrib.auth.decorators import login_required

from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import date
from datetime import datetime
from django.views.decorators.cache import cache_page

db_name = 'db2'

def log(request):
    if  request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request=request, user = user)
            
            return redirect('/profile/')
            # return render(request, 'my_admin/clustering.html')
        else:
            form = UserForm()
            return render(request, 'my_admin/login.html', {'form':form, 'error':"Такого пользователя не существует"})
    else:
        form = UserForm()
        return render(request, 'my_admin/login.html', {'form':form})


@login_required
def profile(request):
    user = request.user
    n = [{'text':o.text, 'title':o.title}for o in user.news.all()]
    return render(request,'my_admin/profile.html', {'my_articles':n})


@login_required
def fast_cluster_page(request, id_, number):
    client = pymongo.MongoClient()
    
    # Get two last clusterisations data and results

    cluster = client[db_name].clustering_wmd.find_one({'_id':ObjectId(id_)})
    idxs = cluster['labels2id'][str(number)]

    news = client[db_name].news
    cluster_list = []

    for i in idxs:
        cluster_list.append({'title': news.find_one({'_id': ObjectId(i)})['title'],'text': news.find_one({'_id': ObjectId(i)})['description'], 'evolution':[]})
    return  render(request, 'my_admin/cluster_fast.html', {'list_of_news':cluster_list, 'status': cluster['status'][str(number)], 'addr':str(id_)+"/cluster/" +str(number) })


@login_required
def full_cluster_page(request, id_, number):
    client = pymongo.MongoClient()
    # Get two last clusterisations data and results

    cluster = client[db_name].clustering_doc2vec.find_one({'_id':ObjectId(id_)})
    print(cluster)
    idxs = cluster['labels2id'][str(number)]

    news = client[db_name].news
    cluster_list = []

    for i in idxs:
        evolution = []
        
        ev = client[db_name].events_evolution_on_duplicates.find_one(sort=[('date', pymongo.DESCENDING)])['id2labels'].get(i)
        if ev:
            ev_idx = client[db_name].events_evolution_on_duplicates.find_one(sort=[('date', pymongo.DESCENDING)])['id2labels'][i]
            for l in client[db_name].events_evolution_on_duplicates.find_one(sort=[('date', pymongo.DESCENDING)])['labels2id'][ev_idx]:
                if len(l):
                    evolution.append({'title': news.find_one({'_id': ObjectId(l[0])})['title'],'text': news.find_one({'_id': ObjectId(l[0])})['description']})
    
        cluster_list.append({'title': news.find_one({'_id': ObjectId(i)})['title'],'text': news.find_one({'_id': ObjectId(i)})['description'], 'evolution':evolution})

    return  render(request, 'my_admin/cluster_full.html', {'list_of_news':cluster_list, 'status': cluster['status'][str(number)], 'addr':str(id_)+"/cluster/" +str(number) })


@login_required
def edit_news(request, full, id_, number):
    full = int(full)
    if full:
        coll = 'clustering_doc2vec'
    else:
        coll = 'clustering_wmd'
    i = id_ + "_" + number

    client = pymongo.MongoClient()
    status = client[db_name][coll].find_one({'_id':ObjectId(id_)})['status'][str(number)]

    cluster = client[db_name][coll].find_one({'_id':ObjectId(id_)})
    idxs = cluster['labels2id'][str(number)]

    news = client[db_name].news
    cluster_list = []

    for i in idxs:
        evolution = []
        if full:
            ev = client[db_name].events_evolution_on_duplicates.find_one(sort=[('date', pymongo.DESCENDING)])['id2labels'].get(i)
            if ev:
                ev_idx = client[db_name].events_evolution_on_duplicates.find_one(sort=[('date', pymongo.DESCENDING)])['id2labels'][i]
                for l in client[db_name].events_evolution_on_duplicates.find_one(sort=[('date', pymongo.DESCENDING)])['labels2id'][ev_idx]:
                    if len(l):
                        evolution.append({'title': news.find_one({'_id': ObjectId(l[0])})['title'],'text': news.find_one({'_id': ObjectId(l[0])})['description']})
        
        cluster_list.append({'title': news.find_one({'_id': ObjectId(i)})['title'],'text': news.find_one({'_id': ObjectId(i)})['description'], 'evolution':evolution})


    if status == 0:
        form = NewsForm()
        new_status = client[db_name][coll].find_one({'_id':ObjectId(id_)})['status']
        new_status[str(number)] = 1
        client[db_name][coll].update({'_id':ObjectId(id_)}, {'$set':{'status':new_status}} )

        return render(request, 'my_admin/edit_page.html', {'form':form, 'id_':id_, 'number':number, 'list_of_news':cluster_list, 'full':full})

    if status == 1:
        return render(request, 'my_admin/edit_page.html', {'error':'Данный документ сейчас редактируется другим пользователем', 'id_':id_, 'number':number, 'full':full})
    if status == 3:
        return render(request, 'my_admin/edit_page.html', {'error':'Эта статья уже завершена', 'id_':id_, 'number':number, 'full':full})

    if status == 2:
        obj = News.objects.get_or_create(news_id=str(full) + '_' + id_ + "_" + number)[0]

        form = NewsForm(instance=obj)
        new_status = client[db_name][coll].find_one({'_id':ObjectId(id_)})['status']
        new_status[str(number)] = 1
        client[db_name][coll].update({'_id':ObjectId(id_)}, {'$set':{'status':new_status}} )
        return render(request, 'my_admin/edit_page.html', {'form':form, 'id_':id_, 'number':number, 'list_of_news':cluster_list, 'full':full})


@login_required
def save_news(request,full, id_, number):

    full = int(full)
    client = pymongo.MongoClient()
    author = request.user
    title = request.POST.get('title')
    text = request.POST.get('text')
    obj = News.objects.get_or_create(news_id=str(full) + '_' + id_ + "_" + number)[0]

    if author.id not in obj.author.all():
        obj.author.add(author)
    obj.title = title
    obj.text = text
    obj.save()

    if full == 1:

        new_status = client[db_name].clustering_doc2vec.find_one({'_id':ObjectId(id_)})['status']
        new_status[str(number)] = 2
        client[db_name].clustering_doc2vec.update({'_id':ObjectId(id_)}, {'$set':{'status':new_status}} )

        return redirect('/full_clustering/')
    else:
        new_status = client[db_name].clustering_wmd.find_one({'_id':ObjectId(id_)})['status']
        new_status[str(number)] = 2
        client[db_name].clustering_wmd.update({'_id':ObjectId(id_)}, {'$set':{'status':new_status}} )
        return redirect('/fast_clustering/')


@login_required
def update_status(request, full, id_, number):
    client = pymongo.MongoClient()
    if int(full) == 1:
        coll = 'clustering_doc2vec'
    else:
        coll = 'clustering_wmd'
    new_status = client[db_name][coll].find_one({'_id':ObjectId(id_)})['status']
    new_status[str(number)] = 2
    client[db_name][coll].update({'_id':ObjectId(id_)}, {'$set':{'status':new_status}} )

    if  int(full) == 1:
        return redirect('/full_clustering/')
    else:
        return redirect('/fast_clustering/')
        

@login_required
def save_to_mongo(obj):
    client = pymongo.MongoClient()
    author = [a.username for a in obj.author.all()]
    print(author)
    d = {'_id':obj.news_id,'title':obj.title, 'text':obj.text, 'date':obj.published_date, 'authors':author}

    client[db_name].articles.insert_one(d)


@login_required
def publish(request,full, id_, number):
    client = pymongo.MongoClient()
    author = request.user
    title = request.POST.get('title')
    text = request.POST.get('text')

    obj = News.objects.get_or_create(news_id=full + '_' + id_ + "_" + number)[0]
    full = int(full)
    if author.id not in obj.author.all():
        obj.author.add(author)
    obj.title = title
    obj.text = text
    obj.save()
    obj.publish()
    
    if full == 1:
        new_status = client[db_name].clustering_doc2vec.find_one({'_id':ObjectId(id_)})['status']
        new_status[str(number)] = 3
        client[db_name].clustering_doc2vec.update({'_id':ObjectId(id_)}, {'$set':{'status':new_status}} )

        save_to_mongo(obj)
        return redirect('/full_clustering/')
    else:
        new_status = client[db_name].clustering_wmd.find_one({'_id':ObjectId(id_)})['status']
        new_status[str(number)] = 3
        client[db_name].clustering_wmd.update({'_id':ObjectId(id_)}, {'$set':{'status':new_status}} )

        save_to_mongo(obj)
        return redirect('/fast_clustering/')















@login_required
def archive_full_clustering(request):
    client = MongoClient()
    clustering = client['db2'].clustering_doc2vec
    cl = clustering.find(sort=[('date', pymongo.DESCENDING)] ).limit(10)
    array = []
    for c in cl:
        print(c)
        d = datetime.fromtimestamp(c['date']).strftime('%H:%M %d/%m/%Y') #
        array.append({'id' : str(c['_id']), 'date' : d})
    return render(request, 'my_admin/archive_full_clustering.html', {'clusterings': array}) 


@login_required
def archive_fast_clustering(request):
    client = MongoClient()
    clustering = client['db2'].clustering_wmd
    cl = clustering.find(sort=[('date', pymongo.DESCENDING)] ).limit(10)
    array = []
    for c in cl:
        d = datetime.fromtimestamp(c['date']).strftime('%H:%M %d/%m/%Y')
        array.append({'id' : str(c['_id']), 'date' : d})
    return render(request, 'my_admin/archive_fast_clustering.html', {'clusterings': array})

@login_required
#@cache_page(60*15)
def full_clustering_one(request, Id):
    client = MongoClient()
    clustering = client['db2'].clustering_doc2vec
    cl = clustering.find_one({'_id' : ObjectId(Id)})
    labels2id = cl['labels2id']
    num = cl['n_clusters']
    News = client['db2'].news
    data = []
    for i in range(num):
        Id_news = cl['centers'][i]
        n = News.find_one({'_id' : ObjectId(Id_news)})
        data.append(dict(label=n['title'], size=len(labels2id[str(i)]), Id=i))
    data.sort(key= lambda x: -x['size'])
    a = int(len(data)*0.05) + 1
    return render(request, 'my_admin/full_clustering.html', {'data': data[a : a + 40], 'id_' : Id}) #'data': data[:30]

@login_required
#@cache_page(60*15)
def fast_clustering_one(request, Id):
    client = MongoClient()
    clustering = client['db2'].clustering_wmd
    cl = clustering.find_one({'_id' : ObjectId(Id)}) #sort=[('date', pymongo.DESCENDING)]
    labels2id = cl['labels2id']
    num = cl['n_clusters']
    News = client['db2'].news
    data = []
    for i in range(num):
        Id_news = labels2id[str(i)][0]
        n = News.find_one({'_id' : ObjectId(Id_news)})
        data.append(dict(label=n['title'], size=len(labels2id[str(i)]), Id=i))
    data.sort(key= lambda x: -x['size'])
    return render(request, 'my_admin/fast_clustering.html', {'data': data[:40], 'id_' : Id}) #'data': data[:30]

@login_required
#@cache_page(60 * 15)
def full_clustering_list(request, Id):
    client = MongoClient()
    clustering = client['db2'].clustering_doc2vec
    cl = clustering.find_one({'_id' : ObjectId(Id)})
    labels2id = cl['labels2id']
    num = cl['n_clusters']
    News = client['db2'].news
    data = []
    for i in range(num):
        Id_news = cl['centers'][i]
        n = News.find_one({'_id' : ObjectId(Id_news)})
        data.append(dict(title=n['title'], Id=i, size=len(labels2id[str(i)])))
    data.sort(key= lambda x: -x['size'])
    return render(request, 'my_admin/full_clustering_list.html', {'data': data, 'id_' : Id})

@login_required
#@cache_page(60 * 15)
def fast_clustering_list(request, Id):
    client = MongoClient()
    clustering = client['db2'].clustering_wmd
    cl = clustering.find_one({'_id' : ObjectId(Id)}) #sort=[('date', pymongo.DESCENDING)]
    labels2id = cl['labels2id']
    num = cl['n_clusters']
    News = client['db2'].news
    data = []
    for i in range(num):
        Id_news = labels2id[str(i)][0]
        n = News.find_one({'_id' : ObjectId(Id_news)})
        data.append(dict(title=n['title'], size=len(labels2id[str(i)]), Id=i))
    data.sort(key= lambda x: -x['size'])
    return render(request, 'my_admin/fast_clustering_list.html', {'data': data, 'id_' : Id})