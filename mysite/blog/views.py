from django.shortcuts import render, get_object_or_404
from .models import Post
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.
# we retrieve all the posts with the PUBLISHED status using the published manager created
def post_list(request):
    post_list = Post.published.all()
    # pagination with 3 posts per page
    paginator = Paginator(post_list, 3) # instantiate paginator class with the number of objects to return
    page_number = request.GET.get('page', 1) # retrive the page GET HTTP parameter and store it in the page_number variable
    # added a try and except block to manage the EmptyPage exception when retrieving a page.
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        # if page_number is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        # if page_number is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages)
    
    # posts = paginator.page(page_number)  obtain objects for the page calling page() method. Returns a page object that we store in the posts variable
    return render(request, 'blog/post/list.html', {'posts':posts}) # pass the age number and the posts object to the template

# this is the post detail view. takes the id argument of a post, trying to retrieve the post
# object with the given id by calling the get() method
def post_detail(request, year, month, day, post):
    # try:
    #     post = Post.published.get(id=id)
    # except Post.DoesNotExist:
    #     raise Http404("No Post found.")
    # we use get_object_or_404 to retrieve the desired post. Retrieves the object that matches the given parameter
    # or and HTTP 404 exception if no object is found
    post = get_object_or_404(Post, status=Post.Status.PUBLISHED,
                            # this take the year, month and day and post arguments and retrieve 
                            # a published post with the given slug and publication date
                            slug=post,
                            publish__year=year,
                            publish__month=month,
                            publish__day=day)
    
    return render(request, 'blog/post/detail.html', {'post':post})
