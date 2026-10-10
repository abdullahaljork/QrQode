import os, re, shutil

PASS = 'vMTXJoGgXAHeDZnm99sH'
base = 'android/app/src/main'
mp = base + '/AndroidManifest.xml'
s = open(mp, encoding='utf-8').read()

# صلاحية الكاميرا
PERMS = ''.join('<uses-permission android:name="android.permission.%s" />\n    ' % x for x in ('CAMERA', 'ACCESS_WIFI_STATE', 'CHANGE_WIFI_STATE', 'ACCESS_NETWORK_STATE', 'CHANGE_NETWORK_STATE'))
s = s.replace('<application', PERMS + '<application', 1)

# رابط داخلي qrtool:// تفتح فيه الأزرار الشاشة المطلوبة
filt = '''<intent-filter>
                <action android:name="android.intent.action.VIEW" />
                <category android:name="android.intent.category.DEFAULT" />
                <category android:name="android.intent.category.BROWSABLE" />
                <data android:scheme="qrtool" />
            </intent-filter>
        '''
s = s.replace('</activity>', filt + '</activity>', 1)

# أزرار الإعدادات السريعة
META = '<meta-data android:name="com.google.mlkit.vision.DEPENDENCIES" android:value="barcode_ui" />\n    '

def tile(cls, label, icon):
    return '''<service android:name=".%s" android:label="%s"
            android:icon="@drawable/%s" android:exported="true"
            android:permission="android.permission.BIND_QUICK_SETTINGS_TILE">
            <intent-filter>
                <action android:name="android.service.quicksettings.action.QS_TILE" />
            </intent-filter>
        </service>
        ''' % (cls, label, icon)

s = s.replace('</application>', tile('CreateTile', 'إنشاء QR', 'ic_tile_create') + tile('ReadTile', 'قراءة QR', 'ic_tile_read') + META + '</application>', 1)
open(mp, 'w', encoding='utf-8').write(s)

jd = base + '/java/com/qrtool/app'
os.makedirs(jd, exist_ok=True)
for f in ('BaseTile.java', 'CreateTile.java', 'ReadTile.java', 'QrNativePlugin.java', 'MainActivity.java'):
    shutil.copy('native/' + f, jd + '/' + f)

os.makedirs(base + '/res/drawable', exist_ok=True)
for f in ('ic_tile_create.xml', 'ic_tile_read.xml'):
    shutil.copy('native/' + f, base + '/res/drawable/' + f)

# ---- الماسح الأصلي يحتاج minSdk 23 ----
vp = 'android/variables.gradle'
if os.path.exists(vp):
    v = open(vp, encoding='utf-8').read()
    v = re.sub(r'minSdkVersion\s*=\s*\d+', 'minSdkVersion = 23', v)
    open(vp, 'w', encoding='utf-8').write(v)

# ---- التوقيع (شهادة ثابتة) ورقم الإصدار ----
shutil.copy('keystore/release.jks', 'android/app/release.jks')
gp = 'android/app/build.gradle'
g = open(gp, encoding='utf-8').read()
run = os.environ.get('GITHUB_RUN_NUMBER', '1')
g = re.sub(r'versionCode\s+\d+', 'versionCode ' + run, g)
g = re.sub(r'versionName\s+"[^"]*"', 'versionName "1.0.' + run + '"', g)
sign = '''signingConfigs {
        release {
            storeFile file("release.jks")
            storePassword "%s"
            keyAlias "qrtool"
            keyPassword "%s"
        }
    }
    buildTypes {''' % (PASS, PASS)
g = g.replace('buildTypes {', sign, 1)
i = g.index('buildTypes {')
g = g[:i] + g[i:].replace('release {', 'release {\n            signingConfig signingConfigs.release', 1)
g = re.sub(r'android\s*\{', 'android {\n    lint {\n        abortOnError false\n        checkReleaseBuilds false\n    }', g, count=1)
open(gp, 'w', encoding='utf-8').write(g)
print('patched')
