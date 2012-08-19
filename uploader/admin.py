from django.contrib import admin
from uploader.models import User, FOF, Frame

class FrameInline(admin.TabularInline):
    model = Frame
    extra =  5

class FOFInline(admin.TabularInline):
    model = FOF
    extra =  7

class UserInline(admin.TabularInline):
    model = User
    extra = 3

class FrameAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['url']}),
        ('Index', {'fields': ['index']}),
        ('FOF', {'fields': ['fof']}),
    ]
    list_display = ('url', 'index')

class FOFAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['name']}),
        ('Size', {'fields': ['size']}),
    ]
    inlines = [FrameInline]
    list_display = ('name', 'size')
    
class UserAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['device_id']}),
        ('Name', {'fields': ['name']}),
    ]
    inlines = [FOFInline]
    list_display = ('device_id', 'name')    


admin.site.register(User, UserAdmin)
admin.site.register(FOF, FOFAdmin)
admin.site.register(Frame, FrameAdmin)
