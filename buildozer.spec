[app]
title = Seal Game
package.name = sealgame
package.domain = org.tulen
source.dir = .
source.include_exts = py,png,jpg,ttf,atlas
version = 1.0.0
requirements = python3==3.10.10,hostpython3==3.10.10,kivy==2.3.0
orientation = portrait
icon.filename = %(source.dir)s/icon.png
fullscreen = 1
android.api = 33
android.minapi = 24
android.ndk = 25b
android.ndk_path = /home/runner/.buildozer/android/platform/android-ndk-r25b
android.archs = arm64-v8a
android.allow_backup = True
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
p4a.njobs = 2
