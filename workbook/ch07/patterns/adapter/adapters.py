#!/usr/bin/env python3

import os
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom


# XMLtoJSONAdapter: Converts XML to JSON
class XMLtoJSONAdapter:
    def __init__(self, xml_source):
        self.xml_source = xml_source
        self.root = self._parse_xml_source()
    
    def _parse_xml_source(self):
        if isinstance(self.xml_source, str):
            if os.path.isfile(self.xml_source):
                return ET.parse(self.xml_source).getroot()
            else:
                return ET.fromstring(self.xml_source)
        else:
            raise TypeError("xml_source must be a string (XML content or file path)")
    
    def _element_to_dict(self, element):
        result = {}

        if element.attrib:
            result["@attributes"] = dict(element.attrib)
        
        tag = element.tag
        namespace = None
        
        if "}" in tag:
            namespace, tag = tag.split("}", 1)
            namespace = namespace[1:]
            result["@namespace"] = namespace
        
        result["@tag"] = tag
        
        children = list(element)
        if children:
            child_dict = {}
            
            for child in children:
                child_data = self._element_to_dict(child)
                child_tag = child_data["@tag"]
                
                if child_tag in child_dict:
                    if isinstance(child_dict[child_tag], list):
                        child_dict[child_tag].append(child_data)
                    else:
                        child_dict[child_tag] = [child_dict[child_tag], child_data]
                else:
                    child_dict[child_tag] = child_data
            
            result["@children"] = child_dict
        
        if element.text and element.text.strip():
            result["@text"] = element.text.strip()
        
        return result
    
    def to_dict(self):
        return self._element_to_dict(self.root)
    
    def to_json(self, indent=None, preserve_whitespace=False):
        if not preserve_whitespace and "@text" in self.to_dict():
            dict_data = self.to_dict()
            dict_data["@text"] = dict_data["@text"].strip()
        else:
            dict_data = self.to_dict()
        
        return json.dumps(dict_data, indent=indent)
    
    def save_json(self, file_path, indent=4):
        with open(file_path, 'w') as f:
            f.write(self.to_json(indent=indent))


# JSONtoXMLAdapter: Converts JSON to XML
class JSONtoXMLAdapter:    
    def __init__(self, json_source, namespace_map=None):
        self.json_source = json_source
        self.namespace_map = namespace_map or {}
        self.data = self._parse_json_source()
        self.root = None
    
    def _parse_json_source(self):
        if isinstance(self.json_source, dict):
            return self.json_source
        elif isinstance(self.json_source, str):
            if os.path.isfile(self.json_source):
                with open(self.json_source, 'r') as f:
                    return json.load(f)
            else:
                return json.loads(self.json_source)
        else:
            raise TypeError("json_source must be a dict, string (JSON content), or file path")
    
    def _dict_to_element(self, data, parent=None):
        tag = data.get("@tag", "element")
        namespace = data.get("@namespace")
        
        if namespace and parent is None:
            for prefix, uri in self.namespace_map.items():
                if uri == namespace:
                    element = ET.Element(f"{{{namespace}}}{tag}")
                    ET.register_namespace(prefix, uri)
                    break
            else:
                element = ET.Element(f"{{{namespace}}}{tag}")
        elif namespace:
            for prefix, uri in self.namespace_map.items():
                if uri == namespace:
                    element = ET.SubElement(parent, f"{{{namespace}}}{tag}")
                    break
            else:
                element = ET.SubElement(parent, f"{{{namespace}}}{tag}")
        elif parent is None:
            element = ET.Element(tag)
        else:
            element = ET.SubElement(parent, tag)
        
        if "@attributes" in data:
            for key, value in data["@attributes"].items():
                if ":" in key:
                    prefix, local_name = key.split(":", 1)
                    if prefix in self.namespace_map:
                        ns_uri = self.namespace_map[prefix]
                        element.set(f"{{{ns_uri}}}{local_name}", value)
                    else:
                        element.set(key, value)
                else:
                    element.set(key, value)
        
        if "@text" in data:
            element.text = data["@text"]
        
        if "@children" in data:
            for child_tag, child_data in data["@children"].items():
                if isinstance(child_data, list):
                    for item in child_data:
                        self._dict_to_element(item, element)
                else:
                    self._dict_to_element(child_data, element)
        
        return element
    
    def to_xml(self):
        self.root = self._dict_to_element(self.data)
        return self.root
    
    def to_xml_string(self, pretty_print=False, xml_declaration=False, encoding="utf-8"):
        if self.root is None:
            self.to_xml()
        
        xml_string = ET.tostring(self.root, encoding=encoding)
        
        if pretty_print:
            xml_string = minidom.parseString(xml_string).toprettyxml(indent="  ", encoding=encoding)
        
        xml_string = xml_string.decode(encoding)
        
        if not xml_declaration:
            xml_string = xml_string.split('\n', 1)[-1] if '\n' in xml_string else xml_string
        
        return xml_string
    
    def save_xml(self, file_path, pretty_print=True, xml_declaration=True):
        xml_string = self.to_xml_string(pretty_print, xml_declaration)
        with open(file_path, 'w') as f:
            f.write(xml_string)

