import base64
from io import BytesIO
from PIL import Image

class ImagePreprocessor:
    @staticmethod
    def encode_to_base64_string(image: Image.Image, format="PNG", quality=85):
        """Encodes PIL Image to base64 string."""
        buffered = BytesIO()
        image.save(buffered, format=format)
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

    @staticmethod
    def resize_for_vision_model(image: Image.Image, max_dim=1024):
        """Resizes image to stay within vision model context limits while maintaining aspect ratio."""
        width, height = image.size
        
        # Calculate aspect ratio
        if width > max_dim or height > max_dim:
            if width > height:
                new_width = max_dim
                new_height = int(height * (max_dim / width))
            else:
                new_height = max_dim
                new_width = int(width * (max_dim / height))
            
            return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        return image
