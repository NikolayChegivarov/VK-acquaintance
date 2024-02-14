from params import user_token
import requests
URL = 'https://api.vk.com/method/'
from datetime import datetime, timedelta


def get_city_id_by_name(city_name, vk_user):
    """Функция переводит название города в его цифровой артикул"""
    response = vk_user.database.getCities(q=city_name, count=1)
    if response['items']:
        return response['items'][0]['id']
    else:
        return None

def change_of_date(date_string, years):
    """Функция предназначена для прибавления или вычета лет к дате """
    date_format = '%d.%m.%Y'
    date_obj = datetime.strptime(date_string, date_format)
    new_date_obj = date_obj + timedelta(days=365*years)
    return new_date_obj.strftime(date_format)


def get_user_info(user_id, vk_user):
    """Функция предназначена находить данные у пользователя
     и добавлять их в словарь match_criteria"""
    user_info = vk_user.users.get(user_id=user_id, fields='sex,bdate,city')[0]
    age = user_info.get('bdate') or 'Возраст неуказан'  # возраст
    city_name = user_info.get('city', {}).get('title') or 'Город неуказан'  # город
    city_id = get_city_id_by_name(city_name, vk_user)  # Get the city ID using the city name
    gender = user_info.get('sex') or 'Пол неуказан'  # пол
    if gender == 1:  # если девочка
        match_criteria = {
            'age': {
                'min': age,
                'max': change_of_date(age, 5)
            },
            'gender': gender,
            'city': city_id  # Здесь нужен именно цифровой идентификатор города, а не название.
        }
        result = match_criteria
    elif gender == 2:  # если мальчик
        match_criteria = {
            'age': {
                'min': change_of_date(age, -5),
                'max': age
            },
            'gender': gender,
            'city': city_id  # Здесь нужен именно цифровой идентификатор города, а не название.
        }
        result = match_criteria
    else:
        match_criteria = 'что то пошло не так в функции get_user_info'
        return match_criteria
    return result


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
        'count': search_count,
        'has_photo': 1,
        'verified': 1,
        'is_closed': True,
        'birth_date': f"{min_age}-{max_age}",  # Assuming birth_date format is YYYY-MM-DD
        'fields': 'bdate, sex, city',
    }
    response = requests.get(URL + method, params=params)
    result = []
    for item in response.json()['response']['items']:
        result.append([
            item['first_name'] + ' ' + item['last_name'],
            'https://vk.com/id' + str(item['id']), str(item['id'])
        ])
    return result

def get_top_three_photos(user_id, vk_user):
    """Функция получения трех фотографий пользователя с наибольшим количеством лайков"""
    # Получаем все фотографии из альбома профиля
    photos = vk_user.photos.get(owner_id=user_id, album_id='profile')

    # Создаём словарь для хранения фотографий с их количеством лайков
    photos_likes = {}

    # Проходимся по всем фотографиям и считаем количество лайков
    for photo in photos['items']:
        photo_id = photo['id']
        likes_info = vk_user.likes.getList(type='photo', owner_id=user_id, item_id=photo_id)
        likes_count = likes_info['count']
        # кортеж с photo_id в качестве ключа вместо всего словаря фотографий
        photos_likes[(photo_id)] = likes_count

    # Сортируем фотографии по количеству лайков и возвращаем первые три
    sorted_photos = sorted(photos_likes.items(), key=lambda x: x[1], reverse=True)
    # Use int() to convert strings to integers
    top_three_photos = [(int(user_id), int(photo_id)) for photo_id, _ in sorted_photos[:3]]
    
    return top_three_photos