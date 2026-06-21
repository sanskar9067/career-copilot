"""
URL configuration for careercopilot project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from user.views import signup, login
from userinfo.views import create_user_info, update_user_info
from resumeanalyzer.views import index_resume_view, retrieve_resume_view
from atsscore.views import score_resume_view
from intervieweragent.views import interviewer_agent_view, get_interview_plan_view, generate_results_view
from roadmapgenerator.views import roadmap_generator_view
urlpatterns = [
    path('admin/', admin.site.urls),
    path('signup/', signup, name='signup'),
    path('login/', login, name='login'),
    path('create_user_info/', create_user_info, name='create_user_info'),
    path('update_user_info/', update_user_info, name='update_user_info'),
    path('index_resume/', index_resume_view, name='index_resume'),
    path('retrieve_resume/', retrieve_resume_view, name='retrieve_resume'),
    path('score_resume/', score_resume_view, name='score_resume'),
    path('interviewer_agent/', interviewer_agent_view, name='interviewer_agent'),
    path('get_interview_plan/', get_interview_plan_view, name='get_interview_plan'),
    path('generate_results/', generate_results_view, name='generate_results'),
    path('roadmap_generator/', roadmap_generator_view, name='roadmap_generator'),
]
