"""
文獻解析模組
Reference Parser Module

功能：
- 從純文字中提取文獻資訊
- 識別 DOI
- 判斷文獻類型
- 評估資料完整度
"""

import re
from typing import Dict, Optional, List


class ReferenceParser:
    """文獻解析器"""

    # DOI 正則表達式
    DOI_PATTERN = r'10\.\d{4,9}/[-._;()/:A-Za-z0-9]+'

    # 年份正則表達式（1900-2099）
    YEAR_PATTERN = r'\b(19\d{2}|20\d{2})\b'

    # 作者模式（Last, F. M. 或 First Last）
    AUTHOR_PATTERN = r'([A-Z][a-z]+(?:-[A-Z][a-z]+)?(?:,\s*[A-Z]\.(?:\s*[A-Z]\.)?)?)'

    # 期刊卷期頁碼模式
    VOLUME_ISSUE_PATTERN = r'(\d+)\((\d+)\),?\s*(\d+(?:-\d+)?)'

    def parse_reference(self, text: str) -> Dict:
        """
        解析純文字文獻

        Args:
            text: 原始文獻文字

        Returns:
            結構化的文獻資料字典
        """
        result = {
            'original_text': text,
            'authors': [],
            'year': None,
            'title': None,
            'journal': None,
            'volume': None,
            'issue': None,
            'pages': None,
            'doi': None,
            'url': None,
            'publisher': None,
            'type': 'unknown',  # article, book, website, unknown
            'completeness': 0.0,  # 0.0 到 1.0
            'confidence': 0.0,  # 解析信心度
        }

        # 1. 提取 DOI（優先）
        result['doi'] = self.extract_doi(text)

        # 2. 提取年份
        result['year'] = self.extract_year(text)

        # 3. 提取作者
        result['authors'] = self.extract_authors(text)

        # 4. 提取標題（粗略估計）
        result['title'] = self.extract_title(text)

        # 5. 提取期刊資訊
        journal_info = self.extract_journal_info(text)
        if journal_info:
            result.update(journal_info)

        # 6. 提取 URL
        result['url'] = self.extract_url(text)

        # 7. 判斷文獻類型
        result['type'] = self.detect_reference_type(result)

        # 8. 計算完整度和信心度
        result['completeness'] = self.calculate_completeness(result)
        result['confidence'] = self.calculate_confidence(result)

        return result

    def extract_doi(self, text: str) -> Optional[str]:
        """提取 DOI"""
        # 移除常見的 DOI 前綴
        text = text.replace('doi:', '').replace('DOI:', '').replace('https://doi.org/', '')

        match = re.search(self.DOI_PATTERN, text, re.IGNORECASE)
        if match:
            doi = match.group(0)
            # 清理尾部標點符號
            doi = doi.rstrip('.,;')
            return doi
        return None

    def extract_year(self, text: str) -> Optional[str]:
        """提取年份"""
        # 通常年份在括號中：(2020) 或在作者後：Smith 2020
        year_match = re.search(r'\((' + self.YEAR_PATTERN + r')\)', text)
        if year_match:
            return year_match.group(1)

        # 如果沒找到括號中的年份，找任何年份
        year_match = re.search(self.YEAR_PATTERN, text)
        if year_match:
            return year_match.group(0)

        return None

    def extract_authors(self, text: str) -> List[Dict[str, str]]:
        """
        提取作者姓名

        Returns:
            作者列表，每個作者包含 'last' 和 'first' 欄位
        """
        authors = []

        # 嘗試匹配 APA 格式：Last, F. M.
        apa_pattern = r'([A-Z][a-z]+(?:-[A-Z][a-z]+)?),\s*([A-Z]\.(?:\s*[A-Z]\.)?)'
        matches = re.findall(apa_pattern, text)

        for match in matches:
            authors.append({
                'last': match[0],
                'first': match[1].replace('.', '').replace(' ', '')
            })

        # 如果沒找到，嘗試匹配簡單格式：FirstName LastName
        if not authors:
            simple_pattern = r'\b([A-Z][a-z]+)\s+([A-Z][a-z]+)\b'
            matches = re.findall(simple_pattern, text[:100])  # 只搜尋前 100 字元

            for match in matches[:3]:  # 最多取 3 個
                authors.append({
                    'last': match[1],
                    'first': match[0][0]  # 只取首字母
                })

        return authors

    def extract_title(self, text: str) -> Optional[str]:
        """
        提取標題（粗略估計）

        策略：
        1. 如果有句號，假設第一個句號後、第二個句號前是標題
        2. 移除年份和作者後的文字可能是標題
        """
        # 移除 DOI 和 URL
        clean_text = re.sub(r'https?://\S+', '', text)
        clean_text = re.sub(self.DOI_PATTERN, '', clean_text)

        # 嘗試找到年份後的第一個句點之前的文字
        year_match = re.search(r'\(?\d{4}\)?\.\s*(.+?)\.', clean_text)
        if year_match:
            title = year_match.group(1).strip()
            # 移除期刊名稱（通常是斜體或大寫）
            title = re.sub(r'\s*[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*,?\s*$', '', title)
            return title

        # 如果找不到，返回 None
        return None

    def extract_journal_info(self, text: str) -> Optional[Dict]:
        """提取期刊、卷、期、頁碼資訊"""
        # 匹配格式：Volume(Issue), Pages 或 Volume, Pages
        match = re.search(self.VOLUME_ISSUE_PATTERN, text)

        if match:
            return {
                'volume': match.group(1),
                'issue': match.group(2),
                'pages': match.group(3)
            }

        # 嘗試只匹配卷號和頁碼
        simple_match = re.search(r'(\d+),\s*(\d+(?:-\d+)?)', text)
        if simple_match:
            return {
                'volume': simple_match.group(1),
                'pages': simple_match.group(2)
            }

        return None

    def extract_url(self, text: str) -> Optional[str]:
        """提取 URL"""
        url_pattern = r'https?://[^\s]+'
        match = re.search(url_pattern, text)
        if match:
            url = match.group(0)
            # 清理尾部標點符號
            url = url.rstrip('.,;)')
            return url
        return None

    def detect_reference_type(self, data: Dict) -> str:
        """
        根據欄位判斷文獻類型

        Returns:
            'article', 'book', 'website', 'unknown'
        """
        # 有期刊、卷、期 -> 期刊文章
        if data.get('journal') or (data.get('volume') and data.get('issue')):
            return 'article'

        # 有出版商但無期刊 -> 書籍
        if data.get('publisher') and not data.get('journal'):
            return 'book'

        # 有 URL 但無 DOI 和期刊 -> 網站
        if data.get('url') and not data.get('doi') and not data.get('journal'):
            return 'website'

        # 有 DOI -> 很可能是期刊文章
        if data.get('doi'):
            return 'article'

        return 'unknown'

    def calculate_completeness(self, data: Dict) -> float:
        """
        計算資料完整度

        根據文獻類型，檢查必要欄位是否存在
        """
        required_fields = {
            'article': ['authors', 'year', 'title', 'journal'],
            'book': ['authors', 'year', 'title', 'publisher'],
            'website': ['title', 'url'],
            'unknown': ['authors', 'year', 'title']
        }

        ref_type = data.get('type', 'unknown')
        fields = required_fields.get(ref_type, required_fields['unknown'])

        present = 0
        for field in fields:
            value = data.get(field)
            if value and (not isinstance(value, list) or len(value) > 0):
                present += 1

        return present / len(fields) if fields else 0.0

    def calculate_confidence(self, data: Dict) -> float:
        """
        計算解析信心度

        基於以下因素：
        - 是否有 DOI（最可靠）
        - 是否有明確的結構化資訊
        - 欄位的數量和品質
        """
        confidence = 0.0

        # DOI 存在：+0.4
        if data.get('doi'):
            confidence += 0.4

        # 作者存在且格式良好：+0.2
        if data.get('authors') and len(data['authors']) > 0:
            confidence += 0.2

        # 年份存在：+0.1
        if data.get('year'):
            confidence += 0.1

        # 標題存在：+0.1
        if data.get('title'):
            confidence += 0.1

        # 期刊資訊存在：+0.2
        if data.get('journal') or data.get('volume'):
            confidence += 0.2

        return min(confidence, 1.0)

    def parse_multiple(self, text: str, separator: str = '\n') -> List[Dict]:
        """
        解析多條文獻

        Args:
            text: 包含多條文獻的文字
            separator: 分隔符（預設為換行）

        Returns:
            文獻列表
        """
        lines = text.split(separator)
        references = []

        for line in lines:
            line = line.strip()
            if line:  # 忽略空行
                ref = self.parse_reference(line)
                references.append(ref)

        return references
