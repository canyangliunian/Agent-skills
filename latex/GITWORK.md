# GITWORK（本仓库 Git 全流程记录）

> 仓库路径：/Users/lingguiwang/Documents/Coding/LLM/12LaTex
> 远程地址：git@github.com:canyangliunian/Latex-Skills.git

## 1. 初始化仓库
```bash
cd /Users/lingguiwang/Documents/Coding/LLM/12LaTex
git init
```
说明：初始化本地 Git 仓库，默认分支为 master。

## 2. 查看状态（先确认待加入文件）
```bash
git status
```
说明：先确认当前文件变更范围，再决定如何暂存。

## 3. 添加文件到暂存区
```bash
git add .
```
说明：将当前目录下全部文件加入暂存区（也可按需添加指定文件）。

## 4. 再次查看状态
```bash
git status
```
说明：确认新增文件已进入暂存区。

## 5. 首次提交
```bash
git commit -m "Latex Skills"
```
说明：完成首次提交，包含 121 个新文件。

## 6. 添加远程仓库
```bash
git remote add origin git@github.com:canyangliunian/Latex-Skills.git
```
说明：设置远程仓库名为 origin。

## 7. 重命名主分支
```bash
git branch -M main
```
说明：将本地主分支从 master 重命名为 main。

## 8. 推送到远程并建立追踪（首次/后续）
```bash
# 首次推送并设置上游追踪
git push -u origin main

# 后续推送（已建立追踪后）
git push
```
说明：首次推送需要 `-u` 建立上游追踪；之后只需 `git push` 即可。
