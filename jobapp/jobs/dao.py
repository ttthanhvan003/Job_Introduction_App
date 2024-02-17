from django.db.models.functions import ExtractYear, ExtractQuarter

from .models import Category, Job, User, JobApplication
from django.db.models import Count

def load_jobs(params={}): #tìm kiếm công việc (job) theo id, keyword, tag
    q = Job.objects.filter(active=True)

    kw = params.get('kw')
    if kw:
        q=q.filter(title__icontains=kw)

    cate_id = params.get('cate_id')
    if cate_id:
        q = q.filter(category_id = cate_id)

    tag = params.get('tag')
    if tag:
        q = q.filter(tags__name=tag)

    return q


def load_employer(params={}): #tìm kiếm nhà tuyển dụng (employer) theo id, keyword, tag
    q = User.objects.filter(role=User.EMPLOYER)

    username = params.get('username')
    if username:
        q = q.filter(username=username)

    category_id = params.get('category_id')
    if category_id:
        q = q.filter(joblisting__category_id=category_id)

    tag = params.get('tag')
    if tag:
        q = q.filter(tags__name=tag)

    category_name = params.get('category_name')
    if category_name:
        q = q.filter(joblisting__category_name=category_name)

    return q


def load_candidate(params={}): #tìm kiếm ứng viên (candidate) theo id, keyword, tag
    q = User.objects.filter(role=User.CANDIDATE)

    username = params.get('username')
    if username:
        q = q.filter(username=username)

    category_id = params.get('category_id')
    if category_id:
        q = q.filter(joblisting__category_id=category_id)

    tag = params.get('tag')
    if tag:
        q = q.filter(tags__name=tag)

    category_name = params.get('category_name')
    if category_name:
        q = q.filter(joblisting__category_name=category_name)

    return q

# def count_jobapplication_by_cate():
#
#     def name(self, obj):
#         return f'{obj.job.title} - {obj.candidate.username}'
#
#     return Category.objects.annotate(count=Count('jobs__jobapplication__id')).values("id", 'name', "count").order_by('-count')


def count_applications_by_quarter_and_year():
    return (
        JobApplication.objects
        .annotate(quarter=ExtractQuarter('created_date'))
        .annotate(year=ExtractYear('created_date'))
        .values('quarter', 'year', 'job__category__name')
        .annotate(count=Count('id'))
        .order_by('year', 'quarter', 'job__category__name')
    )


def count_applications_by_year():
    return (
        JobApplication.objects
        .annotate(year=ExtractYear('created_date'))
        .values('year', 'job__category__name')
        .annotate(count=Count('id'))
        .order_by('year', 'job__category__name')
    )

def count_applications_by_quarter():
    return (
        JobApplication.objects
        .annotate(quarter=ExtractQuarter('created_date'))
        .annotate(year=ExtractYear('created_date'))
        .values('quarter', 'year', 'job__category__name')
        .annotate(count=Count('id'))
        .order_by('year', 'quarter', 'job__category__name')
    )