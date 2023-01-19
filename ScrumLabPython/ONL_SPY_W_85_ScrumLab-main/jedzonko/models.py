from datetime import datetime
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse


class Recipe(models.Model):
    name = models.CharField(max_length=64, null=False)
    ingredients = models.TextField()
    description = models.TextField()
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(blank=True)
    preparation_time = models.IntegerField()
    votes = models.IntegerField(default=0)
    preparation_method = models.TextField(null=True)


    def save(self, *args, **kwargs):
        self.updated = datetime.now()
        super().save(*args, **kwargs)


class Plan(models.Model):
    name = models.CharField(max_length=64, unique=True)
    description = models.TextField()
    created = models.DateField(auto_now_add=True)
    recipes = models.ManyToManyField(Recipe, through='RecipePlan')


class DayName(models.Model):
    DAYS = (
        ('PON', 'Poniedziałek'),
        ('WTO', 'Wtorek'),
        ('SRO', 'Środa'),
        ('CZW', 'Czwartek'),
        ('PIA', 'Piątek'),
        ('SOB', 'Sobota'),
        ('NIE', 'Niedziela'),
    )
    ORDER = (
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
        (6, 6),
        (7, 7),
    )
    day_name = models.CharField(max_length=3, choices=DAYS, unique=True)
    order = models.IntegerField(choices=ORDER, unique=True)


class RecipePlan(models.Model):
    meal_name = models.CharField(max_length=64)
    recipe = models.ForeignKey(Recipe, on_delete=models.SET_NULL, null=True)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    order = models.IntegerField(null=True)
    day_name = models.ForeignKey(DayName, on_delete=models.CASCADE, null=True)


class Page(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField()
    slug = models.SlugField()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("landig_page", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title.replace('ł', 'l').replace('Ł', 'L'))
        return super().save(*args, **kwargs)

