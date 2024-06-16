from ..models import AgencyRequests, Account
from django.http import HttpRequest, HttpResponseRedirect
from dotenv import load_dotenv
from django.shortcuts import redirect
from django.urls import reverse
from os import getenv
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from .page_utils import get_pages_slice

load_dotenv()


class AgencyRequestsListManager:
    def __init__(
        self,
        request: HttpRequest,
        agency_requests: list[AgencyRequests],
    ) -> None:
        self.request = request
        self.agency_requests = agency_requests
        self.paginator = Paginator(agency_requests, getenv('REQUESTS_PER_PAGE', 15))


    def render_agency_request_card(self, agency_request: AgencyRequests) -> str:
        return render_to_string(
            'parts/agency_request_card.html',
            {
                'agency_request': agency_request,
            },
            request=self.request,
        )

    def render_agency_requests_list(self, page: int) -> str:
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
        if self.request.method == 'POST':
            if 'accept' in self.request.POST.keys():
                id = self.request.POST.get('id')
                account = Account.objects.filter(id=id).first()
                agency_request = AgencyRequests.objects.filter(account=account).first()
                if agency_request:
                    agency = agency_request.agency
                    account.agency = agency
                    account.save()
                    agency_request.delete()
                    return redirect(reverse('my_profile'))
                else:
                    return redirect(reverse('my_profile'))
            if 'decline' in self.request.POST.keys():
                id = self.request.POST.get('id')
                account = Account.objects.filter(id=id).first()
                agency_request = AgencyRequests.objects.filter(account=account).first()
                if agency_request:
                    agency = agency_request.agency
                    agency.delete()
                    agency_request.delete()
                    return redirect(reverse('my_profile'))
                else:
                    return redirect(reverse('my_profile'))
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