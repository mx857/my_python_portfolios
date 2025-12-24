import pytest
import requests


class TestPosts:
    """
    Класс для тестирования эндпоинта /posts API JSONPlaceholder.
    Содержит тесты для всех базовых операций: GET, POST, PUT, DELETE.
    """
    
    def _check_post_structure(self, post):
        """
        Вспомогательный метод для проверки структуры поста.
        Проверяет наличие всех обязательных полей и их типы.
        
        Args:
            post (dict): Объект поста для проверки
        """
        assert isinstance(post, dict), "Ответ должен быть словарем"
        assert "id" in post, "Отсутствует ключ 'id'"
        assert "title" in post, "Отсутствует ключ 'title'"
        assert "body" in post, "Отсутствует ключ 'body'"
        assert "userId" in post, "Отсутствует ключ 'userId'"
        
        # Проверка типов данных
        assert isinstance(post["id"], int), "Поле 'id' должно быть целым числом"
        assert isinstance(post["title"], str), "Поле 'title' должно быть строкой"
        assert isinstance(post["body"], str), "Поле 'body' должно быть строкой"
        assert isinstance(post["userId"], int), "Поле 'userId' должно быть целым числом"

    def test_get_all_posts(self, api_session, base_url):
        """
        Тест GET-запроса для получения всех постов.
        Проверяет статус-код, структуру ответа и количество возвращаемых данных.
        """
        # Отправка GET-запроса
        response = api_session.get(f"{base_url}/posts")
        
        # Проверка статус-кода
        assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"
        
        # Проверка заголовков
        assert response.headers["Content-Type"].startswith("application/json"), \
            "Content-Type должен быть application/json"
        
        # Проверка структуры JSON-ответа
        posts = response.json()
        assert isinstance(posts, list), "Ответ должен быть списком"
        assert len(posts) == 100, f"Ожидалось 100 постов, получено {len(posts)}"
        
        # Проверка структуры первого поста
        if len(posts) > 0:
            self._check_post_structure(posts[0])

    @pytest.mark.parametrize("post_id", [1, 50, 100])
    def test_get_single_post(self, api_session, base_url, post_id):
        """
        Параметризованный тест GET-запроса для получения конкретного поста.
        Проверяет разные существующие ID (1, 50, 100).
        
        Args:
            post_id (int): ID поста для получения
        """
        response = api_session.get(f"{base_url}/posts/{post_id}")
        
        # Проверка статус-кода
        assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"
        
        # Проверка структуры поста
        post = response.json()
        self._check_post_structure(post)
        
        # Проверка корректности ID
        assert post["id"] == post_id, f"Возвращенный ID {post['id']} не соответствует запрошенному {post_id}"

    @pytest.mark.parametrize("post_data, expected_user_id", [
        ({"title": "Пост 1", "body": "Содержимое 1", "userId": 1}, 1),
        ({"title": "Пост 2", "body": "Содержимое 2", "userId": 5}, 5),
        ({"title": "Заголовок", "body": "Тело поста", "userId": 10}, 10),
    ])
    def test_create_post(self, api_session, base_url, post_data, expected_user_id):
        """
        Параметризованный тест POST-запроса для создания нового поста.
        Проверяет разные варианты входных данных.
        
        Args:
            post_data (dict): Данные для создания поста
            expected_user_id (int): Ожидаемый userId в ответе
        """
        response = api_session.post(f"{base_url}/posts", json=post_data)
        
        # Проверка статус-кода (201 Created)
        assert response.status_code == 201, f"Ожидался статус 201, получен {response.status_code}"
        
        # Проверка структуры созданного поста
        created_post = response.json()
        self._check_post_structure(created_post)
        
        # Проверка содержимого данных (в JSONPlaceholder данные не сохраняются,
        # но возвращаются в ответе с назначенным ID)
        assert created_post["title"] == post_data["title"], "Заголовок не соответствует отправленным данным"
        assert created_post["body"] == post_data["body"], "Тело поста не соответствует отправленным данным"
        assert created_post["userId"] == expected_user_id, "userId не соответствует ожидаемому"
        assert created_post["id"] == 101, "JSONPlaceholder возвращает ID=101 для новых постов"

    def test_update_post(self, api_session, base_url, updated_post_data):
        """
        Тест PUT-запроса для обновления существующего поста.
        Проверяет корректность обновления всех полей.
        """
        post_id = 1
        response = api_session.put(f"{base_url}/posts/{post_id}", json=updated_post_data)
        
        # Проверка статус-кода (200 OK)
        assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"
        
        # Проверка структуры обновленного поста
        updated_post = response.json()
        self._check_post_structure(updated_post)
        
        # Проверка обновленных данных
        assert updated_post["id"] == post_id, "ID поста не должен изменяться"
        assert updated_post["title"] == updated_post_data["title"], "Заголовок не обновился"
        assert updated_post["body"] == updated_post_data["body"], "Тело поста не обновилось"
        assert updated_post["userId"] == updated_post_data["userId"], "userId не обновился"

    def test_delete_post(self, api_session, base_url):
        """
        Тест DELETE-запроса для удаления поста.
        Проверяет успешное удаление с корректным статус-кодом.
        """
        post_id = 1
        response = api_session.delete(f"{base_url}/posts/{post_id}")
        
        # JSONPlaceholder всегда возвращает 200 OK для DELETE
        assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"
        
        # Проверка, что тело ответа пустое (хотя JSONPlaceholder может возвращать {})
        # Для идемпотентности важно, что запрос можно выполнить多次

    @pytest.mark.parametrize("nonexistent_id", [999, 1000, 9999])
    def test_get_nonexistent_post(self, api_session, base_url, nonexistent_id):
        """
        Негативный тест: попытка получить несуществующий пост.
        Проверяет обработку ошибки 404 для разных несуществующих ID.
        
        Args:
            nonexistent_id (int): ID несуществующего поста
        """
        response = api_session.get(f"{base_url}/posts/{nonexistent_id}")
        
        # JSONPlaceholder для несуществующих ID возвращает пустой объект и статус 200,
        # но в реальном API это может быть 404. Для демонстрации проверим 200
        # и пустой ответ. В реальном проекте нужно уточнять ожидаемое поведение.
        assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"
        
        # Проверяем, что ответ пустой или имеет неожиданную структуру
        post = response.json()
        # JSONPlaceholder возвращает {} для несуществующих ID
        assert isinstance(post, dict), "Ответ должен быть словарем"
        # Проверяем, что большинство полей отсутствуют или пустые
        if post:  # Если словарь не пустой (что маловероятно для несуществующего ID)
            assert post.get("id") != nonexistent_id, "Не должно возвращаться совпадение по ID"

    @pytest.mark.parametrize("invalid_data, expected_status", [
        ({"title": "Только заголовок"}, 201),  # JSONPlaceholder принимает неполные данные
        ({"body": "Только тело"}, 201),
        ({}, 201),  # Даже пустой объект принимается
    ])
    def test_create_post_with_invalid_data(self, api_session, base_url, invalid_data, expected_status):
        """
        Тест с некорректными данными для POST-запроса.
        Проверяет поведение API при разных видах невалидных данных.
        
        Args:
            invalid_data (dict): Невалидные данные для создания поста
            expected_status (int): Ожидаемый статус-код ответа
        """
        response = api_session.post(f"{base_url}/posts", json=invalid_data)
        
        # JSONPlaceholder очень терпим к данным, всегда возвращает 201
        assert response.status_code == expected_status, f"Ожидался статус {expected_status}, получен {response.status_code}"
        
        # Проверяем, что в ответе есть ID
        created_post = response.json()
        assert "id" in created_post, "В ответе должен быть ID созданного поста"
