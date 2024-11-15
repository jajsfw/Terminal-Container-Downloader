import subprocess
import sys
import os
import platform

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 7):
        print("错误: Python版本必须 >= 3.7")
        return False
    return True

def install_requirements():
    """安装依赖包"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        print("正在安装依赖包...")
        
        # 读取requirements.txt
        with open('requirements.txt', 'r', encoding='utf-8') as f:
            requirements = f.read().splitlines()
        
        # 分别安装每个包
        for requirement in requirements:
            if requirement:
                print(f"正在安装 {requirement}")
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", requirement])
                except subprocess.CalledProcessError:
                    if 'python-libtorrent' in requirement:
                        print("尝试使用替代方法安装 libtorrent...")
                        # 尝试替代安装方法
                        alternate_packages = [
                            'libtorrent',
                            'deluge-libtorrent',
                            'lbry-libtorrent'
                        ]
                        for pkg in alternate_packages:
                            try:
                                subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
                                print(f"成功安装 {pkg}")
                                break
                            except subprocess.CalledProcessError:
                                continue
                    else:
                        print(f"警告: 安装 {requirement} 失败")
        
        print("依赖包安装完成")
        return True
        
    except Exception as e:
        print(f"安装依赖包时出错: {str(e)}")
        return False

def create_directories():
    """创建必要的目录"""
    directories = [
        'downloads',
        'plugins',
        'themes',
        'logs'
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"创建目录: {directory}")

def setup_environment():
    """设置环境变量"""
    if platform.system() == "Windows":
        # 添加当前目录到PATH
        os.environ["PATH"] = os.path.dirname(os.path.abspath(__file__)) + os.pathsep + os.environ["PATH"]

def main():
    print("开始安装多线程下载器...")
    
    if not check_python_version():
        return 1
        
    if not install_requirements():
        return 1
        
    create_directories()
    setup_environment()
    
    print("\n安装完成！")
    print("你可以通过运行 python run.py 来启动程序")
    
    # 询问是否立即启动程序
    response = input("\n是否立即启动程序？(y/n): ")
    if response.lower() == 'y':
        subprocess.call([sys.executable, "run.py"])
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 