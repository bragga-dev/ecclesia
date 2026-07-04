# utils/request_helpers.py
def get_church_id_from_request(request, param: str = "church_id"):
    if hasattr(request, 'path_params') and request.path_params.get(param):
        return request.path_params[param]
    if hasattr(request, 'query_params') and request.query_params.get(param):
        return request.query_params[param]
    ...