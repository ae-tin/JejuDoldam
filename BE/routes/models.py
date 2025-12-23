from django.db import models
from django.conf import settings
# Create your models here.


class Route(models.Model):
    """
    여행 루트(Route) 모델

    - 어떤 유저가 만든 루트인지: user(FK)
    - 루트 제목, 설명, 생성 시각 등
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="routes",
    )
    title = models.CharField(max_length=200)           # 예: "3박 4일 제주 힐링 여행"
    description = models.TextField(blank=True)         # 루트 한줄 설명/메모
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[Route {self.id}] {self.title} (by {self.user.username})"


class RouteDay(models.Model):
    """
    여행 루트에서의 N일차 정보

    - 어떤 Route에 속한 일차인지: route(FK)
    - day: 1일차, 2일차, 3일차...
    """

    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name="days",
    )
    day = models.PositiveSmallIntegerField()  # 1, 2, 3 ...

    class Meta:
        # 같은 route 안에서는 day가 중복되지 않도록 (1일차가 두 번 생기는 것 방지)
        unique_together = ("route", "day")
        ordering = ["day"]

    def __str__(self):
        return f"{self.route.title} - {self.day}일차"


class RoutePlace(models.Model):
    """
    특정 일차(RouteDay)에 포함된 개별 장소 정보

    - 어떤 일차에 속한 장소인지: route_day(FK)
    - order: 하루 중 순서 (1번, 2번, 3번 방문지)
    - name: 장소 이름
    - address: 주소(선택)
    - lat/lng: 위도/경도(선택)
    - memo: 메모(선택)
    """

    route_day = models.ForeignKey(
        RouteDay,
        on_delete=models.CASCADE,
        related_name="places",
    )
    order = models.PositiveSmallIntegerField()  # 방문 순서(1, 2, 3...)
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=255, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    memo = models.TextField(blank=True)
    photo_url = models.TextField(null=True, blank=True)
    place_url = models.CharField(max_length=150, null=True, blank=True)
    
    class Meta:
        # 한 일차 안에서는 order가 겹치지 않도록
        unique_together = ("route_day", "order")
        # 기본적으로 조회되는 쿼리셋을 order를 기준으로 정렬하여 반환함
        ordering = ["order"]

    def __str__(self):
        return f"{self.route_day} - #{self.order} {self.name}"
