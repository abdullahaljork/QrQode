import os, shutil

base = 'android/app/src/main'
mp = base + '/AndroidManifest.xml'
s = open(mp, encoding='utf-8').read()

# صلاحية الكاميرا
s = s.replace('<application', '<uses-permission android:name="android.permission.CAMERA" />\n    <application', 1)

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
def tile(cls, label):
    return '''<service android:name=".%s" android:label="%s"
            android:icon="@drawable/ic_tile_qr" android:exported="true"
            android:permission="android.permission.BIND_QUICK_SETTINGS_TILE">
            <intent-filter>
                <action android:name="android.service.quicksettings.action.QS_TILE" />
            </intent-filter>
        </service>
        ''' % (cls, label)

s = s.replace('</application>', tile('CreateTile', 'إنشاء QR') + tile('ReadTile', 'قراءة QR') + '</application>', 1)
open(mp, 'w', encoding='utf-8').write(s)

jd = base + '/java/com/qrtool/app'
os.makedirs(jd, exist_ok=True)
for f in ('BaseTile.java', 'CreateTile.java', 'ReadTile.java'):
    shutil.copy('native/' + f, jd + '/' + f)

os.makedirs(base + '/res/drawable', exist_ok=True)
shutil.copy('native/ic_tile_qr.xml', base + '/res/drawable/ic_tile_qr.xml')
print('patched')
