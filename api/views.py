import base64

from django.contrib.auth import authenticate, login, logout

from django.contrib.auth.models import User
from api.serializers import UserSerializer
from rest_framework import generics, permissions
from rest_framework.pagination import PageNumberPagination
from rest_framework import status, viewsets
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import FriendRequest
from .serializers import FriendRequestSerializer
from django.utils import timezone
from datetime import timedelta
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token

class UserRegistrationViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]  # This makes registration accessible without authentication

class UserListViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated] 
    def get_queryset(self):
        keyword = self.request.query_params.get('q', '').strip().lower()
        if '@' in keyword:  # Assuming it's an email search
            return User.objects.filter(email__iexact=keyword)
        else:
            return User.objects.filter(first_name__icontains=keyword) | User.objects.filter(last_name__icontains=keyword)
class LoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })
        
        
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            request.user.auth_token.delete()
            return Response({"detail": "Successfully logged out."})
        except Exception as e:
            return Response({"detail": "Logout failed."}, status=400)


class SendFriendRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        receiver_id = request.data.get('receiver_id')
        receiver = User.objects.get(id=receiver_id)

        if FriendRequest.objects.filter(sender=request.user, receiver=receiver).exists():
            return Response({'detail': 'Friend request already sent.'}, status=status.HTTP_400_BAD_REQUEST)
        
        recent_requests = FriendRequest.objects.filter(sender=request.user, created_at__gte=timezone.now() - timedelta(minutes=1)).count()
        if recent_requests >= 3:
            return Response({'detail': 'You have exceeded the limit of friend requests.'}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        friend_request = FriendRequest(sender=request.user, receiver=receiver)
        friend_request.save()
        return Response(FriendRequestSerializer(friend_request).data, status=status.HTTP_201_CREATED)

class RespondFriendRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        request_id = request.data.get('request_id')
        response = request.data.get('response')  # 'accepted' or 'rejected'

        friend_request = FriendRequest.objects.get(id=request_id)
        if friend_request.receiver != request.user:
            return Response({'detail': 'Not authorized.'}, status=status.HTTP_403_FORBIDDEN)

        if response not in ['accepted', 'rejected']:
            return Response({'detail': 'Invalid response.'}, status=status.HTTP_400_BAD_REQUEST)

        friend_request.status = response
        friend_request.save()
        return Response(FriendRequestSerializer(friend_request).data)
    
class ListFriendsView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(
            id__in=FriendRequest.objects.filter(sender=self.request.user, status='accepted').values('receiver')
        ) | User.objects.filter(
            id__in=FriendRequest.objects.filter(receiver=self.request.user, status='accepted').values('sender')
        )
    
class PendingFriendRequestsView(generics.ListAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FriendRequest.objects.filter(receiver=self.request.user, status='pending')


