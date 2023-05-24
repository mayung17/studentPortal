from django.shortcuts import render, redirect
from .forms import notes, NoteForm, HomeworkForm, DashboardForm, TodoForm,Conversion,ConversionLengthForm,\
 ConversionMassForm, UserRegistrationForm
from django.contrib import messages
from django.views.generic import DetailView
from django.contrib.auth.views import LoginView
from .models import homework, todo
from youtubesearchpython import VideosSearch
# from .models import notes
import requests
import wikipedia
from django.contrib.auth.decorators import login_required


class notes_detailview(DetailView) :
    model = notes


def home(request):
    return render(request, 'dashboard/home.html')

@login_required
def Notes(request):
    if request.method == "POST" :
        form = NoteForm(request.POST)
        if form.is_valid():
            note = notes(user=request.user, title=request.POST['title'], description=request.POST['description'])
            note.save()
            messages.success(request, f'Notes Added from{request.user.username}')
    else:
        form = NoteForm()

    note = notes.objects.filter(user=request.user)
    return render(request,'dashboard/notes.html', {'notes': note, 'forms': form})

@login_required
def delete_note(request, pk=None) :
    notes.objects.get(id=pk).delete()
    return redirect('notes')

@login_required
def Homework(request) :
    if request.method == 'POST' :
        form = HomeworkForm(request.POST)
        if form.is_valid() :
            try :
                finished = request.POST['is_finished']
                if finished == 'on' :
                    finished = True
                else :
                    finished = False
            except :
                finished = False
            homeworks = homework(user=request.user, subject=request.POST['subject'], title=request.POST['title'],
                                 description=request.POST['description'], due=request.POST['due'], is_finished=finished)
            homeworks.save()

            messages.success(request, f'Homework added from {request.user.username}')
    else :
        form = HomeworkForm()

    Homework = homework.objects.filter(user=request.user)
    if len(Homework) == 0 :
        homework_done = True
    else :
        homework_done = False
    context = {'homeworks' : Homework, 'homework_done' : homework_done, 'form' : form}
    return render(request, 'dashboard/homework.html', context)

@login_required
def update_homework(request, pk=None) :
    homeworks = homework.objects.get(id=pk)

    if homeworks.is_finished == True :
        homeworks.is_finished = False
    else :
        homeworks.is_finished = True
    homeworks.save()
    return redirect('homework')


def delete_homework(request, pk=None) :
    homework.objects.get(id=pk).delete()
    return redirect('homework')


def youtube(request) :
    if request.method == 'POST' :
        form = DashboardForm(request.POST)
        text = request.POST['text']
        video = VideosSearch(text, limit=10)
        result_list = []
        for i in video.result()['result'] :
            result_dict = {
                'input' : text,
                'title' : i['title'],
                'duration' : i['duration'],
                'thumbnail' : i['thumbnails'][0]['url'],
                'channel' : i['channel']['name'],
                'link' : i['link'],
                'views' : i['viewCount']['short'],
                'published' : i['publishedTime']
            }
            desc = ''
            if i['descriptionSnippet'] :
                for j in i['descriptionSnippet'] :
                    desc += j['text']
            result_dict['description'] = desc
            result_list.append(result_dict)
            context = {
                'form' : form,
                'results' : result_list
            }
        return render(request, 'dashboard/youtube.html', context)
    else :

        form = DashboardForm()
    context = {
        'form' : form
    }

    return render(request, "dashboard/youtube.html", context)

@login_required
def Todo(request) :
    if request.method == "POST" :
        form = TodoForm(request.POST)
        if form.is_valid :
            try :
                finished = request.POST['is_finished']
                if finished == 'on' :
                    finished = True
                else :
                    finished = False
            except :
                finished = False
            todos = todo(user=request.user,  # spelling
                         title=request.POST['title'],
                         is_finished=finished
                         )
            todos.save()
            messages.success(request, f'Todo added from {request.user.username}')
    else :
        form = TodoForm()
    to_dos = todo.objects.filter(user=request.user)  # spelling wrong
    if len(to_dos) == 0 :
        todo_done = True
    else :
        todo_done = False

    context = {
        'todo' : to_dos,
        'form' : form,
        'todo_done' : todo_done

    }
    return render(request, 'dashboard/todo.html', context)

@login_required
def update_todo(request, pk=None) :
    todos = todo.objects.get(id=pk)

    if todos.is_finished == True :

        todos.is_finished = False
    else :
        todos.is_finished = True
    todos.save()
    return redirect('todo')

@login_required
def delete_todo(request, pk=None) :
    todo.objects.get(id=pk).delete()
    return redirect('todo')


def books(request) :
    if request.method == 'POST' :
        form = DashboardForm(request.POST)
        text = request.POST['text']
        url = "https://www.googleapis.com/books/v1/volumes?q=" + text
        r = requests.get(url)
        answer = r.json()
        result_list = []
        for i in range(10) :
            result_dict = {
                'title' : answer['items'][i]['volumeInfo']['title'],
                'subtitle' : answer['items'][i]['volumeInfo'].get('subtitle'),
                'description' : answer['items'][i]['volumeInfo'].get('description'),
                'count' : answer['items'][i]['volumeInfo'].get('pageCount'),
                'categories' : answer['items'][i]['volumeInfo'].get('categories'),
                'rating' : answer['items'][i]['volumeInfo'].get('pageRating'),
                'thumbnail' : answer['items'][i]['volumeInfo'].get('imageLinks').get('thumbnail'),
                'preview' : answer['items'][i]['volumeInfo'].get('previewLink')
            }
            result_list.append(result_dict)
            context = {
                'form' : form,
                'results' : result_list
            }
        return render(request, 'dashboard/books.html', context)
    else :

        form = DashboardForm()
    context = {
        'form' : form
    }

    return render(request, "dashboard/books.html", context)


def dictionary(request):
    if request.method == "POST":
        form = DashboardForm(request.POST)
        text = request.POST['text']
        url = "https://api.dictionaryapi.dev/api/v2/entries/en/"+text
        r = requests.get(url)
        answer = r.json()
        try:
            phonetics=answer[0]['phonetics'][0]['text']
            audio=answer[0]['phonetics'][0]['audio']
            definition=answer[0]['meanings'][0]['definitions'][0]['definition']
            example=answer[0]['meanings'][0]['definitions'][0]['example']
            synonyms=answer[0]['meanings'][0]['definitions'][0]['synonyms']
            context={
                'form':form,
                'input': text,
                'phonetics':phonetics,
                'audio':audio,
                'definition':definition,
                'example':example,
                'synonyms':synonyms
            }

        except:
            context={
                'form':form,
                'input':''
            }
        return render(request,'dashboard/dictionary.html',context)
    else:
        form=DashboardForm()
        context={
            'form':form
        }
    return render(request,'dashboard/dictionary.html',context)


def wiki(request):
    if request.method=="POST":
        text=request.POST['text']
        form=DashboardForm(request.POST)
        search=wikipedia.page(text)
        context={
            'form':form,
            'title':search.title,
            'link':search.url,
            'details':search.summary
        }

        return render(request,'dashboard/wiki.html',context)
    else:
        form=DashboardForm()
        context={
        'form':form
    }
    return render(request,'dashboard/wiki.html',context)

def conversion(request):
    if request.method=="POST":
        form=Conversion(request.POST)
        if request.POST['measurement'] == 'length':
            measurement_form = ConversionLengthForm()
            context = {
                'form': form,
                'm_form': measurement_form,
                'input': True
            }
            if 'input' in request.POST:
                first = request.POST['measure1']
                second = request.POST['measure2']
                input = request.POST['input']
                answer=''
                if input and int(input) >=0:
                    if first =='yard' and second == 'foot':
                        answer=f'{input} yard ={int(input)*3} foot'
                    if first == 'foot' and second =='yard':
                        answer=f'{input} foot ={int(input)*3} yard'
                context = {
                    'form':form,
                    'm_form':measurement_form,
                    'input':True,
                    'answer':answer
                }

        if request.POST['measurement'] == 'mass':
            measurement_form = ConversionMassForm()
            context = {
                    'form' : form,
                    'm_form' : measurement_form,
                    'input' : True
                }
            if 'input' in request.POST :
                first = request.POST['measure1']
                second = request.POST['measure2']
                input = request.POST['input']
                answer = ''
                if input and int(input) >= 0 :
                    if first == 'pound' and second == 'kilogram' :
                        answer = f'{input} pound ={int(input) * 0.453592} kilogram'
                    if first == 'kilogram' and second == 'pound' :
                        answer = f'{input}Kilogram ={int(input) * 2.20462} pound'
                context = {
                    'form': form,
                    'm_form': measurement_form,
                    'input' : True,
                    'answer' : answer
                }


    else:
        form=Conversion()
        context = {
            'form': form,
            'input': False
                }
    return render(request,'dashboard/conversion.html',context)


def register(request):
    if request.method=='POST':
        form=UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username= form.cleaned_data.get('username')
            messages.success(request,f'account created for{username}')
            return redirect('login')


    else:
        form=UserRegistrationForm()
    context={
        'form':form
        }
    return render(request,'dashboard/register.html',context)

@login_required
def profile(request):
    homeworks=homework.objects.filter(is_finished=False,user=request.user)
    todos = todo.objects.filter(is_finished=False, user=request.user)
    if len(homeworks)==0:
        homework_done=True
    else:
        homework_done=False
    if len(todos)==0:
        todo_done=True
    else:
        todo_done=False
    context={
        'homeworks':homeworks,
        'todos':todos,
        'homework_done':homework_done,
        'todo_done':todo_done
    }
    return render(request,'dashboard/profile.html',context)

