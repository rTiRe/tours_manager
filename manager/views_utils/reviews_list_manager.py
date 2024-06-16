from os import getenv

from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from dotenv import load_dotenv

from ..forms import UserReviewForm
from ..models import Account, Review, Tour
from ..validators import get_datetime
from .page_utils import get_pages_slice

load_dotenv()


class ReviewsListManager:
    def __init__(
        self,
        request: HttpRequest,
        reviews: list[Review] | tuple[Review],
        redirect_url: str,
        review_template_name: str = 'parts/review.html',
    ) -> None:
        self.request = request
        self.reviews = reviews
        self.redirect_url = redirect_url
        self.review_template_name = review_template_name
        self.reviews_count = len(reviews)
        self.paginator = Paginator(reviews, getenv('REVIEWS_PER_PAGE', 10))

    def get_tour(self) -> Tour:
        tour_id = self.request.path.split('/')[-2]
        return Tour.objects.filter(id=tour_id).first()

    def delete(self, review: Review, redirect_url: str) -> HttpResponseRedirect:
        review.delete()
        return redirect(redirect_url)
    
    def render_not_existing_review(self, tour: Tour) -> str:
        account = Account.objects.filter(account=self.request.user).first()
        if self.request.method == 'POST':
            form = UserReviewForm(self.request.POST)
            if form.is_valid():
                rating = form.cleaned_data['rating']
                text = form.cleaned_data['text']
                Review.objects.create(
                    tour=tour,
                    account=account,
                    rating=rating,
                    text=text,
                )
                redirect_url = reverse('tour', kwargs={'uuid': tour.id})
                return redirect(f'{redirect_url}#reviews')
            else:
                ...
                # TODO: errors print
        else:
            form = UserReviewForm()
        return render_to_string(
            'parts/not_created_review.html',
            {
                'form': form.my_render(self.request),
                'account': account,
                'style_files': [
                    'css/rating.css',
                    'css/review_create.css',
                ],
            },
            request=self.request,
        )

    def render_review(self, review: Review, render_form: bool = False) -> str:
        initial_data = {}
        initial_data['rating'] = review.rating
        initial_data['text'] = review.text
        form = None
        if self.request.method == 'POST' and render_form:
            if 'delete' in self.request.POST.keys() and \
            str(review.id) == self.request.POST['delete'] and \
            self.request.user == review.account.account:
                return self.delete(review, self.redirect_url)
            form = UserReviewForm(self.request.POST, initial=initial_data)
            if form.is_valid():
                rating = form.cleaned_data['rating']
                text = form.cleaned_data['text']
                review.rating = rating
                review.text = text
                review.edited = get_datetime()
                review.save()
                return redirect(self.redirect_url)
            else:
                ...
                # TODO: errors print
        if render_form:
            form = UserReviewForm(initial=initial_data)
        style_files = ['css/rating.css', 'css/review_create.css']
        if form:
            form = form.my_render(self.request, review)
            style_files.append('css/review_edit.css')
        return render_to_string(
            self.review_template_name,
            {
                'form': form,
                'review': review,
                'request': self.request,
                'style_files': style_files,
            },
            request=self.request,
        )

    def render_reviews_list(self, page: int) -> str:
        rendered_reviews = []
        reviews_page = self.paginator.get_page(page)
        for review in reviews_page:
            if not review:
                tour = self.get_tour()
                rendered_review = self.render_not_existing_review(tour)
            elif review.account.account == self.request.user:
                rendered_review = self.render_review(review, True)
            else:
                rendered_review = self.render_review(review)
            if isinstance(rendered_review, HttpResponseRedirect):
                return rendered_review
            rendered_reviews.append(rendered_review)
        return render_to_string(
            'parts/reviews_list.html',
            {
                'reviews': rendered_reviews,
            },
            request=self.request,
        )

    def render_reviews_block(self, display: bool = False, check_user_review: bool = True) -> str:
        page = int(self.request.GET.get('page', 1))
        if check_user_review:
            user_review, account = self.get_tour().get_request_user_review(self.request) 
            if user_review:
                self.reviews.remove(user_review)
                self.reviews.insert(0, user_review)
            elif self.request.user.is_authenticated and account.agency == None:
                self.reviews.insert(0, None)
        reviews_list = self.render_reviews_list(page=page)
        if isinstance(reviews_list, HttpResponseRedirect):
            return reviews_list
        num_pages = int(self.paginator.num_pages)
        pages_slice = get_pages_slice(page, num_pages)
        pages_slice = ''.join(pages_slice)
        return render_to_string(
            'parts/reviews.html',
            {
                'request': self.request,
                'reviews_list': reviews_list,
                'pages': {
                    'current': page,
                    'total': num_pages,
                    'slice': pages_slice,
                },
                'display': display,
                'reviews_title_literal': _('Reviews'),
                'reviews_count': self.reviews_count,
                'style_files': [
                    'css/reviews.css',
                    'css/pages.css',
                ],
            },
            request=self.request,
        )
