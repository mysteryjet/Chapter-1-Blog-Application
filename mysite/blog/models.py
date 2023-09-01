from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse

# Create your models here.
# method to implement a manager that will allow us to retrieve posts using the notation Post.published.all()
class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()\
            .filter(status=Post.Status.PUBLISHED)


# Post model that will allow us to store blog posts in the database
class Post(models.Model):

    class Status(models.TextChoices):
        DRAFT = 'DF', 'Draft'
        PUBLISHED = 'PB', 'Published' 

    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique_for_date='publish')
    # this field defines a many-to-one relationship, meaning that each post is written by a user
    # and a user can write any number of posts. Django create a foreign key using the PK of the related model
    author = models.ForeignKey(User,
                            on_delete=models.CASCADE,
                            related_name='blog_posts')
    body = models.TextField()
    # we will use it to store the date and time when the post was published
    publish = models.DateTimeField(default=timezone.now)
    # we will use it to store the date and time when the post was created
    created = models.DateTimeField(auto_now_add=True)
    # we will use it to store the last date and time when the post was updated
    updated = models.DateTimeField(auto_now=True)
    # we will be using Draft and Published statuses for posts
    status = models.CharField(max_length=2,
                            choices=Status.choices,
                            default=Status.DRAFT)


    # this is from the custom manager with notation Post.published.all()
    objects = models.Manager() # the default manager
    published = PublishedManager() # our custom manager

    # this defines metadata for the model. we use the ordering attribute to tell django that it should sort the results
    # by the publish field. the hyphen is used to indicate descending order
    class Meta:
        ordering = ['-publish']
        indexes = [
            models.Index(fields=['-publish']),
        ]

    # this return a string with the human readable representation of the object
    def __str__(self):
        return self.title
    
    # the reverse function build the url dynamically using the url name defined in the url patterns
    def get_absolute_url(self):
        return reverse('blog:post_detail', 
                        args=[self.publish.year,
                            self.publish.month,
                            self.publish.day,
                            self.slug])
    