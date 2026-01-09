"""
Image cache manager - stores captured screenshots until analysis
"""
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Optional
import os

from config import MAX_CACHED_IMAGES, CACHE_DIR


@dataclass
class CachedImage:
    """Represents a cached screenshot"""
    path: Path
    timestamp: datetime
    order: int
    window_title: str = ""
    
    def __post_init__(self):
        if isinstance(self.path, str):
            self.path = Path(self.path)


class ImageCache:
    """Manages captured screenshots in memory and on disk"""
    
    def __init__(self):
        self._images: List[CachedImage] = []
        self._counter = 0
        
    @property
    def count(self) -> int:
        """Number of images in cache"""
        return len(self._images)
    
    @property
    def images(self) -> List[CachedImage]:
        """Get all cached images"""
        return self._images.copy()
    
    @property
    def image_paths(self) -> List[Path]:
        """Get all image paths"""
        return [img.path for img in self._images]
    
    def add(self, path: Path, window_title: str = "") -> bool:
        """
        Add a new image to the cache.
        Returns True if added, False if cache is full.
        """
        if self.count >= MAX_CACHED_IMAGES:
            print(f"⚠️ Cache full ({MAX_CACHED_IMAGES} images max)")
            return False
        
        self._counter += 1
        cached = CachedImage(
            path=path,
            timestamp=datetime.now(),
            order=self._counter,
            window_title=window_title
        )
        self._images.append(cached)
        print(f"📦 Cached image #{self._counter} ({self.count}/{MAX_CACHED_IMAGES})")
        return True
    
    def clear(self, delete_files: bool = True) -> int:
        """
        Clear all cached images.
        Returns the number of images cleared.
        """
        count = self.count
        
        if delete_files:
            for img in self._images:
                try:
                    if img.path.exists():
                        os.remove(img.path)
                except Exception as e:
                    print(f"Could not delete {img.path}: {e}")
        
        self._images.clear()
        self._counter = 0
        print(f"🗑️ Cache cleared ({count} images)")
        return count
    
    def remove_last(self) -> Optional[CachedImage]:
        """Remove and return the last cached image"""
        if not self._images:
            return None
        
        img = self._images.pop()
        try:
            if img.path.exists():
                os.remove(img.path)
        except:
            pass
        
        print(f"↩️ Removed last image, {self.count} remaining")
        return img
    
    def get_summary(self) -> str:
        """Get a summary of cached images"""
        if not self._images:
            return "No images cached"
        
        lines = [f"📷 {self.count} image(s) cached:"]
        for img in self._images:
            time_str = img.timestamp.strftime("%H:%M:%S")
            lines.append(f"  #{img.order}: {time_str} - {img.window_title[:30]}")
        
        return "\n".join(lines)


# Global cache instance
cache = ImageCache()


def cleanup_old_cache_files():
    """Remove any leftover cache files from previous sessions"""
    try:
        for file in CACHE_DIR.glob("capture_*.png"):
            os.remove(file)
        for file in CACHE_DIR.glob("fullscreen_*.png"):
            os.remove(file)
        print("🧹 Cleaned up old cache files")
    except Exception as e:
        print(f"Cache cleanup error: {e}")


if __name__ == "__main__":
    # Test cache
    print("Testing image cache...")
    
    # Create dummy test
    test_cache = ImageCache()
    print(f"Empty cache count: {test_cache.count}")
    print(test_cache.get_summary())
