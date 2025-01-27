# Dota2 Quick Chat

一个轻量级的 Dota2 快捷文本工具，可以通过自定义快捷键快速复制预设文本到剪贴板。

## 功能特点

- 支持自定义文本和快捷键
- 全局快捷键监听
- 设置自动保存
- 跨平台支持 (Windows & macOS)

## 使用方法

1. 运行程序
2. 在输入框中输入要使用的文本
3. 点击快捷键输入框，设置快捷键组合
4. 点击"添加"按钮保存设置
5. 在游戏中按下设置的快捷键即可将对应文本复制到剪贴板

## 开发环境配置

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安装依赖
pip install PyQt6 keyboard pyinstaller

# 运行程序
python dota2_clipboard.py

# 打包程序
python build.py
```

## 注意事项

- 在 macOS 上首次运行时需要授予辅助功能权限
- 建议避免使用游戏中已有的快捷键
- 保存的设置存储在程序同目录下的 settings.json 文件中 