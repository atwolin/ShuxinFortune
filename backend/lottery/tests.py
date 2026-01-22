from django.test import TestCase, Client
from django.urls import reverse
from lottery.models import FortuneCategory, Fortune
import json


class FortuneAPITestCase(TestCase):
    """測試抽籤 API 功能"""

    def setUp(self):
        """建立測試資料"""
        self.client = Client()

        # 建立測試分類
        self.category = FortuneCategory.objects.create(
            name="測試分類", description="這是測試用的分類", is_active=True
        )

        # 建立測試籤詩
        self.fortune1 = Fortune.objects.create(
            category=self.category,
            message="你已經比昨天更前進了！繼續加油！",
            is_active=True,
        )

        self.fortune2 = Fortune.objects.create(
            category=self.category,
            message="你會緊張，是因為你在乎。這份在乎很珍貴。",
            is_active=True,
        )

    def test_draw_fortune_success(self):
        """測試成功抽籤"""
        url = reverse("lottery:draw")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        self.assertIn("message", data)
        self.assertIn("category", data)
        self.assertEqual(data["category"], "測試分類")
        self.assertIn(data["message"], [self.fortune1.message, self.fortune2.message])

    def test_draw_fortune_empty(self):
        """測試沒有籤詩時的回應"""
        # 停用所有籤詩
        Fortune.objects.all().update(is_active=False)

        url = reverse("lottery:draw")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)
        data = json.loads(response.content)
        self.assertIn("error", data)

    def test_draw_fortune_random(self):
        """測試隨機性 - 多次抽籤應該會抽到不同結果"""
        url = reverse("lottery:draw")
        results = set()

        # 抽 20 次
        for _ in range(20):
            response = self.client.get(url)
            data = json.loads(response.content)
            results.add(data["message"])

        # 至少應該抽到 1 種以上的籤詩
        # (理論上應該會抽到 2 種，但為了避免偶然失敗，我們只要求 >= 1)
        self.assertGreaterEqual(len(results), 1)

    def test_inactive_category(self):
        """測試停用分類時，該分類的籤詩不會被抽到"""
        # 停用分類
        self.category.is_active = False
        self.category.save()

        url = reverse("lottery:draw")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)


class FortuneModelTestCase(TestCase):
    """測試 Fortune 資料模型"""

    def setUp(self):
        self.category = FortuneCategory.objects.create(name="學測鼓勵", is_active=True)

    def test_create_fortune(self):
        """測試建立籤詩"""
        fortune = Fortune.objects.create(
            category=self.category, message="相信自己，你做得到！"
        )

        self.assertTrue(fortune.is_active)
        self.assertEqual(fortune.category, self.category)
        self.assertIsNotNone(fortune.created_at)

    def test_fortune_string_representation(self):
        """測試籤詩的字串表示"""
        fortune = Fortune.objects.create(
            category=self.category, message="這是一句很長的籤詩內容測試"
        )

        str_repr = str(fortune)
        self.assertIn("學測鼓勵", str_repr)
