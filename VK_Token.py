from urllib.parse import urlencode

"""Здесь мы получаем ссылку на токен"""
# ID приложения VK
APP_ID = '51772280'
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



