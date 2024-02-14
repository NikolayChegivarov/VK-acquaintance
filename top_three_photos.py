
def get_top_three_photos(user_id, vk):
    """Функция получения трех лучших фотографий пользователя"""
    photos = vk.photos.get(owner_id=user_id, album_id='profile', count=3)
    return photos['items']