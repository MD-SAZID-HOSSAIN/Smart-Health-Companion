from django.contrib import admin
from .models import Tip, Doctor


@admin.register(Tip)
class TipAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "is_published", "created_at")
    list_filter = ("category", "is_published", "created_at")
    search_fields = ("title", "summary", "content")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("-created_at",)


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ("name", "specialty", "email", "phone", "is_published", "created_at")
    list_filter = ("specialty", "is_published", "created_at")
    search_fields = ("name", "specialty", "email", "phone", "bio")
    ordering = ("-created_at",)
