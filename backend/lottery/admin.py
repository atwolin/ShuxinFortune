from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from .models import FortuneCategory, Fortune


@admin.register(FortuneCategory)
class FortuneCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "order", "is_active", "created_at"]
    list_editable = ["is_active"]
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

    def get_urls(self):
        """Add custom URL for bulk import"""
        urls = super().get_urls()
        custom_urls = [
            path(
                "bulk-import/",
                self.admin_site.admin_view(self.bulk_import_view),
                name="lottery_fortune_bulk_import",
            ),
        ]
        return custom_urls + urls

    def bulk_import_view(self, request):
        """Handle bulk import of fortunes"""
        if request.method == "POST":
            category_id = request.POST.get("category")
            fortunes_text = request.POST.get("fortunes_text", "").strip()

            # Validate inputs
            if not category_id:
                messages.error(request, "請選擇一個分類。")
                return redirect(".")

            if not fortunes_text:
                messages.error(request, "請輸入至少一條籤詩。")
                return redirect(".")

            # Parse lines and filter empty ones
            lines = [line.strip() for line in fortunes_text.split("\n") if line.strip()]

            if not lines:
                messages.error(request, "沒有有效的籤詩內容，請檢查輸入。")
                return redirect(".")

            # Bulk create fortunes in a transaction
            try:
                with transaction.atomic():
                    Fortune.objects.bulk_create(
                        [
                            Fortune(category_id=category_id, message=line)
                            for line in lines
                        ]
                    )
                messages.success(request, f"成功導入 {len(lines)} 條籤詩！")
                return redirect("..")
            except Exception as e:
                messages.error(request, f"導入失敗：{str(e)}")
                return redirect(".")

        # GET request: show form
        context = {
            **self.admin_site.each_context(request),
            "title": "批量導入籤詩",
            "categories": FortuneCategory.objects.filter(is_active=True),
            "opts": self.model._meta,
        }
        return render(request, "admin/lottery/fortune/bulk_import.html", context)

    def changelist_view(self, request, extra_context=None):
        """Override to add bulk import button"""
        extra_context = extra_context or {}
        extra_context["show_bulk_import_button"] = True
        return super().changelist_view(request, extra_context=extra_context)
