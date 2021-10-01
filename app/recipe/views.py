from rest_framework import viewsets, mixins
# line above ables us to get acces to the CRUD functions
# thanks to generic viwsets and mixins DRF features such as
# create, list, retrieve...
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Ingredient, Recipe

from recipe import serializers


class BaseRecipeAttrViewSet(viewsets.GenericViewSet,
                            mixins.ListModelMixin,
                            mixins.CreateModelMixin):
    """Base viewset for user owned recipe attributes"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    # We override this mixins.ListModelMixin feature getting
    # tags associated to the user who made the request
    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        return self.queryset.filter(user=self.request.user).order_by('-name')

        # We override this mixins.CreateModelMixin feature to be able
        # to create a new tag associated to the user who made the request
    def perform_create(self, serializer):
        """Create a new object"""
        serializer.save(user=self.request.user)


class TagViewSet(BaseRecipeAttrViewSet):
    """Manage tags in the database"""
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class IngredientViewSet(BaseRecipeAttrViewSet):
    """Manage ingredients in the database"""
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer


# We use ModelViewSet because we want to provide the class with all of the
# functionalities that a ViewSet can bring to us
# .list(), .retrieve(), .create()...
# Using ModelViewSet we don't need to use any mixin
# We used GenericViewSet before because we only wanted
# to bring to these classes
# some functionalities, not all of them. Thats why we used mixins
class RecipeViewSet(viewsets.ModelViewSet):
    """Manage recipes in the database"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Recipe.objects.all()
    # Here we are LISTING data from recipes which returns Recipe objects
    serializer_class = serializers.RecipeSerializer

    def get_queryset(self):
        """Retrieve the recipes for the authenticated user"""
        return self.queryset.filter(user=self.request.user)

    # We override this function because we want to RETRIEVE data from 1 recipe
    # Then we need to get the serializer which does that
    def get_serializer_class(self):
        """Return appropiate serializer class"""
        # If we are retrieving info from one Recipe obj
        # we will return the appropiate serializer
        if self.action == 'retrieve':
            return serializers.RecipeDetailSerializer
        # Othwerwise, we will return de default serializer defined lines above
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new Recipe obj owned by the user who made the request"""
        serializer.save(user=self.request.user)
