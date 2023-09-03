import markdown
from django.contrib.syndication.views import Feed
from django.template.defaultfilters import truncatewords_html
from django.urls import reverse_lazy
from .models import Post

class LatestPostsFeed(Feed):
    title = 'My blog'
    link = reverse_lazy('blog:post_list') # generate the URL for the link attribute. The reverse() method allows you to build URLs by their name and pass optional parameters
    description = 'New posts of my blog.'

    # retrieves the objects to be included in the feed. We retrieve the last five published 
    # posts to include them in the feed
    def items(self):
        return Post.published.all()[:5]
    
    # he item_title(), item_description(), and item_pubdate() methods will receive each object
    # returned by items() and return the title, description and publication date for each item
    def item_title(self, item):
        return item.title

    # we use the markdown() function to convert Markdown content 
    # to HTML and the truncatewords_html() template filter function to cut the description of posts after 
    # 30 words, avoiding unclosed HTML tags
    def item_description(self, item):
        return truncatewords_html(markdown.markdown(item.body), 30)


    def item_pubdate(self, item):
        return item.publish