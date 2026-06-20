import json
import hashlib
import os
import re
from datetime import datetime
from pathlib import Path

# 导入链接解析和网页获取模块
try:
    from .link_parser import LinkParser
    from .web_fetcher import WebFetcher
    LINK_MODULES_AVAILABLE = True
except ImportError:
    LINK_MODULES_AVAILABLE = False

CONFIG_PATH = "/Users/wujing/QingZhen/Tiktok/TikTokShop/知识库/config.json"
INDEX_PATH = "/Users/wujing/QingZhen/Tiktok/TikTokShop/知识库/index.json"
METADATA_PATH = "/Users/wujing/QingZhen/Tiktok/TikTokShop/知识库/metadata/entry_metadata.json"
KNOWLEDGE_DIR = "/Users/wujing/QingZhen/Tiktok/TikTokShop/知识库"
HISTORY_DIR = "/Users/wujing/QingZhen/Tiktok/TikTokShop/知识库/history"
BACKUP_DIR = "/Users/wujing/QingZhen/Tiktok/TikTokShop/知识库/backup"

class KnowledgePersistence:
    def __init__(self):
        self.config = self._load_config()
        self.index = self._load_index()
        self.metadata = self._load_metadata()
    
    def _load_config(self):
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _load_index(self):
        if os.path.exists(INDEX_PATH):
            with open(INDEX_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _load_metadata(self):
        if os.path.exists(METADATA_PATH):
            with open(METADATA_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_json(self, path, data):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _generate_id(self, title):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        hash_str = hashlib.md5(title.encode()).hexdigest()[:8]
        return f"entry_{hash_str}_{timestamp}"
    
    def _generate_version(self, current_version=None):
        if not current_version:
            return "1.0"
        major, minor = map(int, current_version.split('.'))
        return f"{major}.{minor + 1}"
    
    def _detect_knowledge(self, text):
        patterns = self.index.get('auto_capture_rules', {}).get('patterns', [])
        exclude_patterns = self.index.get('auto_capture_rules', {}).get('exclude_patterns', [])
        
        for exclude in exclude_patterns:
            if exclude in text:
                return False
        
        for pattern in patterns:
            if re.search(pattern, text):
                return True
        return False
    
    def _classify_knowledge(self, text):
        entries = self.index.get('entries', [])
        for entry in entries:
            for keyword in entry['keywords']:
                if keyword in text:
                    return entry['file'].replace('.md', ''), entry['priority']
        return "常见问题", 2
    
    def _validate_content(self, content):
        rules = self.config.get('validation_rules', {})
        min_len = rules.get('min_content_length', 10)
        max_len = rules.get('max_content_length', 10000)
        
        if len(content.strip()) < min_len:
            return False, "内容太短，至少需要{}个字符".format(min_len)
        if len(content) > max_len:
            return False, "内容太长，最多允许{}个字符".format(max_len)
        if not content.strip():
            return False, "内容不能为空"
        
        return True, "验证通过"
    
    def _detect_duplicate(self, content):
        content_hash = hashlib.md5(content.encode()).hexdigest()
        for entry in self.metadata.get('entries', []):
            entry_path = os.path.join(ENTRIES_DIR, f"{entry['category']}.md")
            if os.path.exists(entry_path):
                with open(entry_path, 'r', encoding='utf-8') as f:
                    existing_hash = hashlib.md5(f.read().encode()).hexdigest()
                    if existing_hash == content_hash:
                        return True
        return False
    
    def capture_knowledge(self, text, context=""):
        if not self._detect_knowledge(text):
            return {"success": False, "message": "未检测到新知识"}
        
        is_valid, msg = self._validate_content(text)
        if not is_valid:
            return {"success": False, "message": msg}
        
        if self._detect_duplicate(text):
            return {"success": False, "message": "检测到重复内容，已跳过"}
        
        category, priority = self._classify_knowledge(text)
        entry_id = self._generate_id(text[:20])
        
        now = datetime.now().isoformat()
        
        knowledge_entry = {
            "id": entry_id,
            "title": text[:50] + "..." if len(text) > 50 else text,
            "category": category,
            "content": text,
            "tags": self._extract_tags(text),
            "created_at": now,
            "updated_at": now,
            "version": "1.0",
            "source": "auto_capture",
            "context": context,
            "priority": priority,
            "hash": hashlib.md5(text.encode()).hexdigest()
        }
        
        self._save_entry(knowledge_entry)
        self._update_metadata(knowledge_entry, "create")
        self._create_version_history(knowledge_entry, "初始创建")
        
        return {
            "success": True,
            "message": "✅ 知识已成功保存！",
            "entry_id": entry_id,
            "category": category,
            "version": "1.0",
            "timestamp": now
        }
    
    def _extract_tags(self, text):
        tags = []
        entries = self.index.get('entries', [])
        for entry in entries:
            for keyword in entry['keywords']:
                if keyword in text and keyword not in tags:
                    tags.append(keyword)
        return tags[:5]
    
    def _save_entry(self, entry):
        category_file = os.path.join(KNOWLEDGE_DIR, f"{entry['category']}.md")
        
        if os.path.exists(category_file):
            with open(category_file, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = f"# {entry['category']}\n\n"
        
        new_section = f"\n## {entry['title']}\n\n{entry['content']}\n\n---\n"
        content += new_section
        
        with open(category_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _update_metadata(self, entry, action):
        self.metadata['entries'].append({
            "id": entry['id'],
            "category": entry['category'],
            "title": entry['title'],
            "created_at": entry['created_at'],
            "version": entry['version']
        })
        self.metadata['total_entries'] += 1
        self.metadata['last_updated'] = datetime.now().isoformat()
        self.metadata['statistics']['total_created'] += 1
        if entry['category'] in self.metadata['statistics']['categories']:
            self.metadata['statistics']['categories'][entry['category']] += 1
        
        self._save_json(METADATA_PATH, self.metadata)
    
    def _create_version_history(self, entry, change_summary):
        history_dir = os.path.join(HISTORY_DIR, entry['category'])
        os.makedirs(history_dir, exist_ok=True)
        
        history_file = os.path.join(history_dir, f"{entry['id']}_history.json")
        
        history_entry = {
            "version": entry['version'],
            "timestamp": entry['created_at'],
            "action": "create",
            "content_hash": entry['hash'],
            "change_summary": change_summary,
            "title": entry['title'],
            "category": entry['category']
        }
        
        if os.path.exists(history_file):
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        else:
            history = {"entry_id": entry['id'], "versions": []}
        
        history['versions'].append(history_entry)
        self._save_json(history_file, history)
    
    def update_knowledge(self, entry_id, new_content):
        for entry in self.metadata['entries']:
            if entry['id'] == entry_id:
                old_version = entry.get('version', '1.0')
                new_version = self._generate_version(old_version)
                
                category = entry['category']
                category_file = os.path.join(KNOWLEDGE_DIR, f"{category}.md")
                
                if os.path.exists(category_file):
                    with open(category_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    old_title = entry['title']
                    new_title = new_content[:50] + "..." if len(new_content) > 50 else new_content
                    
                    content = content.replace(f"## {old_title}", f"## {new_title}")
                    
                    with open(category_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    entry['title'] = new_title
                    entry['version'] = new_version
                    entry['updated_at'] = datetime.now().isoformat()
                    self.metadata['last_updated'] = entry['updated_at']
                    self.metadata['statistics']['total_updated'] += 1
                    self._save_json(METADATA_PATH, self.metadata)
                    
                    history_dir = os.path.join(HISTORY_DIR, category)
                    history_file = os.path.join(history_dir, f"{entry_id}_history.json")
                    if os.path.exists(history_file):
                        with open(history_file, 'r', encoding='utf-8') as f:
                            history = json.load(f)
                    else:
                        history = {"entry_id": entry_id, "versions": []}
                    
                    history['versions'].append({
                        "version": new_version,
                        "timestamp": datetime.now().isoformat(),
                        "action": "update",
                        "content_hash": hashlib.md5(new_content.encode()).hexdigest(),
                        "change_summary": "内容更新"
                    })
                    self._save_json(history_file, history)
                    
                    return {"success": True, "message": "✅ 知识已更新！", "version": new_version}
        
        return {"success": False, "message": "未找到知识条目"}
    
    def search_knowledge(self, keyword):
        results = []
        for entry in self.index.get('entries', []):
            if any(keyword.lower() in kw.lower() for kw in entry['keywords']):
                category_file = os.path.join(KNOWLEDGE_DIR, entry['file'])
                if os.path.exists(category_file):
                    with open(category_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        snippet = content[:200] + "..." if len(content) > 200 else content
                        results.append({
                            "category": entry['file'].replace('.md', ''),
                            "priority": entry['priority'],
                            "snippet": snippet
                        })
        
        results.sort(key=lambda x: x['priority'])
        return results
    
    def create_backup(self):
        import zipfile
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(BACKUP_DIR, f"backup_{timestamp}.zip")
        
        with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk("/Users/wujing/QingZhen/Tiktok/TikTokShop/知识库"):
                for file in files:
                    if not file.startswith('.'):
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, "/Users/wujing/QingZhen/Tiktok/TikTokShop/知识库")
                        zipf.write(file_path, arcname)
        
        self.metadata['backup_count'] += 1
        self._save_json(METADATA_PATH, self.metadata)
        
        return {"success": True, "message": "✅ 备份成功！", "backup_file": backup_file}
    
    def get_statistics(self):
        return {
            "total_entries": self.metadata.get('total_entries', 0),
            "categories": self.metadata.get('statistics', {}).get('categories', {}),
            "backup_count": self.metadata.get('backup_count', 0),
            "last_updated": self.metadata.get('last_updated', '')
        }
    
    def learn_from_link(self, url):
        """从链接学习并保存知识"""
        if not LINK_MODULES_AVAILABLE:
            return {"success": False, "message": "链接解析模块未加载"}
        
        is_valid, msg = LinkParser.validate_url(url)
        if not is_valid:
            return {"success": False, "message": f"URL验证失败：{msg}"}
        
        title, content, links, error = WebFetcher.fetch_and_parse(url)
        if error:
            return {"success": False, "message": f"获取内容失败：{error}"}
        
        if not content:
            return {"success": False, "message": "未能提取到有效内容"}
        
        is_valid, msg = self._validate_content(content)
        if not is_valid:
            return {"success": False, "message": msg}
        
        if self._detect_duplicate(content):
            return {"success": False, "message": "检测到重复内容，已跳过"}
        
        link_type = LinkParser.detect_link_type(url)
        category, priority = self._classify_knowledge(content)
        
        entry_id = self._generate_id(title[:20] if title else url[:20])
        now = datetime.now().isoformat()
        
        knowledge_entry = {
            "id": entry_id,
            "title": title if title else url[:50],
            "category": category,
            "content": content,
            "tags": self._extract_tags(content),
            "created_at": now,
            "updated_at": now,
            "version": "1.0",
            "source": "link_learning",
            "context": f"来源链接：{url}",
            "priority": priority,
            "hash": hashlib.md5(content.encode()).hexdigest(),
            "link_type": link_type,
            "original_url": url
        }
        
        self._save_entry(knowledge_entry)
        self._update_metadata(knowledge_entry, "create")
        self._create_version_history(knowledge_entry, f"从链接学习：{url}")
        
        result = {
            "success": True,
            "message": "✅ 链接内容学习成功！",
            "entry_id": entry_id,
            "category": category,
            "title": title,
            "url": url,
            "version": "1.0",
            "timestamp": now,
            "links_found": len(links) if links else 0
        }
        
        if links and len(links) > 0:
            result["suggestion"] = f"检测到 {len(links)} 个相关链接，是否继续学习？"
        
        return result
    
    def learn_from_links(self, urls):
        """批量从多个链接学习"""
        results = []
        for url in urls:
            result = self.learn_from_link(url)
            results.append(result)
        
        success_count = sum(1 for r in results if r.get('success'))
        return {
            "success": success_count == len(urls),
            "message": f"批量学习完成，成功 {success_count}/{len(urls)}",
            "results": results
        }

if __name__ == "__main__":
    kp = KnowledgePersistence()
    print("知识持久化系统初始化完成")
    print("统计信息:", kp.get_statistics())