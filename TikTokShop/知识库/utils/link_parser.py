import re
import validators
from urllib.parse import urlparse

class LinkParser:
    """链接解析模块"""
    
    # 支持的域名白名单
    ALLOWED_DOMAINS = [
        'tiktokglobalshop.com',
        'seller.tiktokglobalshop.com',
        'university.tiktokglobalshop.com',
        '1688.com',
        'taobao.com',
        'jd.com',
        'pinduoduo.com',
        'aliexpress.com',
        'amazon.com',
        'shopee.com',
        'lazada.com'
    ]
    
    # 链接类型识别模式
    LINK_PATTERNS = {
        'tiktok_shop': r'https?://(seller\.)?tiktokglobalshop\.com/.*',
        'tiktok_university': r'https?://university\.tiktokglobalshop\.com/.*',
        '1688': r'https?://.*1688\.com/.*',
        'taobao': r'https?://.*taobao\.com/.*',
        'jd': r'https?://.*jd\.com/.*',
        'pdd': r'https?://.*pinduoduo\.com/.*',
        'aliexpress': r'https?://.*aliexpress\.com/.*',
        'amazon': r'https?://.*amazon\.com/.*',
        'shopee': r'https?://.*shopee\.com/.*',
        'lazada': r'https?://.*lazada\.com/.*'
    }
    
    @staticmethod
    def validate_url(url):
        """验证URL格式是否有效"""
        if not url or not isinstance(url, str):
            return False, "URL不能为空"
        
        url = url.strip()
        
        # 检查基本格式
        if not validators.url(url):
            return False, "URL格式不正确"
        
        # 检查域名白名单
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # 检查是否在允许的域名列表中
        allowed = any(allowed_domain in domain for allowed_domain in LinkParser.ALLOWED_DOMAINS)
        if not allowed:
            return False, f"不支持的域名：{domain}，仅支持TikTok Shop、1688、淘宝等平台"
        
        return True, "URL验证通过"
    
    @staticmethod
    def detect_link_type(url):
        """识别链接类型"""
        url = url.lower()
        for link_type, pattern in LinkParser.LINK_PATTERNS.items():
            if re.match(pattern, url):
                return link_type
        return 'unknown'
    
    @staticmethod
    def extract_urls(text):
        """从文本中提取所有URL"""
        url_pattern = r'https?://[^\s<>"\']+'
        urls = re.findall(url_pattern, text)
        return urls
    
    @staticmethod
    def get_domain(url):
        """获取域名"""
        parsed = urlparse(url)
        return parsed.netloc
    
    @staticmethod
    def is_same_domain(url1, url2):
        """判断两个URL是否同域"""
        return LinkParser.get_domain(url1) == LinkParser.get_domain(url2)
    
    @staticmethod
    def clean_url(url):
        """清理URL，去除多余参数"""
        parsed = urlparse(url)
        # 保留主要路径，去除跟踪参数
        clean = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        return clean