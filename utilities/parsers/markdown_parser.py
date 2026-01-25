"""Markdown parsing utilities."""

import re
from typing import Dict, Any, List, Optional


class MarkdownParser:
    """Markdown parsing utilities."""
    
    HEADING_PATTERN = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
    CODE_BLOCK_PATTERN = re.compile(r'```(\w*)\n([\s\S]*?)```', re.MULTILINE)
    INLINE_CODE_PATTERN = re.compile(r'`([^`]+)`')
    LINK_PATTERN = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
    BOLD_PATTERN = re.compile(r'\*\*([^*]+)\*\*')
    ITALIC_PATTERN = re.compile(r'\*([^*]+)\*')
    LIST_PATTERN = re.compile(r'^[\s]*[-*+]\s+(.+)$', re.MULTILINE)
    NUMBERED_LIST_PATTERN = re.compile(r'^[\s]*\d+\.\s+(.+)$', re.MULTILINE)
    BLOCKQUOTE_PATTERN = re.compile(r'^>\s+(.+)$', re.MULTILINE)
    TABLE_PATTERN = re.compile(r'\|(.+)\|\n\|[-:| ]+\|\n((?:\|.+\|\n?)+)')
    
    @staticmethod
    def parse(content: str) -> Dict[str, Any]:
        """Parse markdown to structured data.
        
        Args:
            content: Markdown content.
            
        Returns:
            Structured data.
        """
        return {
            "headings": MarkdownParser.extract_headings(content),
            "code_blocks": MarkdownParser.extract_code_blocks(content),
            "links": MarkdownParser.extract_links(content),
            "lists": MarkdownParser.extract_lists(content),
            "plain_text": MarkdownParser.extract_plain_text(content)
        }
    
    @staticmethod
    def extract_headings(content: str) -> List[Dict[str, Any]]:
        """Extract headings from markdown.
        
        Args:
            content: Markdown content.
            
        Returns:
            List of headings with level and text.
        """
        headings = []
        for match in MarkdownParser.HEADING_PATTERN.finditer(content):
            level = len(match.group(1))
            text = match.group(2).strip()
            headings.append({"level": level, "text": text})
        return headings
    
    @staticmethod
    def extract_code_blocks(content: str) -> List[Dict[str, Any]]:
        """Extract code blocks from markdown.
        
        Args:
            content: Markdown content.
            
        Returns:
            List of code blocks with language and code.
        """
        blocks = []
        for match in MarkdownParser.CODE_BLOCK_PATTERN.finditer(content):
            language = match.group(1)
            code = match.group(2).strip()
            blocks.append({"language": language, "code": code})
        return blocks
    
    @staticmethod
    def extract_links(content: str) -> List[Dict[str, str]]:
        """Extract links from markdown.
        
        Args:
            content: Markdown content.
            
        Returns:
            List of links with text and URL.
        """
        links = []
        for match in MarkdownParser.LINK_PATTERN.finditer(content):
            text = match.group(1)
            url = match.group(2)
            links.append({"text": text, "url": url})
        return links
    
    @staticmethod
    def extract_lists(content: str) -> List[Dict[str, Any]]:
        """Extract lists from markdown.
        
        Args:
            content: Markdown content.
            
        Returns:
            List of list items.
        """
        items = []
        for match in MarkdownParser.LIST_PATTERN.finditer(content):
            items.append({"type": "bullet", "text": match.group(1).strip()})
        for match in MarkdownParser.NUMBERED_LIST_PATTERN.finditer(content):
            items.append({"type": "numbered", "text": match.group(1).strip()})
        return items
    
    @staticmethod
    def extract_plain_text(content: str) -> str:
        """Extract plain text from markdown.
        
        Args:
            content: Markdown content.
            
        Returns:
            Plain text.
        """
        text = content
        
        text = MarkdownParser.CODE_BLOCK_PATTERN.sub('', text)
        text = MarkdownParser.HEADING_PATTERN.sub(r'\2', text)
        text = MarkdownParser.LIST_PATTERN.sub(r'\1\n', text)
        text = MarkdownParser.BLOCKQUOTE_PATTERN.sub(r'\1', text)
        text = MarkdownParser.INLINE_CODE_PATTERN.sub(r'\1', text)
        text = MarkdownParser.BOLD_PATTERN.sub(r'\1', text)
        text = MarkdownParser.ITALIC_PATTERN.sub(r'\1', text)
        
        lines = [line.strip() for line in text.split('\n')]
        return '\n'.join(line for line in lines if line)
    
    @staticmethod
    def to_html(markdown: str) -> str:
        """Convert markdown to HTML.
        
        Args:
            markdown: Markdown content.
            
        Returns:
            HTML content.
        """
        html = markdown
        
        html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
        html = re.sub(r'`(.+?)`', r'<code>\1</code>', html)
        html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html)
        html = re.sub(r'^- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        html = re.sub(r'\n', r'<br>\n', html)
        
        return html
