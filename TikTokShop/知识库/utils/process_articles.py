#!/usr/bin/env python3
"""处理已收集的 knowledge_id 并保存文章内容到知识库"""
import json
import os
import re
import sys

KNOWLEDGE_BASE = "/Users/wujing/QingZhen/Tiktok/TikTokShop/知识库"

def parse_quill_delta(content_json):
    """解析 Quill Delta 格式为纯文本"""
    try:
        data = json.loads(content_json)
        if data.get("version") != 2:
            return None
        deltas = data.get("deltas", {})
        lines = []
        for key in sorted(deltas.keys(), key=int):
            ops = deltas[key].get("ops", [])
            for op in ops:
                if isinstance(op.get("insert"), str):
                    lines.append(op["insert"])
                if op.get("attributes", {}).get("image"):
                    url = op.get("attributes", {}).get("src", "")
                    if url:
                        lines.append(f"\n[图片: {url}]\n")
        return "".join(lines)
    except Exception as e:
        return f"[解析错误: {e}]"

def save_article(knowledge_id, name, content):
    """保存文章到知识库"""
    safe_name = re.sub(r'[/:*?"<>|]', '_', name)
    filepath = os.path.join(KNOWLEDGE_BASE, f"{knowledge_id}_{safe_name}.md")
    
    text = parse_quill_delta(content)
    if not text:
        return False, "Quill 解析失败"
    
    md_content = f"# {name}\n\n> knowledge_id: {knowledge_id}\n\n{text}\n"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    return True, filepath

def process_temp_file(temp_file_path):
    """处理 MCP 输出的临时文件"""
    with open(temp_file_path, 'r') as f:
        content = f.read().strip()
    
    # MCP 响应格式: [{"type":"text","text":"..."}, ..., {"type":"text","text":"\"{...}\""}]
    # 找到最后一个 "text" 字段的值（包含 JSON 字符串）
    # 提取引号包裹的 JSON 字符串
    try:
        # 先尝试直接解析整个响应为 JSON 数组
        mcp_response = json.loads(content)
        if isinstance(mcp_response, list):
            # 找到包含结果的 text 对象（通常是最后一个或倒数第二个）
            for item in reversed(mcp_response):
                if isinstance(item, dict) and item.get("type") == "text":
                    text = item.get("text", "")
                    if text.startswith('"') and 'knowledge_id' in text:
                        json_str = json.loads(text)  # 解析转义的 JSON 字符串
                        return process_knowledge_data(json_str)
        print("错误: 无法从 MCP 响应中提取结果")
        return
    except json.JSONDecodeError:
        pass
    
    # 备用方法: 正则提取
    # 找到 "3691388223227664" 之类的模式
    match = re.search(r'\{"(\d{15,19})":', content)
    if match:
        start = match.start()
        # 提取 JSON 对象
        json_str = content[start:]
        # 找到匹配的结束括号
        depth = 0
        end = 0
        for i, c in enumerate(json_str):
            if c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
        json_str = json_str[:end]
        # 处理转义
        json_str = json_str.replace('\\"', '"').replace('\\\\', '\\')
        try:
            data = json.loads(json_str)
            return process_knowledge_data(data)
        except json.JSONDecodeError as e:
            print(f"备用方法 JSON 解析错误: {e}")
    
    print("无法提取 JSON 数据")

def process_knowledge_data(data):
    """处理知识数据字典"""
    print(f"共 {len(data)} 个知识条目")
    
    success = []
    failed = []
    
    for kid, api_response in data.items():
        try:
            resp = json.loads(api_response)
            if resp.get("code") != 0:
                failed.append((kid, f"API 错误: {resp.get('message')}"))
                continue
            
            detail = resp.get("data", {}).get("knowledge_detail", {})
            name = detail.get("knowledge_name", "未知")
            raw_content = detail.get("knowledge_content", "")
            
            if not raw_content:
                failed.append((kid, "无内容"))
                continue
            
            ok, path = save_article(kid, name, raw_content)
            if ok:
                success.append((kid, name, path))
            else:
                failed.append((kid, f"保存失败: {path}"))
        except Exception as e:
            failed.append((kid, str(e)))
    
    print(f"\n成功: {len(success)}")
    for kid, name, path in success:
        print(f"  ✅ {kid}: {name} -> {os.path.basename(path)}")
    
    print(f"\n失败: {len(failed)}")
    for kid, reason in failed:
        print(f"  ❌ {kid}: {reason}")
    
    return {"success": success, "failed": failed}

if __name__ == "__main__":
    if len(sys.argv) > 1:
        process_temp_file(sys.argv[1])
    else:
        print("用法: python process_articles.py <temp_file_path>")