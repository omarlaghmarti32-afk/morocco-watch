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

> يحتوي فرع `gh-pages` على نسخة أولية. يلزم تفعيل GitHub Pages على هذا الفرع قبل أن يعمل الرابط.

## 📚 المصادر الرسمية

- [المندوبية السامية للتخطيط (HCP)](https://www.hcp.ma/)
- [بنك المغرب (Bank Al-Maghrib)](https://www.bkam.ma/)
- [صندوق النقد الدولي (IMF)](https://www.imf.org/en/Countries/MAR)
- [البنك الدولي (World Bank)](https://data.worldbank.org/country/morocco)

هذه بوابات مرجعية للبحث عن السلاسل الأصلية، وليست إسناداً لقيم منشورة في هذه النسخة.

## 🚀 النشر والتحديث

يبني GitHub Actions الموقع وينشره:
- عند كل `push` إلى فرع `main`.
- يومياً عند الساعة 06:00 UTC.
- يدوياً من تبويب **Actions** عبر **Run workflow**.

من **Settings → Pages** اختر **Deploy from a branch** ثم الفرع `gh-pages` والمجلد `/(root)`. أُنشئ الفرع يدوياً للنسخة الأولية؛ ويحتاج التحديث الآلي إلى أن يتمكن GitHub Actions من تشغيل سير العمل والكتابة إلى الفرع.

**تنبيه:** التشغيل المجدول يعيد بناء الموقع ونشره، لكنه لا يسحب بيانات جديدة. المؤشرات في النسخة الحالية بلا قيم إلى حين إضافة بيانات موثقة إلى `data/indicators.json` أو إعداد تكامل بيانات مستقل.

## 📁 هيكل المشروع

```text
morocco-watch/
├── README.md
├── requirements.txt
├── data/
│   └── indicators.json
├── src/
│   └── generator.py
├── output/
│   └── index.html (يُولَّد تلقائياً)
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

ثبّت الاعتماديات المحددة في `requirements.txt` ثم شغّل مولّد الموقع:

```bash
python -m pip install -r requirements.txt
python src/generator.py
python -m http.server 8000 --directory output
```

ثم افتح `http://localhost:8000`.

## إضافة البيانات

حرر `data/indicators.json`. لكل مؤشر يمكن ضبط `value`, `unit`, `period`, `reference` و`source_url`. لا تضف قيمة إلا بعد التحقق من تعريف المؤشر والفترة والمصدر الأصلي؛ احرص على أن يحدد `reference` التقرير أو الجدول ورقم الصفحة أو الرابط الدقيق. راجع البيانات تحريرياً قبل نشرها.

## 📜 الترخيص

MIT — راجع [LICENSE](LICENSE).

---

**«هذا ليس رأياً — هذه أرقام رسمية.»**
