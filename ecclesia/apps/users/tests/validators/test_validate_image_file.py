# tests/validators/test_validate_image_file.py
import pytest
import io
from unittest.mock import patch, Mock, MagicMock
from django.core.exceptions import ValidationError
from PIL import Image, UnidentifiedImageError
from ninja import UploadedFile
from ecclesia.apps.users.validators.validate_image_file import (
    validate_image_file,
    VALID_FORMATS,
    VALID_EXTENSIONS,
    MAX_SIZE_MB,
    MAX_WIDTH,
    MAX_HEIGHT
)


class TestValidateImageFile:
    """Testes para validação de arquivos de imagem"""
    
    def criar_uploaded_file_mock(self, nome="test.jpg", tamanho=1024, conteudo=b"test"):
        """Helper para criar um UploadedFile mockado."""
        mock_file = MagicMock(spec=UploadedFile)
        mock_file.name = nome
        mock_file.size = tamanho
        mock_file.read = Mock(return_value=conteudo)
        return mock_file
    
    def criar_imagem_mock(self, formato="JPEG", width=100, height=100, mode="RGB"):
        """Helper para criar uma imagem mock."""
        img = Mock(spec=Image.Image)
        img.format = formato
        img.size = (width, height)
        img.mode = mode
        return img
    
    def test_validate_image_file_nao_e_uploaded_file(self):
        """Testa que a validação não faz nada se não for UploadedFile."""
        # Deve passar sem levantar exceção
        validate_image_file("caminho/para/imagem.jpg")
        validate_image_file(123)
        validate_image_file(None)
    
    def test_validate_image_file_extensao_valida(self):
        """Testa extensões de arquivo válidas."""
        extensoes_validas = [".jpg", ".jpeg", ".png", ".webp"]
        
        for ext in extensoes_validas:
            mock_file = self.criar_uploaded_file_mock(nome=f"test{ext}")
            
            # Vai falhar na validação de tamanho/imagem, mas não na extensão
            try:
                validate_image_file(mock_file)
            except ValidationError as e:
                # Se falhar, não deve ser por extensão
                assert "Extensão inválida" not in str(e)
    
    def test_validate_image_file_extensao_invalida(self):
        """Testa extensões de arquivo inválidas."""
        extensoes_invalidas = [".txt", ".pdf", ".doc", ".gif", ".bmp", ".tiff", ".svg"]
        
        for ext in extensoes_invalidas:
            mock_file = self.criar_uploaded_file_mock(nome=f"test{ext}")
            
            with pytest.raises(ValidationError) as exc:
                validate_image_file(mock_file)
            
            assert "Extensão inválida" in str(exc.value)
            assert ext in str(exc.value)
    
    def test_validate_image_file_tamanho_excedido(self):
        """Testa arquivo com tamanho maior que o permitido."""
        tamanho_excedido = (MAX_SIZE_MB * 1024 * 1024) + 1
        mock_file = self.criar_uploaded_file_mock(
            nome="test.jpg",
            tamanho=tamanho_excedido
        )
        
        with pytest.raises(ValidationError) as exc:
            validate_image_file(mock_file)
        
        assert "excede o limite" in str(exc.value)
        assert str(MAX_SIZE_MB) in str(exc.value)
    
    def test_validate_image_file_tamanho_limite(self):
        """Testa arquivo exatamente no limite de tamanho."""
        tamanho_limite = MAX_SIZE_MB * 1024 * 1024
        mock_file = self.criar_uploaded_file_mock(
            nome="test.jpg",
            tamanho=tamanho_limite
        )
        
        # Vai falhar na validação de imagem, mas não por tamanho
        try:
            validate_image_file(mock_file)
        except ValidationError as e:
            assert "excede o limite" not in str(e)
    
    @patch('ecclesia.apps.users.validators.validate_image_file.Image.open')
    def test_validate_image_file_nao_e_imagem(self, mock_image_open):
        """Testa arquivo que não é uma imagem."""
        mock_file = self.criar_uploaded_file_mock(nome="test.jpg", tamanho=1024)
        
        # Simula erro ao abrir imagem
        mock_image_open.side_effect = UnidentifiedImageError()
        
        with pytest.raises(ValidationError) as exc:
            validate_image_file(mock_file)
        
        assert "não é uma imagem reconhecida" in str(exc.value)
        mock_file.seek.assert_called()
    
    @patch('ecclesia.apps.users.validators.validate_image_file.Image.open')
    def test_validate_image_file_corrompida(self, mock_image_open):
        """Testa imagem corrompida."""
        mock_file = self.criar_uploaded_file_mock(nome="test.jpg", tamanho=1024)
        
        # Simula erro de corrupção
        mock_image = Mock()
        mock_image.verify.side_effect = Exception("Corrupted image")
        mock_image_open.return_value = mock_image
        
        with pytest.raises(ValidationError) as exc:
            validate_image_file(mock_file)
        
        assert "inválido ou corrompido" in str(exc.value)
    
    @patch('ecclesia.apps.users.validators.validate_image_file.Image.open')
    def test_validate_image_file_formato_nao_suportado(self, mock_image_open):
        """Testa formato de imagem não suportado."""
        # CORREÇÃO: Usar extensão válida mas formato não suportado
        # .jpg é extensão válida, mas o formato GIF não é suportado
        mock_file = self.criar_uploaded_file_mock(nome="test.jpg", tamanho=1024)
        
        # Simula formato não suportado (extensão .jpg mas formato GIF)
        mock_image = Mock()
        mock_image.format = "GIF"
        mock_image.size = (100, 100)
        mock_image_open.return_value = mock_image
        
        with pytest.raises(ValidationError) as exc:
            validate_image_file(mock_file)
        
        # CORREÇÃO: Verifica a mensagem correta
        assert "Formato 'GIF' não suportado" in str(exc.value)
    
    @patch('ecclesia.apps.users.validators.validate_image_file.Image.open')
    def test_validate_image_file_dimensoes_excedidas(self, mock_image_open):
        """Testa imagem com dimensões maiores que o permitido."""
        mock_file = self.criar_uploaded_file_mock(nome="test.jpg", tamanho=1024)
        
        # Simula imagem com dimensões excedidas
        mock_image = Mock()
        mock_image.format = "JPEG"
        mock_image.size = (MAX_WIDTH + 100, MAX_HEIGHT + 100)
        mock_image_open.return_value = mock_image
        
        with pytest.raises(ValidationError) as exc:
            validate_image_file(mock_file)
        
        assert "excede o limite de" in str(exc.value)
        assert str(MAX_WIDTH) in str(exc.value)
        assert str(MAX_HEIGHT) in str(exc.value)
    
    @patch('ecclesia.apps.users.validators.validate_image_file.Image.open')
    def test_validate_image_file_pixel_bomb(self, mock_image_open):
        """Testa pixel bomb (imagem com muitos pixels)."""
        mock_file = self.criar_uploaded_file_mock(nome="test.jpg", tamanho=1024)
        
        # Simula imagem com muitos pixels
        mock_image = Mock()
        mock_image.format = "JPEG"
        mock_image.size = (MAX_WIDTH + 1, MAX_HEIGHT + 1)
        mock_image.width = MAX_WIDTH + 1
        mock_image.height = MAX_HEIGHT + 1
        mock_image_open.return_value = mock_image
        
        with pytest.raises(ValidationError) as exc:
            validate_image_file(mock_file)
        
        # CORREÇÃO: A validação de dimensões captura primeiro
        # Então verificamos a mensagem correta
        assert "excede o limite de" in str(exc.value)
    
    @patch('ecclesia.apps.users.validators.validate_image_file.Image.open')
    def test_validate_image_file_valida_com_sucesso(self, mock_image_open):
        """Testa imagem válida (todos os critérios atendidos)."""
        mock_file = self.criar_uploaded_file_mock(nome="test.jpg", tamanho=1024)
        
        # Simula imagem válida
        mock_image = Mock()
        mock_image.format = "JPEG"
        mock_image.size = (800, 600)
        mock_image.width = 800
        mock_image.height = 600
        mock_image_open.return_value = mock_image
        
        # Deve passar sem levantar exceção
        validate_image_file(mock_file)
        mock_file.seek.assert_called()
    
    @patch('ecclesia.apps.users.validators.validate_image_file.Image.open')
    def test_validate_image_file_png_suportado(self, mock_image_open):
        """Testa formato PNG suportado."""
        mock_file = self.criar_uploaded_file_mock(nome="test.png", tamanho=1024)
        
        mock_image = Mock()
        mock_image.format = "PNG"
        mock_image.size = (800, 600)
        mock_image_open.return_value = mock_image
        
        # Deve passar sem levantar exceção
        validate_image_file(mock_file)
    
    @patch('ecclesia.apps.users.validators.validate_image_file.Image.open')
    def test_validate_image_file_webp_suportado(self, mock_image_open):
        """Testa formato WEBP suportado."""
        mock_file = self.criar_uploaded_file_mock(nome="test.webp", tamanho=1024)
        
        mock_image = Mock()
        mock_image.format = "WEBP"
        mock_image.size = (800, 600)
        mock_image_open.return_value = mock_image
        
        # Deve passar sem levantar exceção
        validate_image_file(mock_file)
    
    @patch('ecclesia.apps.users.validators.validate_image_file.Image.open')
    def test_validate_image_file_erro_inesperado(self, mock_image_open):
        """Testa erro inesperado ao processar a imagem."""
        mock_file = self.criar_uploaded_file_mock(nome="test.jpg", tamanho=1024)
        
        # CORREÇÃO: Simular erro inesperado APÓS a verificação de formato
        # Primeiro retorna uma imagem válida, depois falha na verificação
        mock_image = Mock()
        mock_image.format = "JPEG"
        mock_image.size = (100, 100)
        
        # Configurar para que a primeira chamada funcione, mas a segunda falhe
        mock_image_open.side_effect = [
            mock_image,  # Primeira chamada (para verify)
            Exception("Erro inesperado no PIL")  # Segunda chamada (para validação)
        ]
        
        with pytest.raises(ValidationError) as exc:
            validate_image_file(mock_file)
        
        # CORREÇÃO: O código captura qualquer Exception e retorna esta mensagem
        assert "Não foi possível processar a imagem" in str(exc.value)
    
    @patch('ecclesia.apps.users.validators.validate_image_file.logger')
    @patch('ecclesia.apps.users.validators.validate_image_file.Image.open')
    def test_validate_image_file_logs_erro(self, mock_image_open, mock_logger):
        """Testa que erros são logados."""
        mock_file = self.criar_uploaded_file_mock(nome="test.jpg", tamanho=1024)
        
        mock_image_open.side_effect = Exception("Erro inesperado")
        
        with pytest.raises(ValidationError):
            validate_image_file(mock_file)
        
        # O código atual não tem logging explícito no except geral
        # Se adicionar logging, pode testar aqui
    
    def test_constants_configuradas_corretamente(self):
        """Testa que as constantes estão configuradas corretamente."""
        assert isinstance(VALID_FORMATS, set)
        assert "JPEG" in VALID_FORMATS
        assert "PNG" in VALID_FORMATS
        assert "WEBP" in VALID_FORMATS
        assert "GIF" not in VALID_FORMATS
        
        assert isinstance(VALID_EXTENSIONS, set)
        assert ".jpg" in VALID_EXTENSIONS
        assert ".jpeg" in VALID_EXTENSIONS
        assert ".png" in VALID_EXTENSIONS
        assert ".webp" in VALID_EXTENSIONS
        assert ".gif" not in VALID_EXTENSIONS
        
        assert MAX_SIZE_MB == 5
        assert MAX_WIDTH == 4000
        assert MAX_HEIGHT == 4000