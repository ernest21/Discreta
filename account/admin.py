from django.contrib import admin
from account.models import *

admin.site.register(UserProfile)
admin.site.register(Carrera)
admin.site.register(Profesor)
admin.site.register(Materia)
admin.site.register(MateriaDadas)
admin.site.register(ProfesorRate)
admin.site.register(Periods)
