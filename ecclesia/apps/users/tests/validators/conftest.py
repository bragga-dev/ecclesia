# tests/validators/conftest.py
import pytest
from unittest.mock import Mock, MagicMock
from ninja import UploadedFile


@pytest.fixture
def mock_uploaded_file():
    """Fixture para criar um UploadedFile mockado."""
    def _create(name="test.jpg", size=1024, content=b"test"):
        mock_file = MagicMock(spec=UploadedFile)
        mock_file.name = name
        mock_file.size = size
        mock_file.read = Mock(return_value=content)
        return mock_file
    return _create


@pytest.fixture
def valid_cpfs():
    """Lista de CPFs válidos para testes."""
    return [
        "529.982.247-25",
        "111.444.777-35",
        "123.456.789-09",
        "52998224725",
        "11144477735",
    ]


@pytest.fixture
def invalid_cpfs():
    """Lista de CPFs inválidos para testes."""
    return [
        "000.000.000-00",
        "111.111.111-11",
        "123.456.789-10",
        "529.982.247-26",
        "abc.def.ghi-jk",
    ]


@pytest.fixture
def valid_cnpjs():
    """Lista de CNPJs válidos para testes."""
    return [
        "11.222.333/0001-81",
        "12.345.678/0001-95",
        "48.887.708/0001-60",
        "11222333000181",
        "12345678000195",
    ]


@pytest.fixture
def invalid_cnpjs():
    """Lista de CNPJs inválidos para testes."""
    return [
        "00.000.000/0000-00",
        "11.111.111/1111-11",
        "11.222.333/0001-82",
        "12.345.678/0001-00",
        "abc.def.ghi/jkl-mn",
    ]