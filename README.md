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

أُنشئ فرع `gh-pages` يدوياً لنشر النسخة الأولية، وضُبط Pages لخدمته من الجذر. يعتمد التحديث الآلي على توفر GitHub Actions وتشغيل سير العمل بنجاح.

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

تقرأ الرسوم التفاعلية التاريخية للمؤشرات `purchasing-power`, `unemployment-national` و`youth-unemployment` من الخاصية `history`، مرتبة زمنياً من الأقدم إلى الأحدث. أضف لكل نقطة `period` و`value` بعد توثيق مصدرها، مثلاً: `{ "period": "2024", "value": 12.3 }`. تعتمد الرسوم على Chart.js المحمّلة من jsDelivr.

## 📜 الترخيص

MIT — راجع [LICENSE](LICENSE).

---

**«هذا ليس رأياً — هذه أرقام رسمية.»**
