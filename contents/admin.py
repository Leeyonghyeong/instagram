from django.contrib import admin

from .models import Content, Image, FollowRelations
# Register your models here.


class ImageInline(admin.TabularInline):
    model = Image


class ContentAdmin(admin.ModelAdmin):
    inlines = [ImageInline]
    list_display = ('user', 'text', 'created_at')


admin.site.register(Content, ContentAdmin)


class ImageAdmin(admin.ModelAdmin):
    pass


admin.site.register(Image, ImageAdmin)


class FollowRelationsAdmin(admin.ModelAdmin):
    pass


admin.site.register(FollowRelations, FollowRelationsAdmin)
