"""
Profile Image Processor v3
Precise outer-only white background removal with premium gradient glow.
Uses a tighter threshold and better edge handling.
"""
from PIL import Image, ImageDraw, ImageFilter
import math
from collections import deque

def flood_fill_remove_bg(img, threshold=240):
    """
    Remove background by flood-filling from edges inward.
    Only removes connected near-white regions touching the image border.
    Uses a tight threshold to preserve white clothing.
    """
    img = img.convert("RGBA")
    w, h = img.size
    pixels = img.load()
    
    visited = set()
    to_remove = set()
    
    def is_bg(x, y):
        r, g, b, a = pixels[x, y]
        return r > threshold and g > threshold and b > threshold
    
    # Seed queue from all border pixels that are white
    queue = deque()
    
    for x in range(w):
        for y in (0, h - 1):
            if is_bg(x, y):
                queue.append((x, y))
                visited.add((x, y))
    for y in range(h):
        for x in (0, w - 1):
            if (x, y) not in visited and is_bg(x, y):
                queue.append((x, y))
                visited.add((x, y))
    
    # BFS flood fill — 8-connected
    while queue:
        cx, cy = queue.popleft()
        to_remove.add((cx, cy))
        
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    if is_bg(nx, ny):
                        queue.append((nx, ny))
    
    # Create alpha mask
    alpha = Image.new("L", (w, h), 255)
    alpha_pixels = alpha.load()
    
    for (px, py) in to_remove:
        alpha_pixels[px, py] = 0
    
    # Feather the edges: slight blur on alpha for smooth transition
    alpha = alpha.filter(ImageFilter.GaussianBlur(1.2))
    
    # Re-threshold to keep sharp but with soft anti-aliased edges
    alpha = alpha.point(lambda p: 0 if p < 20 else min(255, int(p * 1.3)))
    
    img.putalpha(alpha)
    return img

def create_gradient_glow_bg(width, height):
    """
    Premium radial gradient:
    - Center: dark navy (#080c16)
    - Outer ring: subtle purple→teal angular gradient glow
    """
    bg = Image.new("RGBA", (width, height))
    pixels_arr = bg.load()
    
    cx, cy = width // 2, int(height * 0.38)
    max_r = math.sqrt(max(cx, width - cx)**2 + max(cy, height - cy)**2)
    
    for y in range(height):
        for x in range(width):
            dist = math.sqrt((x - cx)**2 + (y - cy)**2) / max_r
            
            # Center color (dark navy, warmer than pure black)
            cr, cg, cb = 8, 12, 22
            
            # Angle for color gradient (purple top-right, teal bottom-left)
            angle = math.atan2(y - cy, x - cx)
            t_angle = (angle + math.pi) / (2 * math.pi)  # 0→1
            
            # Purple (108,99,255) → Teal (0,180,160)
            gr = int(108 * (1 - t_angle) + 0 * t_angle)
            gg = int(99 * (1 - t_angle) + 180 * t_angle)
            gb = int(255 * (1 - t_angle) + 160 * t_angle)
            
            # Distance curve: keep center dark, glow builds gently outward
            t = max(0.0, min(1.0, (dist - 0.25) / 0.75))
            t = t ** 2.2
            glow = t * 0.38  # Subtle, premium feel
            
            r = int(cr * (1 - glow) + gr * glow)
            g = int(cg * (1 - glow) + gg * glow)
            b = int(cb * (1 - glow) + gb * glow)
            
            pixels_arr[x, y] = (r, g, b, 255)
    
    return bg

def process_profile_image(input_path, output_path):
    print("Loading image...")
    original = Image.open(input_path)
    w, h = original.size
    print(f"Image size: {w}x{h}")
    
    print("Removing outer white background (tight threshold)...")
    cutout = flood_fill_remove_bg(original, threshold=240)
    
    print("Creating gradient glow background...")
    gradient_bg = create_gradient_glow_bg(w, h)
    
    print("Compositing...")
    gradient_bg.paste(cutout, (0, 0), cutout)
    
    gradient_bg.save(output_path, "PNG", quality=95)
    print(f"Saved to {output_path}")
    print("Done! Refresh your browser to see the changes.")

if __name__ == "__main__":
    process_profile_image(
        r"c:\portfolio\P230970139_Nishan Hegde (3).png",
        r"c:\portfolio\profile.png"
    )
