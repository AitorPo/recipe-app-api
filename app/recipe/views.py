from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, mixins, status
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
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset
        # return only tags and ingredients assigned to recipes
        if assigned_only:
            queryset = queryset.filter(recipe__isnull=False)

        return queryset.filter(
            user=self.request.user
        ).order_by('-name').distinct()

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

    def _params_to_ints(self, qs):
        """Convert a list of string IDs to a list of integers"""
        # We convert every item in the list to a Integer
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """Retrieve the recipes for the authenticated user"""
        tags = self.request.query_params.get('tags')
        ingredients = self.request.query_params.get('ingredients')
        queryset = self.queryset
        if tags:
            tag_ids = self._params_to_ints(tags)
            # We filter using FK thanks to fk_name__id__in function
            queryset = queryset.filter(tags__id__in=tag_ids)
        if ingredients:
            ingredient_ids = self._params_to_ints(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredient_ids)

        return queryset.filter(user=self.request.user)

    # We override this function because we want to RETRIEVE data from 1 recipe
    # Then we need to get the serializer which does that
    def get_serializer_class(self):
        """Return appropiate serializer class"""
        # If we are retrieving info from one Recipe obj
        # we will return the appropiate serializer
        if self.action == 'retrieve':
            return serializers.RecipeDetailSerializer
        elif self.action == 'upload_image':
            return serializers.RecipeImageSerializer
        # Othwerwise, we will return de default serializer defined lines above
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new Recipe obj owned by the user who made the request"""
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to a recipe"""
        # gets the object referenced by id in the url
        recipe = self.get_object()
        serializer = self.get_serializer(
            recipe,
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
