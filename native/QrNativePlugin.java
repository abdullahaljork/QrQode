package com.qrtool.app;

import android.content.Context;
import android.content.Intent;
import android.net.Uri;
import android.net.wifi.WifiConfiguration;
import android.net.wifi.WifiManager;
import android.net.wifi.WifiNetworkSuggestion;
import android.os.Build;
import android.provider.ContactsContract;
import android.provider.Settings;

import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;

import java.util.ArrayList;

@CapacitorPlugin(name = "QrNative")
public class QrNativePlugin extends Plugin {

    // فتح أي رابط: واتساب، اتصال، رسائل، خرائط، بريد، مواقع
    @PluginMethod
    public void open(PluginCall call) {
        try {
            Intent i = new Intent(Intent.ACTION_VIEW, Uri.parse(call.getString("url", "")));
            i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            getContext().startActivity(i);
            call.resolve();
        } catch (Exception e) {
            call.reject(String.valueOf(e.getMessage()));
        }
    }

    // شاشة إضافة جهة اتصال جاهزة التعبئة
    @PluginMethod
    public void saveContact(PluginCall call) {
        try {
            Intent i = new Intent(ContactsContract.Intents.Insert.ACTION);
            i.setType(ContactsContract.RawContacts.CONTENT_TYPE);
            i.putExtra(ContactsContract.Intents.Insert.NAME, call.getString("name", ""));
            i.putExtra(ContactsContract.Intents.Insert.PHONE, call.getString("phone", ""));
            i.putExtra(ContactsContract.Intents.Insert.EMAIL, call.getString("email", ""));
            i.putExtra(ContactsContract.Intents.Insert.COMPANY, call.getString("org", ""));
            i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            getContext().startActivity(i);
            call.resolve();
        } catch (Exception e) {
            call.reject(String.valueOf(e.getMessage()));
        }
    }

    // الاتصال بشبكة واي فاي
    @PluginMethod
    @SuppressWarnings("deprecation")
    public void connectWifi(PluginCall call) {
        String ssid = call.getString("ssid", "");
        String pass = call.getString("password", "");
        String sec = call.getString("security", "WPA");
        boolean hidden = Boolean.TRUE.equals(call.getBoolean("hidden", false));
        if (ssid.isEmpty()) {
            call.reject("no ssid");
            return;
        }
        boolean open = "nopass".equalsIgnoreCase(sec) || pass.isEmpty();
        try {
            WifiManager wm = (WifiManager) getContext().getApplicationContext()
                    .getSystemService(Context.WIFI_SERVICE);
            if (Build.VERSION.SDK_INT >= 29) {
                WifiNetworkSuggestion.Builder b = new WifiNetworkSuggestion.Builder()
                        .setSsid(ssid)
                        .setIsHiddenSsid(hidden);
                if (!open) {
                    if ("SAE".equalsIgnoreCase(sec)) b.setWpa3Passphrase(pass);
                    else b.setWpa2Passphrase(pass);
                }
                ArrayList<WifiNetworkSuggestion> list = new ArrayList<>();
                list.add(b.build());
                if (Build.VERSION.SDK_INT >= 30) {
                    Intent i = new Intent(Settings.ACTION_WIFI_ADD_NETWORKS);
                    i.putParcelableArrayListExtra(Settings.EXTRA_WIFI_NETWORK_LIST, list);
                    getActivity().startActivity(i);
                } else {
                    int st = wm.addNetworkSuggestions(list);
                    if (st != WifiManager.STATUS_NETWORK_SUGGESTIONS_SUCCESS) {
                        call.reject("status " + st);
                        return;
                    }
                }
            } else {
                WifiConfiguration c = new WifiConfiguration();
                c.SSID = "\"" + ssid + "\"";
                c.hiddenSSID = hidden;
                if (open) c.allowedKeyManagement.set(WifiConfiguration.KeyMgmt.NONE);
                else c.preSharedKey = "\"" + pass + "\"";
                int id = wm.addNetwork(c);
                if (id < 0) {
                    call.reject("add failed");
                    return;
                }
                wm.disconnect();
                wm.enableNetwork(id, true);
                wm.reconnect();
            }
            call.resolve();
        } catch (Exception e) {
            call.reject(String.valueOf(e.getMessage()));
        }
    }
}
