from rest_framework import viewsets, filters
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import (
    IsAuthenticated, IsAuthenticatedOrReadOnly
)
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from posts.models import Post, Group, Follow
from .serializers import (
    PostSerializer, CommentSerializer, GroupSerializer, FollowSerializer
)
from .permissions import IsAuthorOrReadOnly


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def get_queryset(self):
        post = get_object_or_404(Post, pk=self.kwargs.get('post_id'))
        return post.comments.all()

    def perform_create(self, serializer):
        post = get_object_or_404(Post, pk=self.kwargs.get('post_id'))
        serializer.save(author=self.request.user, post=post)


class FollowViewSet(viewsets.ModelViewSet):
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (filters.SearchFilter,)
    search_fields = ('following__username',)

    def get_queryset(self):
        return Follow.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        following_user = serializer.validated_data.get('following')

        if self.request.user == following_user:
            raise ValidationError('Вы не можете подписаться на самого себя!')

        if Follow.objects.filter(
            user=self.request.user, following=following_user
        ).exists():
            raise ValidationError(
                'Вы уже подписаны на этого пользователя!'
            )

        serializer.save(user=self.request.user)
