from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from PIL import Image, UnidentifiedImageError
import os
from django.core.exceptions import ValidationError
from brazilcep import get_address_from_cep, WebService, exceptions as brazil_exc
import re
import logging

logger = logging.getLogger(__name__)



# =========================================================
# VALIDAÇÃO DE IMAGEM
# =========================================================

VALID_FORMATS = {"JPEG", "PNG", "WEBP"}
VALID_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_SIZE_MB = 5
MAX_WIDTH = 4000
MAX_HEIGHT = 4000


def validate_image_file(value):
    if not value:
        return

    # 1. Valida extensão do arquivo antes de abrir
    ext = os.path.splitext(value.name)[-1].lower()
    if ext not in VALID_EXTENSIONS:
        raise ValidationError(
            _("Extensão inválida '%(ext)s'. Use: %(valid)s."),
            params={"ext": ext, "valid": ", ".join(sorted(VALID_EXTENSIONS))},
        )

    # 2. Valida tamanho do arquivo antes de abrir (mais eficiente)
    if value.size > MAX_SIZE_MB * 1024 * 1024:
        raise ValidationError(
            _("O arquivo (%(size).1f MB) excede o limite de %(max)s MB."),
            params={"size": value.size / (1024 * 1024), "max": MAX_SIZE_MB},
        )

    # 3. Abre e verifica a integridade da imagem
    try:
        value.seek(0)
        img = Image.open(value)
        img.verify()  # Detecta arquivos corrompidos
    except UnidentifiedImageError:
        raise ValidationError(_("O arquivo não é uma imagem reconhecida."))
    except Exception:
        raise ValidationError(_("Arquivo inválido ou corrompido."))
    finally:
        value.seek(0)  # Garante reset mesmo em caso de erro

    # 4. Reabre após verify() (obrigatório — verify() invalida o objeto)
    try:
        img = Image.open(value)
        img_format = img.format or ""

        # 5. Valida formato real (não apenas extensão)
        if img_format.upper() not in VALID_FORMATS:
            raise ValidationError(
                _("Formato '%(fmt)s' não suportado. Use: %(valid)s."),
                params={"fmt": img_format, "valid": ", ".join(sorted(VALID_FORMATS))},
            )

        # 6. Valida dimensões
        width, height = img.size
        if width > MAX_WIDTH or height > MAX_HEIGHT:
            raise ValidationError(
                _("A imagem (%(w)dx%(h)d px) excede o limite de %(mw)dx%(mh)d px."),
                params={
                    "w": width, "h": height,
                    "mw": MAX_WIDTH, "mh": MAX_HEIGHT,
                },
            )

        # 7. Bloqueia pixel bomb (imagens com dimensões enganosas)
        if width * height > MAX_WIDTH * MAX_HEIGHT:
            raise ValidationError(_("A imagem possui muitos pixels e pode sobrecarregar o servidor."))

    except ValidationError:
        raise
    except Exception:
        raise ValidationError(_("Não foi possível processar a imagem."))
    finally:
        value.seek(0)  # Deixa o arquivo pronto para uso posterior



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