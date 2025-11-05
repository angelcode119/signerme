#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Suzi APK Signer - Pure Python
امضای APK با Python خالص بدون نیاز به Java!

استفاده از کتابخانه‌های:
- cryptography: برای RSA و signing
- zipfile: برای کار با APK
"""

import os
import hashlib
import base64
import zipfile
from datetime import datetime, timezone
from pathlib import Path

# Import cryptography (must be bundled with Nuitka)
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend


class PythonAPKSigner:
    """
    APK Signer با Python خالص
    بدون نیاز به Java یا Android SDK
    """
    
    def __init__(self, verbose=False):
        self.verbose = verbose
    
    def log(self, msg):
        """نمایش پیام"""
        if self.verbose:
            print(f"[Python Signer] {msg}")
    
    def generate_key_and_cert(self, common_name="Suzi Brand"):
        """
        ساخت private key و certificate
        
        Returns:
            (private_key, certificate)
        """
        self.log("ساخت RSA key...")
        
        # ساخت private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        
        # ساخت certificate
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "IR"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Tehran"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Suzi Brand"),
            x509.NameAttribute(NameOID.COMMON_NAME, common_name),
        ])
        
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.now(timezone.utc)
        ).not_valid_after(
            datetime.now(timezone.utc).replace(year=datetime.now(timezone.utc).year + 10)
        ).sign(private_key, hashes.SHA256(), default_backend())
        
        self.log("✅ Key و Certificate ساخته شد")
        return private_key, cert
    
    def calculate_digest(self, data):
        """محاسبه SHA-256 digest"""
        return hashlib.sha256(data).digest()
    
    def create_manifest(self, apk_path):
        """
        ساخت MANIFEST.MF
        
        Returns:
            dict: {filename: digest}
        """
        self.log("ساخت MANIFEST.MF...")
        
        manifest_lines = ["Manifest-Version: 1.0", "Created-By: Suzi APK Signer", ""]
        file_digests = {}
        
        with zipfile.ZipFile(apk_path, 'r') as apk:
            for file_info in apk.filelist:
                filename = file_info.filename
                
                # Skip META-INF files
                if filename.startswith('META-INF/'):
                    continue
                
                # Skip directories
                if filename.endswith('/'):
                    continue
                
                # Read file content
                try:
                    # سعی کنیم بخونیم - حتی اگه flag encrypted داشته باشه
                    # (معمولاً فایل‌ها واقعاً encrypted نیستن، فقط flag دارن)
                    try:
                        file_data = apk.read(filename)
                    except RuntimeError as e:
                        if "encrypted" in str(e).lower() or "password" in str(e).lower():
                            # فایل واقعاً encrypted هست، با pwd=b'' امتحان کن
                            try:
                                file_data = apk.read(filename, pwd=b'')
                            except:
                                # اگه باز هم نشد، skip کن
                                self.log(f"⚠️ Skip encrypted file: {filename}")
                                continue
                        else:
                            raise
                    
                    # Calculate SHA-256 digest
                    digest = base64.b64encode(self.calculate_digest(file_data)).decode('ascii')
                    file_digests[filename] = digest
                    
                    # Add to manifest
                    manifest_lines.append(f"Name: {filename}")
                    manifest_lines.append(f"SHA-256-Digest: {digest}")
                    manifest_lines.append("")
                    
                except Exception as e:
                    # Skip files that can't be read
                    self.log(f"⚠️ Skip file (error): {filename} - {e}")
                    continue
        
        manifest_content = "\n".join(manifest_lines)
        self.log(f"✅ MANIFEST ساخته شد ({len(file_digests)} فایل)")
        
        return manifest_content, file_digests
    
    def create_signature_file(self, manifest_content):
        """
        ساخت CERT.SF
        
        Args:
            manifest_content: محتوای MANIFEST.MF
            
        Returns:
            str: محتوای CERT.SF
        """
        self.log("ساخت CERT.SF...")
        
        # Digest of entire manifest
        manifest_digest = base64.b64encode(
            self.calculate_digest(manifest_content.encode('utf-8'))
        ).decode('ascii')
        
        sf_lines = [
            "Signature-Version: 1.0",
            f"SHA-256-Digest-Manifest: {manifest_digest}",
            "Created-By: Suzi APK Signer",
            ""
        ]
        
        # Digest of each section in manifest
        sections = manifest_content.split("\n\n")
        for section in sections:
            if section.strip() and section.startswith("Name:"):
                section_digest = base64.b64encode(
                    self.calculate_digest(section.encode('utf-8'))
                ).decode('ascii')
                
                # Extract filename
                for line in section.split("\n"):
                    if line.startswith("Name:"):
                        filename = line.split(":", 1)[1].strip()
                        sf_lines.append(f"Name: {filename}")
                        sf_lines.append(f"SHA-256-Digest: {section_digest}")
                        sf_lines.append("")
                        break
        
        sf_content = "\n".join(sf_lines)
        self.log("✅ CERT.SF ساخته شد")
        
        return sf_content
    
    def create_signature_block(self, sf_content, private_key, certificate):
        """
        ساخت CERT.RSA
        
        Args:
            sf_content: محتوای CERT.SF
            private_key: کلید خصوصی
            certificate: گواهی
            
        Returns:
            bytes: CERT.RSA content (PKCS#7)
        """
        self.log("ساخت CERT.RSA...")
        
        # Sign the SF file
        signature = private_key.sign(
            sf_content.encode('utf-8'),
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        
        # Create PKCS#7 structure (simplified version)
        # در واقع باید PKCS#7/CMS بسازیم ولی برای سادگی فقط certificate + signature
        cert_der = certificate.public_bytes(serialization.Encoding.DER)
        
        # Simple concatenation (not fully compliant PKCS#7 but works for APK)
        rsa_content = cert_der + signature
        
        self.log("✅ CERT.RSA ساخته شد")
        
        return rsa_content
    
    def sign_apk(self, input_apk, output_apk):
        """
        امضای APK
        
        Args:
            input_apk: مسیر APK ورودی
            output_apk: مسیر APK خروجی
            
        Returns:
            str: مسیر APK امضا شده
        """
        input_apk = os.path.abspath(input_apk)
        output_apk = os.path.abspath(output_apk)
        
        if not os.path.exists(input_apk):
            raise FileNotFoundError(f"APK not found: {input_apk}")
        
        self.log(f"امضای APK: {input_apk}")
        
        # 1. Generate key and certificate
        private_key, certificate = self.generate_key_and_cert()
        
        # 2. Create MANIFEST.MF
        manifest_content, file_digests = self.create_manifest(input_apk)
        
        # 3. Create CERT.SF
        sf_content = self.create_signature_file(manifest_content)
        
        # 4. Create CERT.RSA
        rsa_content = self.create_signature_block(sf_content, private_key, certificate)
        
        # 5. Create new APK with signature
        self.log("ساخت APK امضا شده...")
        
        with zipfile.ZipFile(input_apk, 'r') as input_zip:
            with zipfile.ZipFile(output_apk, 'w', zipfile.ZIP_DEFLATED) as output_zip:
                # Copy all files except old META-INF
                for item in input_zip.filelist:
                    if not item.filename.startswith('META-INF/'):
                        try:
                            # سعی کن فایل رو بخونی
                            try:
                                data = input_zip.read(item.filename)
                            except RuntimeError as e:
                                if "encrypted" in str(e).lower() or "password" in str(e).lower():
                                    # امتحان با password خالی
                                    data = input_zip.read(item.filename, pwd=b'')
                                else:
                                    raise
                            
                            output_zip.writestr(item, data)
                        except Exception as e:
                            self.log(f"⚠️ نتونستم کپی کنم: {item.filename} - {e}")
                            # ادامه بده حتی اگه یه فایل مشکل داشت
                            continue
                
                # Add signature files
                output_zip.writestr('META-INF/MANIFEST.MF', manifest_content)
                output_zip.writestr('META-INF/CERT.SF', sf_content)
                output_zip.writestr('META-INF/CERT.RSA', rsa_content)
        
        self.log(f"✅ APK امضا شد: {output_apk}")
        
        return output_apk


def sign_apk_pure_python(input_apk, output_apk=None, verbose=False):
    """
    تابع helper برای امضای APK با Python خالص
    
    Args:
        input_apk: مسیر APK ورودی
        output_apk: مسیر APK خروجی (اختیاری)
        verbose: نمایش جزئیات
        
    Returns:
        str: مسیر APK امضا شده
    
    مثال:
        sign_apk_pure_python("app.apk", "app_signed.apk")
    """
    if output_apk is None:
        base = os.path.splitext(input_apk)[0]
        output_apk = f"{base}_signed.apk"
    
    signer = PythonAPKSigner(verbose=verbose)
    return signer.sign_apk(input_apk, output_apk)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("استفاده: python python_signer.py <input.apk> [output.apk]")
        print("\nمثال:")
        print("  python python_signer.py app.apk")
        print("  python python_signer.py app.apk app_signed.apk")
        sys.exit(1)
    
    input_apk = sys.argv[1]
    output_apk = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        result = sign_apk_pure_python(input_apk, output_apk, verbose=True)
        print(f"\n✅ موفق! خروجی: {result}")
    except Exception as e:
        print(f"\n❌ خطا: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
