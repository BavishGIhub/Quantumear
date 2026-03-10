# Android Build Guide — QuantumEAR

## Prerequisites

1. **Android Studio** — Download from [developer.android.com](https://developer.android.com/studio)
2. **Java JDK 17+** — Required by Gradle
3. **Node.js 18+** and npm
4. **Android SDK 33+** (API Level 33)

## Step 1: Build the Next.js App

```bash
cd app
npm run build
```

This creates a static export in the `out/` directory.

## Step 2: Initialize Capacitor Android

```bash
npx cap add android
npx cap sync android
```

## Step 3: Open in Android Studio

```bash
npx cap open android
```

## Step 4: Configure Android Settings

In Android Studio:
1. Open `android/app/build.gradle`
2. Set `minSdkVersion` to 24 (Android 7.0+)
3. Set `targetSdkVersion` to 34

## Step 5: Build APK

### Debug APK (for testing):
```bash
cd android
./gradlew assembleDebug
```
APK will be at: `android/app/build/outputs/apk/debug/app-debug.apk`

### Release APK (for distribution):
1. Generate signing key:
```bash
keytool -genkey -v -keystore quantumear.keystore -alias quantumear -keyalg RSA -keysize 2048 -validity 10000
```

2. Build release APK:
```bash
cd android
./gradlew assembleRelease
```

## Step 6: Install on Device

```bash
adb install -r android/app/build/outputs/apk/debug/app-debug.apk
```

## Network Configuration

For the Android app to communicate with the FastAPI backend:
- **Development**: Use `10.0.2.2:8000` (Android emulator → host machine)
- **Production**: Deploy FastAPI to a cloud server and update `NEXT_PUBLIC_API_URL`

## Permissions

The app requires:
- `INTERNET` — For API communication
- `READ_EXTERNAL_STORAGE` — For file picking (audio files)

These are configured in `android/app/src/main/AndroidManifest.xml`.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| White screen | Check `webDir` in capacitor.config.ts points to `out` |
| API connection fails | Ensure backend is running and URL is correct |
| File picker not working | Check storage permissions are granted |
| Build fails | Run `npx cap sync android` after any frontend changes |
