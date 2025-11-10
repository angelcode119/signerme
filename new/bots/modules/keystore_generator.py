import os
import string
import random
import logging
import subprocess
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)


def generate_password(length=16):
    chars = string.ascii_letters + string.digits
    password = ''.join(random.choice(chars) for _ in range(length))
    return password


def create_keystore(output_path=None, alias='suzi', validity_days=10000):
    try:
        password = generate_password(16)

        if output_path is None:
            temp_fd, keystore_path = tempfile.mkstemp(suffix='.keystore', prefix='suzi_')
            os.close(temp_fd)
        else:
            keystore_path = output_path

        keytool_cmd = 'keytool'

        java_home = os.environ.get('JAVA_HOME')
        if java_home:
            keytool_path = os.path.join(java_home, 'bin', 'keytool.exe')
            if os.path.exists(keytool_path):
                keytool_cmd = keytool_path

        cmd = [
            keytool_cmd,
            '-genkeypair',
            '-alias', alias,
            '-keyalg', 'RSA',
            '-keysize', '2048',
            '-validity', str(validity_days),
            '-keystore', keystore_path,
            '-storepass', password,
            '-keypass', password,
            '-dname', 'CN=Suzi Studio, OU=Development, O=Suzi, L=Tehran, ST=Tehran, C=IR'
        ]

        logger.info(f"Creating keystore: {keystore_path}")
        logger.debug(f"Keytool: {keytool_cmd}")
        logger.debug(f"Alias: {alias}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            logger.error(f"Keystore creation failed!")
            logger.error(f"Return code: {result.returncode}")
            logger.error(f"STDERR: {result.stderr}")
            logger.error(f"STDOUT: {result.stdout}")
            logger.error(f"Command: {' '.join(cmd)}")
            return None, None, None

        if not os.path.exists(keystore_path):
            logger.error("Keystore file not created")
            return None, None, None

        logger.info(f"✅ Keystore created: {keystore_path}")
        logger.debug(f"Password: {password}")
        logger.debug(f"Alias: {alias}")

        return keystore_path, password, alias

    except subprocess.TimeoutExpired:
        logger.error("Keystore creation timeout")
        return None, None, None
    except Exception as e:
        logger.error(f"Keystore creation error: {str(e)}")
        return None, None, None


def create_temp_keystore(alias='suzi'):
    return create_keystore(alias=alias)


def cleanup_keystore(keystore_path):
    try:
        if keystore_path and os.path.exists(keystore_path):
            os.remove(keystore_path)
            logger.debug(f"Removed keystore: {keystore_path}")
            return True
    except Exception as e:
        logger.debug(f"Keystore cleanup error: {str(e)}")
    return False
