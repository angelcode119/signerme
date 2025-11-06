import os
import re
import zipfile
import shutil
import asyncio
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class APKAnalyzer:
    """Extract information from APK files"""
    
    def __init__(self, apk_path):
        self.apk_path = apk_path
        self.temp_dir = None
    
    async def extract_icon(self, output_path):
        """Extract app icon from APK"""
        try:
            with zipfile.ZipFile(self.apk_path, 'r') as zip_ref:
                # Common icon paths in APK
                icon_patterns = [
                    'res/mipmap-xxxhdpi/ic_launcher.png',
                    'res/mipmap-xxhdpi/ic_launcher.png',
                    'res/mipmap-xhdpi/ic_launcher.png',
                    'res/mipmap-hdpi/ic_launcher.png',
                    'res/drawable-xxxhdpi/ic_launcher.png',
                    'res/drawable-xxhdpi/ic_launcher.png',
                    'res/drawable-xhdpi/ic_launcher.png',
                    'res/drawable-hdpi/ic_launcher.png',
                    'res/drawable/ic_launcher.png',
                ]
                
                # Try to find icon
                for icon_path in icon_patterns:
                    try:
                        zip_ref.extract(icon_path, output_path)
                        extracted_icon = os.path.join(output_path, icon_path)
                        
                        # Move to root of output_path
                        final_icon = os.path.join(output_path, 'icon.png')
                        shutil.move(extracted_icon, final_icon)
                        
                        # Clean up extracted dirs
                        res_dir = os.path.join(output_path, 'res')
                        if os.path.exists(res_dir):
                            shutil.rmtree(res_dir)
                        
                        logger.info(f"✅ Icon extracted: {icon_path}")
                        return final_icon
                    except KeyError:
                        continue
                
                logger.warning("Icon not found in common paths")
                return None
                
        except Exception as e:
            logger.error(f"Error extracting icon: {str(e)}")
            return None
    
    async def get_app_name(self):
        """Extract app name from APK"""
        try:
            # Decompile APK to get strings
            temp_dir = f"temp_analyze_{os.path.basename(self.apk_path)}"
            
            process = await asyncio.create_subprocess_exec(
                'java', '-jar', 'apktool.jar',
                'd', self.apk_path,
                '-o', temp_dir,
                '-f', '-s',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await process.communicate()
            
            if process.returncode != 0:
                logger.error("Failed to decompile APK")
                return None
            
            # Try to get app name from AndroidManifest.xml
            manifest_path = os.path.join(temp_dir, 'AndroidManifest.xml')
            if os.path.exists(manifest_path):
                with open(manifest_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    # Look for app label
                    label_match = re.search(r'android:label="([^"]+)"', content)
                    if label_match:
                        label = label_match.group(1)
                        
                        # If it's a reference like @string/app_name
                        if label.startswith('@string/'):
                            string_name = label.replace('@string/', '')
                            app_name = await self._get_string_value(temp_dir, string_name)
                            if app_name:
                                # Cleanup
                                await asyncio.to_thread(shutil.rmtree, temp_dir, ignore_errors=True)
                                logger.info(f"✅ App name: {app_name}")
                                return app_name
                        else:
                            # Direct label
                            await asyncio.to_thread(shutil.rmtree, temp_dir, ignore_errors=True)
                            logger.info(f"✅ App name: {label}")
                            return label
            
            # Cleanup
            await asyncio.to_thread(shutil.rmtree, temp_dir, ignore_errors=True)
            logger.warning("App name not found")
            return None
            
        except Exception as e:
            logger.error(f"Error getting app name: {str(e)}")
            return None
    
    async def _get_string_value(self, decompiled_dir, string_name):
        """Get string value from strings.xml"""
        try:
            strings_path = os.path.join(decompiled_dir, 'res', 'values', 'strings.xml')
            
            if not os.path.exists(strings_path):
                return None
            
            with open(strings_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                # Look for <string name="app_name">Value</string>
                pattern = f'<string name="{string_name}">([^<]+)</string>'
                match = re.search(pattern, content)
                
                if match:
                    return match.group(1)
            
            return None
            
        except Exception as e:
            logger.error(f"Error reading strings.xml: {str(e)}")
            return None
    
    async def get_package_name(self):
        """Extract package name from APK"""
        try:
            with zipfile.ZipFile(self.apk_path, 'r') as zip_ref:
                # Read AndroidManifest.xml (binary)
                manifest_data = zip_ref.read('AndroidManifest.xml')
                
                # Simple regex to find package (works for most cases)
                # Note: This is a simplified approach
                manifest_str = manifest_data.decode('utf-8', errors='ignore')
                
                # Try to find package name pattern
                package_match = re.search(r'package="([^"]+)"', manifest_str)
                if package_match:
                    package = package_match.group(1)
                    logger.info(f"✅ Package name: {package}")
                    return package
            
            logger.warning("Package name not found")
            return None
            
        except Exception as e:
            logger.error(f"Error getting package name: {str(e)}")
            return None
    
    async def analyze(self, output_dir):
        """Full analysis of APK"""
        os.makedirs(output_dir, exist_ok=True)
        
        results = {
            'app_name': await self.get_app_name(),
            'package_name': await self.get_package_name(),
            'icon_path': await self.extract_icon(output_dir)
        }
        
        return results
