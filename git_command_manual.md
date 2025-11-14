# Git & GitHub CLI 完整教程手册

## 🚀 前言

本教程将Git和GitHub CLI（gh）完美结合，让你从命令行小白成长为版本控制高手！

## 目录

- [第一章：环境准备篇](#第一章环境准备篇)
- [第二章：Git基础操作篇](#第二章git基础操作篇)
- [第三章：GitHub CLI 专属功能篇](#第三章github-cli-专属功能篇)
- [第四章：代码提交与推送篇](#第四章代码提交与推送篇)
- [第五章：分支管理篇](#第五章分支管理篇)
- [第六章：Issue管理篇](#第六章issue管理篇)
- [第七章：高级协作篇](#第七章高级协作篇)
- [第八章：日常开发工作流](#第八章日常开发工作流)
- [第九章：实用技巧篇](#第九章实用技巧篇)
- [第十章：故障排除篇](#第十章故障排除篇)
- [第十一章：别名和快捷方式](#第十一章别名和快捷方式)
- [第十二章：实战场景示例](#第十二章实战场景示例)
- [第十三章：最佳实践篇](#第十三章最佳实践篇)
- [第十四章：Git内部原理](#第十四章git内部原理)
- [第十五章：高级GitHub CLI功能](#第十五章高级github-cli功能)
- [第十六章：企业级应用](#第十六章企业级应用)
- [常用命令速查表](#常用命令速查表)

## 第一章：环境准备篇

### 1.1 安装Git

**Windows:**

```bash
# 下载 Git for Windows
# 访问：https://git-scm.com/download/win
```

**macOS:**

```bash
# 使用 Homebrew
brew install git

# 或者使用 MacPorts
sudo port install git
```

**Linux (Ubuntu/Debian):**

```bash
sudo apt update && sudo apt install git
```

**Linux (CentOS/RHEL/Fedora):**

```bash
# CentOS/RHEL
sudo yum install git

# Fedora
sudo dnf install git
```

### 1.2 安装GitHub CLI (gh)

**Windows:**

```bash
# 使用 winget (Windows 10/11 内置)
winget install GitHub.cli

# 使用 Chocolatey
choco install gh

# 使用 Scoop
scoop install gh
```

**macOS:**

```bash
# 使用 Homebrew
brew install gh

# 使用 MacPorts
sudo port install gh
```

**Linux:**

```bash
# Ubuntu/Debian
sudo apt install gh

# CentOS/RHEL/Fedora
sudo dnf install gh

# 使用官方安装脚本
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo gpg --dearmor -o /usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh
```

### 1.3 配置用户信息

```bash
# 设置全局用户信息
git config --global user.name "你的用户名"
git config --global user.email "你的邮箱"

# 设置默认编辑器
git config --global core.editor "vim"  # 或其他你喜欢的编辑器

# 设置默认分支名（适用于较新版本的Git）
git config --global init.defaultBranch main

# 登录 GitHub CLI
gh auth login
```

### 1.4 验证安装

```bash
# 检查 Git 版本
git --version

# 检查 GitHub CLI 版本
gh --version

# 检查 Git 配置
git config --list
```

## 第二章：Git基础操作篇

### 2.1 初始化项目

```bash
# 初始化一个新的 Git 仓库
git init

# 初始化一个裸仓库（通常用于服务器端）
git init --bare

# 指定目录初始化
git init my-project
```

**中文释义**：给我初始化一个Git仓库，别磨蹭！

**终端输出示例：**

```
初始化空的 Git 仓库于 /path/to/your/project/.git/
```

### 2.2 克隆仓库

```bash
# 传统Git方式
git clone https://github.com/username/repo.git

# 克隆到指定目录
git clone https://github.com/username/repo.git my-directory

# 克隆特定分支
git clone -b branch-name https://github.com/username/repo.git

# 浅克隆（只获取最近一次提交）
git clone --depth 1 https://github.com/username/repo.git

# 使用gh更简单的方式
gh repo clone username/repo
```

**中文释义**：快把那个项目给我复制过来！

**终端输出示例（gh方式）：**

```
正在克隆 'username/repo'...
✓ 已克隆到 'repo' 目录
```

### 2.3 查看状态

```bash
# 查看工作区状态
git status

# 简洁显示状态
git status -s

# 显示分支信息
git status -b
```

**中文释义**：我的代码现在是个什么状态？

**终端输出示例：**

```
位于分支 main
您的分支与 'origin/main' 保持一致。

尚未暂存以备提交的变更：
  修改：     readme.md

未跟踪的文件:
  新文件：   new-file.txt
```

### 2.4 查看差异

```bash
# 查看工作区与暂存区的差异
git diff

# 查看暂存区与最后一次提交的差异
git diff --cached

# 查看工作区与最后一次提交的差异
git diff HEAD

# 比较两个提交之间的差异
git diff commit1 commit2

# 比较两个分支之间的差异
git diff branch1 branch2
```

## 第三章：GitHub CLI 专属功能篇

### 3.1 身份认证

```bash
# 登录
gh auth login

# 使用已有token登录
gh auth login --with-token

# 列出已认证账户
gh auth list

# 切换活动账户
gh auth switch

# 注销账户
gh auth logout
```

**中文释义**：让我登录GitHub，获取魔法权限！

**终端输出示例：**

```
? What account do you want to log into? GitHub.com
? How would you like to authenticate? Login with a web browser

Press Enter to open github.com in your browser...
✓ Authentication complete.
```

### 3.2 创建新仓库

```bash
# 交互式创建仓库
gh repo create

# 创建私有仓库
gh repo create my-repo --private

# 创建公共仓库并添加描述
gh repo create my-repo --public --description "My awesome project"

# 从现有本地仓库创建远程仓库
gh repo create my-org/my-repo --push --source=. --remote=origin

# 创建模板仓库
gh repo create my-repo --template owner/template-repo
```

**中文释义**：在GitHub上创建一个新仓库！

**终端输出示例：**

```
? Repository name my-new-repo
? Description A new repository
? Visibility Public
? This will create 'username/my-new-repo' on GitHub. Continue? Yes
✓ Created repository username/my-new-repo on GitHub
✓ Added remote https://github.com/username/my-new-repo.git
```

### 3.3 快速查看仓库信息

```bash
# 查看当前仓库信息
gh repo view

# 查看指定仓库信息
gh repo view owner/repo

# 在浏览器中打开仓库
gh repo view --web

# 查看仓库的贡献者
gh repo view -- contributors

# 以JSON格式输出
gh repo view --json name,description,url,stargazerCount
```

**中文释义**：让我看看这个仓库的基本信息！

**终端输出示例：**

```
https://github.com/username/repo

  24 stars  5 forks  12 issues
  Last updated about 1 hour ago

  A sample repository for demonstration
  Readme: ✓  License: MIT
```

## 第四章：代码提交与推送篇

### 4.1 添加文件

```bash
# 添加单个文件
git add filename.txt

# 添加所有文件
git add .

# 添加特定类型文件
git add *.js

# 添加部分文件到暂存区
git add -p

# 添加被忽略但临时需要的文件
git add -f filename.txt

# 查看将要添加的文件
git add --dry-run .
```

**中文释义**：把所有改动都给我抓起来！

### 4.2 提交代码

```bash
# 基本提交
git commit -m "你的提交信息"

# 提交并跳过钩子
git commit -m "message" --no-verify

# 修改上次提交
git commit --amend

# 提交时添加文件并提交
git commit -a -m "message"

# 空提交
git commit --allow-empty -m "empty commit"

# 查看提交历史
git log

# 单行显示提交历史
git log --oneline

# 图形化显示提交历史
git log --graph
```

**中文释义**：给我记下来，我刚才做了什么伟大的改动！

**终端输出示例：**

```
[main 1a2b3c4] 你的提交信息
 1 file changed, 5 insertions(+)
```

### 4.3 推送代码

```bash
# 推送到默认远程仓库
git push

# 推送到指定远程仓库和分支
git push origin main

# 推送并设置上游分支
git push -u origin feature-branch

# 推送所有分支
git push --all

# 强制推送（谨慎使用）
git push --force

# 使用gh的智能推送
gh repo sync

# 推送标签
git push --tags
```

**中文释义**：把我的成果推送到GitHub！

**终端输出示例（gh方式）：**

```
✓ 同步完成！本地分支已更新到最新状态
```

## 第五章：分支管理篇

### 5.1 查看分支

```bash
# 查看本地分支
git branch

# 查看远程分支
git branch -r

# 查看所有分支
git branch -a

# 查看合并到当前分支的分支
git branch --merged

# 查看未合并到当前分支的分支
git branch --no-merged

# 以简洁形式查看分支
git branch -v
```

**中文释义**：看看我都有哪些分身？

**终端输出示例：**

```
  develop
* main
  feature/login
```

### 5.2 创建和切换分支

```bash
# 创建新分支
git branch feature/new-feature

# 切换分支
git checkout feature/new-feature

# 创建并切换到新分支
git checkout -b feature/new-feature

# 基于某个提交创建分支
git checkout -b feature/new-feature commit-hash

# 创建并切换到新分支（新版本Git）
git switch -c feature/new-feature

# 切换分支（新版本Git）
git switch main

# 从远程分支创建本地分支
git checkout -b feature/new-feature origin/feature/new-feature
```

### 5.3 删除分支

```bash
# 删除本地分支
git branch -d feature/old-feature

# 强制删除本地分支
git branch -D feature/old-feature

# 删除远程分支
git push origin --delete feature/old-feature

# 清理已删除的远程分支引用
git remote prune origin
```

### 5.4 使用gh管理Pull Request

#### 创建PR

```bash
# 交互式创建PR
gh pr create

# 指定标题和描述创建PR
gh pr create --title "Fix bug" --body "Fixed a critical bug"

# 从草稿开始创建PR
gh pr create --draft

# 指定目标分支
gh pr create --base develop

# 指定审查者
gh pr create --reviewer user1,user2

# 将PR分配给某人
gh pr create --assignee user1

# 添加标签
gh pr create --label bug,urgent
```

**中文释义**：我要提交代码审查请求！

**终端输出示例：**

```
? Title: 添加新功能
? Body: <Received> [Enter to launch editor]
? What's next? Submit
✓ Created pull request #42
```

#### 查看PR列表

```bash
# 查看所有开放的PR
gh pr list

# 查看指定状态的PR
gh pr list --state closed

# 查看分配给我的PR
gh pr list --assignee @me

# 查看需要我审查的PR
gh pr list --reviewer @me

# 查看特定作者的PR
gh pr list --author username

# 按标签筛选PR
gh pr list --label bug

# 限制返回结果数量
gh pr list --limit 10

# 以JSON格式输出
gh pr list --json number,title,author,state
```

**中文释义**：看看有哪些待处理的代码审查！

**终端输出示例：**

```
#42  添加新功能    feature/new-feature
#41  修复bug       bugfix/login-issue
```

#### 查看特定PR

```bash
# 查看PR详情
gh pr view 42

# 在浏览器中查看PR
gh pr view 42 --web

# 仅查看PR状态
gh pr view 42 --json state

# 查看PR的diff
gh pr diff 42

# 查看PR的commits
gh pr commits 42
```

**中文释义**：让我仔细看看第42号PR的详情！

**终端输出示例：**

```
标题：添加新功能
状态：OPEN
分支：feature/new-feature -> main
作者：yourname
标签：enhancement

这是一个很棒的新功能描述...
```

## 第六章：Issue管理篇

### 6.1 创建Issue

```bash
# 交互式创建Issue
gh issue create

# 指定标题和描述创建Issue
gh issue create --title "Bug report" --body "Description of the bug"

# 创建Issue并分配给某人
gh issue create --assignee username

# 创建Issue并添加标签
gh issue create --label bug,urgent

# 创建Issue并关联里程碑
gh issue create --milestone "v1.0"

# 从文件读取Issue内容
gh issue create --title "Bug" --body-file issue-content.md
```

**中文释义**：报告一个问题或建议！

**终端输出示例：**

```
? Title: 发现一个bug
? Body: <Received> [Enter to launch editor]
? What's next? Submit
✓ Created issue #123
```

### 6.2 查看Issue列表

```bash
# 查看所有开放的Issue
gh issue list

# 查看关闭的Issue
gh issue list --state closed

# 查看分配给我的Issue
gh issue list --assignee @me

# 查看由我创建的Issue
gh issue list --author @me

# 按标签筛选Issue
gh issue list --label bug

# 按里程碑筛选Issue
gh issue list --milestone "v1.0"

# 搜索Issue
gh issue list --search "bug sort:updated"

# 限制返回结果数量
gh issue list --limit 20

# 以JSON格式输出
gh issue list --json number,title,state,assignees
```

**中文释义**：看看项目有哪些待解决的问题！

**终端输出示例：**

```
#123  发现一个bug      bug
#122  功能建议        enhancement
```

### 6.3 关闭Issue

```bash
# 关闭Issue
gh issue close 123

# 关闭Issue并添加注释
gh issue close 123 --comment "Fixed in PR #456"

# 重新打开Issue
gh issue reopen 123
```

**中文释义**：这个问题已经解决了！

**终端输出示例：**

```
✓ Closed issue #123
```

### 6.4 管理Issue评论

```bash
# 查看Issue评论
gh issue comment 123 --list

# 添加评论
gh issue comment 123 --body "This looks good to me"

# 添加多行评论
gh issue comment 123 --body-file comment.txt
```

## 第七章：高级协作篇

### 7.1 代码审查

```bash
# 对PR进行审查
gh pr review 42

# 批准PR
gh pr review 42 --approve

# 请求修改
gh pr review 42 --request-changes

# 评论PR而不批准
gh pr review 42 --comment

# 添加审查评论
gh pr review 42 --body "Looks good, but consider adding tests"
```

**中文释义**：我要对PR进行代码审查！

**终端输出示例：**

```
? Review type: Approve
? Review comment: Great work! LGTM ✓
✓ Submitted review
```

### 7.2 合并Pull Request

```bash
# 合并PR
gh pr merge 42

# 合并PR并删除分支
gh pr merge 42 --delete-branch

# Squash并合并
gh pr merge 42 --squash

# Rebase并合并
gh pr merge 42 --rebase

# 创建合并提交
gh pr merge 42 --merge

# 合并时自定义提交信息
gh pr merge 42 --subject "Custom merge message"
```

**中文释义**：把这个PR合并到主分支！

**终端输出示例：**

```
? Merge method: Create a merge commit
? Delete branch: Yes
✓ Merged pull request #42
```

### 7.3 检查CI状态

```bash
# 检查PR的CI状态
gh pr checks 42

# 检查特定检查的状态
gh pr checks 42 --watch

# 列出所有检查
gh pr checks 42 --list
```

**中文释义**：看看CI测试通过了没？

**终端输出示例：**

```
✓ CI Tests passed
✓ CodeQL Analysis completed
```

### 7.4 管理项目

```bash
# 查看项目板
gh project list

# 查看项目中的条目
gh project item-list

# 创建项目卡
gh project item-create
```

## 第八章：日常开发工作流

### 8.1 功能开发完整流程

```bash
# 1. 更新主分支
git checkout main
git pull origin main

# 2. 创建功能分支
git checkout -b feature/awesome-feature

# 3. 开发代码...
# 编辑文件，实现功能

# 4. 提交更改
git add .
git commit -m "实现超棒的新功能"

# 5. 推送到远程
git push origin feature/awesome-feature

# 6. 创建Pull Request
gh pr create --title "添加超棒新功能" --body "功能描述..."

# 7. 等待审查和合并
# 根据审查意见进行修改
git add .
git commit --amend
git push --force-with-lease

# 8. 合并后清理
git checkout main
git pull origin main
git branch -d feature/awesome-feature
```

### 8.2 Bug修复流程

```bash
# 1. 从主分支创建修复分支
git checkout main
git pull origin main
git checkout -b bugfix/critical-issue

# 2. 修复bug...
# 编辑相关文件

# 3. 提交修复
git add .
git commit -m "修复严重问题"

# 4. 推送并创建紧急PR
git push origin bugfix/critical-issue
gh pr create --title "紧急修复：严重问题" --body "修复描述..."

# 5. 请求快速审查
gh pr comment 45 --body "请优先审查这个紧急修复"

# 6. 合并后清理
gh pr merge 45 --delete-branch
git checkout main
git pull origin main
git branch -d bugfix/critical-issue
```

### 8.3 版本发布流程

```bash
# 1. 确保主分支是最新的
git checkout main
git pull origin main

# 2. 创建发布分支
git checkout -b release/v1.2.0

# 3. 更新版本号
# 编辑 package.json 或其他版本文件

# 4. 提交版本更新
git add .
git commit -m "Bump version to 1.2.0"

# 5. 创建标签
git tag -a v1.2.0 -m "Release version 1.2.0"

# 6. 推送标签和分支
git push origin release/v1.2.0
git push origin v1.2.0

# 7. 在GitHub上创建Release
gh release create v1.2.0 --title "Version 1.2.0" --notes "Release notes here"

# 8. 合并回主分支
git checkout main
git merge release/v1.2.0
git push origin main

# 9. 清理发布分支
git branch -d release/v1.2.0
git push origin --delete release/v1.2.0
```

## 第九章：实用技巧篇

### 9.1 快速打开GitHub页面

```bash
# 在浏览器中打开当前仓库
gh repo view --web

# 在浏览器中打开特定文件
gh browse path/to/file.js

# 在浏览器中打开特定行
gh browse path/to/file.js#L10-L20

# 在浏览器中打开特定提交
gh browse commit-sha

# 在浏览器中打开Issues
gh browse --issues

# 在浏览器中打开PR
gh browse --pull-requests
```

**中文释义**：在浏览器中打开这个仓库！

**终端输出示例：**

```
✓ 在浏览器中打开 https://github.com/username/repo
```

### 9.2 查看仓库Star数

```bash
# 查看Star数
gh api repos/username/repo --jq '.stargazers_count'

# 查看Fork数
gh api repos/username/repo --jq '.forks_count'

# 查看Watcher数
gh api repos/username/repo --jq '.subscribers_count'

# 获取完整的仓库统计信息
gh api repos/username/repo --jq '{name:.name,stars:.stargazers_count,forks:.forks_count}'
```

**中文释义**：看看我的项目有多少人Star了！

**终端输出示例：**

```
42
```

### 9.3 创建Gist

```bash
# 创建公开Gist
gh gist create script.py

# 创建私有Gist
gh gist create --private script.py

# 从stdin创建Gist
cat script.py | gh gist create

# 创建包含多个文件的Gist
gh gist create file1.txt file2.txt

# 添加描述
gh gist create script.py --desc "My useful script"
```

**中文释义**：分享这个代码片段！

**终端输出示例：**

```
✓ 创建Gist：https://gist.github.com/1a2b3c4d5e
```

### 9.4 文件操作技巧

```bash
# 查看文件历史
git log --follow filename.txt

# 查看文件的修改者和时间
git blame filename.txt

# 恢复文件到特定版本
git checkout commit-sha -- filename.txt

# 比较分支间文件差异
git diff branch1..branch2 -- filename.txt

# 查找包含特定内容的文件
git grep "search-term"

# 查找历史中删除的文件
git log --diff-filter=D --summary
```

## 第十章：故障排除篇

### 10.1 认证问题

```bash
# 检查登录状态
gh auth status

# 列出所有认证主机
gh auth list

# 更新认证令牌
gh auth refresh

# 使用SSH而非HTTPS
git config --global url."git@github.com:".insteadOf "https://github.com/"
```

**终端输出示例：**

```
github.com
  ✓ 已登录为 yourname (/Users/you/.config/gh/hosts.yml)
  ✓ Git 操作认证：已配置
  ✓ Token: gho_************************************
```

### 10.2 同步问题

```bash
# 强制同步远程更改
gh repo sync --force

# 手动同步远程分支
git fetch origin
git reset --hard origin/main

# 解决合并冲突
git mergetool

# 放弃本地更改
git reset --hard HEAD

# 撤销最后一次提交但仍保留更改
git reset --soft HEAD~1
```

### 10.3 查看gh配置

```bash
# 查看所有配置
gh config list

# 查看特定配置项
gh config get git_protocol

# 设置配置项
gh config set editor vim

# 查看Git配置
git config --global --list
```

**终端输出示例：**

```
git_protocol: https
editor: vim
prompt: enabled
```

### 10.4 处理大文件

```bash
# 使用Git LFS处理大文件
git lfs install
git lfs track "*.psd"
git add .gitattributes
git add file.psd
git commit -m "Add large PSD file"
git push origin main
```

## 第十一章：别名和快捷方式

### 11.1 Git别名设置

```bash
# 常用Git别名
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.unstage 'reset HEAD --'

# 日志相关的别名
git config --global alias.lg "log --oneline --decorate --all --graph"
git config --global alias.last 'log -1 HEAD'

# 常用组合命令别名
git config --global alias.cm '!git add -A && git commit -m'
git config --global alias.alias "! git config --get-regexp ^alias\. | sed -e s/^alias\.// -e s/\ /\ =\ /"
```

### 11.2 gh别名设置

```bash
# 常用gh别名
gh alias set prs "pr list"
gh alias set issues "issue list"
gh alias set mine "pr list --author @me"
gh alias set review "pr list --review-requested @me"

# 复杂的gh别名
gh alias set co-pr "pr checkout"
gh alias set create-pr "pr create --web"
gh alias set release-latest "release list --limit 1"
```

### 11.3 常用组合命令

**快速开发流程：**

```bash
# 一键完成提交和PR创建
git add . && git commit -m "更新" && git push && gh pr create

# 快速同步主分支
git checkout main && git pull && git branch --merged | grep -v "\*\|main\|master" | xargs -n 1 git branch -d
```

**检查我的工作：**

```bash
# 查看我所有的PR和Issue
gh pr list --author @me && gh issue list --author @me

# 查看待办事项
gh issue list --assignee @me && gh pr list --review-requested @me
```

## 第十二章：实战场景示例

### 12.1 参与开源项目

```bash
# 1. Fork仓库（在GitHub网页操作）
# 2. 克隆自己Fork的仓库
gh repo clone myname/project

# 3. 添加上游仓库
git remote add upstream https://github.com/original/project

# 4. 同步最新代码
git fetch upstream
git checkout main
git merge upstream/main

# 5. 创建特性分支
git checkout -b feature/contribution

# 6. 贡献代码...
# 编辑文件

# 7. 提交更改
git add .
git commit -m "Add new feature"

# 8. 推送到自己的Fork
git push origin feature/contribution

# 9. 创建PR
gh pr create --repo original/project --title "Add new feature" --body "Description"
```

### 12.2 团队协作流程

```bash
# 晨会前检查任务
gh issue list --assignee @me
gh pr list --review-requested @me

# 开始新功能
gh issue create --title "新功能任务" --body "任务描述..." --assignee @me
git checkout -b feature/new-task

# 完成后提交审查
gh pr create --reviewer teammate1,teammate2 --assignee @me

# 团队成员审查代码
gh pr review 42 --comment --body "Consider edge cases"

# 根据反馈修改
git add .
git commit --amend
git push --force-with-lease

# 审查通过后合并
gh pr review 42 --approve
gh pr merge 42 --delete-branch
```

### 12.3 处理紧急修复

```bash
# 1. 基于最新的生产版本创建热修复分支
git fetch origin
git checkout -b hotfix/critical-bug origin/main

# 2. 实施修复
# 编辑文件

# 3. 提交修复
git add .
git commit -m "Hotfix: Fix critical bug"

# 4. 推送热修复分支
git push origin hotfix/critical-bug

# 5. 创建PR并标记为紧急
gh pr create --title "[URGENT] Hotfix for critical bug" --label urgent,bug

# 6. 通知团队成员紧急审查
gh pr comment --body "@team Please review this urgent fix immediately"

# 7. 合并后部署
gh pr merge --rebase
```

## 第十三章：最佳实践篇

### 13.1 提交信息规范

```
feat: 添加新功能
fix: 修复bug
docs: 文档更新
style: 代码格式调整（不影响代码运行的变动）
refactor: 重构（即不是新增功能，也不是修改bug的代码变动）
perf: 性能优化
test: 增加测试
chore: 构建过程或辅助工具的变动
revert: 回滚到上一个版本
merge: 合并分支
```

**提交信息格式：**

```
<type>(<scope>): <subject>
<BLANK LINE>
<body>
<BLANK LINE>
<footer>
```

**示例：**

```
feat(user): 添加用户登录功能

- 添加登录表单
- 实现JWT认证
- 添加登录验证

Close #123
```

### 13.2 分支命名规范

```
feature/用户登录功能              # 新功能开发
bugfix/修复支付问题              # Bug修复
hotfix/紧急生产问题              # 紧急生产问题修复
release/版本发布                # 发布版本
develop/实验性功能               # 实验性功能开发
docs/更新API文档                # 文档更新
```

### 13.3 PR描述模板

```markdown
## 变更描述
[简要描述这次PR的变更]

## 相关Issue
[关联的Issue编号，例如：Closes #123, Related to #456]

## 解决方案
[详细描述解决方案，包括技术选型、关键实现等]

## 测试验证
- [ ] 已进行单元测试
- [ ] 已进行集成测试
- [ ] 已进行端到端测试
- [ ] 已更新文档
- [ ] 已在不同环境下验证

## 性能影响
[如果有性能方面的变化，在此描述]

## 截图/屏幕录制
[如有UI变更，请提供截图]

## 其他信息
[任何其他相关信息]
```

### 13.4 代码审查检查清单

1. 代码是否符合项目编码规范？
2. 是否有足够的测试覆盖？
3. 是否存在潜在的安全问题？
4. 错误处理是否得当？
5. 代码是否易于理解和维护？
6. 是否有不必要的复杂性？
7. 注释是否清晰准确？
8. 是否考虑了边界情况？

## 第十四章：Git内部原理

### 14.1 Git对象模型

Git有四种基本对象类型：

1. **blob对象** - 存储文件数据
2. **tree对象** - 存储目录结构
3. **commit对象** - 存储提交信息
4. **tag对象** - 存储标签信息

### 14.2 Git引用

```bash
# 查看所有引用
git show-ref

# 查看分支引用
git show-ref refs/heads

# 查看远程引用
git show-ref refs/remotes

# 查看标签引用
git show-ref refs/tags
```

### 14.3 Git存储机制

```bash
# 查看对象内容
git cat-file -p <object-hash>

# 查看对象类型
git cat-file -t <object-hash>

# 计算对象hash
git hash-object <file>
```

### 14.4 Git索引

```bash
# 查看索引内容
git ls-files --stage

# 清空索引
git rm --cached .

# 重建索引
git add .
```

## 第十五章：高级GitHub CLI功能

### 15.1 自定义扩展

GitHub CLI支持通过外部程序扩展功能：

```bash
# 安装扩展
gh extension install owner/gh-extension

# 列出已安装扩展
gh extension list

# 升级扩展
gh extension upgrade owner/gh-extension

# 创建自己的扩展
gh extension create my-extension
```

### 15.2 使用GitHub API

```bash
# GET请求
gh api user

# POST请求
gh api --method POST repos/{owner}/{repo}/issues --field title='New issue'

# 使用jq处理响应
gh api repos/owner/repo --jq '.stargazers_count'

# 使用模板格式化输出
gh api repos/owner/repo --template '{{.stargazers_count}}'
```

### 15.3 环境变量

GitHub CLI支持多种环境变量：

```bash
# 设置GitHub主机
GH_HOST=github.example.com

# 设置认证令牌
GH_TOKEN=ghp_*****

# 设置编辑器
GH_EDITOR=vim

# 启用调试模式
GH_DEBUG=true
```

## 第十六章：企业级应用

### 16.1 GitHub Enterprise支持

```bash
# 配置企业实例
gh auth login --hostname github.company.com

# 在企业实例上工作
gh repo clone github.company.com/org/repo
```

### 16.2 安全最佳实践

```bash
# 扫描凭证泄露
git credential-manager-core erase
git credential-manager-core store

# 使用加密密钥
gh secret set MY_SECRET

# 查看仓库密钥
gh secret list
```

### 16.3 大规模项目管理

```bash
# 使用里程碑管理版本
gh release list

# 管理项目板
gh project list

# 批量操作Issue
gh issue list --label bug --state open | xargs -I {} gh issue close {}
```

## 🎯 结语

通过结合Git和GitHub CLI，你的开发工作流将变得更加高效和愉快。记住：

- Git 负责本地版本控制
- gh 负责与GitHub的交互
- 两者结合，天下无敌！

掌握这些工具不仅能提高个人效率，还能增强团队协作能力。持续学习和实践是精通这些工具的关键。

## 常用命令速查表

| 任务         | Git命令                          | gh命令                              |
| ------------ | -------------------------------- | ----------------------------------- |
| 克隆仓库     | `git clone url`                | `gh repo clone repo`              |
| 创建PR       | (多步骤)                         | `gh pr create`                    |
| 查看Issue    | (需打开浏览器)                   | `gh issue list`                   |
| 管理仓库     | (需手动操作)                     | `gh repo create`                  |
| 代码审查     | (需打开浏览器)                   | `gh pr review`                    |
| 查看状态     | `git status`                   | `gh status`                       |
| 推送代码     | `git push`                     | `gh repo sync`                    |
| 查看PR列表   | (需打开浏览器)                   | `gh pr list`                      |
| 创建Issue    | (需打开浏览器)                   | `gh issue create`                 |
| 查看PR详情   | (需打开浏览器)                   | `gh pr view`                      |
| 合并PR       | (需打开浏览器)                   | `gh pr merge`                     |
| 查看仓库信息 | `git remote show origin`       | `gh repo view`                    |
| 分支操作     | `git branch`, `git checkout` | (Git命令)                           |
| 查看历史     | `git log`                      | `gh history` (如果安装了相关扩展) |
