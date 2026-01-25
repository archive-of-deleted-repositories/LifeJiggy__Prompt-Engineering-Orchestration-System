"""XML parsing utilities."""

import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional


class XMLParser:
    """XML parsing utilities."""
    
    @staticmethod
    def parse(content: str) -> Optional[Any]:
        """Parse XML string.
        
        Args:
            content: XML string.
            
        Returns:
            Root element.
        """
        try:
            return ET.fromstring(content)
        except ET.ParseError:
            return None
    
    @staticmethod
    def parse_safe(content: str, default: Any = None) -> Any:
        """Safely parse XML with fallback.
        
        Args:
            content: XML string.
            default: Default value on error.
            
        Returns:
            Root element or default.
        """
        try:
            return ET.fromstring(content)
        except ET.ParseError:
            return default
    
    @staticmethod
    def to_dict(element: ET.Element) -> Dict[str, Any]:
        """Convert XML element to dictionary.
        
        Args:
            element: XML element.
            
        Returns:
            Dictionary representation.
        """
        result = {}
        
        if element.attrib:
            result["@attributes"] = element.attrib
        
        if element.text and element.text.strip():
            result["text"] = element.text.strip()
        
        children = list(element)
        if children:
            result["children"] = []
            for child in children:
                child_dict = XMLParser.to_dict(child)
                child_tag = child.tag
                
                if child_tag in result:
                    if not isinstance(result[child_tag], list):
                        result[child_tag] = [result[child_tag]]
                    result[child_tag].append(child_dict)
                else:
                    result[child_tag] = child_dict
        
        return result
    
    @staticmethod
    def find_elements(element: ET.Element, path: str) -> List[ET.Element]:
        """Find elements by path.
        
        Args:
            element: Root element.
            path: XPath-like path.
            
        Returns:
            List of matching elements.
        """
        return list(element.findall(path))
    
    @staticmethod
    def get_text(element: ET.Element, path: str = None) -> str:
        """Get text content.
        
        Args:
            element: Element or path.
            path: Optional element path.
            
        Returns:
            Text content.
        """
        if path:
            elem = element.find(path)
        else:
            elem = element
        
        if elem is not None and elem.text:
            return elem.text.strip()
        return ""
