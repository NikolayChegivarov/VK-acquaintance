from config import user_token
from datetime import datetime
from dateutil.relativedelta import relativedelta
from tqdm import tqdm
import requests
from vk_api.exceptions import ApiError
URL = 'https://api.vk.com/method/'


def get_city_id_by_name(city_name, vk_user):
    """Функция конвертирует название города в его вк идентификатор.
    Используется в модуле main.py/Обработка сообщения как ответ на запрос о городе."""
    response = vk_user.database.getCities(q=city_name, count=1)
    if response['items']:
        return response['items'][0]['id']
    else:
        return None

def change_of_date(date_string, years):
    """Функция предназначена для прибавления или вычета лет к дате рождения пользователя.
    Используется в функции age_range."""
    date_format = '%d.%m.%Y'
    try:
        date_obj = datetime.strptime(date_string, date_format)
        new_date_obj = date_obj + relativedelta(years=years)
        return new_date_obj.strftime(date_format)
    except ValueError:
        return 'Возраст неуказан'

def get_user_info(vk_user, user_id=None, vk_session=None, peer_id=None):
    """Функция предназначена находить данные пользователя.

    Параметры:
    - vk_user: объект VkApi для выполнения запросов к API VK.
    - user_id: идентификатор пользователя, информацию о котором нужно получить.
                Если не указан, функция будет получать информацию о текущем пользователе.
    """
    if user_id is None:
        # Получаем информацию о текущем профиле пользователя
        profile_info = vk_user.account.getProfileInfo()
    else:
        # Получаем информацию о профиле пользователя по его идентификатору
        profile_info = vk_user.users.get(user_ids=user_id, fields='bdate,sex,city')[0]

    # Извлекаем нужные данные из profile_info
    age = profile_info.get('bdate') or 'Возраст неуказан'  # возраст
    city_id = profile_info.get('city', {}).get('id') or 'Город неуказан'
    gender = profile_info.get('sex') or 'Пол неуказан'  # пол
    match_criteria = {
        'age': age,
        'gender': gender,
        'city': city_id  # Используем ID города
    }
    result = match_criteria
    return result

def age_range(user_state):
    """Функция предназначена для установки
    диапазона по возрасту."""
    age = user_state['criteria']['age']
    gender = user_state['criteria']['gender']
    city_id = user_state['criteria']['city']
    if gender == 1:  # если девочка
        match_criteria = {
            'age': {
                'min': change_of_date(age, -5),
                'max': change_of_date(age, 0),
            },
            'gender': gender,
            'city': city_id  # Используем ID города
        }
    elif gender == 2:  # если мальчик
        match_criteria = {
            'age': {
                'min': change_of_date(age, 0),
                'max': change_of_date(age, 5),
            },
            'gender': gender,
            'city': city_id
        }
    else:
        match_criteria = 'что то пошло не так в функции get_user_info'

    user_state['criteria'] = match_criteria
    return user_state

def search_users_info(criteria, search_count=10):
    """Функция предназначена для поиска потенциальных
    партнеров по критериям заданным в get_user_info"""
    user_city = criteria.get('city')
    user_sex = criteria.get('gender')
    min_age = criteria.get('age').get('min')
    max_age = criteria.get('age').get('max')

    if user_sex == 1:
        sex = 2
    else:
        sex = 1

    method = 'users.search'
    params = {
        'access_token': user_token,
        'v': '5.131',
        'sex': sex,
        'city': user_city,
        'count': search_count,  # search_count указывает на максимальное количество пользователей.
        'has_photo': 1,  # у которых есть фотографии в профиле
        'verified': 1,  # Пользователи, имеющие подтвержденный профиль, будут иметь значок верификации, и их профили будут более надежными.
        'is_closed': 0,  # Только открытые профили.
        'birth_date': f"{min_age}-{max_age}",
        'fields': 'bdate, sex, city',
        'not_friends': 1  # Параметр для поиска не по друзьям.
    }
    response = requests.get(URL + method, params=params)
    result = []
    counter = 1
    for item in response.json()['response']['items']:
        result.append([
            item['first_name'] + ' ' + item['last_name'],
            'https://vk.com/id' + str(item['id']),
            str(item['id']),
            str(counter)
        ])
        counter += 1
    return result

def get_top_three_photos(user_id, vk_user):
    """Функция получения трех фотографий пользователя с наибольшим количеством лайков"""
    print('Листаем фоточки.')
    try:
        # Получаем все фотографии из альбома профиля
        photos = vk_user.photos.get(owner_id=user_id, album_id='profile')
        # Создаём словарь для хранения фотографий с их количеством лайков
        photos_likes = {}
        top_three_photos = []
        # Проходимся по всем фотографиям и считаем количество лайков
        for photo in tqdm(photos['items'], desc="Загрузка фотографий", unit="фото"):

            photo_id = photo['id']
            owner_id = photo['owner_id']
            likes_info = vk_user.likes.getList(type='photo', owner_id=owner_id, item_id=photo_id)
            likes_count = likes_info['count']
            # кортеж с photo_id в качестве ключа вместо всего словаря фотографий
            photos_likes[(photo_id)] = likes_count
            # Сортируем фотографии по количеству лайков и возвращаем первые три
            sorted_photos = sorted(photos_likes.items(), key=lambda x: x[1], reverse=True)
            # Правильно форматируем строки для вложений
            top_three_photos = ['photo{}_{}'.format(owner_id, photo_id) for photo_id, _ in sorted_photos[:3]]
        return top_three_photos
    except ApiError as e:
        if e.code == 30:  # Профиль закрытый.
            print(f"Профиль с идентификатором {user_id} является закрытым. Пропускаем.")
            return []  # Вернуть пустой список или обработать при необходимости
        else:
            raise  # Повторно вызовем исключение, если это не проблема конфиденциальности профиля.

def get_next_pipl(pipl, list_of_potential):
    """Функция для переключения на следующего потенциального партнера. """
    current_index = list_of_potential.index(pipl)
    if current_index + 1 < len(list_of_potential):
        return list_of_potential[current_index + 1]
    else:
        return None
