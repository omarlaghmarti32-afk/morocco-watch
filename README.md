# 🇲🇦 مؤشر المواطن المغربي

منصة مستقلة لتحليل واقع المواطن المغربي بالأرقام الرسمية.

## 📊 المؤشرات

- 💰 القدرة الشرائية الحقيقية
- 💼 فرص العمل وبطالة الشباب
- 🏠 عبء السكن
- 🎓 بطالة حاملي الشهادات
- 🌍 الفجوة التنافسية مع أوروبا

## 🌐 الموقع المباشر

👉 [زيارة الموقع](https://omarlaghmarti32-afk.github.io/morocco-watch/)

> الموقع منشور الآن من فرع `gh-pages` والمجلد `/`، والنسخة الحالية هي إصدار أولي.

## 📚 المصادر الرسمية

- [المندوبية السامية للتخطيط (HCP)](https://www.hcp.ma/)
- [بنك المغرب (Bank Al-Maghrib)](https://www.bkam.ma/)
- [صندوق النقد الدولي (IMF)](https://www.imf.org/en/Countries/MAR)
- [البنك الدولي (World Bank)](https://data.worldbank.org/country/morocco)

هذه بوابات مرجعية للبحث عن السلاسل الأصلية، وليست إسناداً لقيم منشورة في هذه النسخة.

تتضمن النسخة الحالية قيماً منشورة عن البطالة والقدرة الشرائية: المعدل الوطني للبطالة 13.3% في 2024 و13.0% في 2025، وبطالة الشباب (15–24 سنة) 36.7% ثم 37.2% وفق [HCP](https://www.hcp.ma/Situation-du-marche-du-travail-en-2025_a4248.html). وتحسن القدرة الشرائية للأسر 1.8 نقطة في 2023 و5.1 نقاط في 2024 وفق [حسابات HCP](https://www.hcp.ma/Les-comptes-nationaux-des-secteurs-institutionnels-2024-Base-2014-Decembre-2025-Rapport-complet_a4225.html)، وتؤكدها [البوابة الحكومية المغربية](https://maroc.ma/fr/actualites/maroc-amelioration-du-pouvoir-dachat-des-menages-de-51-points-en-2024). نقاط القدرة الشرائية بوحدة «نقطة تحسّن» وليست نسباً مئوية.

## 🚀 النشر والتحديث

سير GitHub Actions مُهيأ لإعادة بناء الموقع ونشره:
- عند كل `push` إلى فرع `main`.
- يومياً عند الساعة 06:00 UTC.
- يدوياً من تبويب **Actions** عبر **Run workflow**.

حالياً لا يبدأ سير البناء المخصص لأن حساب GitHub مقفل بسبب مشكلة فوترة. إلى أن تُحل، استخدم [سكربت النشر المحلي](scripts/deploy-local.sh) لرفع الموقع إلى `gh-pages`. إعداد Pages الحالي يخدم هذا الفرع من المجلد `/`.

**تنبيه:** التشغيل المجدول يعيد بناء الموقع ونشره، لكنه لا يسحب بيانات جديدة. تُحدّث المؤشرات يدوياً في `data/indicators.json` بعد التحقق من مصادرها.

## 📁 هيكل المشروع

```text
morocco-watch/
├── README.md
├── requirements.txt
├── scripts/
│   └── deploy-local.sh
├── data/
│   └── indicators.json
├── src/
│   └── generator.py
├── output/
│   ├── index.html (يُولَّد تلقائياً)
│   ├── feed.xml وatom.xml (خلاصات التحديث)
│   ├── changelog/index.html (سجل التغييرات)
│   └── api/v1/ (واجهات JSON)
└── .github/
    └── workflows/
        └── deploy.yml
```

## 🛠️ التقنيات

- Python 3.11
- HTML5 وCSS3
- GitHub Actions
- GitHub Pages

## تشغيل محلي

على Linux أو macOS أو WSL/Git Bash، استخدم Python 3.11 أو 3.12، وأنشئ بيئة وثبّت الاعتماديات ثم شغّل مولّد الموقع. يظل إعداد GitHub Actions على Python 3.11:

```bash
python3 -m venv .venv
# Linux/macOS/WSL:
source .venv/bin/activate
# Windows Git Bash بدلاً من السطر السابق:
# source .venv/Scripts/activate
python -m pip install -r requirements.txt
python src/generator.py
python -m http.server 8000 --directory output
```

ثم افتح `http://localhost:8000`.

## النشر المحلي المؤقت

يتطلب النشر صلاحية كتابة على المستودع. ثبّت [GitHub CLI](https://cli.github.com/) وسجّل الدخول مرة واحدة، ثم فعّل اعتماد Git:

```bash
gh auth login
gh auth setup-git
```

اضبط هوية Git إذا لم تكن مضبوطة مسبقاً، ثم اسحب آخر نسخة من `main` وتأكد من عدم وجود تغييرات غير ملتزمة:

```bash
git config --global user.name "اسمك"
git config --global user.email "بريدك أو عنوان GitHub noreply"
git switch main
git pull --ff-only origin main
```

بعد تفعيل بيئة Python أعلاه وتشغيل الأمر التالي، سيعيد السكربت بناء الصفحة، وينسخ الناتج إلى نسخة مؤقتة من `gh-pages`، ثم يدفع التغيير العادي إلى GitHub:

```bash
./scripts/deploy-local.sh
```

يشترط السكربت أن تكون على `main` وأن تطابق نسختك `origin/main`، ولا يستخدم `force-push`. إذا تغيّر `gh-pages` بالتزامن ورُفض الدفع، اسحب آخر `main` ثم أعد تشغيله. هذا النشر **يدوي عند كل تحديث** ولا يفعّل الجدولة اليومية؛ كما يجب أن يبقى GitHub Pages مضبوطاً على `gh-pages` و`/`.

## إضافة البيانات

حرر `data/indicators.json`. لكل مؤشر يمكن ضبط `value`, `unit`, `period`, `reference` و`source_url`. لا تضف قيمة إلا بعد التحقق من تعريف المؤشر والفترة والمصدر الأصلي؛ احرص على أن يحدد `reference` التقرير أو الجدول ورقم الصفحة أو الرابط الدقيق. راجع البيانات تحريرياً قبل نشرها.

تقرأ الرسوم التفاعلية التاريخية للمؤشرات `purchasing-power`, `unemployment-national` و`youth-unemployment` من الخاصية `history`، مرتبة زمنياً من الأقدم إلى الأحدث. أضف لكل نقطة `period` و`value` بعد توثيق مصدرها، مثلاً: `{ "period": "2024", "value": 12.3 }`. تعتمد الرسوم على Chart.js المحمّلة من jsDelivr.

## إشعارات RSS/Atom وسجل التغييرات

بعد النشر، يمكن للمستخدمين الاشتراك في الخلاصات عبر قارئ RSS/Atom:

- RSS: <https://omarlaghmarti32-afk.github.io/morocco-watch/feed.xml>
- Atom: <https://omarlaghmarti32-afk.github.io/morocco-watch/atom.xml>
- سجل التغييرات: <https://omarlaghmarti32-afk.github.io/morocco-watch/changelog/>
- سجل JSON: <https://omarlaghmarti32-afk.github.io/morocco-watch/api/v1/changelog.json>

يبني المولّد السجل بمقارنة التزامات Git التي غيّرت `data/indicators.json`، ثم ينشر التحديثات ذات القيم الموثقة فقط. لذلك احفظ كل تحديث للبيانات في التزام Git. يحمّل Workflow كامل سجل Git، ويتحقق سكربت النشر المحلي من اكتمال السجل إذا كانت النسخة shallow. قارئات RSS/Atom تتحقق من الخلاصة وفق جدولها؛ هذا اشتراك بالخلاصة وليس رسالة فورية أو بريداً إلكترونياً.

حالياً، بسبب مشكلة الفوترة التي تمنع سير Actions المخصص من العمل، شغّل `./scripts/deploy-local.sh` بعد اعتماد تحديث البيانات كي تُنشر الخلاصات وسجل التغييرات. بعد حل المشكلة، يعيد Workflow بناءها عند كل `push` إلى `main`.

## API للقراءة فقط

ينسخ مولّد الموقع البيانات إلى نقطة JSON ثابتة بإصدار `v1`:

```text
https://omarlaghmarti32-afk.github.io/morocco-watch/api/v1/indicators.json
```

تدعم النقطة طلب `GET` وتعيد كائن `updated_at` ومصفوفة `indicators` بالتنسيق نفسه الموجود في `data/indicators.json`. مثال من سطر الأوامر:

```bash
curl -sS https://omarlaghmarti32-afk.github.io/morocco-watch/api/v1/indicators.json
```

ومثال من تطبيق JavaScript في المتصفح:

```javascript
const response = await fetch(
  "https://omarlaghmarti32-afk.github.io/morocco-watch/api/v1/indicators.json"
);
if (!response.ok) throw new Error(`API request failed: ${response.status}`);
const payload = await response.json();
const unemployment = payload.indicators.find(
  (item) => item.id === "unemployment-national"
);
console.log(payload.updated_at, unemployment?.value, unemployment?.unit);
```

هذه واجهة **قراءة عامة فقط** وليست خادماً ديناميكياً: لا تدعم `POST` أو كتابة البيانات أو المصادقة أو المرشحات على الخادم. الموقع العام يرسل حالياً `Access-Control-Allow-Origin: *`، ما يسمح لتطبيقات المتصفح بقراءة البيانات من نطاقات مختلفة؛ ولا يتيح GitHub Pages ضبط رأس CORS مخصص لكل نطاق [مناقشة GitHub Pages حول CORS](https://github.com/orgs/community/discussions/157852). لذلك لا تضع مفاتيح أو بيانات خاصة في `indicators.json`. يتحدث المسار عند بناء الموقع ونشره، سواء عبر GitHub Actions أو سكربت النشر المحلي.

## 📜 الترخيص

MIT — راجع [LICENSE](LICENSE).

---

**«هذا ليس رأياً — هذه أرقام رسمية.»**
