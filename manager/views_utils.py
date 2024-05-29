from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from .forms import UserReviewForm
from .models import Account, Review, Tour
from .validators import get_datetime
from django.shortcuts import redirect
from django.utils.safestring import mark_safe

def render_review(
    request: HttpRequest,
    review: Review,
    form_create: bool = False,
    link_to_tour: bool = False,
) -> str:
    initial_data = {
        'text': review.text if review else '',
        'rating': review.rating if review else ''
    }
    if request.method == 'POST' and form_create:
        if not link_to_tour:
            tour_id = request.path.split('/')[-2]
            tour = Tour.objects.get(id=tour_id)
        if 'delete' in request.POST.keys():
            review.delete()
            if not link_to_tour:
                return redirect(f'/tour/{tour.id}')
            else:
                return redirect(f'/profile/{review.account.account.userame}')
        form = UserReviewForm(request.POST, initial=initial_data)
        if form.is_valid():
            rating = form.cleaned_data['rating']
            text = form.cleaned_data['text']
            account = Account.objects.get(account=request.user) if request.user else None
            if review:
                tour = review.tour
            if review:
                review.text = text
                review.rating = rating
                review.edited = get_datetime()
                review.save()
            else:
                Review.objects.create(
                    tour=tour,
                    account=account,
                    rating=rating,
                    text=text,
                    created=get_datetime(),
                )
            return redirect(f'/tour/{tour.id}')
        
    form = UserReviewForm(initial=initial_data)
    return render_to_string(
        'parts/review.html',
        {
            'form': form,
            'review': review,
            'request': request,
            'link_to_tour': link_to_tour,
            'style_files': [
                'css/rating.css',
                'css/review_create.css'
            ],
        },
        request=request,
    )


def render_reviews(
    request: HttpRequest,
    reviews: list | tuple,
    display: bool = False,
    check_user_review: bool = True,
    link_to_tour: bool = False,
) -> str:
    reviews_count = len(reviews)
    if check_user_review:
        account = Account.objects.get(account=request.user) if request.user else None
        user_review = None
        for review in reviews:
            if review.account == account:
                user_review = review
                break
        if user_review:
            reviews.remove(user_review)
            reviews.insert(0, user_review)
        elif request.user.is_authenticated:
            reviews.insert(0, None)
    rendered_reviews = []
    for review in reviews:
        if not review or review.account.account == request.user:
            rendered_review = render_review(
                request,
                review,
                form_create=True,
                link_to_tour=link_to_tour
            )
        else:
            rendered_review = render_review(request, review, link_to_tour=link_to_tour)
        if isinstance(rendered_review, HttpResponseRedirect):
                return rendered_review
        rendered_reviews.append(rendered_review)

    return render_to_string(
        'parts/reviews.html',
        {
            'reviews': rendered_reviews,
            'request': request,
            'display': display,
            'reviews_title_literal': _('Reviews'),
            'reviews_count': reviews_count,
            'style_files': [
                'css/reviews.css',
            ],
        },
        request=request,
    )

