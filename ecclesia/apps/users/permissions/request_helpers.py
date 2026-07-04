"""
Utilitários para extração de dados do request.
Centraliza lógica repetida em múltiplos checkers/decorators.
"""


def get_church_id_from_request(request, param: str = "church_id"):
    """
    Extrai o church_id do request tentando múltiplas origens na ordem:
    path params → query params → body JSON → parser_context → atributo direto.
    """
    # Path params (Django Ninja / DRF)
    if hasattr(request, "path_params"):
        value = request.path_params.get(param)
        if value:
            return value

    # Query params
    if hasattr(request, "query_params"):
        value = request.query_params.get(param)
        if value:
            return value

    # Body JSON (DRF)
    if hasattr(request, "data"):
        value = request.data.get(param)
        if value:
            return value

    # parser_context kwargs (DRF)
    if hasattr(request, "parser_context"):
        value = request.parser_context.get("kwargs", {}).get(param)
        if value:
            return value

    # Atributo direto no request
    return getattr(request, param, None)