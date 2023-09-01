from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from .forms import EmailPostForm, CommentForm
from django.core.mail import send_mail
from django.views.decorators.http import require_POST




# CLASS-BASED VIEWS
class PostListView(ListView):
    '''
    Alternative post list view
    '''
    queryset = Post.published.all()
    context_object_name = 'posts' # for the query results
    paginate_by = 3 # this define the pagination of results returning 3 objects per page
    template_name = 'blog/post/list.html'


# FUNCTIONS-BASED VIEWS
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
    # list of active comments for this post
    comments = post.comments.filter(active=True)
    form = CommentForm()
        
    return render(request, 'blog/post/detail.html', {'post':post,
                                                    'comments': comments,
                                                    'form': form})


def post_share(request, post_id):
    # retrieve post by id
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    sent = False

    if request.method == 'POST':
        # form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # form fields passed validation
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(
                post.get_absolute_url())
            subject = f"{cd['name']} recommends you read "\
                f"{post.title}"
            message = f"Read {post.title} at {post_url}\n\n" \
                f"{cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, 'manuelgualitov@gmail.com',
                    [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post,
                                                    'form': form,
                                                    'sent': sent})


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED) # retrieve a published post by its id
    comment = None # this store the comment object when it gets created
    # a comment was posted
    form = CommentForm(data=request.POST) # instantiate the form using the submitted POST data
    if form.is_valid(): # this validates using is_valid() method
        # create a comment object without saving it to the database
        comment = form.save(commit=False) # if form is valid, create a new Comment object, creates an instance of the model that the form is linked to and saves it to the database
        # assing the post to the comment
        comment.post = post # we assign the post to the comment we created
        # save the comment to the database
        comment.save() # save the new comment to the database by calling its save() method
    return render(request, 'blog/post/comment.html', {'post':post,
                                                    'form':form,
                                                    'comment':comment})

