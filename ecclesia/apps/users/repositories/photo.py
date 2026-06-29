"""
Photo Repository — gerenciamento de fotos e banners.
"""
from django.core.files.uploadedfile import InMemoryUploadedFile
from ecclesia.apps.users.models.user import User
from ecclesia.apps.users.models.church import Church


def set_user_photo(user: User, photo: InMemoryUploadedFile) -> User:
    # Remove arquivo antigo do MinIO antes de substituir
    if user.photo and user.photo.name != "default/user_img.jpg":
        user.photo.delete(save=False)
    user.photo = photo
    user.save(update_fields=["photo"])
    return user


def remove_user_photo(user: User) -> User:
    if user.photo and user.photo.name != "default/user_img.jpg":
        user.photo.delete(save=False)
    user.photo = "default/user_img.jpg"
    user.save(update_fields=["photo"])
    return user


def set_church_banner(church: Church, banner) -> Church:
    if church.banner and church.banner.name != "default/banner.jpg":
        church.banner.delete(save=False)
    church.banner = banner
    church.save(update_fields=["banner"])
    return church


def remove_church_banner(church: Church) -> Church:
    if church.banner and church.banner.name != "default/banner.jpg":
        church.banner.delete(save=False)
    church.banner = "default/banner.jpg"
    church.save(update_fields=["banner"])
    return church