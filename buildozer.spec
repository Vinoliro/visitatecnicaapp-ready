[app]
title = Visita Técnica
package.name = VisitaTecnica
package.domain = org.vini.visita
version = 0.1

source.dir = .
source.main = visita_tecnica_app/main.py
source.include_patterns = visita_tecnica_app/**/*.kv, visita_tecnica_app/**/*.db, visita_tecnica_app/**/*.png, visita_tecnica_app/**/*.jpeg

requirements = python3,kivy,sqlite3,Pillow,cython,pyjnius

android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, CAMERA
fullscreen = 1
orientation = portrait

android.api = 31
android.minapi = 21
android.target = 31
android.build_tools_version = 33.0.2
android.ndk = 23b
android.archs = arm64-v8a, armeabi-v7a

# força build-tools 33.0.2 para evitar erro com 36
android.environ = P4A_FORCE_BUILD_TOOLS_VERSION=33.0.2

p4a.source = https://github.com/kivy/python-for-android.git
p4a.branch = develop

presplash.filename = %(source.dir)s/data/presplash.png
icon.filename = %(source.dir)s/data/icon.png

android.debug = 1

[buildozer]
log_level = 2
warn_on_root = 1
