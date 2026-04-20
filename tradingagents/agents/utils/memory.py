"""使用 BM25 进行词法相似度匹配的金融情景记忆模块。

检索依赖 BM25（Best Matching 25）算法，无需 API 调用、
没有 token 限制，并且可离线配合任意 LLM 提供方使用。
"""

from rank_bm25 import BM25Okapi
from typing import List, Tuple
import re


class FinancialSituationMemory:
    """基于 BM25 存储和检索金融情景的记忆系统。"""

    def __init__(self, name: str, config: dict = None):
        """初始化记忆系统。

        参数：
            name: 当前记忆实例的名称标识
            config: 配置字典（为兼容 API 保留，BM25 本身不使用）
        """
        self.name = name
        self.documents: List[str] = []
        self.recommendations: List[str] = []
        self.bm25 = None

    def _tokenize(self, text: str) -> List[str]:
        """为 BM25 建索引执行分词。

        采用简单的“小写化 + 空白/标点切分”策略。
        """
        # 转为小写，并按非字母数字字符切分
        tokens = re.findall(r'\b\w+\b', text.lower())
        return tokens

    def _rebuild_index(self):
        """在新增文档后重建 BM25 索引。"""
        if self.documents:
            tokenized_docs = [self._tokenize(doc) for doc in self.documents]
            self.bm25 = BM25Okapi(tokenized_docs)
        else:
            self.bm25 = None

    def add_situations(self, situations_and_advice: List[Tuple[str, str]]):
        """添加金融情景及其对应建议。

        参数：
            situations_and_advice: `(情景, 建议)` 形式的元组列表
        """
        for situation, recommendation in situations_and_advice:
            self.documents.append(situation)
            self.recommendations.append(recommendation)

        # 新增文档后重建 BM25 索引
        self._rebuild_index()

    def get_memories(self, current_situation: str, n_matches: int = 1) -> List[dict]:
        """使用 BM25 相似度查找匹配建议。

        参数：
            current_situation: 当前需要匹配的金融情景
            n_matches: 返回的最高匹配数量

        返回：
            List[dict]: 包含 `matched_situation`、`recommendation` 与
            `similarity_score` 的字典列表
        """
        if not self.documents or self.bm25 is None:
            return []

        # 对查询做分词
        query_tokens = self._tokenize(current_situation)

        # 获取所有文档的 BM25 分数
        scores = self.bm25.get_scores(query_tokens)

        # 按分数降序获取前 n 个索引
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:n_matches]

        # 构建结果
        results = []
        max_score = float(scores.max()) if len(scores) > 0 and scores.max() > 0 else 1.0

        for idx in top_indices:
            # 为保持一致性，将分数归一化到 0-1 区间
            normalized_score = scores[idx] / max_score if max_score > 0 else 0
            results.append({
                "matched_situation": self.documents[idx],
                "recommendation": self.recommendations[idx],
                "similarity_score": normalized_score,
            })

        return results

    def clear(self):
        """清空全部已存储记忆。"""
        self.documents = []
        self.recommendations = []
        self.bm25 = None


if __name__ == "__main__":
    # 使用示例
    matcher = FinancialSituationMemory("test_memory")

    # 示例数据
    example_data = [
        (
            "高通胀叠加利率上升，消费者支出持续走弱",
            "可关注消费必需品、公用事业等防御性板块，并重新审视固收组合久期。",
        ),
        (
            "科技板块波动显著放大，机构卖压持续上升",
            "降低高增长科技股敞口，转而关注现金流稳健、估值更合理的成熟科技公司。",
        ),
        (
            "强美元冲击新兴市场，外汇波动率持续抬升",
            "对国际仓位进行汇率对冲，并考虑降低新兴市场债券配置。",
        ),
        (
            "市场出现行业轮动迹象，同时收益率上行",
            "重新平衡组合以维持目标配置，并考虑增配受益于高利率环境的行业。",
        ),
    ]

    # 写入示例情景与建议
    matcher.add_situations(example_data)

    # 示例查询
    current_situation = """
    科技板块波动加剧，机构投资者正在减仓，
    同时利率上升也在压制成长股估值
    """

    try:
        recommendations = matcher.get_memories(current_situation, n_matches=2)

        for i, rec in enumerate(recommendations, 1):
            print(f"\n匹配结果 {i}：")
            print(f"相似度分数：{rec['similarity_score']:.2f}")
            print(f"匹配情景：{rec['matched_situation']}")
            print(f"建议：{rec['recommendation']}")

    except Exception as e:
        print(f"检索建议时出错：{str(e)}")
