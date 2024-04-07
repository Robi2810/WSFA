from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse

from .models import Profile, Achievement, Task, GroupProfile, User, Group
from .forms import ProfileForm, AchievementForm, TaskForm, SignUpForm, ProfileEditForm, GroupProfileForm,\
    GroupCreationForm, AddUsersToGroupForm


def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            Profile.objects.create(user=user)
            messages.success(
                request,
                f'Account created for {username}. You can now log in.')
            return redirect(
                'login'
            )  # Redirect to login page after successful registration
    else:
        form = SignUpForm()
    return render(request, 'registration/reg.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'You have been logged in successfully.')
            return redirect(
                'userprofile')  # Redirect to profile page after login
        else:
            messages.error(request, 'Invalid username or password.')
            render(request, 'registration/login.html',
                   {"error": 'Неверный логин или пароль'})
    return render(request, 'registration/login.html')


@login_required(login_url='login')
def user_profile(request):
    userprofile = Profile.objects.get(user=request.user)
    own_groups = GroupProfile.objects.filter(creator=request.user)
    user_groups = request.user.groups.all()

    groups = []

    for own_group in own_groups:
        people = len(User.objects.filter(groups__id=own_group.group.id))
        achievements = len(Achievement.objects.filter(current_group=own_group))
        tasks = len(Task.objects.filter(current_group=own_group))
        groups.append({
            'people': people,
            'achievements': achievements,
            'tasks': tasks,
            'name': own_group.group.name,
            'id': own_group.id,
            'sudo': own_group.creator == request.user
        })

    for user_group in user_groups:
        people = len(User.objects.filter(groups__id=user_group.id))
        achievements = len(
            Achievement.objects.filter(current_group__group=user_group))
        tasks = len(Task.objects.filter(current_group__group=user_group))
        groups.append({
            'people': people,
            'achievements': achievements,
            'tasks': tasks,
            'name': user_group.name,
            'id': GroupProfile.objects.get(group_id=user_group.id).id
        })

    user_achievements = userprofile.achievement.all()

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=userprofile)
        if form.is_valid():
            form.save()
            return redirect('userprofile')
    else:
        form = ProfileForm(instance=userprofile)
    print('abc', userprofile.profile_pic, type(userprofile.profile_pic), 'def')
    return render(
        request, 'userprofile.html', {
            'profile': userprofile,
            'groups': groups,
            'achievements': user_achievements
        })


@login_required(login_url='login')
def create_task(request, profile_group_id):
    if request.method == 'POST':
        print('profile_group_id', profile_group_id)
        user_email = request.POST['user_email']
        user = User.objects.get(email=user_email)
        deadline = request.POST['deadline']
        print('deadline', deadline)
        post = {
            'title': request.POST['title'],
            'description': request.POST['description'],
            'deadline': deadline,
            'current_group': profile_group_id,
            'user': user.id,
        }
        form = TaskForm(post)
        print('form.is_valid()', form.is_valid())
        if form.is_valid():
            task = form.save(commit=False)
            print('task', task)
            task.save()
            form.save_m2m()
            return redirect('group', profile_group_id=profile_group_id)
        else:
            return HttpResponse(form.errors.values())

    else:
        form = TaskForm(user=request.user)
        user_groups = GroupProfile.objects.filter(creator=request.user)
        form.fields['current_group'].queryset = user_groups

    return redirect('userprofile')


@login_required(login_url='login')
def create_achievement(request, group_id):
    group_profile = get_object_or_404(GroupProfile,
                                      id=group_id,
                                      creator=request.user)
    if request.method == 'POST':
        form = AchievementForm(request.POST, request.FILES)
        if form.is_valid():
            new_achievement = form.save(commit=False)
            new_achievement.current_group = group_profile
            new_achievement.save()
            return redirect('group', profile_group_id=group_id)
    else:
        form = AchievementForm()

    return render(request, 'achievement_create.html', {'form': form})


def get_group_users(request, group_id):
    group_profile = get_object_or_404(GroupProfile, id=group_id)
    users = list(group_profile.group.user_set.values('id', 'username'))
    return JsonResponse(users, safe=False)


@login_required(login_url='login')
def group_tasks(request, group_id):
    group_profile = get_object_or_404(GroupProfile, id=group_id)
    print(group_profile.creator == request.user)
    tasks = Task.objects.filter(current_group=group_profile)
    achievements = Achievement.objects.filter(current_group=group_profile)
    return render(
        request, 'group_tasks.html', {
            'group_profile': group_profile,
            'tasks': tasks,
            'achievements': achievements
        })


@login_required(login_url='login')
def task_list(request):
    tasks = Task.objects.all()
    return render(request, 'task_list.html', {'tasks': tasks})


@login_required(login_url='login')
def create_group(request):
    if request.method == 'POST':
        form = GroupCreationForm(request.POST)
        print(request.POST)
        if form.is_valid():
            new_group = form.save()
            user_email = form.cleaned_data.get('user_email')
            print('user_email', user_email)
            if user_email:
                user = User.objects.get(email=user_email)
                print('user', user)
                new_group.user_set.add(user)

            GroupProfile.objects.create(group=new_group, creator=request.user)

        return redirect('userprofile')
    else:
        form = GroupCreationForm()

    return render(request, 'create_group.html', {'form': form})


@login_required(login_url='login')
def group_view(request, profile_group_id):
    print(profile_group_id)
    profile = get_object_or_404(Profile, id=request.user.id)
    profile_group = get_object_or_404(GroupProfile, id=profile_group_id)
    tasks = Task.objects.filter(current_group=profile_group)
    print(tasks)
    participants = Profile.objects.filter(user__groups__id=profile_group_id)
    tasks = Task.objects.filter(current_group__id=profile_group_id)
    print(tasks)
    achievements = Achievement.objects.filter(
        current_group__id=profile_group_id)
    creator = Profile.objects.get(id=profile_group.creator.id)
    return render(
        request, 'group_view.html', {
            'profile': profile,
            'user': request.user,
            'profile_group': profile_group,
            'creator': creator,
            'participants': participants,
            'tasks': tasks,
            'achievements': achievements,
            'is_creator': request.user == profile_group.creator
        })


@login_required(login_url='login')
def add_user_to_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    if request.method == 'POST':
        user_email = request.POST['user_email']
        user = User.objects.get(email=user_email)
        group.user_set.add(user)
        return redirect('group', profile_group_id=group_id)


@login_required(login_url='login')
def delete_group(request):
    group_id = request.POST['group_id']
    group = get_object_or_404(Group, id=group_id)

    if request.user.has_perm(
            'auth.delete_group') or group.profile.creator == request.user:
        group.delete()

    return redirect('userprofile')


def delete_task(request):
    task_id = request.POST['task_id']
    group_id = request.POST['group_id']
    task = get_object_or_404(Task, id=task_id)
    task.delete()

    return redirect('group', profile_group_id=group_id)


@login_required(login_url='login')
def achievement_list(request):
    # Achievements obtained by completing tasks
    completed_task_achievements = Achievement.objects.filter(
        task_achievement__user=request.user,
        task_achievement__complete=True).distinct()

    # Achievements created for groups where the user is the creator
    created_group_achievements = Achievement.objects.filter(
        current_group__creator=request.user).distinct()

    # Combine all unique achievements
    all_achievements = (completed_task_achievements
                        | created_group_achievements).distinct()

    return render(request, 'achievement_list.html',
                  {'achievements': all_achievements})


@login_required
def bulk_assign_achievements(request, group_id):
    if request.method == 'POST':
        group_profile = get_object_or_404(GroupProfile,
                                          id=group_id,
                                          creator=request.user)
        task_id = request.POST['task_id']
        task = Task.objects.get(id=task_id, current_group=group_profile)
        achievement_name = request.POST['achievement']
        achievement = Achievement.objects.filter(title=achievement_name)[0]
        task.achievement = achievement
        if task.user:
            user_profil = Profile.objects.get(user=task.user)
            user_profil.achievement.add(achievement)
            user_profil.score += achievement.weight
            user_profil.save()
        task.save()
        return redirect('group', profile_group_id=group_id)
        # task.save()
        # for key, value in request.POST.items():
        #     if key.startswith('achievement_'):
        #         task_id = key.split('_')[1]
        #         achievement_id = value
        #         task = Task.objects.get(id=task_id,
        #                                 current_group=group_profile)
        #         if achievement_id:
        #             achievement = Achievement.objects.get(id=achievement_id)
        #             task.achievement = achievement
        #             if task.user:
        #                 user_profil = Profile.objects.get(user=task.user)
        #                 user_profil.achievement.add(achievement)
        #                 user_profil.score += achievement.weight
        #                 user_profil.save()
        #         else:
        #             task.achievement = None
        #         task.save()
        # return redirect('group_tasks', group_id=group_id)
    # Add else condition for GET request or error handling


@login_required(login_url='login')
def edit_profile(request):
    userprofile = Profile.objects.get(user=request.user)
    form = ProfileEditForm(instance=userprofile)
    if request.method == 'POST':
        form = ProfileEditForm(request.POST,
                               request.FILES,
                               instance=userprofile)
        if form.is_valid():
            form.save()
            return redirect('userprofile')
        else:
            print('fail')
    return render(request, 'edituserprofile.html', {'form': form})
