import unittest
from app import app, db, User, Post
from flask import session
from werkzeug.security import generate_password_hash


class BlogPlatformTestCase(unittest.TestCase):

    def setUp(self):
        """Настройка тестового окружения"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Используем SQLite в памяти
        app.config['SECRET_KEY'] = 'test_secret_key'
        self.app = app.test_client()

        # Создаем контекст приложения
        self.app_context = app.app_context()
        self.app_context.push()

        db.create_all()

        # Создаем тестового пользователя с корректным хэшированием пароля
        self.test_user = User(
            name='Test User',
            email='test@example.com',
            password=generate_password_hash('password123', method='pbkdf2:sha256')
        )
        db.session.add(self.test_user)
        db.session.commit()

    def tearDown(self):
        """Очистка после тестов"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()  # Убираем контекст приложения

    def test_register(self):
        """Тест регистрации нового пользователя"""
        response = self.app.post('/register', data={
            'name': 'New User',
            'email': 'new@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Registration was successful. Please login.', response.data)

    def test_login(self):
        """Тест логина"""
        with self.app as client:
            # Выполняем POST-запрос для входа
            response = client.post('/login', data={
                'email': 'test@example.com',
                'password': 'password123'  # Используем правильный пароль
            }, follow_redirects=True)

            # Проверяем, что авторизация прошла успешно
            self.assertIn(b'Login completed successfully.', response.data)

            # Проверяем, что в сессии установлен user_id
            with client.session_transaction() as sess:
                self.assertIn('user_id', sess)
                self.assertEqual(sess['user_id'], self.test_user.id)

    def test_home_redirect(self):
        """Тест перенаправления с главной страницы при отсутствии логина"""
        response = self.app.get('/', follow_redirects=False)
        self.assertEqual(response.status_code, 302)  # Проверяем код редиректа
        self.assertIn('/login', response.headers['Location'])  # Проверяем, что редирект на /login

    def test_add_post(self):
        """Тест добавления нового поста"""
        with self.app.session_transaction() as sess:
            sess['user_id'] = self.test_user.id

        response = self.app.post('/profile/posts/add', data={
            'title': 'Test Post',
            'content': 'This is a test post content.'
        }, follow_redirects=True)
        self.assertIn(b'Post added successfully.', response.data)

        post = Post.query.filter_by(title='Test Post').first()
        self.assertIsNotNone(post)
        self.assertEqual(post.content, 'This is a test post content.')

    def test_add_friend(self):
        """Тест добавления друга"""
        # Добавляем еще одного пользователя
        friend_user = User(name='Friend User', email='friend@example.com', password='hashed_password')
        db.session.add(friend_user)
        db.session.commit()

        with self.app.session_transaction() as sess:
            sess['user_id'] = self.test_user.id

        response = self.app.get(f'/profile/friends/add/{friend_user.id}', follow_redirects=True)
        self.assertIn(b'User Friend User added as a friend.', response.data)

        self.assertIn(friend_user, self.test_user.friends)

    def test_logout(self):
        """Тест выхода из системы"""
        with self.app as client:
            # Устанавливаем user_id в сессии
            with client.session_transaction() as sess:
                sess['user_id'] = self.test_user.id

            # Выполняем запрос на выход
            response = client.get('/logout', follow_redirects=True)

            # Проверяем, что сообщение об успешном выходе отображается
            self.assertIn(b'You are logged out', response.data)

            # Проверяем, что user_id больше нет в сессии
            with client.session_transaction() as sess:
                self.assertNotIn('user_id', sess)


if __name__ == '__main__':
    unittest.main()
