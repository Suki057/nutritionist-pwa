#!/bin/bash
# 公共营养师三级 PWA —— 一键部署到 GitHub Pages
# 前置：gh 已登录（终端跑 `gh auth status` 显示已认证）
#       或导出环境变量 GITHUB_TOKEN=你的有效PAT 后运行本脚本
set -e
cd "$(dirname "$0")"

REPO=suki057/nutritionist-pwa
REMOTE=https://github.com/$REPO.git

# 确保 remote 指向正确地址
git remote remove origin 2>/dev/null || true
git remote add origin "$REMOTE"

# 提交本地最新改动（无改动则跳过）
git add -A
git commit -m "chore: 更新营养师资讯 $(date +%Y-%m-%d)" >/dev/null 2>&1 || echo "（无新改动，跳过提交）"

# 建仓（若不存在）并推送
if gh repo view "$REPO" >/dev/null 2>&1; then
  echo "仓库已存在，直接推送…"
  git push -u origin main
else
  echo "创建仓库并推送…"
  gh repo create "$REPO" --public -s . --push -d "公共营养师三级 PWA 应试宝典（移动端可安装）"
fi

echo "✅ 完成。GitHub Pages 地址：https://${REPO}"
