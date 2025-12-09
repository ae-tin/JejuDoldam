from django.shortcuts import get_list_or_404, get_object_or_404
from .models import Post
from .serialzers import PostSerialzer
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
# Create your views here.


User = get_user_model()

class PostListCreateAPIView(APIView):
    """
    Get /posts/ -> 게시글 목록 조회
    POST /posts/ -> 게시글 작성
    """
    # 로그인 하지 않은 사용자는 상호작용 할 수 없음
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        사용자의 GET 요청을 받아 작성된 모든 게시글을 조회하는 함수
        """
        # 최신순으로 정렬
        posts = Post.objects.order_by("-created_at")
        serializer = PostSerialzer(posts, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        """
        사용자의 POST 요청을 받아 유효성 검사를 수행하고
        게시글을 DB에 반영하는 함수
        """
        # 사용자의 입력을 직렬화
        serilaizer = PostSerialzer(data=request.data)
        if serilaizer.is_valid():
            post = serilaizer.save(user=request.user)
            return Response(
                serilaizer.data,
                status=status.HTTP_201_CREATED,
            )
        return Response(serilaizer.errors, status=status.HTTP_400_BAD_REQUEST)



class PostDetailAPIView(APIView):
    """
    GET    /posts/<id>/   → 게시글 상세 조회
    PUT    /posts/<id>/   → 게시글 전체 수정
    PATCH  /posts/<id>/   → 게시글 부분 수정
    DELETE /posts/<id>/   → 게시글 삭제
    """
    # 로그인한 사용자만 상호작용 가능
    permission_classes = [IsAuthenticated]

    # 요청된 pk에 맞는 post 객체를 반환
    def get_object(self, post_pk):
        return get_object_or_404(Post, pk=post_pk)
    

    def get(self, request, post_pk):
        """
        사용자의 GET 요청을 받아 post_pk에 해당하는 post를 조회하는 함수
        """
        post = self.get_object(post_pk)
        serializer = PostSerialzer(post)
        return Response(serializer.data)
    

    def put(self, request, post_pk):
        """
        사용자의 PUT 요청을 받아 게시글 전체를 수정하는 함수
        """
        post = self.get_object(post_pk)
        # 만약 요청한 사용자와 현재 사용자가 다르다면 400 코드를 반환
        if request.user != post.user:
            return Response({'message': '권한이 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = PostSerialzer(post, data=request.data)
        
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=post.user)
            return Response(serializer.data)
        
    
    def patch(self, request, post_pk):
        """
        사용자의 PATCH 요청을 받아 게시글 일부를 수정하는 함수
        """
        post = self.get_object(post_pk)
        # 요청한 사용자와 현재 사용자가 다르면 400 코드를 반환
        if request.user != post.user:
            return Response({'message': '권한이 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = PostSerialzer(post, data=request.data, partial=True)

        if serializer.is_valid(raise_exception=True):
            serializer.save(user=post.user)
            return Response(serializer.data)
        
    def delete(self, request, post_pk):
        """
        사용자의 DELETE 요청을 받아 게시글 삭제를 수행하는 함수
        """
        post = self.get_object(post_pk)
        if request.user != post.user:
            return Response({'message': '권한이 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        post.delete()
        return Response({'message': '삭제가 완료되었습니다.'}, status=status.HTTP_204_NO_CONTENT)




