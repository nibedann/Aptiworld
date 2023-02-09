from django.shortcuts import render, redirect;
from django.contrib.auth  import authenticate,  login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import *
from django.http import JsonResponse
from .forms import QuizForm, QuestionForm
from django.forms import inlineformset_factory
from django.contrib.auth.decorators import user_passes_test
from django.contrib.admin.views.decorators import staff_member_required





# Create your views here.

def index(request):
    quiz = Quiz.objects.all()
    para = {'quiz': quiz}
    return render(request, 'index.html', para)


@user_passes_test(lambda u: u.is_superuser, login_url='login')
def Signup(request):
    if request.method=="POST":
        username = request.POST['username']
        email = request.POST['email']
        first_name=request.POST['first_name']
        last_name=request.POST['last_name']
        password = request.POST['password1']
        confirm_password = request.POST['password2']

        if password != confirm_password:
            return redirect('/index')

        user = User.objects.create_user(username, email, password)
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        Avatar.objects.create(user=user, image = 'static/avatars/bee_qCPs9vg.png')

        return render(request, 'login.html')
    return render(request, "signup.html")


@login_required(login_url = '/login')
def quiz(request, myid):
    quiz = Quiz.objects.get(id=myid)
    return render(request, "quiz.html", {'quiz':quiz})

@login_required(login_url = '/login')
def quiz_data_view(request, myid):
    quiz = Quiz.objects.get(id=myid)
    questions = []
    for q in quiz.get_questions():
        answers = []
        for a in q.get_answers():
            answers.append(a.content)
        questions.append({str(q): answers})
    return JsonResponse({
        'data': questions,
        'time': quiz.time,
    })

def save_quiz_view(request, myid):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        questions = []
        data = request.POST
        data_ = dict(data.lists())

        data_.pop('csrfmiddlewaretoken')

        for k in data_.keys():
            print('key: ', k)
            question = Question.objects.get(content=k)
            questions.append(question)

        user = request.user
        quiz = Quiz.objects.get(id=myid)

        score = 0
        marks = []
        correct_answer = None

        for q in questions:
            a_selected = request.POST.get(q.content)

            if a_selected != "":
                question_answers = Answer.objects.filter(question=q)
                for a in question_answers:
                    if a_selected == a.content:
                        if a.correct:
                            score += 1
                            correct_answer = a.content
                    else:
                        if a.correct:
                            correct_answer = a.content

                marks.append({str(q): {'correct_answer': correct_answer, 'answered': a_selected}})
            else:
                marks.append({str(q): 'not answered'})

        Marks_Of_User.objects.create(quiz=quiz, user=user, score=score)

        return JsonResponse({'passed': True, 'score': score, 'marks': marks})


def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("/")
        else:
            messages.error(request, 'Username or Password is not correct, Please try again!');
            return redirect('login')
    else:
        return render(request, 'login.html')

def logout_user(request):
    logout(request)
    messages.success(request, 'You have been logged out!')
    return redirect('/')

@staff_member_required(login_url='login')
def add_quiz(request):
    if request.method=="POST":
        form = QuizForm(data=request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.save()
            obj = form.instance
            return render(request, "add_quiz.html", {'obj':obj})
    else:
        form = QuizForm()
    return render(request, "add_quiz.html", {'form':form})

@staff_member_required(login_url='login')
def add_question(request):
    questions = Question.objects.all()
    questions = Question.objects.filter().order_by('-id')
    if request.method=="POST":
        form = QuestionForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, "add_question.html")
    else:
        form=QuestionForm()
    return render(request, "add_question.html", {'form':form, 'questions':questions})

@staff_member_required(login_url='login')
def delete_question(request, myid):
    question = Question.objects.get(id=myid)
    if request.method == "POST":
        question.delete()
        return redirect('/add_question')
    return render(request, "delete_question.html", {'question':question})

@staff_member_required(login_url='login')
def add_options(request, myid):
    question = Question.objects.get(id=myid)
    QuestionFormSet = inlineformset_factory(Question, Answer, fields=('content','correct', 'question'), extra=4)
    if request.method=="POST":
        formset = QuestionFormSet(request.POST, instance=question)
        if formset.is_valid():
            formset.save()
            alert = True
            return render(request, "add_options.html", {'alert':alert})
    else:
        formset=QuestionFormSet(instance=question)
    return render(request, "add_options.html", {'formset':formset, 'question':question})


def results(request):
    marks = Marks_Of_User.objects.filter(user = request.user).order_by('-score')
    return render(request, "results.html", {'marks':marks})

@staff_member_required(login_url='login')
def all_results(request):
    result = Marks_Of_User.objects.all().order_by('-score')
    return render(request, "results.html", {'marks': result})

@staff_member_required(login_url='login')
def results_logical_reasoning(request):
    marks1 = Marks_Of_User.objects.filter(quiz__name = "LOGICAL REASONING").order_by('-score')[:5]
    print(marks1)
    return render(request, "results2.html", {'marks':marks1})

@staff_member_required(login_url='login')
def results_current_Affairs(request):
    marks1 = Marks_Of_User.objects.filter(quiz__name = "CURRENT AFFAIRS").order_by('-score')[:5]
    print(marks1)
    return render(request, "results2.html", {'marks':marks1})

@staff_member_required(login_url='login')
def results_engineering(request):
    marks1 = Marks_Of_User.objects.filter(quiz__name = "ENGINEERING").order_by('-score')[:5]
    print(marks1)
    return render(request, "results2.html", {'marks':marks1})

@staff_member_required(login_url='login')
def results_general_knowledge(request):
    marks1 = Marks_Of_User.objects.filter(quiz__name = "GENERAL KNOWLEDGE").order_by('-score')[:5]
    print(marks1)
    return render(request, "results2.html", {'marks':marks1})


@staff_member_required(login_url='login')
def delete_result(request, myid):
    marks = Marks_Of_User.objects.get(id=myid)
    if request.method == "POST":
        marks.delete()
        return redirect('/results')
    return render(request, "delete_result.html", {'marks':marks})


user_passes_test(lambda u: u.is_superuser, login_url='login')
def teacherSignup(request):
    if request.method=="POST":
        username = request.POST['username']
        email = request.POST['email']
        first_name=request.POST['first_name']
        last_name=request.POST['last_name']
        password = request.POST['password1']
        confirm_password = request.POST['password2']

        if password != confirm_password:
            return redirect('/index')

        user = User.objects.create_user(username, email, password)
        user.is_staff = True
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        Avatar.objects.create(user=user, image = 'static/avatars/bee_qCPs9vg.png')

        return render(request, 'login.html')
    return render(request, "teacherSignup.html")


def ava(request):
    avatar = Avatar.objects.filter(user = request.user)
    marks = Marks_Of_User.objects.filter(user = request.user)

    logicalReasoningScore = [4]
    CurrentAffairsScore = [3]
    engineeringScore = [4]
    generalKnowledgeScore = [4]
    for mark in marks:
        if(str(mark) == 'LOGICAL REASONING'):
            logicalReasoningScore.append(int(mark.score))
        elif(str(mark) == 'CURRENT AFFAIRS'):
            CurrentAffairsScore.append(int(mark.score))
        elif(str(mark) == 'ENGINEERING'):
            engineeringScore.append(int(mark.score))
        elif(str(mark) == 'GENERAL KNOWLEDGE'):
            generalKnowledgeScore.append(int(mark.score))

    maxLogicalReasoning = max(logicalReasoningScore)
    maxCurrentAffairs= max(CurrentAffairsScore)
    maxEngineering = max(engineeringScore)
    maxGeneralKnowledge = max(generalKnowledgeScore)
    highestScore = maxLogicalReasoning + maxCurrentAffairs + maxEngineering + maxGeneralKnowledge

    lasLogicalReasoning = [4]
    lasCurrentAffairs= [3]
    lasEngineeering = [2]
    lasGeneralKnowledge = [2]

    maxLogicalReasoning = [5]
    maxCurrentAffairs= [5]
    maxEngineering = [4]
    maxGeneralKnowledge = [5]


    for image in avatar:
        if(highestScore >= 10 and highestScore < 15):
            image.image = 'static/avatars/jake.svg'
        elif(highestScore >= 15 and highestScore < 20):
            image.image = 'static/avatars/stormtrooper.svg'
        elif(highestScore >= 20 and highestScore < 25):
            image.image = 'static/avatars/homer-simpson.svg'
        elif(highestScore >= 25 and highestScore < 30):
            image.image = 'static/avatars/walter-white.svg'
        elif(highestScore >= 30):
            image.image = 'static/avatars/iron-man.svg'
        else :
            image.image = 'static/avatars/scream.svg'

    return render(request,'dashboard.html', {'avatar': avatar, 'score':highestScore, 'lasLogicalReasoning':lasLogicalReasoning, 'lasCurrentAffairs':lasCurrentAffairs, 'lasEngineering':lasEngineeering, 'lasGeneralKnowledge':lasGeneralKnowledge, 'maxLogicalReasoning':maxLogicalReasoning,'maxCurrentAffairs':maxCurrentAffairs,'maxEngineering':maxEngineering, 'maxGeneralKnowledge':maxGeneralKnowledge})
