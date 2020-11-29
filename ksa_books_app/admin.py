from django.contrib import admin
from .models import Subject, Course, Book, Offer, Comment, StudentUser, Notification
from django import forms
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = StudentUser
        fields = ('student_id', 'name')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = f'{user.student_id}@ksa.hs.kr'
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = StudentUser
        fields = ('student_id', 'name', 'is_active', 'is_admin')

    def clean_password(self):
        return ''


@admin.register(StudentUser)
class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    fieldsets = (
        (None, {'fields': ('student_id', 'name', 'email')}),
        ('Notifications', {'fields': ('notify_new_offer', 'notify_books', 'notify_comment', 'notify_sold_to_user',
                                      'notify_sold_to_other', 'notify_new_want', 'notifications',
                                      'unread_notification')}),
        ('Permissions', {'fields': ('is_admin', 'is_superuser', 'is_staff')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('student_id', 'name', 'password1', 'password2'),
        }),
    )
    list_display = ('student_id', 'name', 'is_admin')
    list_filter = ('is_admin',)
    ordering = ('student_id',)
    filter_horizontal = ()


admin.site.unregister(Group)
admin.site.register(Subject)
admin.site.register(Offer)
admin.site.register(Comment)
admin.site.register(Notification)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_filter = ('subject',)
    list_display = ('name', 'subject')


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'subject', 'display_courses')
