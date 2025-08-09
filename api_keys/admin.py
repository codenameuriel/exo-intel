from django.contrib import admin

from .models import APIKey


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    """
    Admin interface for the APIKey model.
    """

    # method get_key_preview will be used to produce a column value
    # and column name is set by the short_description attribute
    list_display = ("name", "user", "get_key_preview", "created_at")

    readonly_fields = ("key", "created_at")

    def get_key_preview(self, obj):
        return f"{str(obj.key)[:8]}..."

    get_key_preview.short_description = "Key Preview"
