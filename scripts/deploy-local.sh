#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_DIR="$ROOT_DIR/output"
PYTHON_BIN="${PYTHON_BIN:-python3}"
REMOTE_NAME="origin"
DEPLOY_BRANCH="gh-pages"

fail() {
  printf 'خطأ: %s\n' "$1" >&2
  exit 1
}

cd "$ROOT_DIR"

command -v git >/dev/null 2>&1 || fail "لم يتم العثور على git."
command -v "$PYTHON_BIN" >/dev/null 2>&1 || fail "لم يتم العثور على Python المحدد في PYTHON_BIN."

CURRENT_BRANCH="$(git branch --show-current)"
[[ "$CURRENT_BRANCH" == "main" ]] || fail "شغّل النشر من فرع main (الفرع الحالي: $CURRENT_BRANCH)."
[[ -z "$(git status --porcelain --untracked-files=normal)" ]] || fail "هناك تغييرات محلية غير ملتزمة. احفظها وادفعها إلى main أولاً."

"$PYTHON_BIN" -c 'import sys; raise SystemExit(0 if sys.version_info[:2] in {(3, 11), (3, 12)} else 1)' \
  || fail "يتطلب المشروع Python 3.11 أو 3.12. فعّل البيئة الافتراضية ثم أعد المحاولة."

REMOTE_URL="$(git remote get-url "$REMOTE_NAME")"
[[ -n "$REMOTE_URL" ]] || fail "تعذر قراءة عنوان المستودع البعيد origin."

git fetch --quiet "$REMOTE_NAME" main "$DEPLOY_BRANCH" \
  || fail "تعذر جلب main وgh-pages. تحقق من الاتصال وصلاحية الوصول."

LOCAL_MAIN="$(git rev-parse HEAD)"
REMOTE_MAIN="$(git rev-parse "refs/remotes/$REMOTE_NAME/main")"
[[ "$LOCAL_MAIN" == "$REMOTE_MAIN" ]] \
  || fail "نسختك المحلية من main ليست مطابقة لـorigin/main. اسحب آخر التغييرات ثم أعد المحاولة."

if [[ "$(git rev-parse --is-shallow-repository)" == "true" ]]; then
  git fetch --quiet --unshallow "$REMOTE_NAME" main \
    || fail "تعذر استكمال سجل Git المطلوب لتوليد سجل التغييرات."
fi

"$PYTHON_BIN" "$ROOT_DIR/src/generator.py"
[[ -s "$OUTPUT_DIR/index.html" ]] || fail "لم يُنشأ output/index.html."

AUTHOR_NAME="$(git config user.name || git log -1 --format=%an)"
AUTHOR_EMAIL="$(git config user.email || git log -1 --format=%ae)"
[[ -n "$AUTHOR_NAME" && -n "$AUTHOR_EMAIL" ]] \
  || fail "اضبط git config user.name وgit config user.email قبل النشر."

TEMP_DIR="$(mktemp -d)"
trap 'rm -rf -- "$TEMP_DIR"' EXIT

git clone --quiet --single-branch --depth 1 --branch "$DEPLOY_BRANCH" \
  "$REMOTE_URL" "$TEMP_DIR/site" \
  || fail "تعذر استنساخ gh-pages. تحقق من صلاحية الكتابة للمستودع."

# Keep branch metadata such as .nojekyll, then replace/add generated site files.
cp -a "$OUTPUT_DIR"/. "$TEMP_DIR/site"/
git -C "$TEMP_DIR/site" add -A

if git -C "$TEMP_DIR/site" diff --cached --quiet; then
  printf 'لا توجد تغييرات جديدة للنشر؛ gh-pages محدث بالفعل.\n'
  exit 0
fi

SOURCE_SHA="$(git rev-parse --short HEAD)"
git -C "$TEMP_DIR/site" \
  -c "user.name=$AUTHOR_NAME" \
  -c "user.email=$AUTHOR_EMAIL" \
  commit -m "Deploy site from $SOURCE_SHA"

git -C "$TEMP_DIR/site" push "$REMOTE_NAME" "HEAD:refs/heads/$DEPLOY_BRANCH" \
  || fail "رُفض الدفع، غالباً لأن gh-pages تغيّر بالتزامن. لم يُستخدم force-push؛ أعد تشغيل السكربت بعد جلب آخر نسخة."

printf '\nتم النشر بنجاح إلى %s.\n' "$DEPLOY_BRANCH"
printf 'افحص الموقع: https://omarlaghmarti32-afk.github.io/morocco-watch/\n'
