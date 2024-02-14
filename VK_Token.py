from urllib.parse import urlencode

"""Здесь мы получаем ссылку на токен"""
# ID приложения VK
APP_ID = '51772280'  # '51852427'
# базовая ссылка из документации VK_API
OAUTH_BASE_URL = 'https://oauth.vk.com/authorize'
# Параметры
params = {
    # обязательные параметры:
    # кто запрашивает - id приложения
    'client_id': APP_ID,
    # ссылка куда пользователь попадает после авторизации
    'redirect_uri': 'https://oauth.vk.com/blank.html',
    # указывает тип отображения страницы авторизации - форма авторизации в отдельном окне;
    'display': 'page',
    # какие права запрашивать
    # 'scope': 'photos, offline, wal, status',
    # что хотим увидеть в результате
    'response_type': 'token'
}
oauth_url = f'{OAUTH_BASE_URL}?{urlencode(params)}'
print(oauth_url)

token = 'vk1.a.Vgk04pxzPWhKyJtMPQWqukH1TI-x0gYLsEjcuzZT9xkRTYEJc_Fw64VKk0rYFMbz530AM07qujbeuLs44dIAs_BASzsM8mqpv5Ur3JZ4cg8-xa0e2KOmmBXjM9UBSRa4OftJUW804X_YMMtTIAZJT4mMNXLrLieXG52QY5wSl8-hJxM-Sh6cx3FANFBPISA5'

