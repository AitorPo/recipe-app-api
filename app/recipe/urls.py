from django.urls import path, include

from rest_framework.routers import DefaultRouter

from recipe import views

"""
    A default router is a feater of the DRF that will automatically generate
    the urls for our viewset. When you have a viewset
    you may have multiple urls associated to one viewset
    i.e: "/api/recipe/tags/", "/api/recipe/tags/1"
"""
router = DefaultRouter()
router.register('tags', views.TagViewSet)
router.register('ingredients', views.IngredientViewSet)
router.register('recipes', views.RecipeViewSet)

app_name = 'recipe'

urlpatterns = [
    path('', include(router.urls)),
]
