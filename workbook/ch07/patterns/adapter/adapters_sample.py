
import xml.etree.ElementTree as ET
import json
import os
from typing import Dict, Any, Union, List, Optional


# XML --> JSON
class XMLtoJSONAdapter:
    def __init__(self, xml_input: Union[str, bytes, os.PathLike] = None):
        self.root = None
        if xml_input:
            self.parse(xml_input)
    
    def parse(self, xml_input: Union[str, bytes, os.PathLike]) -> None:
        if isinstance(xml_input, (str, bytes)) and os.path.isfile(str(xml_input)):
            try:
                self.root = ET.parse(xml_input).getroot()
            except ET.ParseError as e:
                with open(xml_input, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    self.root = ET.fromstring(content)
        elif isinstance(xml_input, str) and '<' in xml_input:
            self.root = ET.fromstring(xml_input.strip())
        elif isinstance(xml_input, bytes):
            self.root = ET.fromstring(xml_input)
        else:
            raise ValueError("Input must be an XML string, bytes, or file path")
    
    def to_json(self, indent: int = 2) -> str:
        if self.root is None:
            raise ValueError("No XML data has been parsed")
        
        python_dict = self._element_to_dict(self.root)
        return json.dumps(python_dict, indent=indent)
    
    def to_dict(self) -> Dict[str, Any]:
        if self.root is None:
            raise ValueError("No XML data has been parsed")
        
        return self._element_to_dict(self.root)
    
    def save_json(self, file_path: os.PathLike, indent: int = 2) -> None:
        if self.root is None:
            raise ValueError("No XML data has been parsed")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self._element_to_dict(self.root), f, indent=indent)
    
    def _element_to_dict(self, element: ET.Element) -> Dict[str, Any]:
        tag = self._strip_namespace(element.tag)
        node: Dict[str, Any] = {}
        
        attribs = {}
        for attr_name, attr_value in element.attrib.items():
            full_name = self._qualify_attrib_name(attr_name)
            attribs[full_name] = attr_value
        
        if attribs:
            node["@attributes"] = attribs
        
        children = list(element)
        if children:
            child_dict: Dict[str, List] = {}
            
            for child in children:
                child_tag = self._strip_namespace(child.tag)
                child_content = self._element_to_dict(child)
                
                if child_tag not in child_dict:
                    child_dict[child_tag] = []
                
                child_dict[child_tag].append(child_content[child_tag])
            
            for k, v in child_dict.items():
                if len(v) == 1:
                    child_dict[k] = v[0]
            
            node.update(child_dict)
        
        text = (element.text or '').strip()
        if text:
            node["#text"] = text
            
        tail = (element.tail or '').strip()
        if tail:
            node["#tail"] = tail
            
        return {tag: node}
    
    def _strip_namespace(self, tag: str) -> str:
        if '}' in tag:
            return tag.split('}', 1)[1]
        return tag
    
    def _qualify_attrib_name(self, attr_name: str) -> str:
        if '}' in attr_name:
            ns, name = attr_name.split('}', 1)
            ns_uri = ns[1:]
            return f"{ns_uri}:{name}"
        return attr_name

# JSON --> XML
class JSONtoXMLAdapter:
    def __init__(self, json_input: Union[str, Dict, os.PathLike] = None, 
                 namespace_map: Optional[Dict[str, str]] = None):
        self.data = None
        self.namespace_map = namespace_map or {}
        
        if json_input:
            self.parse(json_input)
    
    def parse(self, json_input: Union[str, Dict, os.PathLike]) -> None:
        if isinstance(json_input, dict):
            self.data = json_input
        elif isinstance(json_input, str) and os.path.isfile(json_input):
            with open(json_input, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        elif isinstance(json_input, str):
            self.data = json.loads(json_input)
        else:
            raise ValueError("Input must be a JSON string, dictionary, or file path")
    
    def to_xml_string(self, encoding: str = 'unicode', 
                      xml_declaration: bool = False,
                      pretty_print: bool = False) -> str:
        if self.data is None:
            raise ValueError("No JSON data has been parsed")
            
        if len(self.data) != 1:
            raise ValueError("JSON root must have exactly one top-level key")
            
        root_tag = list(self.data.keys())[0]
        root_content = self.data[root_tag]
        root_element = self._dict_to_element(root_tag, root_content)
        
        for prefix, uri in self.namespace_map.items():
            root_element.set(f"xmlns:{prefix}", uri)
        
        xml_string = ET.tostring(root_element, encoding=encoding, 
                                 xml_declaration=xml_declaration)
        
        if pretty_print and encoding == 'unicode':
            import xml.dom.minidom
            xml_string = xml.dom.minidom.parseString(xml_string).toprettyxml(indent="  ")
        
        return xml_string
    
    def save_xml(self, file_path: os.PathLike, 
                 encoding: str = 'utf-8',
                 xml_declaration: bool = True,
                 pretty_print: bool = True) -> None:
        if self.data is None:
            raise ValueError("No JSON data has been parsed")
            
        if pretty_print:
            import xml.dom.minidom
            root_tag = list(self.data.keys())[0]
            root_content = self.data[root_tag]
            root_element = self._dict_to_element(root_tag, root_content)
            
            for prefix, uri in self.namespace_map.items():
                root_element.set(f"xmlns:{prefix}", uri)
                
            xml_str = ET.tostring(root_element, encoding='unicode')
            dom = xml.dom.minidom.parseString(xml_str)
            xml_content = dom.toprettyxml(indent="  ")
            
            if xml_content.startswith('<?xml'):
                xml_content = xml_content[xml_content.index('?>')+2:].lstrip()
        else:
            xml_content = self.to_xml_string(encoding='unicode', 
                                           xml_declaration=False,
                                           pretty_print=False)
        
        with open(file_path, 'w', encoding=encoding) as f:
            if xml_declaration:
                f.write(f'<?xml version="1.0" encoding="{encoding}"?>\n')
            f.write(xml_content)
    
    def _dict_to_element(self, tag: str, content: Any) -> ET.Element:
        if ':' in tag and tag.split(':')[0] in self.namespace_map:
            prefix, local_name = tag.split(':', 1)
            ns_uri = self.namespace_map[prefix]
            tag = f"{{{ns_uri}}}{local_name}"
        
        element = ET.Element(tag)
        
        if not isinstance(content, dict):
            element.text = str(content)
            return element
        
        attribs = content.get("@attributes", {})
        for k, v in attribs.items():
            if ':' in k:
                prefix, local_name = k.split(':', 1)
                if prefix in self.namespace_map:
                    ns_uri = self.namespace_map[prefix]
                    k = f"{{{ns_uri}}}{local_name}"
            element.set(k, str(v))
        
        text = content.get("#text")
        if text is not None:
            element.text = str(text)
        
        tail = content.get("#tail")
        if tail is not None:
            element.tail = str(tail)
        
        for key, value in content.items():
            if key in ("@attributes", "#text", "#tail"):
                continue
                
            if isinstance(value, list):
                for item in value:
                    child = self._dict_to_element(key, item)
                    element.append(child)
            else:
                child = self._dict_to_element(key, value)
                element.append(child)
                
        return element


# Example (how to use)
def example_xml_to_json(xml_input, output_file=None):
    adapter = XMLtoJSONAdapter(xml_input)
    json_result = adapter.to_json(indent=2)
    
    if output_file:
        adapter.save_json(output_file)
        
    return json_result

def example_json_to_xml(json_input, namespace_map=None, output_file=None):
    adapter = JSONtoXMLAdapter(json_input, namespace_map)
    xml_result = adapter.to_xml_string(pretty_print=True)
    
    if output_file:
        adapter.save_xml(output_file)
        
    return xml_result


# Sample data for testing
sample_xml = '''
<ns0:person xmlns:ns0="http://example.org/person" id="123">
    <ns0:name>John Doe</ns0:name>
    <ns0:email>john@example.com</ns0:email>
    <ns0:phones>
        <ns0:phone type="mobile">123-456</ns0:phone>
        <ns0:phone type="home">789-012</ns0:phone>
    </ns0:phones>
</ns0:person>
'''

sample_json = {
  "person": {
    "@attributes": {
      "id": "123"
    },
    "name": {
      "#text": "John Doe"
    },
    "email": {
      "#text": "john@example.com"
    },
    "phones": {
      "phone": [
        {
          "@attributes": {
            "type": "mobile"
          },
          "#text": "123-456"
        },
        {
          "@attributes": {
            "type": "home"
          },
          "#text": "789-012"
        }
      ]
    }
  }
}

# Test
if __name__ == "__main__":

    # Example 1: XML string to JSON
    print("Example 1: XML string to JSON")
    json_result = example_xml_to_json(sample_xml)
    print(json_result)
    print("\n" + "-" * 80 + "\n")
    
    # Example 2: JSON to XML
    print("Example 2: JSON to XML")
    namespace_map = {"ns0": "http://example.org/person"}
    xml_result = example_json_to_xml(sample_json, namespace_map)
    print(xml_result)
    print("\n" + "-" * 80 + "\n")
    
    # Example 3: Save XML to file and read it back
    print("Example 3: Save XML to file and read it back")
    try:
        # Create XML and save to file
        json_adapter = JSONtoXMLAdapter(sample_json, namespace_map)
        json_adapter.save_xml("person.xml")
        print(f"Saved XML to 'person.xml'")
        
        # Now read it back
        xml_adapter = XMLtoJSONAdapter("person.xml")
        json_from_file = xml_adapter.to_json()
        print("JSON from file:")
        print(json_from_file)
    except Exception as e:
        print(f"Error in Example 3: {e}")
    print("\n" + "-" * 80 + "\n")
    
    # Example 4: Save JSON to file and read it back
    print("Example 4: Save JSON to file and read it back")
    try:
        # Create JSON and save to file
        xml_adapter = XMLtoJSONAdapter(sample_xml)
        xml_adapter.save_json("person.json")
        print(f"Saved JSON to 'person.json'")
        
        # Now read it back
        json_adapter = JSONtoXMLAdapter("person.json")
        xml_from_file = json_adapter.to_xml_string(pretty_print=True)
        print("XML from file:")
        print(xml_from_file)
    except Exception as e:
        print(f"Error in Example 4: {e}")

