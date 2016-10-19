from donkidik import settings


def get_paging(request):
    page_number = int(request.GET.get('p', '1'))
    page_size = int(settings.PAGINATION_PAGE_SIZE)
    from_idx = ((page_number - 1) * page_size)
    to_idx = (from_idx + page_size)
    return (from_idx, to_idx)
