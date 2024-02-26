from jobs.models import Category, Job, Tag, User, Comment, Rating, JobApplication
from rest_framework import serializers



class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password', 'email', 'role', 'avatar']
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }
    def create(self, validated_data):
        data = validated_data.copy()
        user = User(**data)
        user.set_password(data['password'])

        if user.role == 'employer':
            user.is_active = False
        user.save()

        return user

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class JobSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    #tags = serializers.SlugRelatedField(slug_field='name', queryset=Tag.objects.all(), many=True)
    employer = serializers.SlugRelatedField(slug_field='username', queryset=User.objects.all(), many=False)
    #category = serializers.SlugRelatedField(slug_field='id', queryset=Category.objects.all(), many=False)
    category_id = serializers.PrimaryKeyRelatedField(source='category', read_only=True)

    class Meta:
        model = Job
        fields = ['id', 'tags', 'employer', 'category_id', 'created_date', 'updated_date', 'active', 'title', 'description']
        ordering = ['-created_date']




class JobApplicationSerializer(serializers.ModelSerializer):
    candidate = UserSerializer()
    job = JobSerializer()

    class Meta:
        model = JobApplication
        fields = '__all__'



class BaseSerializer(serializers.ModelSerializer):
    candidate = UserSerializer()
    employer = UserSerializer()

class CommentSerializer(BaseSerializer):

    class Meta:
        model = Comment
        fields = ['id', 'content', 'candidate', 'employer']

class RateSerializer(BaseSerializer):
    class Meta:
        model = Rating
        fields = ['id', 'rate', 'candidate', 'employer']