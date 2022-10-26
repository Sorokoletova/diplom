from django.urls import reverse
from django.utils import timezone
from parameterized import parameterized
from rest_framework import status
from rest_framework.test import APITestCase

from core.models import User
from goals.models import Board, BoardParticipant


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


class CategoryCreateTestCase(APITestCase):

    def setUp(self) -> None:
        self.url = reverse('create_category')

    def test_auth_required(self):
        response = self.client.post(self.url, {'title': 'Category'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
