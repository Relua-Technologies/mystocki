from typing import Any
from django.views.generic import ListView
from .base import BaseModelView
from extra_views import SearchableListMixin
from django.urls import reverse, NoReverseMatch


class BaseListView(SearchableListMixin, BaseModelView, ListView):
    operation_mode = 'Lista'
    template_name = '_list.html'
    list_display = []
    short_descriptions = {}
    paginate_by = 5
    url_name = None
    create_url = None
    update_url = None

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.order_by('pk')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['list_display'] = self.get_context_list_display()
        context['create_url'] = self.get_create_url()
        context['update_url'] = self.get_update_url()
        context['objects_with_values'] = self.get_objects_with_values(context['page_obj'])
        return context

    def get_attribute_by_path(self, obj, attr):
        attrs = attr.split('__')
        attr_value = obj
        for attr_name in attrs:
            attr_value = getattr(attr_value, attr_name)
        return attr_value


    def get_objects_with_values(self, object_list):
        fields = self.list_display
        
        object_list_values = []
        for obj in object_list:
            obj_dict = {
                'object': obj,
                'values': [self.get_attribute_by_path(obj, field_path) for field_path in fields],
            }
            object_list_values.append(obj_dict)
        
        return object_list_values
    
    def get_url_name(self):
        return self.url_name 

    def get_action_url(self, action_type, fake_id=None):
        url_name = self.get_url_name()
        if url_name:
            try:
                if fake_id is not None:
                    full_url = reverse(f'{url_name}_{action_type}', kwargs={'pk': fake_id})
                    clean_url = full_url.replace(f'{fake_id}/', '')
                    return clean_url
                else:
                    return reverse(f'{url_name}_{action_type}')
            except NoReverseMatch:
                return None
        return None

    def get_create_url(self):
        return self.get_action_url('create')
    
    def get_update_url(self):
        return self.get_action_url('update', fake_id=0)
    
    def get_list_display(self):
        return self.list_display
    
    def get_short_descriptions(self):
        return self.short_descriptions
    
    def get_context_list_display(self):
        model_fields = [field.name for field in self.model._meta.get_fields()]
        short_descriptions = self.get_short_descriptions()

        verbose_names = []
        for field_path in self.list_display:
            if field_path in short_descriptions.keys():
                verbose_name = short_descriptions[field_path]
            elif '__' in field_path:
                field_parts = field_path.split('__')
                model = self.model

                for part in field_parts:
                    field_path = model._meta.get_field(part)
                    if getattr(field_path, 'related_model', None):
                        model = field_path.related_model
                    else:
                        break

                verbose_name = f'{model._meta.verbose_name} {field_path.verbose_name}'
            elif field_path in model_fields:
                verbose_name = self.model._meta.get_field(field_path).verbose_name
            else:
                verbose_name = field_path.replace('_', ' ')

            verbose_names.append(verbose_name)
        return verbose_names