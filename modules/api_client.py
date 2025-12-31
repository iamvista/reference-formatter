"""
API 查詢模組
API Client Module

功能：
- 透過 DOI 查詢完整文獻資訊
- 透過標題和作者查詢
- 整合多個 API 來源
"""

import requests
import time
from typing import Dict, Optional, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class APIClient:
    """文獻 API 客戶端"""

    CROSSREF_API = "https://api.crossref.org/works"
    OPENALEX_API = "https://api.openalex.org/works"
    DOI_ORG = "https://doi.org"

    # 請求標頭（禮貌性標識）
    HEADERS = {
        'User-Agent': 'AcademicReferenceFormatter/1.0 (mailto:support@example.com)'
    }

    def __init__(self, timeout: int = 10, max_retries: int = 3):
        """
        初始化 API 客戶端

        Args:
            timeout: 請求超時時間（秒）
            max_retries: 最大重試次數
        """
        self.timeout = timeout
        self.max_retries = max_retries

    def query_by_doi(self, doi: str) -> Optional[Dict]:
        """
        通過 DOI 查詢 CrossRef

        Args:
            doi: DOI 識別碼

        Returns:
            文獻元數據字典，失敗返回 None
        """
        if not doi:
            return None

        url = f"{self.CROSSREF_API}/{doi}"

        try:
            response = self._make_request(url)
            if response and response.get('status') == 'ok':
                return self._parse_crossref_response(response['message'])
        except Exception as e:
            logger.error(f"CrossRef 查詢失敗 (DOI: {doi}): {e}")

        return None

    def query_by_metadata(self, title: str, authors: List[str] = None) -> Optional[Dict]:
        """
        通過標題和作者模糊查詢

        Args:
            title: 文章標題
            authors: 作者列表（可選）

        Returns:
            文獻元數據字典，失敗返回 None
        """
        if not title:
            return None

        # 構建查詢參數
        query_parts = [f'title:"{title}"']
        if authors:
            author_query = ' '.join(authors[:2])  # 只用前兩個作者
            query_parts.append(f'author:"{author_query}"')

        query = ' '.join(query_parts)
        url = f"{self.CROSSREF_API}?query={query}&rows=1"

        try:
            response = self._make_request(url)
            if response and response.get('status') == 'ok':
                items = response['message'].get('items', [])
                if items:
                    return self._parse_crossref_response(items[0])
        except Exception as e:
            logger.error(f"標題查詢失敗: {e}")

        return None

    def enrich_reference(self, partial_data: Dict) -> Dict:
        """
        補完不完整的文獻資料

        Args:
            partial_data: 部分解析的文獻資料

        Returns:
            補完後的文獻資料
        """
        enriched = partial_data.copy()
        api_data = None

        # 優先使用 DOI 查詢
        if partial_data.get('doi'):
            logger.info(f"使用 DOI 查詢: {partial_data['doi']}")
            api_data = self.query_by_doi(partial_data['doi'])

        # 如果 DOI 查詢失敗，嘗試標題查詢
        if not api_data and partial_data.get('title'):
            logger.info(f"使用標題查詢: {partial_data['title'][:50]}...")
            authors = [a.get('last', '') for a in partial_data.get('authors', [])]
            api_data = self.query_by_metadata(partial_data['title'], authors)

        # 合併 API 資料
        if api_data:
            enriched = self._merge_data(partial_data, api_data)
            enriched['enriched'] = True
            enriched['enrichment_source'] = 'crossref'
        else:
            enriched['enriched'] = False

        return enriched

    def _make_request(self, url: str) -> Optional[Dict]:
        """
        發送 HTTP 請求（含重試機制）

        Args:
            url: 請求 URL

        Returns:
            JSON 回應，失敗返回 None
        """
        for attempt in range(self.max_retries):
            try:
                response = requests.get(
                    url,
                    headers=self.HEADERS,
                    timeout=self.timeout
                )

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    logger.warning(f"資源不存在 (404): {url}")
                    return None
                elif response.status_code == 429:
                    # 速率限制，等待後重試
                    wait_time = 2 ** attempt
                    logger.warning(f"速率限制，等待 {wait_time} 秒後重試...")
                    time.sleep(wait_time)
                else:
                    logger.warning(f"HTTP {response.status_code}: {url}")

            except requests.Timeout:
                logger.warning(f"請求超時 (嘗試 {attempt + 1}/{self.max_retries})")
            except Exception as e:
                logger.error(f"請求失敗: {e}")
                break

        return None

    def _parse_crossref_response(self, data: Dict) -> Dict:
        """
        解析 CrossRef API 回應

        Args:
            data: CrossRef API 返回的 message 物件

        Returns:
            標準化的文獻資料字典
        """
        result = {
            'title': None,
            'authors': [],
            'year': None,
            'journal': None,
            'volume': None,
            'issue': None,
            'pages': None,
            'doi': None,
            'publisher': None,
            'type': 'article'
        }

        # 標題
        if 'title' in data and data['title']:
            result['title'] = data['title'][0]

        # 作者
        if 'author' in data:
            for author in data['author']:
                result['authors'].append({
                    'last': author.get('family', ''),
                    'first': author.get('given', '')
                })

        # 年份
        if 'published-print' in data:
            date_parts = data['published-print'].get('date-parts', [[]])
            if date_parts and date_parts[0]:
                result['year'] = str(date_parts[0][0])
        elif 'published-online' in data:
            date_parts = data['published-online'].get('date-parts', [[]])
            if date_parts and date_parts[0]:
                result['year'] = str(date_parts[0][0])

        # 期刊名稱
        if 'container-title' in data and data['container-title']:
            result['journal'] = data['container-title'][0]

        # 卷號
        if 'volume' in data:
            result['volume'] = data['volume']

        # 期號
        if 'issue' in data:
            result['issue'] = data['issue']

        # 頁碼
        if 'page' in data:
            result['pages'] = data['page']

        # DOI
        if 'DOI' in data:
            result['doi'] = data['DOI']

        # 出版商
        if 'publisher' in data:
            result['publisher'] = data['publisher']

        # 類型
        if 'type' in data:
            crossref_type = data['type']
            if crossref_type in ['journal-article', 'proceedings-article']:
                result['type'] = 'article'
            elif crossref_type in ['book', 'monograph']:
                result['type'] = 'book'

        return result

    def _merge_data(self, original: Dict, api_data: Dict) -> Dict:
        """
        合併原始資料和 API 資料

        優先使用 API 資料，但保留原始資料中獨有的欄位

        Args:
            original: 原始解析的資料
            api_data: API 查詢的資料

        Returns:
            合併後的資料
        """
        merged = original.copy()

        # 對於每個欄位，如果 API 資料有值且原始資料沒有或不完整，使用 API 資料
        for key, value in api_data.items():
            if value:  # API 資料有值
                if not merged.get(key):  # 原始資料沒有
                    merged[key] = value
                elif isinstance(value, list) and len(value) > len(merged.get(key, [])):
                    # 列表類型且 API 資料更完整
                    merged[key] = value

        return merged
