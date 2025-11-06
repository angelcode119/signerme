import os
import re
import zipfile
import shutil
import asyncio
import logging
import subprocess
from pathlib import Path
from .config import APKTOOL_PATH

logger = logging.getLogger(__name__)


class APKAnalyzer:
    """Extract information from APK files"""
    
    def __init__(self, apk_path):
        self.apk_path = apk_path
        self.temp_dir = None
    
    async def extract_icon(self, output_path):
        """Extract app icon from APK using multiple methods"""
        try:
            # Method 1: Try direct extraction from zip (for non-encrypted APKs)
            icon_extracted = await self._try_direct_extraction(output_path)
            if icon_extracted:
                return icon_extracted
            
            # Method 2: For encrypted APKs - create a placeholder or skip
            logger.info("⚠️ APK is encrypted - Icon extraction not available")
            logger.info("💡 Solution: Use Bot1 to generate unencrypted test APK for icon")
            
            # Optional: Create a placeholder icon
            placeholder = await self._create_placeholder_icon(output_path)
            if placeholder:
                return placeholder
            
            logger.warning("❌ Icon not available")
            return None
                
        except Exception as e:
            logger.error(f"Error extracting icon: {str(e)}")
            return None
    
    async def _try_direct_extraction(self, output_path):
        """Try to extract icon directly from zip"""
        try:
            # Get icon path from aapt
            icon_path = await self._get_icon_path_from_aapt()
            if icon_path:
                extracted = await self._extract_icon_from_zip(icon_path, output_path)
                if extracted:
                    return extracted
            
            # Try common patterns
            with zipfile.ZipFile(self.apk_path, 'r') as zip_ref:
                icon_patterns = [
                    'res/mipmap-xxxhdpi/ic_launcher.png',
                    'res/mipmap-xxhdpi/ic_launcher.png',
                    'res/mipmap-xhdpi/ic_launcher.png',
                    'res/mipmap-hdpi/ic_launcher.png',
                    'res/mipmap-mdpi/ic_launcher.png',
                    'res/drawable-xxxhdpi/ic_launcher.png',
                    'res/drawable-xxhdpi/ic_launcher.png',
                    'res/drawable-xhdpi/ic_launcher.png',
                    'res/drawable-hdpi/ic_launcher.png',
                    'res/drawable-mdpi/ic_launcher.png',
                    'res/drawable/ic_launcher.png',
                ]
                
                for icon_pattern in icon_patterns:
                    extracted = await self._extract_icon_from_zip(icon_pattern, output_path)
                    if extracted:
                        return extracted
                
                # Search for any ic_launcher file
                all_files = zip_ref.namelist()
                for file_path in all_files:
                    if 'ic_launcher' in file_path.lower() and file_path.endswith(('.png', '.jpg', '.webp')):
                        extracted = await self._extract_icon_from_zip(file_path, output_path)
                        if extracted:
                            logger.info(f"✅ Icon found via search: {file_path}")
                            return extracted
            
            return None
            
        except Exception as e:
            logger.debug(f"Direct extraction failed: {str(e)}")
            return None
    
    async def _create_placeholder_icon(self, output_path):
        """Create a simple placeholder icon for encrypted APKs"""
        try:
            # Try to use PIL/Pillow to create a simple icon
            try:
                from PIL import Image, ImageDraw, ImageFont
                
                # Create a simple 512x512 icon
                icon_size = 512
                img = Image.new('RGB', (icon_size, icon_size), color='#2196F3')
                draw = ImageDraw.Draw(img)
                
                # Draw a simple app icon shape (rounded square)
                margin = 50
                draw.rounded_rectangle(
                    [margin, margin, icon_size - margin, icon_size - margin],
                    radius=60,
                    fill='#1976D2',
                    outline='#0D47A1',
                    width=5
                )
                
                # Add text "APK"
                try:
                    font = ImageFont.truetype("arial.ttf", 120)
                except:
                    font = ImageFont.load_default()
                
                text = "APK"
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                text_x = (icon_size - text_width) // 2
                text_y = (icon_size - text_height) // 2
                
                draw.text((text_x, text_y), text, fill='white', font=font)
                
                # Save icon
                icon_path = os.path.join(output_path, 'icon.png')
                img.save(icon_path, 'PNG')
                
                logger.info("✅ Created placeholder icon")
                return icon_path
                
            except ImportError:
                logger.debug("PIL not available, skipping placeholder creation")
                return None
                
        except Exception as e:
            logger.error(f"Error creating placeholder: {str(e)}")
            return None
    
    async def _get_icon_path_from_aapt(self):
        """Get icon path using aapt"""
        try:
            aapt_paths = [
                r"C:\Users\awmeiiir\AppData\Local\Android\Sdk\build-tools\34.0.0\aapt2.exe",
                r"C:\Users\awmeiiir\AppData\Local\Android\Sdk\build-tools\34.0.0\aapt.exe",
                "aapt2",
                "aapt"
            ]
            
            for aapt in aapt_paths:
                try:
                    result = subprocess.run(
                        [aapt, 'dump', 'badging', self.apk_path],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    if result.returncode == 0:
                        # Look for application-icon line
                        icon_match = re.search(r"application-icon-(\d+):'([^']+)'", result.stdout)
                        if icon_match:
                            icon_path = icon_match.group(2)
                            logger.info(f"✅ Icon path from aapt: {icon_path}")
                            return icon_path
                        
                except (FileNotFoundError, subprocess.TimeoutExpired):
                    continue
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting icon path: {str(e)}")
            return None
    
    async def _extract_icon_from_zip(self, icon_path, output_path):
        """Extract specific icon file from APK zip"""
        try:
            with zipfile.ZipFile(self.apk_path, 'r') as zip_ref:
                try:
                    # Extract icon
                    zip_ref.extract(icon_path, output_path)
                    extracted_icon = os.path.join(output_path, icon_path)
                    
                    # Move to root of output_path
                    final_icon = os.path.join(output_path, 'icon.png')
                    
                    # Handle subdirectories
                    if os.path.exists(extracted_icon):
                        shutil.move(extracted_icon, final_icon)
                        
                        # Clean up extracted dirs
                        res_dir = os.path.join(output_path, 'res')
                        if os.path.exists(res_dir):
                            shutil.rmtree(res_dir)
                        
                        logger.info(f"✅ Icon extracted: {icon_path}")
                        return final_icon
                    
                except (KeyError, RuntimeError) as e:
                    # RuntimeError includes encryption errors
                    return None
            
            return None
            
        except Exception as e:
            # Don't log error here, will try decompile method
            return None
    
    async def get_app_info(self):
        """Extract app name and package using aapt or direct extraction"""
        try:
            # Method 1: Try using aapt2/aapt if available
            aapt_paths = [
                r"C:\Users\awmeiiir\AppData\Local\Android\Sdk\build-tools\34.0.0\aapt2.exe",
                r"C:\Users\awmeiiir\AppData\Local\Android\Sdk\build-tools\34.0.0\aapt.exe",
                "aapt2",
                "aapt"
            ]
            
            for aapt in aapt_paths:
                try:
                    result = subprocess.run(
                        [aapt, 'dump', 'badging', self.apk_path],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    if result.returncode == 0:
                        output = result.stdout
                        
                        # Extract package name
                        package_match = re.search(r"package: name='([^']+)'", output)
                        package_name = package_match.group(1) if package_match else None
                        
                        # Extract app label
                        label_match = re.search(r"application-label:'([^']+)'", output)
                        app_name = label_match.group(1) if label_match else None
                        
                        if app_name or package_name:
                            logger.info(f"✅ Info via aapt: {app_name} / {package_name}")
                            return app_name, package_name
                        
                except (FileNotFoundError, subprocess.TimeoutExpired):
                    continue
            
            # Method 2: Direct extraction from APK (fallback)
            return await self._extract_from_manifest()
            
        except Exception as e:
            logger.error(f"Error getting app info: {str(e)}")
            return None, None
    
    async def _extract_from_manifest(self):
        """Extract info directly from AndroidManifest.xml in APK"""
        try:
            with zipfile.ZipFile(self.apk_path, 'r') as zip_ref:
                # Read AndroidManifest.xml
                manifest_data = zip_ref.read('AndroidManifest.xml')
                
                # Decompile just the manifest using apktool
                temp_dir = f"temp_manifest_{os.getpid()}"
                os.makedirs(temp_dir, exist_ok=True)
                
                # Extract just manifest
                manifest_file = os.path.join(temp_dir, 'AndroidManifest.xml')
                with open(manifest_file, 'wb') as f:
                    f.write(manifest_data)
                
                # Use apktool to decode just the manifest
                result = subprocess.run(
                    ['java', '-jar', str(APKTOOL_PATH), 'd', '--only-main-classes', '--no-src', 
                     '--no-res', self.apk_path, '-o', temp_dir, '-f'],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode == 0:
                    manifest_path = os.path.join(temp_dir, 'AndroidManifest.xml')
                    if os.path.exists(manifest_path):
                        with open(manifest_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            
                            # Extract package
                            package_match = re.search(r'package="([^"]+)"', content)
                            package_name = package_match.group(1) if package_match else None
                            
                            # Extract label
                            label_match = re.search(r'android:label="([^"]+)"', content)
                            app_name = label_match.group(1) if label_match else None
                            
                            # Clean app_name if it's a reference
                            if app_name and not app_name.startswith('@'):
                                shutil.rmtree(temp_dir, ignore_errors=True)
                                return app_name, package_name
                
                shutil.rmtree(temp_dir, ignore_errors=True)
            
            return None, None
            
        except Exception as e:
            logger.error(f"Error extracting from manifest: {str(e)}")
            return None, None
    
    
    async def analyze(self, output_dir):
        """Full analysis of APK"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Get app info (name and package together)
        app_name, package_name = await self.get_app_info()
        
        results = {
            'app_name': app_name,
            'package_name': package_name,
            'icon_path': await self.extract_icon(output_dir)
        }
        
        return results
