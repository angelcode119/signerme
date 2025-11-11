import os
import string
import random
import logging
import subprocess
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)

JAPANESE_NAMES = [
    'Tanaka', 'Suzuki', 'Takahashi', 'Watanabe', 'Ito', 'Yamamoto', 'Nakamura', 
    'Kobayashi', 'Kato', 'Yoshida', 'Yamada', 'Sasaki', 'Yamaguchi', 'Saito',
    'Matsumoto', 'Inoue', 'Kimura', 'Hayashi', 'Shimizu', 'Yamazaki', 'Mori',
    'Abe', 'Ikeda', 'Hashimoto', 'Ishikawa', 'Yamashita', 'Nakajima', 'Maeda'
]

JAPANESE_COMPANIES = [
    'Tokyo Systems', 'Osaka Digital', 'Kyoto Tech', 'Yokohama Labs',
    'Nagoya Software', 'Sapporo Digital', 'Fukuoka Tech', 'Kobe Systems',
    'Sendai Digital', 'Hiroshima Tech', 'Kawasaki Labs', 'Saitama Digital'
]

JAPANESE_CITIES = [
    'Tokyo', 'Osaka', 'Kyoto', 'Yokohama', 'Nagoya', 'Sapporo', 'Fukuoka',
    'Kobe', 'Kawasaki', 'Saitama', 'Hiroshima', 'Sendai', 'Chiba', 'Kitakyushu'
]


def generate_password(length=16):
    chars = string.ascii_letters + string.digits
    password = ''.join(random.choice(chars) for _ in range(length))
    return password


def generate_japanese_dname():
    name = random.choice(JAPANESE_NAMES)
    company = random.choice(JAPANESE_COMPANIES)
    city = random.choice(JAPANESE_CITIES)
    
    dname = f'CN={name} {company}, OU=Development, O={company}, L={city}, ST={city}, C=JP'
    return dname


def create_keystore(output_path=None, alias=None, validity_days=10000):
    try:
        password = generate_password(16)
        
        if alias is None:
            alias = random.choice(JAPANESE_NAMES).lower()

        if output_path is None:
            temp_fd, keystore_path = tempfile.mkstemp(suffix='.keystore', prefix='jp_')
            os.close(temp_fd)
            os.remove(keystore_path)
        else:
            keystore_path = output_path

        keytool_cmd = None
        
        java_home = os.environ.get('JAVA_HOME')
        if java_home:
            keytool_path = os.path.join(java_home, 'bin', 'keytool.exe')
            if os.path.exists(keytool_path):
                keytool_cmd = keytool_path
        
        if not keytool_cmd and java_home:
            keytool_path = os.path.join(java_home, 'bin', 'keytool')
            if os.path.exists(keytool_path):
                keytool_cmd = keytool_path
        
        if not keytool_cmd:
            try:
                result = subprocess.run(['which', 'keytool'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    keytool_cmd = result.stdout.strip()
            except:
                pass
        
        if not keytool_cmd:
            try:
                result = subprocess.run(['where', 'keytool'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    keytool_cmd = result.stdout.strip().split('\n')[0]
            except:
                pass
        
        if not keytool_cmd:
            keytool_cmd = 'keytool'
        
        dname = generate_japanese_dname()

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
            '-dname', dname
        ]

        logger.info(f"Creating keystore: {keystore_path}")
        logger.debug(f"Keytool: {keytool_cmd}")
        logger.debug(f"Alias: {alias}")
        logger.debug(f"DN: {dname}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            shell=False
        )

        if result.returncode != 0:
            logger.error(f"Keystore creation failed!")
            logger.error(f"Return code: {result.returncode}")
            logger.error(f"STDERR: {result.stderr}")
            logger.error(f"STDOUT: {result.stdout}")
            logger.error(f"Command: {' '.join(cmd)}")
            logger.error(f"Keytool command used: {keytool_cmd}")
            
            if "not recognized" in result.stderr or "not found" in result.stderr or result.returncode == 1:
                logger.error("⚠️ Java/keytool not found! Please install Java JDK and add to PATH")
            
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
    except FileNotFoundError as e:
        logger.error(f"Keytool not found! Please install Java JDK")
        logger.error(f"Error: {str(e)}")
        logger.error(f"Searched command: {keytool_cmd if 'keytool_cmd' in locals() else 'unknown'}")
        return None, None, None
    except Exception as e:
        logger.error(f"Keystore creation error: {str(e)}", exc_info=True)
        logger.error(f"Keytool command: {keytool_cmd if 'keytool_cmd' in locals() else 'unknown'}")
        if 'cmd' in locals():
            logger.error(f"Full command: {' '.join(cmd)}")
        return None, None, None


def create_temp_keystore(alias=None):
    if alias is None:
        alias = random.choice(JAPANESE_NAMES).lower()
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
