def ip_address_processor(request):
    return { 'ip_address': request.META['REMOTE_ADDR'] }

def page_path_processor(request):
    return { 'path_info': request.path_info }
    