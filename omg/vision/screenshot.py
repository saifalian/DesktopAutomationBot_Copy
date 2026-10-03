import mss
import mss.tools
from PIL import Image
import os
from datetime import datetime

class ScreenShotter:
    def __init__(self):
        self._sct = None
        self.last_screenshot_path = None

    @property
    def sct(self):
        if self._sct is None:
            self.sct = mss.mss()
        return self._sct

    @sct.setter
    def sct(self, value):
        self._sct = value

    def capture(self, output_dir="temp_screenshots", draw_grid=False, grid_density=10):
        """Captures the primary monitor and returns the PIL Image and path."""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Get primary monitor (usually monitor 1)
        monitor = self.sct.monitors[1]
        
        # Capture
        sct_img = self.sct.grab(monitor)
        
        # Convert to PIL Image
        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        
        if draw_grid:
            self._draw_grid_on_image(img, grid_density)
            
        # Save for reference (optional but helpful for logs)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        path = os.path.join(output_dir, f"screenshot_{timestamp}.png")
        img.save(path)
        
        self.last_screenshot_path = path
        return img, path

    def _draw_grid_on_image(self, img, density):
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(img)
        w, h = img.size
        
        # Colors: Blue for lines, Red for labels (consistent with UI)
        line_color = (52, 152, 219) # #3498DB
        label_color = (231, 76, 60) # #E74C3C
        
        # Draw Horizontal Lines
        for i in range(density + 1):
            y = int(h * (i / density))
            if y >= h: y = h - 1
            draw.line([(0, y), (w, y)], fill=line_color, width=1)
            # Label
            label = str(int(100 * (i / density)))
            draw.text((5, y + 2), label, fill=label_color)

        # Draw Vertical Lines
        for i in range(density + 1):
            x = int(w * (i / density))
            if x >= w: x = w - 1
            draw.line([(x, 0), (x, h)], fill=line_color, width=1)
            # Label
            label = str(int(100 * (i / density)))
            draw.text((x + 2, 5), label, fill=label_color)

    def get_screen_size(self):
        monitor = self.sct.monitors[1]
        return monitor["width"], monitor["height"]
