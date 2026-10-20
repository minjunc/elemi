# 엘레미 테일즈 (Elemi Tales)

둥둥이가 원소 구슬을 먹고 변신해 길을 여는 퍼즐 게임. 6월드 × 10스테이지.

## 폴더 구성
- `www/` – 게임 본체(웹앱). 이 폴더만 있으면 어디서든 실행돼요. 인터넷 없이도 동작해요.
- `android/` – 안드로이드 앱 프로젝트 (Capacitor). Android Studio로 열 수 있어요.
- `.github/workflows/android.yml` – GitHub에 올리면 APK를 자동으로 만들어 줘요.

## 1. 웹앱으로 쓰기 (가장 쉬움)
1. https://app.netlify.com/drop 에 `www` 폴더를 끌어다 놓으면 주소가 생겨요. (GitHub Pages, Vercel도 가능)
2. 폰에서 그 주소를 열고
   - 안드로이드 크롬: 메뉴 → **홈 화면에 추가** (또는 "앱 설치")
   - 아이폰 사파리: 공유 → **홈 화면에 추가**
3. 홈 화면 아이콘으로 열면 전체 화면 앱처럼 실행되고, 한 번 열고 나면 오프라인에서도 돼요.

## 2. 안드로이드 APK 만들기
### 방법 A: GitHub에서 자동 빌드 (PC에 설치할 것 없음)
1. 이 폴더 전체를 새 GitHub 저장소에 올려요.
2. 저장소의 **Actions** 탭 → "Build Android APK" 가 자동으로 돌아요 (약 5분).
3. 끝나면 실행 결과 맨 아래 **Artifacts → elemi-tales-apk** 를 받아 압축을 풀면 `app-debug.apk` 가 나와요.
4. 폰에 옮겨서 설치 (처음이면 "출처를 알 수 없는 앱 설치" 허용 필요).

### 방법 B: 내 PC에서 빌드
1. Node.js 22, Android Studio 설치
2. 이 폴더에서 `npm install` → `npx cap sync android` → `npx cap open android`
3. Android Studio에서 ▶ Run (폰을 USB로 연결) 또는 Build → Build APK

## 3. 플레이스토어에 올리려면
- Android Studio → Build → **Generate Signed App Bundle** 로 서명된 `.aab` 를 만들어요 (서명 키는 잘 보관!).
- Google Play Console(등록비 $25 1회)에서 앱 만들기 → 개인정보처리방침 URL, 스크린샷, 콘텐츠 등급 설문을 채우고 `.aab` 업로드.
- 앱 ID는 `com.elemitales.game` 이에요. 바꾸려면 `capacitor.config.json` 의 `appId` 와 `android/app/build.gradle` 의 `applicationId` 를 함께 바꾸세요.

## 게임을 고친 뒤
`www/` 를 새로 만든 다음 `npx cap sync android` 를 다시 실행하면 안드로이드 프로젝트에도 반영돼요.
