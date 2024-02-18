from django.db.models import Q
from django.shortcuts import render
from rest_framework import viewsets, generics, parsers, permissions, status
from rest_framework.decorators import action
from jobs import serializers, paginators
from jobs.models import Category, Job, User, Comment, Rating, JobApplication, Tag
from jobs import perms
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response


class CategoryViewSet(viewsets.ViewSet, generics.ListAPIView, generics.CreateAPIView):
    queryset = Category.objects.all()
    serializer_class = serializers.CategorySerializer
    permission_classes = [perms.IsUserAdmin]

    @action(methods=['get'], detail=True)  # detail=True đi kèm với pk
    def jobs(self, request, pk):  # lấy danh sách các tin ứng tuyển của 1 ngành nghề (category) có id là pk

        category = get_object_or_404(Category, pk=pk)
        joblistings = Job.objects.filter(category=category, active=True).all()

        return Response(serializers.JobSerializer(joblistings, many=True).data)

    def create(self, request):
        c = Category.objects.create(name=request.data.get('name'))

        return Response(serializers.CategorySerializer(c).data, status=status.HTTP_201_CREATED)




class BaseViewSet1(viewsets.ViewSet):
    queryset = Job.objects.filter(active=True).all()
    serializer_class = serializers.JobSerializer


class JobViewSet(BaseViewSet1, generics.ListAPIView):
    pagination_class = paginators.JobPaginator


    def get_queryset(self):
        queries = self.queryset
        q = self.request.query_params.get("q")
        if q:
            queries = queries.filter(title__icontains=q)

        return queries

    def get_permissions(self):
        if self.action in ['upload_job']:
            return [perms.IsUserEmployer()]

        if self.action in ['add_tags']:
            return [perms.IsUserOwner()]

        if self.action in ['search_job']:
            return [perms.IsUserCandidate()]

        return [permissions.AllowAny()]

    @action(methods=['post'], url_path='upload', detail=True)
    def upload_job(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        title = request.data.get('title', '')
        description = request.data.get('description', '')
        employer = request.user


        job_listing = Job.objects.create(
            title=title,
            description=description,
            employer=employer,
            category=category,
        )

        return Response(serializers.JobListingSerializer(job_listing).data, status=status.HTTP_201_CREATED)

    @action(methods=['post'], url_path='tags', detail=True)
    def add_tags(self, request, pk):
        job_listing = get_object_or_404(Job, pk=pk)
        tags_data = request.data.get('tags', [])

        added_tags = []

        for tag_str in tags_data.split(','):
            tag_name = tag_str.strip()
            if tag_name:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                if tag not in job_listing.tags.all():
                    job_listing.tags.add(tag)
                    added_tags.append(tag)

        return Response(serializers.JobListingSerializer(job_listing).data, status=status.HTTP_201_CREATED)

    @action(methods=['get'], url_path='search', detail=False)
    def search_job(self, request):
        keyword = request.data.get('keyword', '')

        return Response(serializers.JobListingSerializer(Job.objects.filter(
            (Q(title__icontains=keyword)) &
            Q(active=True)
        ), many=True).data)


class JobDetailViewSet(BaseViewSet1, generics.RetrieveAPIView):
    pass


class UserViewSet(viewsets.ViewSet, generics.CreateAPIView):
    query = User.objects.filter(is_active=True).all()
    serializer_class = serializers.UserSerializer
    parser_classes = [parsers.MultiPartParser]

    def get_permissions(self):
        if self.action in ['current_user']:
            return [permissions.IsAuthenticated()]

        if self.action in ['add_comment', 'add_rating']:
            return [perms.IsUserCandidate()]

        if self.action in ['search_candidate']:
            return [perms.IsUserEmployer()]

        return [permissions.AllowAny()]

    def get_queryset(self):
        return self.queryset

    @action(methods=['get'], url_name='current-user', detail=False)
    def current_user(self, request):
        request.user
        return Response(serializers.UserSerializer(request.user).data)

    @action(methods=['post'], url_path='comments', detail=True)
    def add_comment(self, request, pk):
        employer_id = pk
        c = Comment.objects.create(candidate_id=self.request.user.id, employer_id=employer_id,
                                   content=request.data.get('content'))

        return Response(serializers.CommentSerializer(c).data, status=status.HTTP_201_CREATED)

    @action(methods=['post'], url_path='ratings', detail=True)
    def add_rating(self, request, pk):
        employer_id = pk
        c = Rating.objects.create(candidate_id=self.request.user.id, employer_id=employer_id,
                                  rate=request.data.get('rate'))

        return Response(serializers.RateSerializer(c).data, status=status.HTTP_201_CREATED)

    @action(methods=['get'], url_path='search_candidate', detail=False)
    def search_candidate(self, request):
        keyword = request.data.get('keyword', '')

        return Response(serializers.UserSerializer(User.objects.filter(
            (Q(title__icontains=keyword) | Q(employer_id__icontains=keyword) | Q(category_id__icontains=keyword)) &
            Q(role='candidate') &
            Q(is_active=True)
        ), many=True).data)



class JobApplicationViewSet(viewsets.ViewSet):
    query = User.objects.filter(is_active=True).all()
    serializer_class = serializers.JobApplicationSerializer()

    def get_permissions(self):
        if self.action in ['submit_job']:
            return [perms.IsUserCandidate()]

        return [permissions.AllowAny()]

    @action(methods=['post'], url_path='submit', detail=True)
    def submit_job(self, request, pk):
        job_id = pk
        introduce = request.data.get('introduce', '')
        resume = request.data.get('resume', '')

        j = JobApplication.objects.create(candidate_id=self.request.user.id, job_id=job_id, introduce=introduce,
                                          resume=resume)

        return Response(serializers.JobApplicationSerializer(j).data, status=status.HTTP_201_CREATED)


class BaseViewSet2(viewsets.ViewSet, generics.DestroyAPIView, generics.UpdateAPIView):
    permission_classes = [perms.OwnerAuthenticated]


class UpdateUserViewSet(viewsets.ViewSet, generics.UpdateAPIView):
    serializer_class = serializers.UserSerializer
    queryset = User.objects.filter(is_active=True).all()
    permission_classes = [perms.IsUserOwner]


class CommentViewSet(BaseViewSet2):
    queryset = Comment.objects.all()
    serializer_class = serializers.CommentSerializer

    @action(methods=['get'], url_path='employer', detail=True)
    def show_cmt(self, request, pk):
        employer = get_object_or_404(User, pk=pk)
        comments = Comment.objects.filter(employer=employer)

        return Response(serializers.CommentSerializer(comments, many=True).data)


class RatingViewSet(BaseViewSet2):
    queryset = Rating.objects.all()
    serializer_class = serializers.RateSerializer

    @action(methods=['get'], url_path='employer', detail=True)
    def show_rating(self, request, pk):
        employer = get_object_or_404(User, pk=pk)
        rate = Rating.objects.filter(employer=employer)

        return Response(serializers.RateSerializer(rate, many=True).data)