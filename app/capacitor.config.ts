import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
    appId: 'com.quantumear.app',
    appName: 'QuantumEAR',
    webDir: 'out',
    server: {
        // For development, point to the Next.js dev server
        // Comment this out for production builds
        // url: 'http://10.0.2.2:3000',
        // cleartext: true,
        androidScheme: 'https',
    },
    plugins: {
        StatusBar: {
            style: 'DARK',
            backgroundColor: '#00000000', // Transparent so our Next.js bg shows through
            overlaysWebView: true,
        },
        SplashScreen: {
            launchAutoHide: true,
            backgroundColor: '#030712',
            androidSplashResourceName: 'splash',
            androidScaleType: 'CENTER_CROP',
            showSpinner: false,
            splashFullScreen: true,
            splashImmersive: true,
        },
    },
    android: {
        backgroundColor: '#030712',
        allowMixedContent: true,
        captureInput: true,
        webContentsDebuggingEnabled: false,
    },
};

export default config;
