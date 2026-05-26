#!/usr/bin/env bash
# Skill 打包脚本
# 用法: bash package_skill.sh <skill-name> [output-dir]
set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd || dirname "$(readlink -f "$0")")"
SKILLS_DIR="$(dirname "$SKILL_DIR")"

SKILL_NAME="$1"
OUTPUT_DIR="${2:-$SKILLS_DIR/dist}"

if [ -z "$SKILL_NAME" ]; then
    echo "用法: bash package_skill.sh <skill-name> [output-dir]"
    exit 1
fi

SKILL_PATH="$SKILLS_DIR/$SKILL_NAME"

if [ ! -d "$SKILL_PATH" ]; then
    echo "❌ Skill 目录不存在: $SKILL_PATH"
    exit 1
fi

mkdir -p "$OUTPUT_DIR"

# 检查 clawhub 是否可用
if command -v clawhub &> /dev/null; then
    echo "📦 使用 clawhub 打包..."
    clawhub package "$SKILL_PATH" "$OUTPUT_DIR"
else
    echo "📦 clawhub 未找到，使用手动打包..."
    OUTPUT_FILE="$OUTPUT_DIR/${SKILL_NAME}.skill"
    cd "$SKILLS_DIR"
    zip -r "$OUTPUT_FILE" "$SKILL_NAME" -x "*/.git/*" -x "*/.gitignore"
    echo "✅ 打包完成：$OUTPUT_FILE"
fi

echo ""
echo "📥 安装方式："
echo "  clawhub install $OUTPUT_DIR/${SKILL_NAME}.skill"
