from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from .forms import UserReviewForm, TourForm, TourEditForm
from .models import Account, Review, Tour, Agency
from .validators import get_datetime
from django.core.paginator import Paginator


def convert_errors(errors: dict) -> dict:
    readable_dict = {}
    for field_name, field_errors in errors.items():
        for error in field_errors:
            error = str(error)
            if error.startswith("['") and error.endswith("']"):
                error = error[2:-2]
                readable_dict[field_name] = error
    return readable_dict


class ReviewManager:
    def __init__(
        self,
        request: HttpRequest,
        reviews: list[Review] | tuple[Review],
        link_to_tour: bool = False,
        items_per_page: int = 5,
    ) -> None:
        self.request = request
        self.reviews = reviews
        self.link_to_tour = link_to_tour
        self.reviews_count = len(reviews)
        self.paginator = Paginator(reviews, items_per_page)

    def get_authenticated_user_review(self) -> Review | None:
        if self.request.user.is_authenticated:
            account = Account.objects.get(account=self.request.user)
        else:
            account = None
        user_review = None
        for review in self.reviews:
            if review.account == account:
                user_review = review
                break
        return user_review, account

    def create(self, tour: Tour, account: Account, rating: int, text: str) -> Review:
        return Review.objects.create(
            tour=tour,
            account=account,
            rating=rating,
            text=text,
            created=get_datetime(),
        )

    def delete(self, review: Review) -> HttpResponseRedirect:
        review.delete()
        tour = review.tour
        username = review.account.account.username
        if not self.link_to_tour:
            return redirect(f'/tour/{tour}')
        return redirect(f'/profile/{username}')

    def render(self, review: Review, form_create: bool = False) -> str:
        if review:
            tour = review.tour
        else:
            tour_id = self.request.path.split('/')[-2]
            tour = Tour.objects.get(id=tour_id)
        initial_data = {}
        if review:
            initial_data['text'] = review.text
            initial_data['rating'] = review.rating
        form = None
        if self.request.method == 'POST' and form_create:
            if 'delete' in self.request.POST.keys():
                return self.delete(review)
            form = UserReviewForm(self.request.POST, initial=initial_data)
            if form.is_valid():
                rating = form.cleaned_data['rating']
                text = form.cleaned_data['text']
                account = Account.objects.filter(account=self.request.user).first()
                if review:
                    review.text = text
                    review.rating = rating
                    review.edited = get_datetime()
                    review.save()
                else:
                    self.create(tour, account, rating, text)
                if self.link_to_tour:
                    redirect_url = f'/profile/{review.account.account.username}'
                else:
                    redirect_url = f'/tour/{tour.id}'
                return redirect(redirect_url)
        if form_create:
            form = UserReviewForm(initial=initial_data)
        return render_to_string(
            'parts/review.html',
            {
                'form': form,
                'review': review,
                'request': self.request,
                'link_to_tour': self.link_to_tour,
                'style_files': [
                    'css/rating.css',
                    'css/review_create.css'
                ],
            },
            request=self.request,
        )

    def render_reviews_list(self, page: int) -> str:
        rendered_reviews = []
        reviews_page = self.paginator.get_page(page)
        for review in reviews_page:
            if not review or review.account.account == self.request.user:
                rendered_review = self.render(review, form_create=True)
            else:
                rendered_review = self.render(review)
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
            user_review, account = self.get_authenticated_user_review()
            if user_review:
                self.reviews.remove(user_review)
                self.reviews.insert(0, user_review)
            elif self.request.user.is_authenticated and account.agency == None:
                self.reviews.insert(0, None)
        reviews_list = self.render_reviews_list(page=page)
        if isinstance(reviews_list, HttpResponseRedirect):
            return reviews_list
        num_pages = int(self.paginator.num_pages)
        pages_slice = []
        for pg_num in range(page - 2, page + 3):
            if pg_num in range(1, num_pages + 1):
                pages_slice.append(str(pg_num))
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


def render_tour_form(
        request: HttpRequest,
        agency: Agency,
        form_data: dict,
        literals: dict,
        tour: Tour = None,
) -> str:
    errors = {}
    if request.method == 'POST':
        post_data = request.POST.copy()
        post_data['agency'] = str(agency.id)
        if tour:
            form = TourEditForm(instance=tour, data=post_data)
        else:
            form = TourForm(data=post_data, instance=tour)
        if form.is_valid():
            if not tour:
                tour = Tour.objects.create(**form.cleaned_data)
            else:
                tour = form.save(commit=False)
                if post_data.get('avatar_clear') == 'on':
                    tour.avatar.delete()
                if 'avatar' in request.FILES and post_data.get('avatar_clear') != 'on':
                    tour.avatar = request.FILES['avatar']
                tour.save()
            addresses = form.cleaned_data.pop('addresses')
            tour.addresses.set(addresses)
            return redirect('tour', uuid=tour.id)
        else:
            errors = form.errors.as_data()
            errors = convert_errors(errors)
            print(errors)
    else:
        form = TourForm(**form_data)
    return render_to_string(
        'parts/tour_form.html',
        {
            'form': form,
            'errors': errors,
            'title': literals.get('title'),
            'button': literals.get('button'),
            'button_name': literals.get('button_name'),
            'style_files': [
                'css/account_form.css',
                'css/tour_form.css',
            ],
        },
        request=request,
    )
