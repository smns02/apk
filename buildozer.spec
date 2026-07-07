[app]
title = SpaceX Ruijie
package.name = spacex
package.domain = org.spacex
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
requirements = python3,kivy,aiohttp,certifi,idna,charset-normalizer,multidict,yarl
android.permissions = INTERNET, ACCESS_NETWORK_STATE
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1
