from django.contrib import admin
from .models import Movie,MyList,MyRating
# Register your models here.


admin.site.register(Movie)
admin.site.register(MyList)
admin.site.register(MyRating)

admin.site.site_title="Admin Panel"
admin.site.site_header="Admin Panel"