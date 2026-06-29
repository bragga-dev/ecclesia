from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from brazilcep import get_address_from_cep, WebService, exceptions as brazil_exc
import re
import logging



logger = logging.getLogger(__name__)



# =========================================================
# VALIDAÇÃO DE CEP
# =========================================================

_CEP_DIGITS_RE = re.compile(r"^\d{8}$")


def _limpar_cep(value: str) -> str:
    """Remove qualquer caractere não numérico do CEP."""
    return re.sub(r"\D", "", value.strip())


def validar_cep(value: str) -> None:
    """
    Valida o formato e a existência do CEP via ViaCEP.

    Aceita formatos: '12345-678', '12345678', '12.345-678', etc.
    Lança ValidationError do Django em caso de formato ou CEP inválido.
    """
    if not value:
        return

    cep = _limpar_cep(value)

    # 1. Valida formato antes de bater na API
    if not _CEP_DIGITS_RE.match(cep):
        raise ValidationError(
            _("CEP inválido: informe 8 dígitos numéricos (ex: 12345-678)."),
            code="cep_formato_invalido",
        )

    # 2. Bloqueia CEPs obviamente falsos (00000000, 11111111…)
    if len(set(cep)) == 1:
        raise ValidationError(
            _("CEP inválido: sequência de dígitos repetidos não é permitida."),
            code="cep_sequencia_invalida",
        )

    # 3. Consulta a API externa
    try:
        get_address_from_cep(cep, webservice=WebService.VIACEP)

    except brazil_exc.InvalidCEP:
        raise ValidationError(
            _("CEP '%(cep)s' possui formato inválido."),
            code="cep_formato_invalido",
            params={"cep": value},
        )

    except brazil_exc.CEPNotFound:
        raise ValidationError(
            _("CEP '%(cep)s' não encontrado. Verifique e tente novamente."),
            code="cep_nao_encontrado",
            params={"cep": value},
        )

    except brazil_exc.ConnectionError:
        logger.warning("Timeout ao consultar CEP '%s' via ViaCEP.", cep)
        raise ValidationError(
            _("Não foi possível validar o CEP no momento. Tente novamente em instantes."),
            code="cep_servico_indisponivel",
        )

    except Exception:
        logger.exception("Erro inesperado ao validar CEP '%s'.", cep)
        raise ValidationError(
            _("Erro ao validar o CEP. Tente novamente."),
            code="cep_erro_inesperado",
        )
    
