from django.urls import path, include
import os


class AppURLManager:
    def __init__(self, urls_folder=None):
        if not hasattr(self, 'urls_folder'):
            self.urls_folder = urls_folder

    def include_url_file(self, file_name, url=None):
        file_name_path = f'{self.urls_folder}.{file_name}' 
        prefix = (url or file_name).replace('_', '-')
        return path(f'{prefix}/', include(file_name_path))

    def is_python_module(self, path_to_check):
        return os.path.isdir(path_to_check) and os.path.exists(os.path.join(path_to_check, '__init__.py'))

    @property
    def urlpatterns(self):
        urlpatterns = []

        current_directory = os.getcwd()
        urls_folder_path = f'{current_directory}/{self.urls_folder}'.replace('.', '/')
        
        folder_files_list = os.listdir(urls_folder_path)
        if '__init__.py' in folder_files_list:
            folder_files_list.remove('__init__.py')
        
        for filename in folder_files_list:
            full_path = os.path.join(urls_folder_path, filename)
            
            if filename.endswith('.py'):
                urlpatterns.append(self.include_url_file(filename[:-3]))

            elif self.is_python_module(full_path):
                urlpatterns.append(self.include_url_file(filename))
                
        return urlpatterns
