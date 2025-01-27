import os
import sys
import platform
import subprocess
import shutil
import argparse


def run_command(command, description):
    """运行命令并处理输出"""
    print(f"\n执行命令: {' '.join(command)}")
    try:
        result = subprocess.run(command, capture_output=True, text=True)
        if result.stdout:
            print("输出:")
            print(result.stdout)
        if result.stderr:
            print("错误:")
            print(result.stderr)
        if result.returncode != 0:
            print(f"命令执行失败，返回码: {result.returncode}")
            return False
        return True
    except Exception as e:
        print(f"执行出错: {str(e)}")
        return False


def build_macos():
    """构建 macOS 版本"""
    print("\n=== 开始构建 macOS 版本 ===")

    # 检查 PyInstaller 是否安装
    try:
        import PyInstaller
        print(f"PyInstaller 版本: {PyInstaller.__version__}")
    except ImportError:
        print("错误: PyInstaller 未安装，正在安装...")
        if not run_command(['pip', 'install', 'pyinstaller'], "安装 PyInstaller"):
            return False

    base_command = [
        'pyinstaller',
        '--name=Dota2本色风情',
        '--windowed',
        '--onefile',
        '--clean',
        '--add-data=delicon.svg:.',
        '--noconfirm',
        '--distpath=./dist',
        '--workpath=./build',
        '--specpath=.',
        'dota2_clipboard.py'
    ]

    if not run_command(base_command, "构建 macOS 应用"):
        return False

    if not os.path.exists('dist/Dota2本色风情.app'):
        print("错误: 应用程序未能成功构建")
        return False

    print("macOS 应用程序已构建完成: dist/Dota2本色风情.app")
    return create_dmg()


def build_windows():
    """构建 Windows 版本"""
    print("\n=== 开始构建 Windows 版本 ===")

    # 创建 Windows 运行时钩子
    create_windows_runtime_hook()

    base_command = [
        'pyinstaller',
        '--name=Dota2本色风情',
        '--windowed',
        '--onefile',
        '--clean',
        '--add-data=delicon.svg:.',  # Windows 使用冒号
        '--noconfirm',
        '--runtime-hook=windows_runtime_hook.py',
        '--distpath=./dist',
        '--workpath=./build',
        '--specpath=.',
        'dota2_clipboard.py'
    ]

    if not run_command(base_command, "构建 Windows 应用"):
        return False

    if not os.path.exists('dist/Dota2本色风情.exe'):
        print("错误: Windows 可执行文件未能成功构建")
        return False

    print("Windows 可执行文件已构建完成: dist/Dota2本色风情.exe")
    return True


def create_dmg():
    """创建 DMG 文件"""
    try:
        # 检查是否存在旧的 DMG 文件
        dmg_name = "Dota2本色风情.dmg"
        if os.path.exists(dmg_name):
            os.remove(dmg_name)

        # 检查源文件是否存在
        if not os.path.exists('dist/Dota2本色风情.app'):
            print("错误: 找不到源应用程序")
            return False

        # 创建 DMG
        result = subprocess.run([
            'hdiutil', 'create',
            '-volname', 'Dota2本色风情',
            '-srcfolder', 'dist/Dota2本色风情.app',
            '-ov', '-format', 'UDZO',
            dmg_name
        ], capture_output=True, text=True)

        if result.returncode != 0:
            print(f"创建 DMG 失败: {result.stderr}")
            return False

        if not os.path.exists(dmg_name):
            print("错误: DMG 文件未能成功创建")
            return False

        print(f"DMG 安装包已创建: {dmg_name}")
        return True
    except Exception as e:
        print(f"创建 DMG 文件时出错: {e}")
        return False


def create_windows_runtime_hook():
    """创建 Windows 运行时钩子"""
    try:
        with open('windows_runtime_hook.py', 'w', encoding='utf-8') as f:
            f.write("""
import os
import sys

# 确保资源文件路径正确
def runtime_hook():
    if getattr(sys, 'frozen', False):
        # 运行于打包环境
        bundle_dir = sys._MEIPASS
    else:
        # 运行于开发环境
        bundle_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 设置工作目录
    os.chdir(bundle_dir)
""")
        return True
    except Exception as e:
        print(f"创建运行时钩子文件时出错: {e}")
        return False


def clean_build():
    """清理构建文件"""
    print("\n=== 清理旧的构建文件 ===")
    try:
        for dir_name in ['build', 'dist']:
            if os.path.exists(dir_name):
                shutil.rmtree(dir_name)
                print(f"已删除: {dir_name}/")

        for file_name in ['windows_runtime_hook.py', 'Dota2本色风情.spec']:
            if os.path.exists(file_name):
                os.remove(file_name)
                print(f"已删除: {file_name}")

        # 确保目录存在
        os.makedirs('dist', exist_ok=True)
        os.makedirs('build', exist_ok=True)
        return True
    except Exception as e:
        print(f"清理文件时出错: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='打包 Dota2本色风情 应用程序')
    parser.add_argument('--platform', choices=['all', 'macos', 'windows'],
                        default='all', help='选择打包平台')
    args = parser.parse_args()

    # 显示当前工作目录
    print(f"当前工作目录: {os.getcwd()}")
    print(f"Python 版本: {sys.version}")
    print(f"操作系统: {platform.platform()}")

    # 检查必要文件
    if not os.path.exists('dota2_clipboard.py'):
        print("错误: 找不到主程序文件 dota2_clipboard.py")
        return
    if not os.path.exists('delicon.svg'):
        print("错误: 找不到图标文件 delicon.svg")
        return

    # 清理旧的构建文件
    if not clean_build():
        return

    success = True

    if args.platform in ['all', 'macos']:
        if not build_macos():
            success = False

    if args.platform in ['all', 'windows']:
        # 清理 macOS 构建产物
        if os.path.exists('dist'):
            shutil.rmtree('dist')
            os.makedirs('dist', exist_ok=True)
        if not build_windows():
            success = False

    if success:
        print("\n=== 打包完成 ===")
        print("文件位置:")
        if args.platform in ['all', 'macos']:
            print("- macOS DMG: ./Dota2本色风情.dmg")
        if args.platform in ['all', 'windows']:
            print("- Windows EXE: ./dist/Dota2本色风情.exe")
    else:
        print("\n=== 打包过程中出现错误 ===")


if __name__ == "__main__":
    main()
