import random
from datetime import datetime

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.views import View

from jedzonko.models import Recipe, Plan, DayName, RecipePlan, Page


class LandingPageView(View):
    def get(self, request):
        random_recipes = list(Recipe.objects.all())
        random.shuffle(random_recipes)
        recipe0 = random_recipes[0]
        recipe1 = random_recipes[1]
        recipe2 = random_recipes[2]
        return render(request, "index.html", context={'recipe0': recipe0, 'recipe1': recipe1, 'recipe2': recipe2})


class RecipeListView(View):
    def get(self, request):
        recipes = Recipe.objects.all().order_by('-votes', '-created')
        paginator = Paginator(recipes, 50)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        page_range = paginator.page_range
        return render(request, 'app-recipes.html', context={'page_obj': page_obj, 'page_range': page_range})


class DashboardView(View):
    def get(self, request):
        count_recipes = Recipe.objects.count()
        plan_count = Plan.objects.count()
        last_created_plan = Plan.objects.all().order_by('-created')[0]
        recipeplan = RecipePlan.objects.filter(plan=last_created_plan).order_by('day_name', 'order')
        days = []
        for plan in recipeplan:
            if not (plan.day_name.get_day_name_display() in days):
                days.append(plan.day_name.get_day_name_display())
        # days = DayName.objects.all().order_by('order')
        return render(request, "dashboard.html", context={'count_recipes': count_recipes,
                                                          'plan_count': plan_count,
                                                          'last_created_plan': last_created_plan,
                                                          'recipeplan': recipeplan,
                                                          'days': days
                                                          })


class PlanListView(View):
    def get(self, request):
        plans = Plan.objects.order_by('name')
        paginator = Paginator(plans, 10)
        page = request.GET.get('page')
        plans = paginator.get_page(page)
        return render(request, 'app-schedules.html', {"object_list": plans})


class AddPlanView(View):
    def get(self, request):
        return render(request, 'app-add-schedules.html')

    def post(self, request):
        plan_name = request.POST.get('plan_name')
        plan_description = request.POST.get('plan_description')
        if '' in (plan_name, plan_description):
            return HttpResponse("niekompletne dane")
        Plan.objects.create(name=plan_name, description=plan_description)
        last_id = Plan.objects.all().order_by('-id')[0].id
        return redirect('plan', last_id)


class PlanView(View):
    def get(self, request, id):
        plan = Plan.objects.get(id=id)
        day_names = DayName.objects.all().order_by("order")
        week_plan = []
        for day_number in day_names:
            meals = plan.recipeplan_set.filter(day_name=day_number.id).order_by('order')
            day = DayName.objects.get(id=day_number.id).get_day_name_display()
            week_plan.append((meals, day))
        return render(request, "app-details-schedules.html", context={'plan': plan,
                                                                      'week_plan': week_plan})


class RecipeDetailsView(View):
    def get(self, request, id):
        recipe = get_object_or_404(Recipe, pk=id)
        return render(request, "app-recipe-details.html", {"recipe": recipe})

    def post(self, request, id):
        recipe_id = request.POST.get('recipe_id')
        click = request.POST.get('click')
        if click == "like":
            recipe = Recipe.objects.get(pk=recipe_id)
            recipe.votes += 1
            recipe.save()
        if click == "dont_like":
            recipe = Recipe.objects.get(pk=recipe_id)
            recipe.votes -= 1
            recipe.save()
        return redirect("recipe-details", id=recipe_id)


class RecipeModifyView(View):
    def get(self, request, id):
        try:
            recipe = Recipe.objects.get(pk=id)
        except Recipe.DoesNotExist:
            return HttpResponse('HTTP 404')
        return render(request, "app-edit-recipe.html", context={'recipe': recipe})

    def post(self, request, id):
        name = request.POST.get("name")
        description = request.POST.get("description")
        time = request.POST.get("time")
        preparation_method = request.POST.get("preparation-method")
        ingredients = request.POST.get("ingredients")
        if name and description and time and preparation_method and ingredients:
            Recipe.objects.create(
                name=name,
                description=description,
                preparation_time=time,
                preparation_method=preparation_method,
                ingredients=ingredients
            )
            return redirect("/recipe/list/")
        else:
            messages.error(request, 'Wypełnij poprawnie wszystkie pola')
            return redirect("modify-recipe", id=id)


class AddRecipeView(View):
    def get(self, request):
        return render(request, "app-add-recipe.html")

    def post(self, request):
        name = request.POST.get("name")
        description = request.POST.get("description")
        time = request.POST.get("time")
        preparation_method = request.POST.get("preparation-method")
        ingredients = request.POST.get("ingredients")
        if name and description and time and preparation_method and ingredients:

            new_recipe = Recipe.objects.create(
                name=name,
                description=description,
                preparation_time=time,
                preparation_method=preparation_method,
                ingredients=ingredients
            )
            return redirect("/recipe/list/")
        else:
            ctx = {
                "error_message": "Wypełnij poprawnie wszystkie pola"
            }
            return render(request, "app-add-recipe.html", ctx)


class PlanAddRecipeView(View):
    last_plan = Plan.objects.all().order_by('-created')[0]

    def get(self, request, plan_id_def=last_plan, recipe_id_def=last_plan):
        last_recipe = Recipe.objects.all().order_by('-created')[0]
        plan_list = Plan.objects.all()
        recipe_list = Recipe.objects.all()
        day_list = DayName.objects.all()
        context = {
            'plan_list': plan_list,
            'recipe_list': recipe_list,
            'day_list': day_list,
            'plan_id_def': plan_id_def,
            'recipe_id_def': recipe_id_def
        }
        return render(request, "app-schedules-meal-recipe.html", context)

    def post(self, request):
        plan_id = request.POST.get('plan_id')
        meal_name = request.POST.get('meal_name')
        order = request.POST.get('order')
        recipe = request.POST.get('recipe_id')
        day = request.POST.get('day_name')
        RecipePlan.objects.create(meal_name=meal_name, recipe=Recipe.objects.get(id=recipe), plan=Plan.objects.get(id=plan_id), order=order, day_name=DayName.objects.get(
            id=day))
        return redirect('plan', plan_id)


class ContactView(View):
    def get(self, request):
        try:
            contact = Page.objects.get(slug="contact")
            if contact:
                context = {
                    "contact": contact
                }
                return render(request, "contact.html", context)
        except Page.DoesNotExist:
            return redirect("/#contact")


class AboutView(View):
    def get(self, request):
        try:
            about = Page.objects.get(slug="about")
            if about:
                context = {
                    "about": about
                }
                return render(request, "about.html", context)
        except Page.DoesNotExist:
            return redirect("/#about")