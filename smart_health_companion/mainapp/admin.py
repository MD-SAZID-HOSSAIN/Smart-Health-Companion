from django.contrib import admin
from .models import Tip


@admin.register(Tip)
class TipAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "is_published", "created_at")
    list_filter = ("category", "is_published", "created_at")
    search_fields = ("title", "summary", "content")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("-created_at",)
