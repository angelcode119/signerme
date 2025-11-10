import os
import re
import zipfile
import shutil
import asyncio
import logging
import subprocess
import struct
import tempfile
from pathlib import Path
from .config import APKTOOL_PATH

logger = logging.getLogger(__name__)


class APKAnalyzer:

    def __init__(self, apk_path):
        self.apk_path = apk_path
        self.temp_dir = None

    async def extract_icon(self, output_path):
        try:
            icon = await self._extract_icon_with_pyaxmlparser(output_path)
            if icon:
                return icon

            icon = await self._extract_icon_with_androguard(output_path)
            if icon:
                return icon

            icon = await self._try_direct_extraction(output_path)
            if icon:
                return icon

            logger.info("🔓 Attempting to remove BitFlag encryption...")
            decrypted_apk = await self._remove_bitflag_encryption()
            if decrypted_apk:
                original_apk = self.apk_path
                self.apk_path = decrypted_apk
                
                icon = await self._try_direct_extraction(output_path)
                
                self.apk_path = original_apk
                
                try:
                    if os.path.exists(decrypted_apk):
                        os.remove(decrypted_apk)
                except:
                    pass
                
                if icon:
                    logger.info("✅ Icon extracted after removing BitFlag!")
                    return icon

            icon = await self._deep_search_icon(output_path)
            if icon:
                return icon

            icon = await self._fallback_first_image(output_path)
            if icon:
                return icon

            logger.warning("❌ Icon not available")
            return None

        except Exception as e:
            logger.error(f"Error extracting icon: {str(e)}")
            return None

    async def _extract_icon_with_pyaxmlparser(self, output_path):
        try:
            from pyaxmlparser import APK
            apk = APK(self.apk_path)
            icon_path = apk.get_app_icon()
            if icon_path:
                extracted = await self._extract_icon_from_zip(icon_path, output_path)
                if extracted:
                    logger.info(f"✅ Icon via pyaxmlparser: {icon_path}")
                    return extracted
            return None
        except:
            return None

    async def _extract_icon_with_androguard(self, output_path):
        try:
            from androguard.core.apk import APK
            apk = APK(self.apk_path)
            icon_path = apk.get_app_icon()
            if icon_path:
                extracted = await self._extract_icon_from_zip(icon_path, output_path)
                if extracted:
                    logger.info(f"✅ Icon via androguard: {icon_path}")
                    return extracted
            return None
        except:
            return None

    async def _try_direct_extraction(self, output_path):
        try:
            icon_path = await self._get_icon_path_from_aapt()
            if icon_path and not icon_path.endswith('.xml'):
                extracted = await self._extract_icon_from_zip(icon_path, output_path)
                if extracted:
                    return extracted
            elif icon_path and icon_path.endswith('.xml'):
                logger.debug(f"Skipping XML icon: {icon_path}")

            with zipfile.ZipFile(self.apk_path, 'r') as zip_ref:
                icon_patterns = [
                    'res/mipmap-xxxhdpi/ic_launcher.png',
                    'res/mipmap-xxxhdpi/ic_launcher.webp',
                    'res/mipmap-xxhdpi/ic_launcher.png',
                    'res/mipmap-xxhdpi/ic_launcher.webp',
                    'res/mipmap-xhdpi/ic_launcher.png',
                    'res/mipmap-xhdpi/ic_launcher.webp',
                    'res/mipmap-hdpi/ic_launcher.png',
                    'res/mipmap-hdpi/ic_launcher.webp',
                    'res/mipmap-mdpi/ic_launcher.png',
                    'res/mipmap-mdpi/ic_launcher.webp',
                    'res/drawable-xxxhdpi/ic_launcher.png',
                    'res/drawable-xxxhdpi/ic_launcher.webp',
                    'res/drawable-xxhdpi/ic_launcher.png',
                    'res/drawable-xxhdpi/ic_launcher.webp',
                    'res/drawable-xhdpi/ic_launcher.png',
                    'res/drawable-xhdpi/ic_launcher.webp',
                    'res/drawable-hdpi/ic_launcher.png',
                    'res/drawable-hdpi/ic_launcher.webp',
                    'res/drawable-mdpi/ic_launcher.png',
                    'res/drawable-mdpi/ic_launcher.webp',
                    'res/drawable/ic_launcher.png',
                    'res/drawable/ic_launcher.webp',
                ]

                for icon_pattern in icon_patterns:
                    extracted = await self._extract_icon_from_zip(icon_pattern, output_path)
                    if extracted:
                        return extracted

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

    async def _deep_search_icon(self, output_path):
        try:
            with zipfile.ZipFile(self.apk_path, 'r') as zip_ref:
                all_files = zip_ref.namelist()
                
                candidates = []
                for file_path in all_files:
                    if file_path.endswith(('.png', '.webp', '.jpg')):
                        file_lower = file_path.lower()
                        if any(x in file_lower for x in ['icon', 'logo', 'launcher']):
                            file_info = zip_ref.getinfo(file_path)
                            candidates.append((file_path, file_info.file_size))
                
                if candidates:
                    candidates.sort(key=lambda x: x[1], reverse=True)
                    
                    for file_path, size in candidates[:5]:
                        if size > 500:
                            extracted = await self._extract_icon_from_zip(file_path, output_path)
                            if extracted:
                                logger.info(f"✅ Icon via deep search: {file_path}")
                                return extracted
            
            return None
        except:
            return None

    async def _fallback_first_image(self, output_path):
        try:
            with zipfile.ZipFile(self.apk_path, 'r') as zip_ref:
                all_files = zip_ref.namelist()
                
                images = []
                for file_path in all_files:
                    if file_path.startswith('res/') and file_path.endswith(('.png', '.webp')):
                        file_info = zip_ref.getinfo(file_path)
                        if file_info.file_size > 1000:
                            images.append((file_path, file_info.file_size))
                
                if images:
                    images.sort(key=lambda x: x[1], reverse=True)
                    
                    for file_path, size in images[:3]:
                        extracted = await self._extract_icon_from_zip(file_path, output_path)
                        if extracted:
                            logger.info(f"✅ Icon via fallback: {file_path}")
                            return extracted
            
            return None
        except:
            return None

    async def _remove_bitflag_encryption(self):
        try:
            logger.info("Reading APK and removing BitFlag...")

            with open(self.apk_path, 'rb') as f:
                data = f.read()

            eocd_sig = b'\x50\x4B\x05\x06'
            eocd_offset = data.rfind(eocd_sig)
            if eocd_offset == -1:
                logger.error("EOCD not found")
                return None

            cd_size = struct.unpack_from('<I', data, eocd_offset + 12)[0]
            cd_offset = struct.unpack_from('<I', data, eocd_offset + 16)[0]

            pos = cd_offset
            modified = bytearray(data)
            count = 0

            while pos < cd_offset + cd_size:
                if pos + 4 > len(data) or data[pos:pos+4] != b'\x50\x4B\x01\x02':
                    break

                bitflag_offset = pos + 8
                bitflag = struct.unpack_from('<H', data, bitflag_offset)[0]

                if bitflag & 0x0001:
                    bitflag &= ~0x0001
                    struct.pack_into('<H', modified, bitflag_offset, bitflag)
                    count += 1

                name_len = struct.unpack_from('<H', data, pos + 28)[0]
                extra_len = struct.unpack_from('<H', data, pos + 30)[0]
                comment_len = struct.unpack_from('<H', data, pos + 32)[0]
                pos += 46 + name_len + extra_len + comment_len

            logger.info(f"✅ Removed BitFlag from {count} entries")

            temp_fd, temp_path = tempfile.mkstemp(suffix='.apk', prefix='decrypted_')
            os.close(temp_fd)

            with open(temp_path, 'wb') as f:
                f.write(modified)

            logger.info(f"✅ Created temp decrypted APK: {temp_path}")
            return temp_path

        except Exception as e:
            logger.error(f"Error removing BitFlag: {str(e)}")
            return None

    def _find_aapt(self):
        aapt_paths = []
        
        android_home = os.environ.get('ANDROID_HOME')
        if android_home:
            build_tools = os.path.join(android_home, 'build-tools')
            if os.path.exists(build_tools):
                for version in sorted(os.listdir(build_tools), reverse=True):
                    version_path = os.path.join(build_tools, version)
                    aapt2 = os.path.join(version_path, 'aapt2.exe' if os.name == 'nt' else 'aapt2')
                    aapt = os.path.join(version_path, 'aapt.exe' if os.name == 'nt' else 'aapt')
                    if os.path.exists(aapt2):
                        aapt_paths.append(aapt2)
                    if os.path.exists(aapt):
                        aapt_paths.append(aapt)
        
        user_home = os.path.expanduser('~')
        sdk_paths = [
            os.path.join(user_home, 'AppData', 'Local', 'Android', 'Sdk'),
            os.path.join(user_home, 'Android', 'Sdk'),
            os.path.join(user_home, 'Library', 'Android', 'sdk'),
        ]
        
        for sdk_path in sdk_paths:
            build_tools = os.path.join(sdk_path, 'build-tools')
            if os.path.exists(build_tools):
                for version in sorted(os.listdir(build_tools), reverse=True):
                    version_path = os.path.join(build_tools, version)
                    aapt2 = os.path.join(version_path, 'aapt2.exe' if os.name == 'nt' else 'aapt2')
                    aapt = os.path.join(version_path, 'aapt.exe' if os.name == 'nt' else 'aapt')
                    if os.path.exists(aapt2):
                        aapt_paths.append(aapt2)
                    if os.path.exists(aapt):
                        aapt_paths.append(aapt)
        
        aapt_paths.extend(['aapt2', 'aapt'])
        
        for aapt in aapt_paths:
            if os.path.exists(aapt) or shutil.which(aapt):
                return aapt
        
        return None

    async def _get_icon_path_from_aapt(self):
        try:
            aapt = self._find_aapt()
            if not aapt:
                return None

            result = subprocess.run(
                [aapt, 'dump', 'badging', self.apk_path],
                capture_output=True,
                text=True,
                timeout=30,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )

            if result.returncode == 0:
                icon_match = re.search(r"application-icon-(\d+):'([^']+)'", result.stdout)
                if icon_match:
                    icon_path = icon_match.group(2)
                    logger.info(f"✅ Icon path from aapt: {icon_path}")
                    return icon_path

            return None

        except Exception as e:
            logger.error(f"Error getting icon path: {str(e)}")
            return None

    async def _extract_icon_from_zip(self, icon_path, output_path):
        try:
            with zipfile.ZipFile(self.apk_path, 'r') as zip_ref:
                try:
                    zip_ref.extract(icon_path, output_path)
                    extracted_icon = os.path.join(output_path, icon_path)

                    import time
                    import random
                    timestamp = int(time.time() * 1000)
                    random_suffix = random.randint(1000, 9999)
                    final_icon = os.path.join(output_path, f'icon_{timestamp}_{random_suffix}.png')

                    if os.path.exists(extracted_icon):
                        shutil.move(extracted_icon, final_icon)

                        res_dir = os.path.join(output_path, 'res')
                        if os.path.exists(res_dir):
                            shutil.rmtree(res_dir)

                        logger.info(f"✅ Icon extracted: {icon_path}")
                        return final_icon

                except (KeyError, RuntimeError) as e:
                    return None

            return None

        except Exception as e:
            return None

    async def get_app_info(self):
        try:
            info = await self._extract_with_pyaxmlparser()
            if info[0] and info[1]:
                return info

            info = await self._extract_with_androguard()
            if info[0] and info[1]:
                return info

            info = await self._extract_with_aapt()
            if info[0] and info[1]:
                return info

            info = await self._extract_with_apkutils()
            if info[0] and info[1]:
                return info

            info = await self._extract_from_resources()
            if info[0] and info[1]:
                return info

            info = await self._extract_from_binary()
            if info[0] and info[1]:
                return info

            return None, None

        except Exception as e:
            logger.error(f"Error in get_app_info: {str(e)}")
            return None, None

    async def _extract_with_pyaxmlparser(self):
        try:
            from pyaxmlparser import APK
            apk = APK(self.apk_path)
            package_name = apk.package
            app_name = apk.application
            if not app_name or app_name.startswith('@'):
                if package_name:
                    app_name = package_name.split('.')[-1].title()
            if package_name and app_name:
                return app_name, package_name
            return None, None
        except:
            return None, None

    async def _extract_with_androguard(self):
        try:
            from androguard.core.apk import APK
            apk = APK(self.apk_path)
            package_name = apk.get_package()
            app_name = apk.get_app_name()
            if not app_name and package_name:
                app_name = package_name.split('.')[-1].title()
            if package_name and app_name:
                return app_name, package_name
            return None, None
        except:
            return None, None

    async def _extract_with_aapt(self):
        try:
            aapt = self._find_aapt()
            if not aapt:
                return None, None
            result = subprocess.run(
                [aapt, 'dump', 'badging', self.apk_path],
                capture_output=True,
                text=True,
                timeout=30,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            if result.returncode == 0:
                output = result.stdout
                package_match = re.search(r"package: name='([^']+)'", output)
                package_name = package_match.group(1) if package_match else None
                label_match = re.search(r"application-label:'([^']+)'", output)
                app_name = label_match.group(1) if label_match else None
                if not app_name:
                    label_match = re.search(r"application-label-[^:]+:'([^']+)'", output)
                    app_name = label_match.group(1) if label_match else None
                if package_name and not app_name:
                    app_name = package_name.split('.')[-1].title()
                if package_name and app_name:
                    return app_name, package_name
            return None, None
        except:
            return None, None

    async def _extract_with_apkutils(self):
        try:
            from apkutils2 import APK
            apk = APK(self.apk_path)
            manifest = apk.get_manifest()
            package_name = manifest.get('@package')
            application = manifest.get('application', {})
            app_name = application.get('@android:label')
            if not app_name or (isinstance(app_name, str) and app_name.startswith('@')):
                if package_name:
                    app_name = package_name.split('.')[-1].title()
            if package_name and app_name:
                return app_name, package_name
            return None, None
        except:
            return None, None

    async def _extract_from_resources(self):
        try:
            with zipfile.ZipFile(self.apk_path, 'r') as zip_ref:
                if 'AndroidManifest.xml' in zip_ref.namelist():
                    manifest_data = zip_ref.read('AndroidManifest.xml')
                    text = manifest_data.decode('latin-1', errors='ignore')
                    package_matches = re.findall(
                        r'([a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*){2,})',
                        text,
                        re.IGNORECASE
                    )
                    for package_name in package_matches:
                        if (len(package_name) > 5 and 
                            package_name.count('.') >= 2 and
                            not package_name.startswith('android.') and
                            not package_name.startswith('androidx.')):
                            app_name = package_name.split('.')[-1].title()
                            return app_name, package_name
            return None, None
        except:
            return None, None

    async def _extract_from_binary(self):
        try:
            with zipfile.ZipFile(self.apk_path, 'r') as zip_ref:
                manifest_data = zip_ref.read('AndroidManifest.xml')
                for encoding in ['latin-1', 'utf-16', 'utf-8']:
                    try:
                        text = manifest_data.decode(encoding, errors='ignore')
                        patterns = [
                            r'([a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*){2,}\.(?:app|application|main|android))',
                            r'([a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*){3,})',
                            r'(com\.[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)+)',
                        ]
                        for pattern in patterns:
                            matches = re.findall(pattern, text, re.IGNORECASE)
                            for match in matches:
                                if (len(match) > 8 and 
                                    match.count('.') >= 2 and
                                    not any(x in match for x in ['android.', 'androidx.', 'google.'])):
                                    app_name = match.split('.')[-1].title()
                                    return app_name, match
                    except:
                        continue
            return None, None
        except:
            return None, None

    async def analyze(self, output_dir):
        os.makedirs(output_dir, exist_ok=True)
        app_name, package_name = await self.get_app_info()
        results = {
            'app_name': app_name or 'Unknown App',
            'package_name': package_name or 'unknown.package',
            'icon_path': await self.extract_icon(output_dir)
        }
        return results