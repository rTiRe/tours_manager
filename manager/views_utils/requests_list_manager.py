"""Module for work with agency requests list."""

from os import getenv

from django.core.paginator import Paginator
from django.http import HttpRequest
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse
from dotenv import load_dotenv

from ..models import Account, AgencyRequests
from .page_utils import get_pages_slice

load_dotenv()
DEFAULT_REQUESTS_PER_PAGE = 15


class AgencyRequestsListManager:
    """Manager for work with list of requests agencies."""

    def __init__(
        self,
        request: HttpRequest,
        agency_requests: list[AgencyRequests] | tuple[AgencyRequests],
    ) -> None:
        """Init method.

        Args:
            request: HttpRequest - request from user.
            agency_requests: list[AgencyRequests] | tuple[AgencyRequests] - agencies requests.
        """
        self.request = request
        self.agency_requests = agency_requests
        self.paginator = Paginator(
            agency_requests,
            getenv('REQUESTS_PER_PAGE', DEFAULT_REQUESTS_PER_PAGE),
        )

    def render_agency_request_card(self, agency_request: AgencyRequests) -> str:
        """Render review card.

        Args:
            agency_request: AgencyRequests - AgencyRequest for render card.

        Returns:
            str: rendered card.
        """
        return render_to_string(
            'parts/agency_request_card.html',
            {
                'agency_request': agency_request,
            },
            request=self.request,
        )

    def render_agency_requests_list(self, page: int) -> str:
        """Render list of agencies requests.

        Args:
            page: int - number of page for render list.

        Returns:
            str: rendered list.
        """
        rendered_requests = []
        requests_page = self.paginator.get_page(page)
        for request in requests_page:
            rendered_request_card = self.render_agency_request_card(request)
            rendered_requests.append(rendered_request_card)
        return render_to_string(
            'parts/agency_requests_list.html',
            {
                'agency_requests': rendered_requests,
            },
            request=self.request,
        )

    def render_agency_requests_block(self) -> str:
        """Render block of agencies requests list.

        Returns:
            str: rendered block.
        """
        if self.request.method == 'POST':
            redirect_link = reverse('my_profile')
            if 'accept' in self.request.POST.keys():
                account_id = self.request.POST.get('id')
                account = Account.objects.filter(id=account_id).first()
                agency_request = AgencyRequests.objects.filter(account=account).first()
                if agency_request:
                    account.agency = agency_request.agency
                    account.save()
                    agency_request.delete()
                    return redirect(redirect_link)
                return redirect(redirect_link)
            if 'decline' in self.request.POST.keys():
                account_id = self.request.POST.get('id')
                account = Account.objects.filter(id=account_id).first()
                agency_request = AgencyRequests.objects.filter(account=account).first()
                if agency_request:
                    agency_request.agency.delete()
                    agency_request.delete()
                    return redirect(redirect_link)
                return redirect(redirect_link)
        page = int(self.request.GET.get('r_page', 1))
        agency_requests_list = self.render_agency_requests_list(page=page)
        num_pages = int(self.paginator.num_pages)
        pages_slice = get_pages_slice(page, num_pages)
        pages_slice = ''.join(pages_slice)
        return render_to_string(
            'parts/agency_requests_block.html',
            {
                'request': self.request,
                'agency_requests_list': agency_requests_list,
                'pages': {
                    'current': page,
                    'total': num_pages,
                    'slice': pages_slice,
                },
                'style_files': [
                    'css/tours.css',
                    'css/pages.css',
                ],
            },
            request=self.request,
        )
