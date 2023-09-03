# simple tag to retrieve the total posts that have been published on the blog
from django import template
from ..models import Post
from django.db.models import Count
from django.utils.safestring import mark_safe
import markdown


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


@register.simple_tag
def get_most_commented_posts(count=5):
    # build a QuerySet using the annotate() function to aggregate the
    # total number of comments for each post.
    return Post.published.annotate(
                total_comments=Count('comments') #  store the number
                                                # of comments in the computed total_comments field for each Post object
                ).order_by('-total_comments')[:count] #  order the QuerySet by
                                                        # the computed field in descending order.


@register.filter(name='markdown')
def markdown_format(text):
    return mark_safe(markdown.markdown(text))

