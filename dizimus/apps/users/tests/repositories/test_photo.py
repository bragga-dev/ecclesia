# dizimus/apps/users/tests/repositories/test_photo.py

import pytest
from unittest.mock import patch
from django.core.files.uploadedfile import SimpleUploadedFile
from dizimus.apps.users.repositories.photo import (
    set_user_photo,
    remove_user_photo,
    set_church_banner,
    remove_church_banner
)


# Constantes (ajuste conforme seu projeto)
DEFAULT_USER_PHOTO = "default/user_img.jpg"
DEFAULT_CHURCH_BANNER = "default/banner.jpg"


@pytest.mark.django_db
class TestPhotoRepository:

    def test_set_user_photo_success(self, member_user):
        """Deve definir foto do usuário"""
        photo_file = SimpleUploadedFile(
            "photo.jpg",
            b"file_content",
            content_type="image/jpeg"
        )

        # Mock para evitar deleção real de arquivo
        with patch.object(member_user.photo, 'delete') as mock_delete:
            updated_user = set_user_photo(member_user, photo_file)

            assert updated_user.photo.name != DEFAULT_USER_PHOTO
            assert updated_user.photo.name.startswith("photos/")
            assert updated_user.photo.name.endswith(".jpg")
            mock_delete.assert_not_called()

    def test_set_user_photo_replaces_existing(self, member_user):
        """Deve substituir foto existente"""
        # Primeira foto
        photo1 = SimpleUploadedFile("photo1.jpg", b"content1", content_type="image/jpeg")
        user_with_photo = set_user_photo(member_user, photo1)
        first_photo_name = user_with_photo.photo.name

        # Segunda foto
        photo2 = SimpleUploadedFile("photo2.jpg", b"content2", content_type="image/jpeg")
        with patch.object(user_with_photo.photo, 'delete') as mock_delete:
            updated_user = set_user_photo(user_with_photo, photo2)

            mock_delete.assert_called_once_with(save=False)
            assert updated_user.photo.name != first_photo_name
            assert updated_user.photo.name.startswith("photos/")
            assert updated_user.photo.name.endswith(".jpg")

    def test_remove_user_photo(self, member_user):
        """Deve remover foto do usuário e restaurar padrão"""
        # Primeiro define uma foto customizada
        photo_file = SimpleUploadedFile("custom.jpg", b"content", content_type="image/jpeg")
        user_with_photo = set_user_photo(member_user, photo_file)

        with patch.object(user_with_photo.photo, 'delete') as mock_delete:
            restored_user = remove_user_photo(user_with_photo)

            assert restored_user.photo.name == DEFAULT_USER_PHOTO
            mock_delete.assert_called_once_with(save=False)

    def test_remove_user_photo_already_default(self, member_user):
        """Deve não fazer nada se foto já é a padrão"""
        with patch.object(member_user.photo, 'delete') as mock_delete:
            restored_user = remove_user_photo(member_user)

            assert restored_user.photo.name == DEFAULT_USER_PHOTO
            mock_delete.assert_not_called()

    def test_set_church_banner_success(self, church_user):
        """Deve definir banner da igreja"""
        banner_file = SimpleUploadedFile(
            "banner.jpg",
            b"banner_content",
            content_type="image/jpeg"
        )
        church = church_user.church

        with patch.object(church.banner, 'delete') as mock_delete:
            updated_church = set_church_banner(church, banner_file)

            assert updated_church.banner.name != DEFAULT_CHURCH_BANNER
            assert updated_church.banner.name.startswith("church_banners/")
            assert updated_church.banner.name.endswith(".jpg")
            mock_delete.assert_not_called()

    def test_set_church_banner_replaces_existing(self, church_user):
        """Deve substituir banner existente"""
        church = church_user.church

        # Primeiro banner
        banner1 = SimpleUploadedFile("banner1.jpg", b"content1", content_type="image/jpeg")
        church_with_banner = set_church_banner(church, banner1)
        first_banner_name = church_with_banner.banner.name

        # Segundo banner
        banner2 = SimpleUploadedFile("banner2.jpg", b"content2", content_type="image/jpeg")
        with patch.object(church_with_banner.banner, 'delete') as mock_delete:
            updated_church = set_church_banner(church_with_banner, banner2)

            mock_delete.assert_called_once_with(save=False)
            assert updated_church.banner.name != first_banner_name
            assert updated_church.banner.name.startswith("church_banners/")
            assert updated_church.banner.name.endswith(".jpg")

    def test_remove_church_banner(self, church_user):
        """Deve remover banner e restaurar padrão"""
        church = church_user.church

        # Define banner customizado
        banner_file = SimpleUploadedFile("custom_banner.jpg", b"content", content_type="image/jpeg")
        church_with_banner = set_church_banner(church, banner_file)

        with patch.object(church_with_banner.banner, 'delete') as mock_delete:
            restored_church = remove_church_banner(church_with_banner)

            assert restored_church.banner.name == DEFAULT_CHURCH_BANNER
            mock_delete.assert_called_once_with(save=False)

    def test_remove_church_banner_already_default(self, church_user):
        """Deve não fazer nada se banner já é o padrão"""
        church = church_user.church

        with patch.object(church.banner, 'delete') as mock_delete:
            restored_church = remove_church_banner(church)

            assert restored_church.banner.name == DEFAULT_CHURCH_BANNER
            mock_delete.assert_not_called()