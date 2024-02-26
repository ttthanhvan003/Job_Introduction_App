from datetime import timezone

from django.db import models
from django.contrib.auth.models import AbstractUser
from ckeditor.fields import RichTextField
from cloudinary.models import CloudinaryField



class BaseModel(models.Model):
    created_date = models.DateField(auto_now_add=True, null=True)
    updated_date = models.DateField(auto_now=True, null=True)
    active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class User(AbstractUser):
    EMPLOYER = 'employer'
    CANDIDATE = 'candidate'
    ADMIN = 'admin'

    ROLE_CHOICES = [
        (EMPLOYER, 'Employer'),
        (CANDIDATE, 'Candidate'),
        (ADMIN, 'Admin')
    ]

    avatar = CloudinaryField('avatar', null=False)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, null=False)


    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class Category(BaseModel):
    name = models.CharField(max_length=50, null=False)

    def __str__(self):
        return self.name


class Tag(BaseModel):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Job(BaseModel):
    title = models.CharField(max_length=255)
    description = RichTextField()
    employer = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.RESTRICT, related_query_name='jobs')
    tags = models.ManyToManyField('Tag')

    class Meta:
        unique_together = ('title', 'category')

    def __str__(self):
        return self.title


class JobApplication(BaseModel):

    job = models.ForeignKey(Job, on_delete=models.CASCADE, null=False)
    candidate = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    introduce = RichTextField(blank=True)
    resume = CloudinaryField('resume', null=True)

    # def __str__(self):
    #     return f'{self.job.title} - {self.candidate.username}'


class Interaction(BaseModel):
    employer = models.ForeignKey(User, on_delete=models.CASCADE, null=False, related_name='%(class)s_employer')
    candidate = models.ForeignKey(User, on_delete=models.CASCADE, null=False, related_name='%(class)s_candidate')

    class Meta:
        abstract = True


class Comment(Interaction):
    content = RichTextField()


class Rating(Interaction):
    rate = models.SmallIntegerField(default=0)
