# tests/utils/test_pagination.py (versão corrigida)
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.db.models import QuerySet
from ecclesia.apps.users.utils.pagination import (
    paginate_queryset, 
    PageOut, 
    PAGE_SIZE_DEFAULT, 
    PAGE_SIZE_MAX
)


class TestPagination:
    
    @pytest.fixture
    def mock_queryset(self):
        """Cria um queryset mockado para testes."""
        qs = Mock(spec=QuerySet)
        qs.count.return_value = 100
        
        # Mock para slicing usando __getitem__ como método
        mock_sliced = Mock(spec=QuerySet)
        mock_sliced.__iter__ = Mock(return_value=iter([Mock(id=i) for i in range(20)]))
        
        # Configurar __getitem__ como um método do mock
        def getitem_side_effect(key):
            if isinstance(key, slice):
                return mock_sliced
            return None
        
        qs.__getitem__ = Mock(side_effect=getitem_side_effect)
        
        return qs
    
    @pytest.fixture
    def mock_serializer(self):
        """Cria um serializer mockado."""
        def serializer(obj):
            return {"id": obj.id}
        return serializer
    
    def test_paginate_queryset_default_page(self, mock_queryset, mock_serializer):
        """Testa paginação com página padrão."""
        result = paginate_queryset(mock_queryset, 1, 20, mock_serializer)
        
        assert isinstance(result, PageOut)
        assert result.total == 100
        assert result.page == 1
        assert result.page_size == 20
        assert result.pages == 5
        assert len(result.items) == 20
        mock_queryset.count.assert_called_once()
        mock_queryset.__getitem__.assert_called_once_with(slice(0, 20))
    
    def test_paginate_queryset_custom_page(self, mock_queryset, mock_serializer):
        """Testa paginação com página customizada."""
        result = paginate_queryset(mock_queryset, 3, 20, mock_serializer)
        
        assert result.page == 3
        assert result.total == 100
        assert result.pages == 5
        mock_queryset.__getitem__.assert_called_once_with(slice(40, 60))
    
    def test_paginate_queryset_custom_page_size(self, mock_queryset, mock_serializer):
        """Testa paginação com tamanho de página customizado."""
        result = paginate_queryset(mock_queryset, 1, 50, mock_serializer)
        
        assert result.page_size == 50
        assert result.pages == 2
        mock_queryset.__getitem__.assert_called_once_with(slice(0, 50))
    
    def test_paginate_queryset_page_size_max_limit(self, mock_queryset, mock_serializer):
        """Testa que o tamanho máximo da página é respeitado."""
        result = paginate_queryset(mock_queryset, 1, 200, mock_serializer)
        
        assert result.page_size == PAGE_SIZE_MAX
        assert result.pages == 1  # 100/100 = 1
    
    def test_paginate_queryset_page_size_min_limit(self, mock_queryset, mock_serializer):
        """Testa que o tamanho mínimo da página é respeitado."""
        result = paginate_queryset(mock_queryset, 1, 0, mock_serializer)
        
        assert result.page_size == 1
        assert result.pages == 100  # 100/1 = 100
    
    def test_paginate_queryset_page_min_limit(self, mock_queryset, mock_serializer):
        """Testa que a página mínima é respeitada."""
        result = paginate_queryset(mock_queryset, -5, 20, mock_serializer)
        
        assert result.page == 1
        mock_queryset.__getitem__.assert_called_once_with(slice(0, 20))
    
    def test_paginate_queryset_empty_queryset(self, mock_serializer):
        """Testa paginação com queryset vazio."""
        empty_qs = Mock(spec=QuerySet)
        empty_qs.count.return_value = 0
        
        # Configurar __getitem__ para retornar lista vazia
        empty_qs.__getitem__ = Mock(return_value=[])
        
        result = paginate_queryset(empty_qs, 1, 20, mock_serializer)
        
        assert result.total == 0
        assert result.pages == 1
        assert len(result.items) == 0
        empty_qs.__getitem__.assert_called_once_with(slice(0, 20))
    
    def test_paginate_queryset_with_serializer_conversion(self):
        """Testa que o serializer é aplicado corretamente a cada item."""
        qs = Mock(spec=QuerySet)
        qs.count.return_value = 3
        
        # Criar objetos com atributos reais em vez de Mocks
        class Item:
            def __init__(self, id, name):
                self.id = id
                self.name = name
        
        mock_items = [
            Item(1, "Item 1"),
            Item(2, "Item 2"),
            Item(3, "Item 3")
        ]
        
        mock_sliced = Mock(spec=QuerySet)
        mock_sliced.__iter__ = Mock(return_value=iter(mock_items))
        qs.__getitem__ = Mock(return_value=mock_sliced)
        
        def custom_serializer(obj):
            return {"id": obj.id, "name": obj.name}
        
        result = paginate_queryset(qs, 1, 10, custom_serializer)
        
        expected_items = [
            {"id": 1, "name": "Item 1"},
            {"id": 2, "name": "Item 2"},
            {"id": 3, "name": "Item 3"}
        ]
        assert result.items == expected_items
    
    def test_paginate_queryset_last_page(self, mock_queryset, mock_serializer):
        """Testa paginação na última página."""
        # Configurar count para 25 para testar última página
        mock_queryset.count.return_value = 25
        
        mock_sliced = Mock(spec=QuerySet)
        mock_sliced.__iter__ = Mock(return_value=iter([Mock(id=i) for i in range(5)]))
        mock_queryset.__getitem__ = Mock(return_value=mock_sliced)
        
        result = paginate_queryset(mock_queryset, 2, 20, mock_serializer)
        
        assert result.page == 2
        assert result.total == 25
        assert result.pages == 2
        assert len(result.items) == 5
        mock_queryset.__getitem__.assert_called_once_with(slice(20, 40))
    
    def test_paginate_queryset_beyond_last_page(self, mock_queryset, mock_serializer):
        """Testa paginação além da última página."""
        mock_queryset.count.return_value = 25
        
        mock_sliced = Mock(spec=QuerySet)
        mock_sliced.__iter__ = Mock(return_value=iter([]))  # Slice vazio
        mock_queryset.__getitem__ = Mock(return_value=mock_sliced)
        
        result = paginate_queryset(mock_queryset, 5, 20, mock_serializer)
        
        assert result.page == 5
        assert result.total == 25
        assert result.pages == 2
        assert len(result.items) == 0
    
    def test_paginate_queryset_with_select_related(self):
        """Testa que select_related é preservado no queryset."""
        qs = Mock(spec=QuerySet)
        qs.count.return_value = 10
        qs.select_related = Mock(return_value=qs)
        
        mock_sliced = Mock(spec=QuerySet)
        mock_sliced.__iter__ = Mock(return_value=iter([Mock(id=i) for i in range(10)]))
        qs.__getitem__ = Mock(return_value=mock_sliced)
        
        def serializer(obj):
            return {"id": obj.id}
        
        qs_with_related = qs.select_related("user")
        result = paginate_queryset(qs_with_related, 1, 10, serializer)
        
        assert result.total == 10
        assert len(result.items) == 10
        qs.select_related.assert_called_once_with("user")
    
    def test_paginate_queryset_multiple_pages_calculation(self):
        """Testa cálculo correto do número de páginas para diferentes totais."""
        qs = Mock(spec=QuerySet)
        
        # Configurar __getitem__ para retornar lista vazia
        qs.__getitem__ = Mock(return_value=[])
        
        def serializer(obj):
            return {"id": obj.id}
        
        # Testar diferentes totais
        test_cases = [
            (0, 20, 1),
            (10, 20, 1),
            (20, 20, 1),
            (21, 20, 2),
            (100, 20, 5),
            (101, 20, 6),
            (1, 20, 1)
        ]
        
        for total, page_size, expected_pages in test_cases:
            qs.count.return_value = total
            result = paginate_queryset(qs, 1, page_size, serializer)
            assert result.pages == expected_pages
            assert result.total == total
            assert result.page == 1
            assert result.page_size == page_size