import pytest
import requests


@pytest.fixture(scope="class")
def api_session():
    """
    Фикстура для создания сессии requests.Session с областью действия 'class'.
    Сессия создается один раз для каждого тестового класса и автоматически
    закрывается после выполнения всех тестов в классе.
    
    Returns:
        requests.Session: HTTP-сессия для выполнения запросов
    """
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    yield session
    session.close()


@pytest.fixture(scope="class")
def base_url():
    """
    Фикстура для базового URL API JSONPlaceholder.
    
    Returns:
        str: Базовый URL для всех запросов
    """
    return "https://jsonplaceholder.typicode.com"


@pytest.fixture
def sample_post_data():
    """
    Фикстура с тестовыми данными для создания нового поста.
    
    Returns:
        dict: Тестовые данные для POST-запроса
    """
    return {
        "title": "Тестовый пост",
        "body": "Это содержимое тестового поста для проверки API",
        "userId": 1
    }


@pytest.fixture
def updated_post_data():
    """
    Фикстура с обновленными данными для тестирования PUT-запроса.
    
    Returns:
        dict: Обновленные данные для PUT-запроса
    """
    return {
        "title": "Обновленный тестовый пост",
        "body": "Обновленное содержимое поста",
        "userId": 2
    }
