import libtorrent as lt

def test_libtorrent():
    try:
        # 创建会话
        session = lt.session()
        # 获取版本
        version = lt.version
        print(f"libtorrent 版本: {version}")
        return True
    except Exception as e:
        print(f"libtorrent 测试失败: {str(e)}")
        return False

if __name__ == "__main__":
    test_libtorrent() 