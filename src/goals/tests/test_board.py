from django.urls import reverse
from django.utils import timezone
from parameterized import parameterized
from rest_framework import status
from rest_framework.test import APITestCase
import datetime

from core.models import User
from goals.models import Board, BoardParticipant, GoalCategory, Goal


class BoardCreateTestCase(APITestCase):

    def setUp(self) -> None:
        self.url = reverse('create_board')

    def test_auth_required(self):
        """Проверяем аутентификацию"""
        response = self.client.post(self.url, {'title': 'board title'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_success(self):
        """Проверяем создание доски"""
        user = User.objects.create_user(
            username='test',
            password='test_password'
        )
        self.client.force_login(user)
        self.assertFalse(Board.objects.exists())
        self.assertFalse(BoardParticipant.objects.exists())
        response = self.client.post(self.url, {'title': 'board title'})
        self.assertTrue(Board.objects.exists())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_board: Board = Board.objects.last()
        self.assertEqual(
            response.json(),
            {
                'id': new_board.id,
                'created': timezone.localtime(new_board.created).isoformat(),
                'updated': timezone.localtime(new_board.updated).isoformat(),
                'title': 'board title',
                'is_deleted': False,
            }
        )
        board_participants = BoardParticipant.objects.filter(
            board=new_board,
            user=user,
        ).all()
        self.assertEqual(len(board_participants), 1)
        self.assertEqual(board_participants[0].role, BoardParticipant.Role.owner)


class BoardRetrievedTestCase(APITestCase):

    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username='test',
            password='test_password'
        )
        self.board = Board.objects.create(title='board_title')
        BoardParticipant.objects.create(board=self.board, user=self.user, role=BoardParticipant.Role.owner)

    @parameterized.expand([
        ('owner', BoardParticipant.Role.owner),
        ('writer', BoardParticipant.Role.writer),
        ('reader', BoardParticipant.Role.reader),
    ])
    def test_success(self, _, role: BoardParticipant.Role):
        """Проверяем получение доски """
        new_user = User.objects.create_user(username='new_test', password='test_password')

        if role is BoardParticipant.Role.owner:
            self.client.force_login(self.user)
        else:
            self.client.force_login(new_user)
            BoardParticipant.objects.create(board=self.board, user=new_user, role=role)

        response = self.client.get(reverse('delete_board', kwargs={'pk': self.board.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_not_participant(self):
        """Проверяем получение доски не участником"""
        new_user = User.objects.create_user(username='new_test_user', password='test_password')
        self.client.force_login(new_user)

        response = self.client.get(reverse('delete_board', kwargs={'pk': self.board.pk}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_deleted_board(self):
        """Проверяем запрос на удаленных досок"""
        self.board.is_deleted = True
        self.board.save(update_fields=('is_deleted',))
        self.client.force_login(self.user)

        response = self.client.get(reverse('delete_board', kwargs={'pk': self.board.pk}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_auth_required(self):
        response = self.client.get(reverse('delete_board', kwargs={'pk': self.board.pk}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class BoardListTestCase(APITestCase):

    def test_auth_required(self):
        response = self.client.get(reverse('list_board'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_success(self):
        """Проверяем сортировку и создание"""
        user = User.objects.create_user(username='test_user', password='test_password')
        boards = Board.objects.bulk_create([
            Board(title='board_3'),
            Board(title='board_1'),
            Board(title='board_2'),
        ])
        boards.append(Board.objects.create(title='board_4', is_deleted=True))
        BoardParticipant.objects.bulk_create([
            BoardParticipant(board=board, user=user)
            for board in boards
        ])
        self.client.force_login(user)

        response = self.client.get(reverse('list_board'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        board_list = response.json()
        self.assertTrue(isinstance(board_list, list))
        self.assertListEqual(
            [board['title'] for board in board_list],
            ['board_1', 'board_2', 'board_3', ]
        )


class CategoryTestCase(APITestCase):
    """тесты на категории"""

    def setUp(self) -> None:
        self.board = Board.objects.create(title='board_title')
        self.url = reverse('create_category')
        self.user = User.objects.create_user(
            username='test',
            password='test_password'
        )
        self.category = GoalCategory.objects.create(title='category_title', user=self.user,
                                                    board=self.board)

    def test_auth_required(self):
        response = self.client.post(self.url, {'title': self.category.title, 'user_id': self.user.id,
                                               'board_id': self.board.id})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_deleted_category(self):
        self.category.is_deleted = True
        self.category.save(update_fields=('is_deleted',))
        self.client.force_login(self.user)

        response = self.client.get(reverse('delete_category', kwargs={'pk': self.category.pk}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_not_participant(self):
        new_user = User.objects.create_user(username='new_test_user', password='test_password')
        self.client.force_login(new_user)

        response = self.client.get(reverse('delete_category', kwargs={'pk': self.category.pk}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_category(self):
        """Проверяем создание категории разными пользователями"""
        users = User.objects.bulk_create([
            User(username='test_user1', password='test_password'),
            User(username='test_user2', password='test_password'),
            User(username='test_user3', password='test_password'),
        ])
        board = Board.objects.create(title='board')
        BoardParticipant.objects.bulk_create([
            BoardParticipant(board=board, user=users[0], role=BoardParticipant.Role.owner),
            BoardParticipant(board=board, user=users[1], role=BoardParticipant.Role.writer),
            BoardParticipant(board=board, user=users[2], role=BoardParticipant.Role.reader),
        ])
        self.client.force_login(users[0])

        response = self.client.post(self.url, {'title': 'title_1', 'is_deleted': False, 'board': board.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.client.force_login(users[1])
        response = self.client.post(self.url, {'title': 'title_2', 'is_deleted': False, 'board': board.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.client.force_login(users[2])
        response = self.client.post(self.url, {'title': 'title_3', 'is_deleted': False, 'board': board.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class GoalCreateTestCase(APITestCase):

    def setUp(self) -> None:
        self.url = reverse('create_goal')
        self.board = Board.objects.create(title='board_title')
        self.user = User.objects.create_user(
            username='test',
            password='test_password'
        )
        self.category = GoalCategory.objects.create(title='category_title', user=self.user, board=self.board)
        self.goal = Goal.objects.create(title='title',
                                        description='description',
                                        due_date=datetime.datetime.today() + datetime.timedelta(days=14),
                                        priority=Goal.Priority.medium,
                                        status=Goal.Status.in_progress,
                                        category=self.category,
                                        user=self.user
                                        )

    def test_auth_required(self):
        response = self.client.post(self.url, {
            'title': 'title',
            'description': 'description',
            'due_date': datetime.datetime.today() + datetime.timedelta(days=14),
            'priority': Goal.Priority.medium,
            'status': Goal.Status.in_progress,
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_not_participant(self):
        new_user = User.objects.create_user(username='new_test_user', password='test_password')
        self.client.force_login(new_user)

        response = self.client.get(reverse('delete_goal', kwargs={'pk': self.goal.pk}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
