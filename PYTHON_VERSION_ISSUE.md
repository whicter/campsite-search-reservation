# Python 版本兼容性问题

## 问题描述

在安装项目依赖时，如果使用 **Python 3.14**（或其他太新的版本），会遇到以下错误：

### 错误 1：Pydantic 版本冲突
```
ERROR: Cannot install -r requirements.txt because these package versions have conflicting dependencies.

The conflict is caused by:
    The user requested pydantic==2.5.3
    fastapi 0.109.0 depends on pydantic>=1.7.4,<3.0.0
    camply 0.15.0 depends on pydantic<2.0,>=1.2
```

**原因：** camply 要求 pydantic 1.x，但原始配置使用了 pydantic 2.x

### 错误 2：pandas 编译失败
```
Building wheel for pandas (pyproject.toml) ... error
error: command '/usr/bin/clang' failed with exit code 1

In file included from pandas/_libs/algos.c:808:
pandas/_libs/src/klib/khash_python.h:140:36: error: member reference base type 'khcomplex128_t' (aka '_Complex double') is not a structure or union
```

**原因：** pandas 1.3.5（camply 的依赖）不支持 Python 3.14，编译时出现兼容性错误

## 根本原因

**Python 3.14 太新了**，很多流行的库还没有适配，包括：
- pandas（通过 camply 的依赖）
- 其他可能的 C 扩展库

## 解决方案

有三种方案可以解决这个问题：

---

### 方案 1：使用 Homebrew 安装多个 Python 版本（简单）

**优点：**
- 简单直接
- 不影响全局 Python 版本
- 多个版本共存

**步骤：**

1. 安装 Python 3.12（不会改变全局版本）：
```bash
brew install python@3.12
```

2. 验证安装：
```bash
python3 --version      # 仍然是 3.14
python3.12 --version   # 新安装的 3.12
```

3. 删除旧虚拟环境并用 Python 3.12 创建新的：
```bash
cd /Users/cohan/Documents/campsite-search-resevation/backend
rm -rf campsite-env
/opt/homebrew/bin/python3.12 -m venv campsite-env
source campsite-env/bin/activate
pip install -r requirements.txt
```

**结果：**
- 全局 `python3` 仍指向 3.14（不变）
- 项目虚拟环境使用 3.12
- 两个版本共存

---

### 方案 2：使用 pyenv 管理 Python 版本（推荐，专业）

**优点：**
- 专业的 Python 版本管理工具
- 可以安装任何 Python 版本（包括 2.x）
- 每个项目可以指定不同的 Python 版本
- 全局版本不受影响

**步骤：**

1. 安装 pyenv：
```bash
brew install pyenv
```

2. 配置 shell（添加到 ~/.zshrc 或 ~/.bash_profile）：
```bash
# pyenv configuration
export PYENV_ROOT="$HOME/.pyenv"
[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
```

3. 重新加载 shell 配置：
```bash
source ~/.zshrc  # 或 source ~/.bash_profile
```

4. 安装 Python 3.12：
```bash
pyenv install 3.12.7
```

5. 为当前项目设置 Python 版本：
```bash
cd /Users/cohan/Documents/campsite-search-resevation
pyenv local 3.12.7
```

这会在项目目录创建 `.python-version` 文件，pyenv 会自动使用指定版本。

6. 创建虚拟环境：
```bash
cd backend
rm -rf campsite-env
python -m venv campsite-env  # 自动使用 Python 3.12
source campsite-env/bin/activate
pip install -r requirements.txt
```

**pyenv 常用命令：**
```bash
pyenv versions              # 查看已安装的 Python 版本
pyenv install --list        # 查看可安装的 Python 版本
pyenv install 3.11.9        # 安装特定版本
pyenv global 3.12.7         # 设置全局默认版本
pyenv local 3.12.7          # 设置当前目录使用的版本
```

**为什么需要 Python 2？**
如果有老项目需要 Python 2：
```bash
pyenv install 2.7.18
cd /path/to/old/project
pyenv local 2.7.18
```

---

### 方案 3：使用 conda/miniconda

**优点：**
- 强大的包管理和环境管理
- 同时管理 Python 版本和依赖
- 适合数据科学项目

**步骤：**

1. 安装 miniconda：
```bash
brew install miniconda
```

2. 初始化 conda：
```bash
conda init zsh  # 或 conda init bash
```

3. 创建带指定 Python 版本的环境：
```bash
conda create -n campsite python=3.12
conda activate campsite
cd /Users/cohan/Documents/campsite-search-resevation/backend
pip install -r requirements.txt
```

4. 使用环境：
```bash
conda activate campsite    # 激活环境
conda deactivate          # 退出环境
```

---

## 推荐方案对比

| 方案 | 适用场景 | 难度 | 优点 | 缺点 |
|------|---------|------|------|------|
| Homebrew 多版本 | 简单项目，偶尔需要切换版本 | ⭐ | 简单直接 | 手动指定路径 |
| pyenv | **推荐**，需要管理多个 Python 版本 | ⭐⭐ | 专业，自动切换 | 需要配置 |
| conda | 数据科学项目 | ⭐⭐ | 功能强大 | 占用空间大 |

## 本项目使用的方案

本项目使用 **pyenv（方案 2）**。

**项目配置：**
- Python 版本：3.12.7
- 版本文件：`.python-version`（由 pyenv 自动管理）
- 虚拟环境：`backend/campsite-env`

**验证安装：**
```bash
# 检查项目 Python 版本
cd /Users/cohan/Documents/campsite-search-resevation
python --version  # 应该显示 Python 3.12.7

# 检查虚拟环境 Python 版本
cd backend
source campsite-env/bin/activate
python --version  # 应该显示 Python 3.12.7
```

## 依赖版本说明

修改后的 `requirements.txt` 使用宽松版本要求，避免依赖冲突：

```txt
fastapi>=0.100.0,<1.0.0     # 兼容 pydantic 1.x
uvicorn[standard]>=0.20.0
pydantic>=1.10.0,<2.0.0     # camply 要求 <2.0
python-dotenv>=1.0.0
camply>=0.15.0
requests>=2.31.0
beautifulsoup4>=4.12.0
lxml>=4.9.0
python-multipart>=0.0.6
```

**关键约束：**
- `pydantic>=1.10.0,<2.0.0` - camply 需要 pydantic 1.x

## 如何避免类似问题

1. **不要使用太新的 Python 版本** - 等待 3-6 个月让生态系统适配
2. **使用 Python 3.11 或 3.12** - 目前最稳定且广泛支持
3. **使用版本管理工具** - pyenv 或 conda
4. **检查依赖兼容性** - 使用 `pip-compile` 或 `poetry` 锁定版本

## 常见问题

**Q: 安装 pyenv 会影响我现有的 Python 吗？**
A: 不会。pyenv 不会修改系统 Python，所有版本都安装在 `~/.pyenv` 目录下。

**Q: 如果我需要切换回 Python 3.14 怎么办？**
A:
```bash
pyenv local 3.14.0  # 或者删除 .python-version 文件
```

**Q: 虚拟环境能改变 Python 版本吗？**
A: 不能。虚拟环境使用创建时的 Python 版本，无法在虚拟环境内改变。

**Q: 为什么不直接升级 camply 以支持 pydantic 2.x？**
A: camply 0.15.0 是当前稳定版本，尚未支持 pydantic 2.x。等待官方更新或使用兼容版本。

## 更新日志

- **2024-12-30**: 发现 Python 3.14 兼容性问题
- **2024-12-30**: 采用 pyenv + Python 3.12.7 解决
- **2024-12-30**: 更新 requirements.txt 为宽松版本约束
