from django.shortcuts import render, get_object_or_404
from .models import Post


# Create your views here.
# we retrieve all the posts with the PUBLISHED status using the published manager created
def post_list(request):
    posts = Post.published.all()
    return render(request, 'blog/post/list.html', {'posts':posts})

# this is the post detail view. takes the id argument of a post, trying to retrieve the post
# object with the given id by calling the get() method
def post_detail(request, id):
    # try:
    #     post = Post.published.get(id=id)
    # except Post.DoesNotExist:
    #     raise Http404("No Post found.")
    # we use get_object_or_404 to retrieve the desired post. Retrieves the object that matches the given parameter
    # or and HTTP 404 exception if no object is found
    post = get_object_or_404(Post, id=id, status=Post.Status.PUBLISHED)
    
    return render(request, 'blog/post/detail.html', {'post':post})
