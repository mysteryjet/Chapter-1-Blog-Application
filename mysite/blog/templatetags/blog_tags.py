# simple tag to retrieve the total posts that have been published on the blog
from django import template
from ..models import Post


# Each module that contains template tags needs to define a variable called 
# register to be a valid tag library. This variable is an instance of template.
# Library, and it’s used to register the template tags and filters of the application
register = template.Library()

@register.simple_tag
def total_posts():
    return Post.published.count()


# specified the template that will be rendered with the returned values using blog/
# post/latest_posts.html
@register.inclusion_tag('blog/post/latest_posts.html')
def show_latest_posts(count=5):
    latest_posts = Post.published.order_by('-publish')[:count]
    return {'latest_posts': latest_posts}