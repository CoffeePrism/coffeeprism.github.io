import datetime
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import content_checks as cc  # noqa: E402

TODAY = datetime.date(2026, 11, 19)


def codes(title, body, **kw):
    return sorted({code for code, _ in cc.findings(title, body, today=TODAY, **kw)})


class FindingsTest(unittest.TestCase):
    def test_clean_practical_text_passes(self):
        body = (
            "手冲的水温常见起点是 90–96°C，粉水比 1:15 左右，萃取率一般在 18%–22%。\n\n"
            "## 怎么判断萃取不足？\n\n入口发酸、余韵短，先把研磨调细一格。\n\n"
            "> 📚 想要系统化的纯净版本？看 [手冲指南](/brewing-methods/) — 一篇页面串起来。\n\n"
            "> ☕ **想系统学冲煮？** [《咖啡冲煮完全指南 2026》PDF 电子书 $3.99](/guide/comprehensive/)\n\n"
            "推荐 [Hario V60](https://www.amazon.com/s?k=Hario%20V60&tag=coffeeprism-20)。"
        )
        self.assertEqual(codes("手冲咖啡水温怎么定", body), [])

    def test_invented_research_quotes_prices_and_stats_are_blocked(self):
        body = (
            "2023年《食品科学》研究显示，每天三杯最好。\n\n"
            "> 世界冠军张三说：好咖啡在于水。\n\n"
            "精品豆约 120 元/200g。\n\n"
            "中国咖啡市场年均增长 15%，已有 3000万 咖啡爱好者。\n\n"
            "我们实测了五款磨豆机。"
        )
        self.assertEqual(codes("标题", body), ["first-hand-claim", "price", "quote-block", "statistic", "unsourced-attribution"])

    def test_links_and_years(self):
        self.assertEqual(codes("2025年最新咖啡豆推荐", "看 [官网](https://example.org/x)。2027年会更好。"),
                         ["external-link", "future-year", "title-year"])
        allowed = "https://news.google.com/rss/articles/abc"
        self.assertEqual(codes("新闻", f"据[原文]({allowed})报道，门店达到 2700 家。", allowed_urls=[allowed]), [])

    def test_news_numbers_are_allowed_when_in_the_source(self):
        body = "瑞幸门店数与星巴克仅差2700家。门店增长 30%。"
        self.assertEqual(codes("新闻", body, source_text="瑞幸全球门店数仅差星巴克2700家"), ["statistic"])

    def test_residue_and_placeholders(self):
        self.assertEqual(codes("t", "希望这篇文章对你有帮助！\n\n[插入图片]"), ["residue"])

    def test_standards_cited_as_a_basis_are_not_attributions(self):
        self.assertEqual(codes("t", "中国有机产品认证依据GB/T 19630系列标准。"), [])

    def test_ai_tell_density(self):
        self.assertGreater(cc.ai_tell_density("这不是咖啡的问题，而是水的问题。值得注意的是，总而言之。"), 0)
        self.assertEqual(cc.ai_tell_density("水温 92°C，研磨中细。"), 0)


if __name__ == "__main__":
    unittest.main()
