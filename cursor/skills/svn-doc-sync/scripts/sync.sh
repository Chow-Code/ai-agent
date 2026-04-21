#!/usr/bin/env bash
# SVN 策划文档转 MD 同步到 Git 子模块脚本
# 用法: ./sync.sh [--dry-run] [--only <文件名>]

set -e

SVN_URL="svn://172.16.4.12/TianLong3/Design/系统文档"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# scripts -> svn-doc-sync -> skills -> .cursor -> 项目根，需上溯 4 级
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
TEMP_DIR="${TEMP:-/tmp}/svn_design_export_$$"
TARGET_DIR="$PROJECT_ROOT/docs/developdoc/策划原文"
SUBMODULE_DIR="$PROJECT_ROOT/docs/developdoc"
LOG_FILE="$SCRIPT_DIR/sync.log"

DRY_RUN=false
ONLY_FILE=""

# 解析参数
while [[ $# -gt 0 ]]; do
  case $1 in
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    --only)
      ONLY_FILE="$2"
      shift 2
      ;;
    *)
      echo "未知参数: $1"
      exit 1
      ;;
  esac
done

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE" 2>/dev/null || echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

# Step 1: SVN export
do_export() {
  log "Step 1: SVN export 到 $TEMP_DIR"
  mkdir -p "$TEMP_DIR"
  svn export --force "$SVN_URL" "$TEMP_DIR" 2>&1 | tee -a "$LOG_FILE" 2>/dev/null || true
}

# Step 2: 转换文件
convert_file() {
  local src="$1"
  local base="${src%.*}"
  local ext="${src##*.}"
  local md_path="${base}.md"
  local rel_path="${src#$TEMP_DIR/}"
  local target_md="$TARGET_DIR/${rel_path%.*}.md"

  if [[ -n "$ONLY_FILE" && "$(basename "$src")" != "$ONLY_FILE" ]]; then
    return 0
  fi

  if $DRY_RUN; then
    log "[dry-run] 将转换: $rel_path -> ${rel_path%.*}.md"
    return 0
  fi

  mkdir -p "$(dirname "$target_md")"
  # Excel 需 markitdown[xlsx] 可选依赖；裸 uvx markitdown 无法读 .xlsx
  if command -v uvx >/dev/null 2>&1 && uvx --from 'markitdown[xlsx]' markitdown "$src" -o "$target_md" 2>/dev/null; then
    log "  转换成功: $rel_path"
  elif python -m markitdown "$src" -o "$target_md" 2>/dev/null; then
    log "  转换成功: $rel_path"
  elif python3 -m markitdown "$src" -o "$target_md" 2>/dev/null; then
    log "  转换成功: $rel_path"
  elif command -v py >/dev/null 2>&1 && py -3 -m markitdown "$src" -o "$target_md" 2>/dev/null; then
    log "  转换成功: $rel_path"
  elif uvx markitdown "$src" -o "$target_md" 2>/dev/null; then
    log "  转换成功: $rel_path"
  else
    log "  转换失败(跳过): $rel_path"
  fi
}

do_convert() {
  log "Step 2: 转换 .xlsx/.xls/.html 为 .md"
  if $DRY_RUN; then
    find "$TEMP_DIR" -type f \( -name "*.xlsx" -o -name "*.xls" -o -name "*.html" \) 2>/dev/null | while read -r f; do
      rel="${f#$TEMP_DIR/}"
      log "[dry-run] 将转换: $rel"
    done
    return 0
  fi

  while IFS= read -r -d '' f; do
    convert_file "$f"
  done < <(find "$TEMP_DIR" -type f \( -name "*.xlsx" -o -name "*.xls" -o -name "*.html" \) -print0 2>/dev/null)
}

# Step 3 & 4: Git 提交到当前分支并推送（直接 develop，无需切换分支）
do_git_push() {
  log "Step 3: Git add/commit/push（提交到当前分支 develop）"
  if $DRY_RUN; then
    log "[dry-run] 将执行: add -> commit -> push origin HEAD"
    return 0
  fi

  cd "$SUBMODULE_DIR"
  if [[ -n "$(git status --porcelain)" ]]; then
    git add .
    git commit -m "sync: 策划文档同步 $(date '+%Y-%m-%d %H:%M')"
    git push origin HEAD
    log "  已提交并推送到当前分支"
  else
    log "  无变更，跳过提交"
  fi
}

# Step 5: 清理
cleanup() {
  if [[ -d "$TEMP_DIR" ]] && [[ "$TEMP_DIR" == *"svn_design_export_"* ]]; then
    rm -rf "$TEMP_DIR"
    log "Step 4: 已清理临时目录"
  fi
}

trap cleanup EXIT

# 主流程
main() {
  log "========== SVN 文档同步开始 =========="
  log "项目根目录: $PROJECT_ROOT"
  log "目标目录: $TARGET_DIR"
  $DRY_RUN && log "模式: 预览 (--dry-run)"

  if [[ ! -e "$SUBMODULE_DIR/.git" ]]; then
    log "错误: docs/developdoc 子模块未初始化，请执行: git submodule update --init docs/developdoc"
    exit 1
  fi
  mkdir -p "$TARGET_DIR"

  do_export
  do_convert
  do_git_push

  log "========== 同步完成 =========="
}

main
