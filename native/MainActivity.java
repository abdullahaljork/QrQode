package com.qrtool.app;

import android.os.Bundle;
import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {
    @Override
    public void onCreate(Bundle savedInstanceState) {
        registerPlugin(QrNativePlugin.class);
        super.onCreate(savedInstanceState);
    }
}
