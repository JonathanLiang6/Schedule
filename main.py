#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
课程表管理系统 - 主程序入口
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import main

if __name__ == '__main__':
    """
    主程序入口
    """
    print("启动课程表管理系统...")
    main()