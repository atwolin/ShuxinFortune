from django.contrib import admin
from .models import FortuneCategory, Fortune


@admin.register(FortuneCategory)
class FortuneCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "order", "is_active", "created_at"]
    list_filter = ["is_active"]
    search_fields = ["name", "description"]
    ordering = ["order", "name"]

    fieldsets = (
        (None, {"fields": ("name", "description", "order", "is_active")}),
        (
            "時間資訊",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )
    readonly_fields = ["created_at", "updated_at"]


class FortuneInline(admin.TabularInline):
    model = Fortune
    extra = 1
    fields = ["message", "is_active"]


@admin.register(Fortune)
class FortuneAdmin(admin.ModelAdmin):
    list_display = ["get_short_message", "category", "is_active", "created_at"]
    list_filter = ["category", "is_active", "created_at"]
    search_fields = ["message", "category__name"]
    ordering = ["category", "-created_at"]

    fieldsets = (
        (None, {"fields": ("category", "message", "is_active")}),
        (
            "時間資訊",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )
    readonly_fields = ["created_at", "updated_at"]

    def get_short_message(self, obj):
        return f"{obj.message[:50]}..." if len(obj.message) > 50 else obj.message

    get_short_message.short_description = "籤詩內容"
