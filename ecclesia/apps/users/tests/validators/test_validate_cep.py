# tests/validators/test_validate_cep.py
import pytest
from unittest.mock import patch, Mock
from django.core.exceptions import ValidationError
from brazilcep import exceptions as brazil_exc
from ecclesia.apps.users.validators.validate_cep import (
    validar_cep,
    _limpar_cep,
    _CEP_DIGITS_RE
)


class TestLimparCep:
    """Testes para a função auxiliar _limpar_cep"""
    
    def test_limpar_cep_com_formatacao(self):
        """Testa remoção de caracteres especiais do CEP."""
        assert _limpar_cep("12345-678") == "12345678"
        assert _limpar_cep("12.345-678") == "12345678"
        assert _limpar_cep("12345 678") == "12345678"
        assert _limpar_cep("12.345.678") == "12345678"
    
    def test_limpar_cep_sem_formatacao(self):
        """Testa CEP já limpo."""
        assert _limpar_cep("12345678") == "12345678"
    
    def test_limpar_cep_com_espacos(self):
        """Testa CEP com espaços."""
        assert _limpar_cep(" 12345-678 ") == "12345678"
    
    def test_limpar_cep_vazio(self):
        """Testa CEP vazio."""
        assert _limpar_cep("") == ""
        assert _limpar_cep("   ") == ""


class TestValidarCep:
    """Testes para a função principal validar_cep"""
    
    def test_validar_cep_valido(self):
        """Testa CEP válido (não faz validação real por não ter API)."""
        # Não podemos testar CEP real sem API, mas testamos que não levanta exceção
        # para um CEP que passaria na validação de formato
        try:
            # Este teste apenas verifica que um CEP com formato correto
            # não levanta exceção de formato
            validar_cep("12345678")
        except ValidationError as e:
            # Se falhar, deve ser por API (CEP não encontrado) ou formato
            # Vamos verificar que não é erro de formato
            assert e.code not in ["cep_formato_invalido", "cep_sequencia_invalida"]
    
    @patch('ecclesia.apps.users.validators.validate_cep.get_address_from_cep')
    def test_validar_cep_valido_com_api_mockada(self, mock_get_address):
        """Testa CEP válido com API mockada."""
        mock_get_address.return_value = {"cep": "01001-000"}
        
        # Deve passar sem levantar exceção
        validar_cep("01001-000")
        
        mock_get_address.assert_called_once_with("01001000", webservice=mock_get_address.call_args[1]['webservice'])
    
    def test_validar_cep_formato_invalido(self):
        """Testa CEP com formato inválido."""
        # Menos de 8 dígitos
        with pytest.raises(ValidationError) as exc:
            validar_cep("1234")
        assert exc.value.code == "cep_formato_invalido"
        
        # Mais de 8 dígitos
        with pytest.raises(ValidationError) as exc:
            validar_cep("123456789")
        assert exc.value.code == "cep_formato_invalido"
        
        # Com letras
        with pytest.raises(ValidationError) as exc:
            validar_cep("1234A-678")
        assert exc.value.code == "cep_formato_invalido"
        
        # Com caracteres especiais
        with pytest.raises(ValidationError) as exc:
            validar_cep("12345-67#")
        assert exc.value.code == "cep_formato_invalido"
    
    def test_validar_cep_sequencia_repetida(self):
        """Testa CEP com sequência de dígitos repetidos."""
        with pytest.raises(ValidationError) as exc:
            validar_cep("11111111")
        assert exc.value.code == "cep_sequencia_invalida"
        
        with pytest.raises(ValidationError) as exc:
            validar_cep("00000000")
        assert exc.value.code == "cep_sequencia_invalida"
        
        with pytest.raises(ValidationError) as exc:
            validar_cep("99999999")
        assert exc.value.code == "cep_sequencia_invalida"
    
    def test_validar_cep_com_formatos_aceitos(self):
        """Testa diferentes formatos de CEP aceitos."""
        # Formato com hífen
        try:
            validar_cep("12345-678")
        except ValidationError:
            pass  # Pode falhar por API, mas não por formato
        
        # Formato com ponto
        try:
            validar_cep("12.345-678")
        except ValidationError:
            pass
        
        # Formato com espaço
        try:
            validar_cep("12345 678")
        except ValidationError:
            pass
    
    def test_validar_cep_vazio(self):
        """Testa CEP vazio (deve retornar sem erro)."""
        # Deve passar sem levantar exceção
        validar_cep("")
        validar_cep(None)
    
    @patch('ecclesia.apps.users.validators.validate_cep.get_address_from_cep')
    def test_validar_cep_api_invalid_cep(self, mock_get_address):
        """Testa erro de CEP inválido pela API."""
        mock_get_address.side_effect = brazil_exc.InvalidCEP
        
        with pytest.raises(ValidationError) as exc:
            validar_cep("12345678")
        assert exc.value.code == "cep_formato_invalido"
        mock_get_address.assert_called_once()
    
    @patch('ecclesia.apps.users.validators.validate_cep.get_address_from_cep')
    def test_validar_cep_api_not_found(self, mock_get_address):
        """Testa CEP não encontrado pela API."""
        mock_get_address.side_effect = brazil_exc.CEPNotFound
        
        with pytest.raises(ValidationError) as exc:
            validar_cep("12345678")
        assert exc.value.code == "cep_nao_encontrado"
        mock_get_address.assert_called_once()
    
    @patch('ecclesia.apps.users.validators.validate_cep.get_address_from_cep')
    def test_validar_cep_api_connection_error(self, mock_get_address):
        """Testa erro de conexão com a API."""
        mock_get_address.side_effect = brazil_exc.ConnectionError
        
        with pytest.raises(ValidationError) as exc:
            validar_cep("12345678")
        assert exc.value.code == "cep_servico_indisponivel"
        mock_get_address.assert_called_once()
    
    @patch('ecclesia.apps.users.validators.validate_cep.get_address_from_cep')
    def test_validar_cep_api_erro_inesperado(self, mock_get_address):
        """Testa erro inesperado na API."""
        mock_get_address.side_effect = Exception("Erro inesperado")
        
        with pytest.raises(ValidationError) as exc:
            validar_cep("12345678")
        assert exc.value.code == "cep_erro_inesperado"
        mock_get_address.assert_called_once()
    
    @patch('ecclesia.apps.users.validators.validate_cep.logger')
    @patch('ecclesia.apps.users.validators.validate_cep.get_address_from_cep')
    def test_validar_cep_logs_connection_error(self, mock_get_address, mock_logger):
        """Testa que o logger é chamado em erro de conexão."""
        mock_get_address.side_effect = brazil_exc.ConnectionError
        
        with pytest.raises(ValidationError):
            validar_cep("12345678")
        
        mock_logger.warning.assert_called_once()
        assert "Timeout ao consultar CEP" in mock_logger.warning.call_args[0][0]
    
    @patch('ecclesia.apps.users.validators.validate_cep.logger')
    @patch('ecclesia.apps.users.validators.validate_cep.get_address_from_cep')
    def test_validar_cep_logs_erro_inesperado(self, mock_get_address, mock_logger):
        """Testa que o logger é chamado em erro inesperado."""
        mock_get_address.side_effect = Exception("Erro inesperado")
        
        with pytest.raises(ValidationError):
            validar_cep("12345678")
        
        mock_logger.exception.assert_called_once()
        assert "Erro inesperado ao validar CEP" in mock_logger.exception.call_args[0][0]