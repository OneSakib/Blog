from django.shortcuts import render, get_object_or_404, HttpResponseRedirect, HttpResponse
from .models import Post
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView, DetailView, View
from .forms import EmailPostForm, CommentsForm
from django.core.mail import send_mail


# Create your views here.
class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'

    def get_context_data(self, **kwargs):
        context = super(PostListView, self).get_context_data(**kwargs)
        toppost = Post.published.order_by('-updated')[:15]
        context['toppost'] = toppost
        return context


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post, status='published', publish__year=year, publish__month=month,
                             publish__day=day)
    toppost = Post.published.order_by('-updated')[:15]

    # list of active comment for this post
    comments = post.comments.filter(active=True)
    new_comment = None
    if request.method == 'POST':
        comment_form = CommentsForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
    else:
        comment_form = CommentsForm()
    return render(request, 'blog/post/detail.html',
                  {'post': post, 'toppost': toppost, 'comment_form': comment_form, 'comments': comments,
                   'new_comment': new_comment})


def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False
    post_url=None
    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            to = form.cleaned_data['to']
            comm = form.cleaned_data['comments']
            post_url = request.build_absolute_uri(post.get_absolute_url())
            sent = False
            subject = f" {name} {email} recommends you reading {post.title}"
            message = f"Read {post.title} at {post_url} \n\n {name}'s Comments {comm}"
            try:
                send = send_mail(subject, message, email, [to])
            except Exception as e:
                return HttpResponse(f"Error is : {e}")
            sent = True
    else:
        form = EmailPostForm()
    toppost = Post.published.order_by('-updated')[:15]
    return render(request, 'blog/post/share.html', {'post': post,
                                                    'form': form,
                                                    'sent': sent, 'toppost': toppost, 'post_url': post_url})
