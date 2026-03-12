from django.contrib import admin
from .models import Application, Comment, Membership, Project, Task

admin.site.register(Project)
admin.site.register(Membership)
admin.site.register(Application)
admin.site.register(Task)
admin.site.register(Comment)
