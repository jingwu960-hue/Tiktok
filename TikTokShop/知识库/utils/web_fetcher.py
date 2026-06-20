import requests
from bs4 import BeautifulSoup
import re
from markdownify import markdownify as md

class WebFetcher:
    """网页内容获取模块"""
    
    # 请求头配置
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0'
    }
    
    # 超时设置（秒）
    TIMEOUT = 30
    
    # 重试次数
    MAX_RETRIES = 3
    
    @staticmethod
    def fetch(url, timeout=TIMEOUT, retries=MAX_RETRIES):
        """获取网页内容"""
        session = requests.Session()
        session.headers.update(WebFetcher.HEADERS)
        
        for attempt in range(retries):
            try:
                response = session.get(url, timeout=timeout)
                response.raise_for_status()
                
                # 检查内容类型
                content_type = response.headers.get('content-type', '')
                if 'text/html' not in content_type.lower():
                    return None, f"不支持的内容类型：{content_type}"
                
                return response.text, None
                
            except requests.exceptions.Timeout:
                if attempt < retries - 1:
                    continue
                return None, f"请求超时（{timeout}秒）"
            except requests.exceptions.HTTPError as e:
                return None, f"HTTP错误：{e.response.status_code}"
            except requests.exceptions.RequestException as e:
                return None, f"请求失败：{str(e)}"
        
        return None, "重试次数已用尽"
    
    @staticmethod
    def parse_html(html):
        """解析HTML，提取关键信息"""
        if not html:
            return None, None, None
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # 提取标题
        title = ""
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text(strip=True)
        
        # 提取正文内容
        content = ""
        
        # 尝试多种方式提取内容
        content_selectors = [
            'article',
            '.article-content',
            '.content',
            '.main-content',
            '.post-content',
            '#content',
            'div.content',
            'div.main',
            'main',
            '.course-content',
            '.lesson-content'
        ]
        
        content_found = False
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                content = WebFetcher._clean_content(element)
                content_found = True
                break
        
        # 如果没有找到特定容器，提取所有段落
        if not content_found:
            paragraphs = soup.find_all('p')
            content = "\n\n".join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
        
        # 提取超链接
        links = []
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            if href.startswith('http'):
                text = a_tag.get_text(strip=True)[:50]
                links.append({'text': text, 'href': href})
        
        return title, content, links
    
    @staticmethod
    def _clean_content(element):
        """清理内容，去除多余标签"""
        # 移除脚本和样式
        for script in element(['script', 'style', 'noscript', 'iframe']):
            script.decompose()
        
        # 获取文本内容
        text = element.get_text(separator='\n')
        
        # 清理多余空白
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        text = text.strip()
        
        return text
    
    @staticmethod
    def to_markdown(html):
        """将HTML转换为Markdown"""
        if not html:
            return ""
        
        # 使用markdownify转换
        md_text = md(html, heading_style="ATX")
        
        # 清理转换后的内容
        md_text = re.sub(r'\n{3,}', '\n\n', md_text)
        md_text = md_text.strip()
        
        return md_text
    
    @staticmethod
    def extract_key_info(content, max_length=3000):
        """提取关键信息，限制长度"""
        if not content:
            return ""
        
        # 移除多余空白和换行
        content = re.sub(r'\s+', ' ', content)
        
        # 限制长度
        if len(content) > max_length:
            # 找到合适的截断点
            truncate_at = content.rfind('。', 0, max_length)
            if truncate_at == -1:
                truncate_at = content.rfind('，', 0, max_length)
            if truncate_at == -1:
                truncate_at = max_length
            
            content = content[:truncate_at + 1] + "..."
        
        return content
    
    @staticmethod
    def fetch_and_parse(url):
        """获取并解析网页内容"""
        html, error = WebFetcher.fetch(url)
        if error:
            return None, None, None, error
        
        title, content, links = WebFetcher.parse_html(html)
        
        # 提取关键信息
        key_info = WebFetcher.extract_key_info(content)
        
        return title, key_info, links, None