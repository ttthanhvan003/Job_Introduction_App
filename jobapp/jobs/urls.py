
from django.urls import path, re_path, include
from rest_framework import routers
from jobs import views

router = routers.DefaultRouter()
router.register('categories', views.CategoryViewSet, basename='categories')
router.register('jobs', views.JobViewSet, basename='jobs')
router.register('jobs', views.JobDetailViewSet, basename='jobsdetail')
router.register('users', views.UserViewSet, basename='users')
router.register('comments', views.CommentViewSet, basename='comments')
router.register('ratings', views.RatingViewSet, basename='ratings')
router.register('users', views.UpdateUserViewSet, basename='update')
router.register('jobs', views.JobViewSet, basename='add_tags')
router.register('jobapplications', views.JobApplicationViewSet, basename='submit')





urlpatterns = [
    path('', include(router.urls)),

]
