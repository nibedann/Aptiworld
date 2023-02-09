from django.contrib import admin

# Register your models here.
from .models import *
admin.site.register(Quiz)

class AnswerInLine(admin.TabularInline):
    model = Answer
    
class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerInLine]
    
class AvatarAdmin(admin.ModelAdmin):
    randomly_field = ('id',)


admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer)
admin.site.register(Marks_Of_User)
admin.site.register(Avatar, AvatarAdmin)