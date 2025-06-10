from django.contrib import admin
from django.forms import ModelForm, PasswordInput
from django.utils.safestring import mark_safe

from .models import Variable, VariableSet


class VariableAdminForm(ModelForm):
    """Custom form for Variable admin to handle secret variables."""

    class Meta:
        model = Variable
        fields = ("name", "description", "is_secret", "value")
        widgets = {
            "value": PasswordInput(render_value=False),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only use password input for secret variables
        if self.instance and self.instance.pk:
            if self.instance.is_secret:
                self.fields["value"].widget = PasswordInput(render_value=False)
                self.fields["value"].help_text = "Leave blank to keep current value"
            else:
                self.fields["value"].widget = admin.widgets.AdminTextareaWidget()

    def clean_value(self):
        """Handle empty value for secret variables (keep existing value)."""
        value = self.cleaned_data.get("value")
        if self.instance and self.instance.pk and self.instance.is_secret and not value:
            # Keep the existing encrypted value
            return self.instance.value
        return value


@admin.register(Variable)
class VariableAdmin(admin.ModelAdmin):
    form = VariableAdminForm
    list_display = ("name", "description", "is_secret", "masked_value", "created_at", "updated_at")
    list_filter = ("is_secret", "created_at", "updated_at")
    search_fields = ("name", "description")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("name", "description", "is_secret", "value")}),
        ("Timestamps", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    @admin.display(description="Value")
    def masked_value(self, obj):
        """Display masked value for secret variables."""
        if obj.is_secret:
            return mark_safe('<span style="color: #666;">••••••••</span>')

        return obj.value

    def get_form(self, request, obj=None, **kwargs):
        """Customize form based on whether it's a secret variable."""
        form = super().get_form(request, obj, **kwargs)
        return form


class VariableInline(admin.TabularInline):
    """Inline for variables in VariableSet."""

    model = VariableSet.variables.through
    extra = 1
    verbose_name = "Variable"
    verbose_name_plural = "Variables"


@admin.register(VariableSet)
class VariableSetAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "variable_count", "created_at", "updated_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("name", "description")
    readonly_fields = ("created_at", "updated_at")
    filter_horizontal = ("variables",)
    fieldsets = (
        (None, {"fields": ("name", "description", "variables")}),
        ("Timestamps", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    @admin.display(description="Variables Count")
    def variable_count(self, obj):
        """Display the number of variables in the set."""
        return obj.variables.count()
