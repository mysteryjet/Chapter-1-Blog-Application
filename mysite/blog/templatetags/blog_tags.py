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