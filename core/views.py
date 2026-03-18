import json
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .forms import ApplicationForm, CommentForm, ProjectForm, SignUpForm, TaskForm
from .models import Application, Membership, Project, Task

def home(request):
    projects = Project.objects.filter(recruitment_status='open')[:6]
    stats = {'projects': Project.objects.count(), 'users': User.objects.count(), 'tasks': Task.objects.count()}
    return render(request, 'core/home.html', {'projects': projects, 'stats': stats})

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully.')
            return redirect('dashboard')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def dashboard(request):
    created_projects = Project.objects.filter(creator=request.user)
    joined_projects = Project.objects.filter(memberships__user=request.user).exclude(creator=request.user).distinct()
    application_status = Application.objects.filter(applicant=request.user).select_related('project')
    contribution_rows = Project.objects.filter(memberships__user=request.user).annotate(task_count=Count('tasks', distinct=True)).distinct()[:6]
    return render(request, 'core/dashboard.html', {'created_projects': created_projects, 'joined_projects': joined_projects, 'application_status': application_status, 'contribution_rows': contribution_rows})

@login_required
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.creator = request.user
            project.save()
            Membership.objects.create(user=request.user, project=project, role='leader')
            messages.success(request, 'Project created successfully.')
            return redirect('project_detail', pk=project.pk)
    else:
        form = ProjectForm()
    return render(request, 'core/project_form.html', {'form': form})

@login_required
def project_explore(request):
    query = request.GET.get('q', '').strip()
    projects = Project.objects.filter(recruitment_status='open').exclude(memberships__user=request.user).distinct()
    if query:
        projects = projects.filter(Q(title__icontains=query) | Q(description__icontains=query) | Q(required_skills__icontains=query))
    return render(request, 'core/project_explore.html', {'projects': projects, 'query': query})

@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    app_form = ApplicationForm()
    has_applied = Application.objects.filter(applicant=request.user, project=project).exists()
    return render(request, 'core/project_detail.html', {'project': project, 'has_applied': has_applied, 'app_form': app_form, 'is_member': project.is_member(request.user), 'is_leader': project.is_leader(request.user)})

@login_required
@require_POST
def apply_to_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.is_member(request.user):
        messages.info(request, 'You are already a member of this project.')
        return redirect('project_detail', pk=pk)
    form = ApplicationForm(request.POST)
    if form.is_valid():
        application = form.save(commit=False)
        application.applicant = request.user
        application.project = project
        application.save()
        messages.success(request, 'Application submitted.')
    else:
        messages.error(request, 'Please correct the application form.')
    return redirect('project_detail', pk=pk)

@login_required
def manage_applications(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if not project.is_leader(request.user):
        return HttpResponseForbidden('Only the project leader can manage applications.')
    filter_value = request.GET.get('status', 'pending')
    applications = project.applications.select_related('applicant')
    if filter_value in {'pending', 'accepted', 'declined'}:
        applications = applications.filter(status=filter_value)
    return render(request, 'core/applications_manage.html', {'project': project, 'applications': applications, 'filter_value': filter_value})

@login_required
@require_POST
def application_decision(request, pk):
    application = get_object_or_404(Application, pk=pk)
    # Only the project leader can approve or decline applications.
    if not application.project.is_leader(request.user):
        return HttpResponseForbidden('Only the leader can update applications.')
    decision = request.POST.get('decision')
    if decision == 'accept':
        application.status = 'accepted'
        application.save(update_fields=['status'])
        # get_or_create prevents a duplicate Membership record if this
        # endpoint is called more than once for the same applicant (e.g. double-click).
        Membership.objects.get_or_create(user=application.applicant, project=application.project, defaults={'role': 'member'})
        messages.success(request, 'Applicant accepted.')
    elif decision == 'decline':
        application.status = 'declined'
        application.save(update_fields=['status'])
        messages.info(request, 'Applicant declined.')
    return redirect('manage_applications', pk=application.project.pk)

@login_required
def task_board(request, pk):
    project = get_object_or_404(Project, pk=pk)
    # Only project members can access the task board;
    # returns 403 immediately to prevent data leakage to unauthorised users.
    if not project.is_member(request.user):
        return HttpResponseForbidden('Only project members can view the task board.')
    # prefetch_related avoids N+1 queries when rendering assignees
    # and comments for each task card in the template.
    columns = {
        'todo': project.tasks.filter(status='todo').prefetch_related('assignees', 'comments'),
        'doing': project.tasks.filter(status='doing').prefetch_related('assignees', 'comments'),
        'done': project.tasks.filter(status='done').prefetch_related('assignees', 'comments'),
    }
    return render(request, 'core/task_board.html', {'project': project, 'columns': columns, 'is_leader': project.is_leader(request.user)})

@login_required
def task_create(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if not project.is_member(request.user):
        return HttpResponseForbidden('Only project members can create tasks.')
    if request.method == 'POST':
        form = TaskForm(request.POST, project=project)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            task.created_by = request.user
            task.save()
            form.save_m2m()
            messages.success(request, 'Task created.')
            return redirect('task_board', pk=project.pk)
    else:
        form = TaskForm(project=project)
    return render(request, 'core/task_form.html', {'form': form, 'project': project})

@login_required
@require_POST
def update_task_status(request, pk):
    task = get_object_or_404(Task, pk=pk)
    # Membership check ensures only project members can mutate task state,
    # even if a user constructs a direct POST request to this endpoint.
    if not task.project.is_member(request.user):
        return JsonResponse({'error': 'Unauthorised'}, status=403)
    data = json.loads(request.body.decode('utf-8'))
    new_status = data.get('status')
    # Whitelist valid statuses to prevent arbitrary value injection into the database.
    if new_status not in {'todo', 'doing', 'done'}:
        return JsonResponse({'error': 'Invalid status'}, status=400)
    task.status = new_status
    # update_fields limits the SQL UPDATE to only the changed columns,
    # avoiding accidental overwrites of unrelated fields.
    task.save(update_fields=['status', 'updated_at'])
    return JsonResponse({'message': 'Task updated', 'status': task.get_status_display(), 'task_id': task.pk, 'new_status_key': new_status})

@login_required
@require_POST
def add_comment(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if not task.project.is_member(request.user):
        return HttpResponseForbidden('Only project members can comment.')
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.task = task
        comment.author = request.user
        comment.save()
        messages.success(request, 'Comment added.')
    else:
        messages.error(request, 'Comment cannot be empty.')
    return redirect('task_board', pk=task.project.pk)
