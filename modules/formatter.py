"""
文獻格式化模組
Reference Formatter Module

支援格式：
- APA 7th Edition
- MLA 9th Edition
- Chicago Manual of Style (17th Edition)
- Harvard Referencing Style
"""

from typing import Dict, List, Optional
from abc import ABC, abstractmethod


class BaseFormatter(ABC):
    """文獻格式化器基類"""

    @abstractmethod
    def format_article(self, data: Dict) -> str:
        """格式化期刊文章"""
        pass

    @abstractmethod
    def format_book(self, data: Dict) -> str:
        """格式化書籍"""
        pass

    @abstractmethod
    def format_website(self, data: Dict) -> str:
        """格式化網站"""
        pass

    def format(self, data: Dict) -> str:
        """
        根據文獻類型自動選擇格式化方法

        Args:
            data: 文獻資料字典

        Returns:
            格式化後的文獻字串
        """
        ref_type = data.get('type', 'unknown')

        if ref_type == 'article':
            return self.format_article(data)
        elif ref_type == 'book':
            return self.format_book(data)
        elif ref_type == 'website':
            return self.format_website(data)
        else:
            # 未知類型，嘗試作為文章格式化
            return self.format_article(data)

    def _format_authors(self, authors: List[Dict], max_authors: int = None,
                       last_first: bool = True, ampersand: bool = False,
                       invert_all: bool = False) -> str:
        """
        格式化作者列表

        Args:
            authors: 作者列表 [{'last': '姓', 'first': '名'}, ...]
            max_authors: 最多顯示作者數（超過則使用 et al.）
            last_first: 是否使用「姓, 名」格式
            ampersand: 是否在最後一個作者前使用 & 而非 and
            invert_all: 是否所有作者都使用「姓, 名」格式

        Returns:
            格式化的作者字串
        """
        if not authors:
            return ""

        # 限制作者數量
        if max_authors and len(authors) > max_authors:
            authors = authors[:max_authors]
            use_et_al = True
        else:
            use_et_al = False

        formatted = []
        for i, author in enumerate(authors):
            last = author.get('last', '')
            first = author.get('first', '')

            # 第一個作者或所有作者都倒置
            if (i == 0 and last_first) or (invert_all and last_first):
                if first:
                    formatted.append(f"{last}, {first}.")
                else:
                    formatted.append(last)
            else:
                if first:
                    formatted.append(f"{first}. {last}")
                else:
                    formatted.append(last)

        # 組合作者
        if len(formatted) == 1:
            result = formatted[0]
        elif len(formatted) == 2:
            connector = " & " if ampersand else " and "
            result = connector.join(formatted)
        else:
            connector = ", & " if ampersand else ", and "
            result = ", ".join(formatted[:-1]) + connector + formatted[-1]

        if use_et_al:
            result += " et al."

        return result


class APAFormatter(BaseFormatter):
    """APA 7th Edition 格式化器"""

    def format_article(self, data: Dict) -> str:
        """
        格式化期刊文章
        格式：Author, A. A. (Year). Title of article. Title of Periodical, volume(issue), pages. https://doi.org/xxx
        """
        parts = []

        # 作者
        authors = self._format_authors(
            data.get('authors', []),
            max_authors=20,
            last_first=True,
            ampersand=True,
            invert_all=True
        )
        if authors:
            parts.append(authors)

        # 年份
        year = data.get('year', 'n.d.')
        parts.append(f"({year}).")

        # 標題（不使用斜體，因為是純文字）
        title = data.get('title', 'Untitled')
        parts.append(f"{title}.")

        # 期刊名稱
        journal = data.get('journal', '')
        if journal:
            journal_part = f"*{journal}*"

            # 卷號
            volume = data.get('volume', '')
            if volume:
                journal_part += f", {volume}"

            # 期號
            issue = data.get('issue', '')
            if issue:
                journal_part += f"({issue})"

            # 頁碼
            pages = data.get('pages', '')
            if pages:
                journal_part += f", {pages}"

            parts.append(journal_part + ".")

        # DOI 或 URL
        doi = data.get('doi', '')
        if doi:
            parts.append(f"https://doi.org/{doi}")
        elif data.get('url'):
            parts.append(data['url'])

        return " ".join(parts)

    def format_book(self, data: Dict) -> str:
        """
        格式化書籍
        格式：Author, A. A. (Year). Title of work. Publisher.
        """
        parts = []

        # 作者
        authors = self._format_authors(
            data.get('authors', []),
            last_first=True,
            ampersand=True,
            invert_all=True
        )
        if authors:
            parts.append(authors)

        # 年份
        year = data.get('year', 'n.d.')
        parts.append(f"({year}).")

        # 書名
        title = data.get('title', 'Untitled')
        parts.append(f"*{title}*.")

        # 出版商
        publisher = data.get('publisher', '')
        if publisher:
            parts.append(f"{publisher}.")

        return " ".join(parts)

    def format_website(self, data: Dict) -> str:
        """
        格式化網站
        格式：Author, A. A. (Year, Month Day). Title of page. Site Name. URL
        """
        parts = []

        # 作者（如果有）
        authors = self._format_authors(
            data.get('authors', []),
            last_first=True,
            ampersand=True,
            invert_all=True
        )
        if authors:
            parts.append(authors)

        # 年份
        year = data.get('year', 'n.d.')
        parts.append(f"({year}).")

        # 標題
        title = data.get('title', 'Untitled webpage')
        parts.append(f"{title}.")

        # 網站名稱（如果有）
        site_name = data.get('site_name', '')
        if site_name:
            parts.append(f"*{site_name}*.")

        # URL
        url = data.get('url', '')
        if url:
            parts.append(url)

        return " ".join(parts)


class MLAFormatter(BaseFormatter):
    """MLA 9th Edition 格式化器"""

    def format_article(self, data: Dict) -> str:
        """
        格式化期刊文章
        格式：Author Last, First. "Title of Article." Title of Journal, vol. #, no. #, Year, pp. #-#.
        """
        parts = []

        # 作者
        authors = self._format_authors(
            data.get('authors', []),
            max_authors=3,
            last_first=True,
            ampersand=False,
            invert_all=False  # 只有第一個作者倒置
        )
        if authors:
            parts.append(authors + ".")

        # 標題（使用引號）
        title = data.get('title', 'Untitled')
        parts.append(f'"{title}."')

        # 期刊名稱（斜體）
        journal = data.get('journal', '')
        if journal:
            journal_part = f"*{journal}*"

            # 卷號
            volume = data.get('volume', '')
            if volume:
                journal_part += f", vol. {volume}"

            # 期號
            issue = data.get('issue', '')
            if issue:
                journal_part += f", no. {issue}"

            parts.append(journal_part + ",")

        # 年份
        year = data.get('year', 'n.d.')
        parts.append(f"{year},")

        # 頁碼
        pages = data.get('pages', '')
        if pages:
            parts.append(f"pp. {pages}.")
        else:
            # 移除最後的逗號
            if parts and parts[-1].endswith(','):
                parts[-1] = parts[-1][:-1] + '.'

        # DOI
        doi = data.get('doi', '')
        if doi:
            parts.append(f"https://doi.org/{doi}")

        return " ".join(parts)

    def format_book(self, data: Dict) -> str:
        """
        格式化書籍
        格式：Author Last, First. Title of Book. Publisher, Year.
        """
        parts = []

        # 作者
        authors = self._format_authors(
            data.get('authors', []),
            max_authors=3,
            last_first=True,
            ampersand=False,
            invert_all=False
        )
        if authors:
            parts.append(authors + ".")

        # 書名（斜體）
        title = data.get('title', 'Untitled')
        parts.append(f"*{title}*.")

        # 出版商
        publisher = data.get('publisher', '')
        if publisher:
            parts.append(f"{publisher},")

        # 年份
        year = data.get('year', 'n.d.')
        parts.append(f"{year}.")

        return " ".join(parts)

    def format_website(self, data: Dict) -> str:
        """
        格式化網站
        格式：Author Last, First. "Title of Page." Website Name, Day Month Year, URL.
        """
        parts = []

        # 作者（如果有）
        authors = self._format_authors(
            data.get('authors', []),
            max_authors=3,
            last_first=True,
            ampersand=False,
            invert_all=False
        )
        if authors:
            parts.append(authors + ".")

        # 標題
        title = data.get('title', 'Untitled webpage')
        parts.append(f'"{title}."')

        # 網站名稱
        site_name = data.get('site_name', '')
        if site_name:
            parts.append(f"*{site_name}*,")

        # 日期
        year = data.get('year', '')
        if year:
            parts.append(f"{year},")

        # URL
        url = data.get('url', '')
        if url:
            parts.append(f"{url}.")

        return " ".join(parts)


class ChicagoFormatter(BaseFormatter):
    """Chicago Manual of Style 17th Edition 格式化器（Notes and Bibliography）"""

    def format_article(self, data: Dict) -> str:
        """
        格式化期刊文章
        格式：Author Last, First. "Title of Article." Title of Journal volume, no. issue (Year): pages.
        """
        parts = []

        # 作者
        authors = self._format_authors(
            data.get('authors', []),
            last_first=True,
            ampersand=False,
            invert_all=False
        )
        if authors:
            parts.append(authors + ".")

        # 標題（使用引號）
        title = data.get('title', 'Untitled')
        parts.append(f'"{title}."')

        # 期刊名稱（斜體）
        journal = data.get('journal', '')
        if journal:
            journal_part = f"*{journal}*"

            # 卷號
            volume = data.get('volume', '')
            if volume:
                journal_part += f" {volume}"

            # 期號
            issue = data.get('issue', '')
            if issue:
                journal_part += f", no. {issue}"

            parts.append(journal_part)

        # 年份
        year = data.get('year', 'n.d.')
        year_part = f"({year})"

        # 頁碼
        pages = data.get('pages', '')
        if pages:
            year_part += f": {pages}."
        else:
            year_part += "."

        parts.append(year_part)

        # DOI
        doi = data.get('doi', '')
        if doi:
            parts.append(f"https://doi.org/{doi}")

        return " ".join(parts)

    def format_book(self, data: Dict) -> str:
        """
        格式化書籍
        格式：Author Last, First. Title of Book. Place of Publication: Publisher, Year.
        """
        parts = []

        # 作者
        authors = self._format_authors(
            data.get('authors', []),
            last_first=True,
            ampersand=False,
            invert_all=False
        )
        if authors:
            parts.append(authors + ".")

        # 書名（斜體）
        title = data.get('title', 'Untitled')
        parts.append(f"*{title}*.")

        # 出版地點（如果有）
        place = data.get('place', '')
        publisher = data.get('publisher', '')

        if place and publisher:
            pub_part = f"{place}: {publisher},"
        elif publisher:
            pub_part = f"{publisher},"
        else:
            pub_part = ""

        if pub_part:
            parts.append(pub_part)

        # 年份
        year = data.get('year', 'n.d.')
        parts.append(f"{year}.")

        return " ".join(parts)

    def format_website(self, data: Dict) -> str:
        """
        格式化網站
        格式：Author Last, First. "Title of Page." Website Name. Accessed Date. URL.
        """
        parts = []

        # 作者（如果有）
        authors = self._format_authors(
            data.get('authors', []),
            last_first=True,
            ampersand=False,
            invert_all=False
        )
        if authors:
            parts.append(authors + ".")

        # 標題
        title = data.get('title', 'Untitled webpage')
        parts.append(f'"{title}."')

        # 網站名稱
        site_name = data.get('site_name', '')
        if site_name:
            parts.append(f"*{site_name}*.")

        # 訪問日期（如果有）
        access_date = data.get('access_date', '')
        if access_date:
            parts.append(f"Accessed {access_date}.")

        # URL
        url = data.get('url', '')
        if url:
            parts.append(f"{url}.")

        return " ".join(parts)


class HarvardFormatter(BaseFormatter):
    """Harvard Referencing Style 格式化器"""

    def format_article(self, data: Dict) -> str:
        """
        格式化期刊文章
        格式：Author, A.A. (Year) 'Title of article', Title of Journal, volume(issue), pp. pages.
        """
        parts = []

        # 作者
        authors = self._format_authors(
            data.get('authors', []),
            last_first=True,
            ampersand=False,
            invert_all=True
        )
        if authors:
            parts.append(authors)

        # 年份
        year = data.get('year', 'n.d.')
        parts.append(f"({year})")

        # 標題（使用單引號）
        title = data.get('title', 'Untitled')
        parts.append(f"'{title}',")

        # 期刊名稱（斜體）
        journal = data.get('journal', '')
        if journal:
            journal_part = f"*{journal}*"

            # 卷號
            volume = data.get('volume', '')
            if volume:
                journal_part += f", {volume}"

            # 期號
            issue = data.get('issue', '')
            if issue:
                journal_part += f"({issue})"

            parts.append(journal_part + ",")

        # 頁碼
        pages = data.get('pages', '')
        if pages:
            parts.append(f"pp. {pages}.")
        else:
            # 移除最後的逗號
            if parts and parts[-1].endswith(','):
                parts[-1] = parts[-1][:-1] + '.'

        # DOI
        doi = data.get('doi', '')
        if doi:
            parts.append(f"doi: {doi}")

        return " ".join(parts)

    def format_book(self, data: Dict) -> str:
        """
        格式化書籍
        格式：Author, A.A. (Year) Title of Book. Place: Publisher.
        """
        parts = []

        # 作者
        authors = self._format_authors(
            data.get('authors', []),
            last_first=True,
            ampersand=False,
            invert_all=True
        )
        if authors:
            parts.append(authors)

        # 年份
        year = data.get('year', 'n.d.')
        parts.append(f"({year})")

        # 書名（斜體）
        title = data.get('title', 'Untitled')
        parts.append(f"*{title}*.")

        # 出版地點和出版商
        place = data.get('place', '')
        publisher = data.get('publisher', '')

        if place and publisher:
            parts.append(f"{place}: {publisher}.")
        elif publisher:
            parts.append(f"{publisher}.")

        return " ".join(parts)

    def format_website(self, data: Dict) -> str:
        """
        格式化網站
        格式：Author, A.A. (Year) 'Title of page', Website Name. Available at: URL (Accessed: date).
        """
        parts = []

        # 作者（如果有）
        authors = self._format_authors(
            data.get('authors', []),
            last_first=True,
            ampersand=False,
            invert_all=True
        )
        if authors:
            parts.append(authors)

        # 年份
        year = data.get('year', '')
        if year:
            parts.append(f"({year})")

        # 標題
        title = data.get('title', 'Untitled webpage')
        parts.append(f"'{title}',")

        # 網站名稱
        site_name = data.get('site_name', '')
        if site_name:
            parts.append(f"*{site_name}*.")

        # URL
        url = data.get('url', '')
        if url:
            parts.append(f"Available at: {url}")

        # 訪問日期（如果有）
        access_date = data.get('access_date', '')
        if access_date:
            parts.append(f"(Accessed: {access_date}).")

        return " ".join(parts)


class ReferenceFormatter:
    """文獻格式化器管理類"""

    FORMATTERS = {
        'apa': APAFormatter(),
        'mla': MLAFormatter(),
        'chicago': ChicagoFormatter(),
        'harvard': HarvardFormatter(),
    }

    @classmethod
    def format(cls, data: Dict, style: str = 'apa') -> str:
        """
        格式化文獻

        Args:
            data: 文獻資料字典
            style: 格式類型 ('apa', 'mla', 'chicago', 'harvard')

        Returns:
            格式化後的文獻字串
        """
        style = style.lower()
        formatter = cls.FORMATTERS.get(style)

        if not formatter:
            raise ValueError(f"不支援的格式: {style}")

        return formatter.format(data)

    @classmethod
    def get_available_styles(cls) -> List[str]:
        """獲取所有可用的格式類型"""
        return list(cls.FORMATTERS.keys())

    @classmethod
    def format_multiple(cls, references: List[Dict], style: str = 'apa') -> List[str]:
        """
        批次格式化多條文獻

        Args:
            references: 文獻資料列表
            style: 格式類型

        Returns:
            格式化後的文獻字串列表
        """
        return [cls.format(ref, style) for ref in references]
