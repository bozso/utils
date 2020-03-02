import re
import requests
import os.path as path
from base64 import b64encode

from utils import str_t

__all__ = (
    "Encoder", "url_regex",
)

url_regex = re.compile("^(http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)?[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?$")

class Encoder(object):
    __slots__ = (
        "encoder",
    )
    
    klass2ext = {
        "text" : frozenset({
            "js", "css",
        }),
        
        "video" : frozenset({
            "mp4",
        }),
        
        "image": frozenset({
            "png", "jpg",
        }),
    }
    
    tpl = "data:{klass}/{mode};charset=utf-8;base64,{data}"
    
    ext2klass = {v: k for k, v in klass2ext.items()}
    
    convert = {
        "js": "javascript",
    }
    
    def __init__(self, encoder=b64encode):
        self.encoder = encoder
    
    def encode_child(self, child):
        if isinstance(child, str_t):
            return

        enc = child.encode
        
        if enc is None:
            return
        
        child.options[enc] = self(child.options[enc])
    
    def encode_children(self, children):
        for child in children:
            if isinstance(child, str_t):
                continue
            
            try:
                self.encode_children(child.children)
            except AttributeError:
                self.encode_child(child)
    
    @staticmethod
    def load_media(media_path):
        if path.isfile(media_path):
            with open(media_path, "rb") as f:
                return f.read()

        if url_regex.match(media_path) is None:
            raise TypeError("Given path ('%s') to encodable media is "
                "not a valid URL or valid filepath!" % media_path)
        
        response = requests.get(media_path)
        response.raise_for_status()
        
        return response.content
    
    def __call__(self, media_path):
        mode = ext = path.splitext(media_path)[1].strip(".")
        
        for key, val in self.ext2klass.items():
            if ext in key:
                klass = val
                break
        
        if mode in self.convert:
            mode = convert[ext]
        
        data = self.encoder(self.load_media(media_path))
        
        return self.tpl.format(
            klass=klass, mode=mode, data=data.decode("utf-8")
        )
