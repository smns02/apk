[app]

# (str) Title of your application
title = SPCX

# (str) Package name
package.name = spx

# (str) Package domain
package.domain = com.spx

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include
source.include_exts = py,png,jpg,kv,atlas

# (str) Application versioning
version = 1.0

# (list) Application requirements
# aiohttp နှင့် သူ့အတွက်လိုအပ်သော dependencies များအားလုံးပါဝင်သည်
requirements = python3,kivy,aiohttp,chardet,idna,multidict,yarl,aiosignal,frozenlist

# (list) Supported orientations
orientation = portrait

# (bool) Indicate if the application should be fullscreen
fullscreen = 0

# (list) Permissions
android.permissions = INTERNET

# (int) Target Android API
android.api = 34

# (int) Minimum API
android.minapi = 24

# (str) Android NDK version
android.ndk = 25b

android.accept_sdk_license = True

# (bool) enables Android auto backup feature
android.allow_backup = True

# (list) The Android archs to build for
android.archs = arm64-v8a, armeabi-v7a

# (str) The format used to package the app
android.release_artifact = aab
android.debug_artifact = apk

[buildozer]
# (int) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2
warn_on_root = 1
