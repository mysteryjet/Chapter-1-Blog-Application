from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from .forms import EmailPostForm, CommentForm, SearchForm
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from taggit.models import Tag
from django.db.models import Count




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
def post_list(request, tag_slug=None):
    post_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tags__in=[tag])
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
    return render(request, 'blog/post/list.html', {'posts':posts,
                                                    'tag': tag}) # pass the age number and the posts object to the template

# this is the post detail view. takes the id argument of a post, trying to retrieve the post
# object with the given id by calling the get() method
def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, status=Post.Status.PUBLISHED,
                            # this take the year, month and day and post arguments and retrieve 
                            # a published post with the given slug and publication date
                            slug=post,
                            publish__year=year,
                            publish__month=month,
                            publish__day=day)
    # list of active comments for this post
    comments = post.comments.filter(active=True)
    # Form for users to comment
    form = CommentForm()

    # List of similar posts
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids)\
    .exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags'))\
    .order_by('-same_tags','-publish')[:4]
        
    return render(request, 'blog/post/detail.html', {'post':post,
                                                    'comments': comments,
                                                    'form': form,
                                                    'similar_posts': similar_posts})


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

# Search Form
def post_search(request):
    form = SearchForm() # instantiate the SearchForm form
    query = None
    results = []

    # create a SearchQuery object, filter results by it, and use SearchRank to order 
    # the results by relevancy
    if 'query' in request.GET:
        form = SearchForm(request.GET) # send the form using the GET method instead of POSTso the resulting URL includes the query parameter 
        if form.is_valid(): # if valid, search for published post with a custom SearchVector instance built with the title and body fields
            query = form.cleaned_data['query']
            search_vector = SearchVector('title', weight='A', config='spanish') + SearchVector('body', weight='B', config='spanish') # pass a config attribute to SearchVector and SearchQuery to use a different search configuration, executes stemming and removes stops in Spanish
            search_query = SearchQuery(query, config='spanish')
            results = Post.published.annotate(
                search=search_vector,
                rank=SearchRank(search_vector, search_query)
                ).filter(rank__gte=0.3).order_by('-rank')
            
    return render(request,
                'blog/post/search.html',
                {'form':form,
                'query':query,
                'results':results})