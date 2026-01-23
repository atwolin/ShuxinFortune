from django.db import models
from django.core.validators import MinLengthValidator


class FortuneCategory(models.Model):
    """Category of fortunes (e.g., 'Exam Encouragement', 'Graduation Wishes')"""

    name = models.CharField("Category Name", max_length=50, unique=True)
    description = models.TextField("Description", blank=True)
    order = models.PositiveIntegerField("Display Order", default=0)
    is_active = models.BooleanField("Is Active", default=True)
    created_at = models.DateTimeField("Created At", auto_now_add=True)
    updated_at = models.DateTimeField("Updated At", auto_now=True)

    class Meta:
        verbose_name = "Fortune Category"
        verbose_name_plural = "Fortune Categories"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class Fortune(models.Model):
    """Fortune message associated with a category"""

    category = models.ForeignKey(
        FortuneCategory,
        on_delete=models.CASCADE,
        related_name="fortunes",
        verbose_name="Category",
    )
    message = models.TextField(
        "Fortune Message", validators=[MinLengthValidator(1)], unique=True
    )
    is_active = models.BooleanField("Is Active", default=True)
    created_at = models.DateTimeField("Created At", auto_now_add=True)
    updated_at = models.DateTimeField("Updated At", auto_now=True)

    class Meta:
        verbose_name = "Fortune"
        verbose_name_plural = "Fortunes"
        ordering = ["category", "-created_at"]

    def __str__(self):
        return f"{self.message[:10]}... in {self.category.name}"
