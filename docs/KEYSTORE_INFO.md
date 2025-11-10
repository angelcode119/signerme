# 🔐 Keystore System - Japanese Signatures

## Overview

The APK Studio uses a **unique keystore generation system** with Japanese company information for each build.

## Features

### 🇯🇵 Japanese Information
Every keystore is signed with random Japanese company details:
- **Names:** Tanaka, Suzuki, Takahashi, Watanabe, etc.
- **Companies:** Tokyo Systems, Osaka Digital, Kyoto Tech, etc.
- **Cities:** Tokyo, Osaka, Kyoto, Yokohama, Nagoya, etc.

### 🔑 Unique Keystores
- **Every build gets a NEW keystore**
- Random Japanese company name
- Random city location
- Unique alias name
- Strong 2048-bit RSA encryption

### 🔒 Security Features
- 16-character random passwords
- 10,000 days validity
- V1, V2, V3 signing enabled
- Automatic cleanup after use
- No keystore reuse

## How It Works

### 1. Keystore Creation
For each build, the system:
```
1. Generates random Japanese company info
2. Creates unique keystore file (prefix: jp_)
3. Uses random alias from Japanese names
4. Sets 16-character random password
5. Signs with RSA 2048-bit key
```

### 2. Signing Process
```
1. APK is built
2. New keystore generated
3. APK signed with keystore
4. Keystore automatically deleted
5. Only signed APK remains
```

### 3. Sample Keystores

**Example 1:**
```
CN=Takahashi Kobe Systems
OU=Development
O=Kobe Systems
L=Chiba
ST=Chiba
C=JP
Alias: takahashi
```

**Example 2:**
```
CN=Yamamoto Tokyo Systems
OU=Development
O=Tokyo Systems
L=Tokyo
ST=Tokyo
C=JP
Alias: yamamoto
```

**Example 3:**
```
CN=Suzuki Osaka Digital
OU=Development
O=Osaka Digital
L=Osaka
ST=Osaka
C=JP
Alias: suzuki
```

## Available Names

### Japanese Family Names (28)
- Tanaka, Suzuki, Takahashi, Watanabe
- Ito, Yamamoto, Nakamura, Kobayashi
- Kato, Yoshida, Yamada, Sasaki
- Yamaguchi, Saito, Matsumoto, Inoue
- Kimura, Hayashi, Shimizu, Yamazaki
- Mori, Abe, Ikeda, Hashimoto
- Ishikawa, Yamashita, Nakajima, Maeda

### Companies (12)
- Tokyo Systems
- Osaka Digital
- Kyoto Tech
- Yokohama Labs
- Nagoya Software
- Sapporo Digital
- Fukuoka Tech
- Kobe Systems
- Sendai Digital
- Hiroshima Tech
- Kawasaki Labs
- Saitama Digital

### Cities (14)
- Tokyo, Osaka, Kyoto, Yokohama
- Nagoya, Sapporo, Fukuoka, Kobe
- Kawasaki, Saitama, Hiroshima, Sendai
- Chiba, Kitakyushu

## Technical Details

### Keystore Specifications
- **Algorithm:** RSA
- **Key Size:** 2048 bits
- **Validity:** 10,000 days
- **Format:** JKS (Java KeyStore)
- **Signing:** v1, v2, v3 enabled

### File Naming
- **Prefix:** `jp_`
- **Suffix:** `.keystore`
- **Location:** Temporary directory
- **Cleanup:** Automatic after signing

### Password Generation
- **Length:** 16 characters
- **Characters:** a-z, A-Z, 0-9
- **Uniqueness:** Random per build
- **Storage:** Memory only (not saved)

## Advantages

### 🎭 Anonymity
- Each APK has different signer
- No pattern recognition
- Distributed identity

### 🔄 Uniqueness
- Never reuse keystores
- Fresh signature every time
- Prevents tracking

### 🇯🇵 Authenticity
- Professional Japanese names
- Realistic company info
- Credible locations

### 🛡️ Security
- Strong encryption
- Random passwords
- Auto-cleanup
- No persistence

## Implementation

### Code Location
```
modules/keystore_generator.py
modules/apk_builder.py
```

### Key Functions

**generate_japanese_dname()**
- Generates random Japanese DN
- Returns formatted string
- Used in keystore creation

**create_temp_keystore()**
- Creates unique keystore
- Returns path, password, alias
- Automatic random selection

**sign_apk()**
- Signs APK with keystore
- Creates if not provided
- Auto-cleanup after use

## Usage in Build Process

### Quick Build
```python
1. User selects APK
2. System creates keystore
   - Random Japanese info
   - Unique alias
   - Strong password
3. APK is signed
4. Keystore is deleted
5. Signed APK delivered
```

### Custom Build
```python
1. User customizes theme
2. APK is built
3. New keystore created
   - Random Japanese company
   - Random city
   - Unique alias
4. APK signed
5. Keystore deleted
6. Custom APK delivered
```

## Logs

### Creation Log
```
INFO: Creating keystore: /tmp/jp_abc123.keystore
DEBUG: Keytool: keytool
DEBUG: Alias: tanaka
DEBUG: DN: CN=Tanaka Tokyo Systems, OU=Development, O=Tokyo Systems, L=Tokyo, ST=Tokyo, C=JP
```

### Signing Log
```
INFO: 🔑 Creating unique keystore with Japanese information...
INFO: ✅ Unique keystore created: yamamoto
INFO: Signing APK: /tmp/build_123.apk
INFO: ✅ Signed successfully
DEBUG: Removed keystore: /tmp/jp_xyz789.keystore
```

## Why Japanese?

### Professional
- Recognized globally
- Technology-oriented country
- Trustworthy reputation

### Diverse
- Many common surnames
- Multiple major cities
- Various company types

### Authentic
- Real-world names
- Actual city names
- Credible combinations

## Statistics

- **28** Different family names
- **12** Company types
- **14** City locations
- **4,704** Unique combinations
- **∞** Possible keystores (with random passwords)

## Security Notes

⚠️ **Important:**
- Keystores are temporary
- Passwords are not stored
- Original keystore never reused
- Cannot update signed APKs
- Each build = fresh start

✅ **Benefits:**
- Maximum anonymity
- No tracking possible
- Professional appearance
- Strong encryption
- Auto-cleanup

## Conclusion

The Japanese keystore system provides:
- ✅ Unique signature per build
- ✅ Professional appearance
- ✅ Maximum security
- ✅ Automatic management
- ✅ No manual intervention

Every APK from APK Studio is signed with a **unique, professional, Japanese company certificate**! 🇯🇵

---

*Last updated: 2025-11-10*
