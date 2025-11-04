from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.cache import cache
from django.contrib.contenttypes.models import ContentType


class GenericForeignKeyChoicesAPIView(APIView):
    allowed_models = []  
    value_fields = {} 
    text_fields = {} 
    show_model_name = False

    def get_show_model_name(self, *args, **kwargs):
        return self.show_model_name

    def get_allowed_models(self, *args, **kwargs):
        return self.allowed_models
    
    def get_value_fields(self, *args, **kwargs):
        return self.value_fields

    def get_text_fields(self, *args, **kwargs):
        return self.text_fields

    def get_queryset(self, model, *args, **kwargs):
        return model.objects.all()

    def get_querysets(self, *args, **kwargs):
        if hasattr(self, 'querysets') and self.querysets:
            return self.querysets
        
        self.querysets = [self.get_queryset(model) for model in self.get_allowed_models()]
        return self.querysets
    
    def get_values_list(self, queryset, filters, value_field, text_field, *args, **kwargs):
        return queryset.filter(**filters).values(value_field, text_field)

    def get_filters(self, query_params):
        return {key: value for key, value in query_params.items()}

    def get_data(self, query_params):
        querysets = self.get_querysets()
        filters = self.get_filters(query_params)
        data = []

        for queryset in querysets:
            model = queryset.model
            value_field = self.get_value_fields().get(model, 'pk')
            text_field = self.get_text_fields().get(model, 'name')
            value_list = self.get_values_list(
                queryset, filters, value_field, text_field
            )
            content_type = ContentType.objects.get_for_model(model)

            for obj in value_list:
                value = f'{content_type.pk}:{obj.get(value_field)}'
                model_verbose_name = model._meta.verbose_name
                label = obj.get(text_field)
                label = (
                    f'{model_verbose_name}/{label}' 
                    if self.get_show_model_name() else
                    label
                )
                data.append([value, label])

        return data

    def get(self, request, *args, **kwargs):
        class_name = self.__class__.__name__
        query_params_hash = hash(frozenset(request.query_params.items()))
        
        cache_key = f'{class_name}_{query_params_hash}'
        cached_response = cache.get(cache_key)

        if cached_response:
            return Response(cached_response)

        data = self.get_data(request.query_params)
        
        cache.set(cache_key, data, timeout=60 * 15)
        return Response(data)

