#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Suzi APK Processor - Build Setup
ساخت نسخه محافظت شده با Cython

این فایل کد Python رو به C تبدیل و کامپایل می‌کنه
"""

from setuptools import setup, Extension
from Cython.Build import cythonize
import sys
import os

# تنظیمات کامپایل
compiler_directives = {
    'language_level': 3,
    'embedsignature': False,
    'boundscheck': False,
    'wraparound': False,
    'cdivision': True,
    'always_allow_keywords': False,
}

# Extension برای apk_processor
apk_processor_ext = Extension(
    name="apk_processor_core",
    sources=["apk_processor.py"],
    extra_compile_args=['-O3'] if sys.platform != 'win32' else ['/O2'],
)

# Extension برای m (runner)
runner_ext = Extension(
    name="m_core",
    sources=["m.py"],
    extra_compile_args=['-O3'] if sys.platform != 'win32' else ['/O2'],
)

setup(
    name="suzi-apk-processor",
    version="1.0.0",
    description="Suzi Brand APK Processor - Protected Version",
    author="Suzi Brand",
    ext_modules=cythonize(
        [apk_processor_ext, runner_ext],
        compiler_directives=compiler_directives,
        build_dir="build",
    ),
    zip_safe=False,
)
