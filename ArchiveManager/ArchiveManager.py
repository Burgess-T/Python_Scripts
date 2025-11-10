#!/usr/bin/env python3
import os
import re
import sys
import shutil
import subprocess
import time
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QCheckBox, QLineEdit, QTextEdit, QProgressBar, QFileDialog,
    QMessageBox, QGroupBox, QFormLayout, QDialog, QScrollArea, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QThread, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QIcon, QColor, QPalette, QPainter, QLinearGradient, QBrush, QPen
from PyQt5.QtCore import QPoint

class ModernStyle:
    """现代化UI样式定义"""
    # 主色调
    PRIMARY_COLOR = "#2563eb"      # 蓝色
    PRIMARY_DARK = "#1d4ed8"       # 深蓝色
    PRIMARY_LIGHT = "#3b82f6"      # 浅蓝色
    
    # 辅助色
    SUCCESS_COLOR = "#10b981"      # 绿色
    WARNING_COLOR = "#f59e0b"      # 黄色
    DANGER_COLOR = "#ef4444"       # 红色
    INFO_COLOR = "#3b82f6"         # 信息蓝色
    
    # 中性色
    BACKGROUND = "#f8fafc"         # 浅灰背景
    CARD_BACKGROUND = "#ffffff"    # 卡片背景
    BORDER_COLOR = "#e2e8f0"       # 边框颜色
    TEXT_COLOR = "#1e293b"         # 主文本
    TEXT_SECONDARY = "#64748b"     # 次要文本
    TEXT_PLACEHOLDER = "#94a3b8"   # 占位符文本
    
    # 阴影
    SHADOW_COLOR = "rgba(0, 0, 0, 0.1)"
    
    # 圆角
    BORDER_RADIUS = "8px"
    BUTTON_RADIUS = "6px"
    
    @staticmethod
    def apply_palette(app):
        """应用现代化调色板"""
        palette = app.palette()
        
        # 基础颜色
        palette.setColor(palette.Window, QColor(ModernStyle.BACKGROUND))
        palette.setColor(palette.WindowText, QColor(ModernStyle.TEXT_COLOR))
        palette.setColor(palette.Base, QColor(ModernStyle.CARD_BACKGROUND))
        palette.setColor(palette.AlternateBase, QColor("#f1f5f9"))
        palette.setColor(palette.ToolTipBase, QColor(ModernStyle.CARD_BACKGROUND))
        palette.setColor(palette.ToolTipText, QColor(ModernStyle.TEXT_COLOR))
        palette.setColor(palette.Text, QColor(ModernStyle.TEXT_COLOR))
        palette.setColor(palette.Button, QColor(ModernStyle.CARD_BACKGROUND))
        palette.setColor(palette.ButtonText, QColor(ModernStyle.TEXT_COLOR))
        palette.setColor(palette.BrightText, QColor(ModernStyle.DANGER_COLOR))
        palette.setColor(palette.Highlight, QColor(ModernStyle.PRIMARY_COLOR))
        palette.setColor(palette.HighlightedText, QColor(ModernStyle.CARD_BACKGROUND))
        
        app.setPalette(palette)

class CardWidget(QFrame):
    """卡片式容器"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("CardWidget")
        self.setStyleSheet(f"""
            #CardWidget {{
                background-color: {ModernStyle.CARD_BACKGROUND};
                border-radius: {ModernStyle.BORDER_RADIUS};
                border: 1px solid {ModernStyle.BORDER_COLOR};
                padding: 16px;
            }}
        """)
        self.setFrameShape(QFrame.NoFrame)

class AnimatedButton(QPushButton):
    """带动画效果的按钮"""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        
    def enterEvent(self, event):
        if hasattr(self, 'hover_style_str'):
            self.setStyleSheet(self.hover_style_str)
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        if hasattr(self, 'normal_style_str'):
            self.setStyleSheet(self.normal_style_str)
        super().leaveEvent(event)

class PrimaryButton(AnimatedButton):
    """主按钮"""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.normal_style_str = f"""
            QPushButton {{
                background-color: {ModernStyle.PRIMARY_COLOR};
                color: white;
                font-weight: 600;
                padding: 8px 20px;
                border-radius: {ModernStyle.BUTTON_RADIUS};
                border: none;
                min-width: 100px;
            }}
        """
        self.hover_style_str = f"""
            QPushButton {{
                background-color: {ModernStyle.PRIMARY_DARK};
                color: white;
                font-weight: 600;
                padding: 8px 20px;
                border-radius: {ModernStyle.BUTTON_RADIUS};
                border: none;
                min-width: 100px;
            }}
        """
        self.setStyleSheet(self.normal_style_str)

class DangerButton(AnimatedButton):
    """危险按钮"""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.normal_style = f"""
            QPushButton {{
                background-color: {ModernStyle.DANGER_COLOR};
                color: white;
                font-weight: 600;
                padding: 8px 20px;
                border-radius: {ModernStyle.BUTTON_RADIUS};
                border: none;
                min-width: 100px;
            }}
        """
        self.hover_style = f"""
            QPushButton {{
                background-color: #dc2626;
                color: white;
                font-weight: 600;
                padding: 8px 20px;
                border-radius: {ModernStyle.BUTTON_RADIUS};
                border: none;
                min-width: 100px;
            }}
        """
        self.setStyleSheet(self.normal_style)

class OutlineButton(AnimatedButton):
    """轮廓按钮"""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.normal_style = f"""
            QPushButton {{
                background-color: transparent;
                color: {ModernStyle.PRIMARY_COLOR};
                font-weight: 500;
                padding: 8px 20px;
                border-radius: {ModernStyle.BUTTON_RADIUS};
                border: 1px solid {ModernStyle.PRIMARY_COLOR};
                min-width: 100px;
            }}
        """
        self.hover_style = f"""
            QPushButton {{
                background-color: {ModernStyle.PRIMARY_COLOR};
                color: white;
                font-weight: 500;
                padding: 8px 20px;
                border-radius: {ModernStyle.BUTTON_RADIUS};
                border: 1px solid {ModernStyle.PRIMARY_COLOR};
                min-width: 100px;
            }}
        """
        self.setStyleSheet(self.normal_style)

class WorkerSignals(QObject):
    """定义工作线程的信号"""
    progress = pyqtSignal(int, int)  # current, total
    log = pyqtSignal(str)
    finished = pyqtSignal()
    error = pyqtSignal(str)

class UnzipWorker(QThread):
    """后台解压工作线程"""
    def __init__(self, folder_path, extract_to_folder, password, custom_formats, sevenzip_path, delete_after):
        super().__init__()
        self.folder_path = Path(folder_path)
        self.extract_to_folder = extract_to_folder
        self.password = password
        self.custom_formats = custom_formats
        self.sevenzip_path = Path(sevenzip_path) if sevenzip_path else None
        self.delete_after = delete_after
        self.signals = WorkerSignals()
        self._is_running = True
        self.current_process = None

    def stop(self):
        """停止解压"""
        self._is_running = False
        
        # 终止当前运行的进程
        if self.current_process and self.current_process.poll() is None:
            try:
                self.current_process.terminate()
                # 等待进程终止
                for _ in range(20):  # 最多等待2秒
                    if self.current_process.poll() is not None:
                        break
                    time.sleep(0.1)
                else:
                    # 如果进程仍未终止，强制杀死
                    self.current_process.kill()
            except Exception as e:
                print(f"终止进程时出错: {e}")

    def extract_archive(self, archive_path, output_dir, password=None):
        """使用7z解压单个归档文件"""
        if not self.sevenzip_path or not self.sevenzip_path.exists():
            self.signals.error.emit(f"7-Zip 路径无效: {self.sevenzip_path}")
            return False
            
        cmd = [str(self.sevenzip_path), 'x', '-y', '-o' + str(output_dir)]
        if password:
            cmd.append(f'-p{password}')
        cmd.append(str(archive_path))
        
        try:
            self.current_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            # 实时读取输出
            while True:
                if not self._is_running:
                    # 如果用户停止了操作，终止进程
                    self.current_process.terminate()
                    break
                    
                output = self.current_process.stdout.readline()
                if output:
                    self.signals.log.emit(f"  {output.strip()}")
                if self.current_process.poll() is not None:
                    break
            
            # 检查是否被用户停止
            if not self._is_running:
                return "stopped"
            
            stderr = self.current_process.stderr.read()
            if stderr:
                stderr_lower = stderr.lower()
                if 'wrong password' in stderr_lower or 'cannot open encrypted file' in stderr_lower:
                    self.signals.log.emit("  × 密码错误")
                    return False
                self.signals.log.emit(f"  × 错误: {stderr.strip()}")
                return False
            
            return True
        except Exception as e:
            self.signals.log.emit(f"  × 异常: {str(e)}")
            return False
        finally:
            self.current_process = None

    def get_supported_formats(self):
        """获取支持的压缩格式集合"""
        # 基础格式
        base_formats = {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.tgz', '.tbz2', '.txz'}
        
        # 分卷格式
        volume_formats = {'.001', '.z01', '.r00', '.r01', '.part1.rar', '.7z.001'}
        
        # 添加自定义格式
        custom_formats_set = set()
        if self.custom_formats:
            for fmt in self.custom_formats.split(','):
                fmt_clean = fmt.strip()
                if fmt_clean:
                    # 确保格式以点开头
                    if not fmt_clean.startswith('.'):
                        fmt_clean = '.' + fmt_clean
                    custom_formats_set.add(fmt_clean.lower())
        
        # 合并所有格式
        all_formats = base_formats.union(volume_formats).union(custom_formats_set)
        return all_formats

    def is_main_volume(self, filename, supported_formats):
        """识别分卷压缩的主文件（第一个分卷）"""
        name_lower = filename.lower()
        
        # 规则1: 标准分卷命名
        if re.search(r'\.(001|z01|r01|part0*1\.rar)$', name_lower):
            return True
        
        # 规则2: RAR传统分卷
        if name_lower.endswith('.rar') and not re.search(r'\.[r-z]\d\d$', name_lower):
            return True
        
        # 规则3: 7z/zip分卷
        if re.search(r'\.(7z|zip)\.001$', name_lower):
            return True
        
        # 规则4: 非分卷压缩文件
        # 检查是否是支持的非分卷格式
        for fmt in supported_formats:
            if name_lower.endswith(fmt):
                # 排除分卷文件
                if not re.search(r'\.[zr]\d\d$', name_lower) and not name_lower.endswith('.002'):
                    # 检查是否是自定义格式
                    if fmt not in {'.001', '.z01', '.r00', '.r01'}:
                        return True
        
        return False

    def get_clean_name(self, filename):
        """移除所有压缩扩展名，获取干净的基础名称"""
        patterns = [
            r'\.part\d+\.rar$',
            r'\.\d{3}$',
            r'\.[zr]\d\d$',
            r'\.(7z|zip|tar|gz|bz2|xz|rar|tgz|tbz2|txz)$'
        ]
        name = Path(filename).stem
        for pattern in patterns:
            name = re.sub(pattern, '', name, flags=re.IGNORECASE)
        return name

    def get_volume_files(self, archive_path):
        """获取分卷集中的所有文件"""
        stem = archive_path.stem
        suffix = archive_path.suffix
        
        # 获取基础名称（移除分卷标识）
        base_name = re.sub(r'(\.part\d+)?(\.\d{3}|[zr]\d\d)?$', '', stem, flags=re.IGNORECASE)
        
        volume_files = []
        dir_path = archive_path.parent
        
        # 定义所有可能的分卷扩展名模式
        patterns = [
            r'\.part\d+\.rar$',
            r'\.\d{3}$',
            r'\.[zr]\d\d$',
            r'\.7z\.\d{3}$',
            r'\.zip\.\d{3}$'
        ]
        
        # 检查目录中的所有文件
        for file in dir_path.iterdir():
            if file.is_file():
                file_name = file.name.lower()
                
                # 检查是否以基础名称开头
                if file_name.startswith(base_name.lower()):
                    # 检查是否符合分卷模式
                    for pattern in patterns:
                        if re.search(pattern, file_name):
                            volume_files.append(file)
                            break
        
        # 添加主文件（如果不在列表中）
        if archive_path not in volume_files:
            volume_files.append(archive_path)
            
        return volume_files

    def delete_archive_files(self, archive_path):
        """删除归档文件及其分卷"""
        # 获取所有相关文件
        files_to_delete = self.get_volume_files(archive_path)
        
        # 尝试删除每个文件
        deleted_files = []
        failed_files = []
        
        for file in files_to_delete:
            try:
                if file.exists():
                    file.unlink()
                    deleted_files.append(file.name)
            except Exception as e:
                failed_files.append((file.name, str(e)))
        
        # 记录结果
        if deleted_files:
            self.signals.log.emit(f"  ✓ 已删除 {len(deleted_files)} 个文件: {', '.join(deleted_files)}")
        if failed_files:
            for name, error in failed_files:
                self.signals.log.emit(f"  × 无法删除 {name}: {error}")

    def run(self):
        """主工作流程"""
        if not self.sevenzip_path or not self.sevenzip_path.exists():
            self.signals.error.emit(
                f"7-Zip 程序不存在！\n\n"
                f"当前路径: {self.sevenzip_path}\n\n"
                f"请在设置中重新指定 7-Zip 路径。"
            )
            return

        archives = []
        processed_volumes = set()
        supported_formats = self.get_supported_formats()
        
        self.signals.log.emit(f"✓ 支持的格式: {', '.join(sorted(supported_formats))}")
        
        # 1. 收集所有主分卷文件
        for file in self.folder_path.iterdir():
            if not self._is_running:
                return
                
            if file.is_file():
                file_ext = file.suffix.lower()
                # 检查是否是支持的格式
                if any(file.name.lower().endswith(fmt) for fmt in supported_formats):
                    if self.is_main_volume(file.name, supported_formats):
                        volume_id = re.sub(r'(\.part\d+)?(\.\d{3}|[zr]\d\d)?$', '', file.stem, flags=re.IGNORECASE)
                        if volume_id not in processed_volumes:
                            archives.append(file)
                            processed_volumes.add(volume_id)
        
        if not archives:
            self.signals.error.emit("未找到有效的压缩文件或分卷主文件")
            self.signals.finished.emit()
            return
        
        self.signals.log.emit(f"✓ 找到 {len(archives)} 个压缩文件/分卷集")
        self.signals.progress.emit(0, len(archives))
        
        # 2. 逐个解压
        for i, archive in enumerate(archives):
            if not self._is_running:
                break
                
            self.signals.log.emit(f"\n📦 处理: {archive.name}")
            
            # 确定输出目录
            if self.extract_to_folder:
                clean_name = self.get_clean_name(archive.name)
                output_dir = self.folder_path / clean_name
                output_dir.mkdir(exist_ok=True)
                self.signals.log.emit(f"  → 解压到文件夹: {clean_name}/")
            else:
                output_dir = self.folder_path
            
            # 3. 尝试解压
            password = self.password if self.password else None
            
            result = self.extract_archive(archive, output_dir, password)
            
            if result is True:
                self.signals.log.emit(f"  ✓ 解压成功: {archive.name}")
                
                # 4. 如果启用删除选项，删除原文件
                if self.delete_after:
                    self.delete_archive_files(archive)
            elif result == "stopped":
                self.signals.log.emit("  × 解压已被用户停止")
                break
            else:
                self.signals.log.emit("  × 解压失败，跳过此文件")
            
            self.signals.progress.emit(i + 1, len(archives))
        
        self.signals.finished.emit()

class SettingsDialog(QDialog):
    """现代化设置对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.setMinimumSize(550, 300)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint | Qt.WindowTitleHint)
        
        # 设置窗口图标
        self.setWindowIcon(parent.windowIcon() if parent else QIcon())
        
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 20, 30, 20)
        main_layout.setSpacing(20)
        
        # 标题
        title_label = QLabel("⚙️ 7-Zip 配置")
        title_label.setFont(QFont("Microsoft YaHei", 16, QFont.Bold))
        title_label.setStyleSheet(f"color: {ModernStyle.TEXT_COLOR};")
        main_layout.addWidget(title_label)
        
        # 7-Zip 路径设置
        path_frame = CardWidget()
        path_layout = QVBoxLayout(path_frame)
        path_layout.setContentsMargins(15, 15, 15, 15)
        path_layout.setSpacing(15)
        
        desc_label = QLabel("指定 7-Zip 程序路径以启用解压功能")
        desc_label.setStyleSheet(f"color: {ModernStyle.TEXT_SECONDARY}; font-size: 13px;")
        path_layout.addWidget(desc_label)
        
        # 路径输入
        input_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("例如: C:\\Program Files\\7-Zip\\7z.exe")
        self.path_input.setStyleSheet(f"""
            QLineEdit {{
                padding: 8px 12px;
                border: 1px solid {ModernStyle.BORDER_COLOR};
                border-radius: {ModernStyle.BUTTON_RADIUS};
                font-family: Consolas;
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border: 1px solid {ModernStyle.PRIMARY_COLOR};
                box-shadow: 0 0 0 2px {ModernStyle.PRIMARY_LIGHT};
            }}
        """)
        
        browse_btn = OutlineButton("浏览")
        browse_btn.setFixedWidth(80)
        browse_btn.clicked.connect(self.browse_sevenzip)
        
        input_layout.addWidget(self.path_input, 1)
        input_layout.addWidget(browse_btn)
        path_layout.addLayout(input_layout)
        
        # 测试按钮
        test_btn = PrimaryButton("测试连接")
        test_btn.setFixedWidth(120)
        test_btn.clicked.connect(self.test_sevenzip)
        path_layout.addWidget(test_btn, alignment=Qt.AlignLeft)
        
        main_layout.addWidget(path_frame)
        
        # 按钮区域
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.save_btn = PrimaryButton("保存设置")
        self.save_btn.setFixedWidth(120)
        self.save_btn.clicked.connect(self.accept)
        
        cancel_btn = OutlineButton("取消")
        cancel_btn.setFixedWidth(100)
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(self.save_btn)
        btn_layout.addStretch()
        
        main_layout.addLayout(btn_layout)
        
        # 加载当前设置
        self.load_settings()
    
    def browse_sevenzip(self):
        """浏览选择 7-Zip 程序"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择 7-Zip 程序",
            "C:\\Program Files\\7-Zip\\",
            "7-Zip 程序 (7z.exe);;所有文件 (*.*)"
        )
        if file_path:
            self.path_input.setText(file_path)
    
    def test_sevenzip(self):
        """测试 7-Zip 路径"""
        path = self.path_input.text().strip()
        if not path:
            QMessageBox.warning(self, "警告", "请先指定 7-Zip 路径")
            return
            
        path_obj = Path(path)
        if not path_obj.exists():
            QMessageBox.critical(self, "错误", f"路径不存在: {path}")
            return
            
        try:
            result = subprocess.run([path, 'i'], capture_output=True, text=True, 
                                  creationflags=subprocess.CREATE_NO_WINDOW, timeout=5)
            if result.returncode == 0:
                QMessageBox.information(self, "成功", f"7-Zip 连接成功!\n")
            else:
                QMessageBox.critical(self, "错误", f"7-Zip 测试失败:\n{result.stderr}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法测试 7-Zip:\n{str(e)}")
    
    def load_settings(self):
        """加载设置"""
        # 尝试从注册表或配置文件加载，这里使用默认值
        default_paths = [
            r"C:\Program Files\7-Zip\7z.exe",
            r"C:\Program Files (x86)\7-Zip\7z.exe",
            shutil.which('7z.exe')
        ]
        
        for path in default_paths:
            if path and Path(path).exists():
                self.path_input.setText(path)
                break
    
    def get_path(self):
        """获取设置的路径"""
        return self.path_input.text().strip()

class UnzipGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ArchiveMaster - 智能解压工具")
        self.setMinimumSize(800, 650)
        self.setWindowIcon(self.get_app_icon())
        
        # 7-Zip 路径
        self.sevenzip_path = self.find_sevenzip_default()
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(30, 20, 30, 20)
        main_layout.setSpacing(25)
        
        # 标题区域
        title_layout = QVBoxLayout()
        title_layout.setSpacing(8)
        
        app_title = QLabel("ArchiveMaster")
        app_title.setFont(QFont("Microsoft YaHei", 24, QFont.Bold))
        app_title.setStyleSheet(f"color: {ModernStyle.PRIMARY_COLOR};")
        
        app_subtitle = QLabel("智能批量解压工具 - 支持分卷文件处理")
        app_subtitle.setFont(QFont("Microsoft YaHei", 12))
        app_subtitle.setStyleSheet(f"color: {ModernStyle.TEXT_SECONDARY};")
        
        title_layout.addWidget(app_title)
        title_layout.addWidget(app_subtitle)
        main_layout.addLayout(title_layout)
        
        # 配置卡片
        config_card = CardWidget()
        config_layout = QVBoxLayout(config_card)
        config_layout.setContentsMargins(25, 20, 25, 20)
        config_layout.setSpacing(20)
        
        # 配置标题
        config_title = QLabel("🔄 解压配置")
        config_title.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        config_layout.addWidget(config_title)
        
        # 配置表单
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(0, 0, 0, 0)
        
        # 工作目录
        folder_layout = QHBoxLayout()
        self.folder_path = os.getcwd()
        self.folder_label = QLabel(self.folder_path)
        self.folder_label.setWordWrap(True)
        self.folder_label.setFont(QFont("Consolas", 10))
        self.folder_label.setStyleSheet(f"""
            color: {ModernStyle.TEXT_SECONDARY};
            background-color: {ModernStyle.BACKGROUND};
            padding: 6px 10px;
            border-radius: {ModernStyle.BUTTON_RADIUS};
            border: 1px solid {ModernStyle.BORDER_COLOR};
        """)
        
        folder_btn = OutlineButton("选择目录")
        folder_btn.setFixedWidth(100)
        folder_btn.clicked.connect(self.select_folder)
        
        folder_layout.addWidget(self.folder_label, 1)
        folder_layout.addWidget(folder_btn)
        form_layout.addRow("工作目录:", folder_layout)
        
        # 7-Zip 配置
        sevenzip_layout = QHBoxLayout()
        self.sevenzip_label = QLabel(self.sevenzip_path or "未配置")
        self.sevenzip_label.setWordWrap(True)
        self.sevenzip_label.setFont(QFont("Consolas", 10))
        status_color = ModernStyle.SUCCESS_COLOR if self.sevenzip_path else ModernStyle.DANGER_COLOR
        self.sevenzip_label.setStyleSheet(f"""
            color: {status_color};
            background-color: {ModernStyle.BACKGROUND};
            padding: 6px 10px;
            border-radius: {ModernStyle.BUTTON_RADIUS};
            border: 1px solid {ModernStyle.BORDER_COLOR};
            font-weight: 500;
        """)
        
        sevenzip_btn = OutlineButton("配置")
        sevenzip_btn.setFixedWidth(80)
        sevenzip_btn.clicked.connect(self.open_settings)
        
        sevenzip_layout.addWidget(self.sevenzip_label, 1)
        sevenzip_layout.addWidget(sevenzip_btn)
        form_layout.addRow("7-Zip 状态:", sevenzip_layout)
        
        # 选项
        options_layout = QVBoxLayout()
        options_layout.setSpacing(8)
        
        self.extract_folder_cb = QCheckBox("解压到同名文件夹 (推荐)")
        self.extract_folder_cb.setChecked(True)
        self.extract_folder_cb.setStyleSheet(f"""
            QCheckBox {{
                font-size: 13px;
                color: {ModernStyle.TEXT_COLOR};
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 1px solid {ModernStyle.BORDER_COLOR};
            }}
            QCheckBox::indicator:checked {{
                background-color: {ModernStyle.PRIMARY_COLOR};
                border: 1px solid {ModernStyle.PRIMARY_COLOR};
                image: url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMiIgaGVpZ2h0PSIxMiIgdmlld0JveD0iMCAwIDEyIDEyIj48cGF0aCBmaWxsPSJ3aGl0ZSIgZD0iTTQgNi41bC0xLjUtMS41TDEgN2wzIDMgNy03LTEuNS0xLjV6Ii8+PC9zdmc+);
            }}
        """)
        
        self.delete_after_cb = QCheckBox("解压后删除原文件及其分卷")
        self.delete_after_cb.setStyleSheet(f"""
            QCheckBox {{
                font-size: 13px;
                color: {ModernStyle.DANGER_COLOR};
                font-weight: 500;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 1px solid {ModernStyle.BORDER_COLOR};
            }}
            QCheckBox::indicator:checked {{
                background-color: {ModernStyle.DANGER_COLOR};
                border: 1px solid {ModernStyle.DANGER_COLOR};
                image: url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMiIgaGVpZ2h0PSIxMiIgdmlld0JveD0iMCAwIDEyIDEyIj48cGF0aCBmaWxsPSJ3aGl0ZSIgZD0iTTQgNi41bC0xLjUtMS41TDEgN2wzIDMgNy03LTEuNS0xLjV6Ii8+PC9zdmc+);
            }}
        """)
        
        options_layout.addWidget(self.extract_folder_cb)
        options_layout.addWidget(self.delete_after_cb)
        form_layout.addRow("解压选项:", options_layout)
        
        # 密码输入
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("留空则跳过加密文件")
        self.password_input.setStyleSheet(f"""
            QLineEdit {{
                padding: 8px 12px;
                border: 1px solid {ModernStyle.BORDER_COLOR};
                border-radius: {ModernStyle.BUTTON_RADIUS};
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border: 1px solid {ModernStyle.PRIMARY_COLOR};
                box-shadow: 0 0 0 2px {ModernStyle.PRIMARY_LIGHT};
            }}
        """)
        form_layout.addRow("全局密码:", self.password_input)
        
        # 自定义格式
        self.custom_formats_input = QLineEdit()
        self.custom_formats_input.setPlaceholderText("例如: .rar删, .zip删, .7z删 (用逗号分隔)")
        self.custom_formats_input.setStyleSheet(f"""
            QLineEdit {{
                padding: 8px 12px;
                border: 1px solid {ModernStyle.BORDER_COLOR};
                border-radius: {ModernStyle.BUTTON_RADIUS};
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border: 1px solid {ModernStyle.PRIMARY_COLOR};
                box-shadow: 0 0 0 2px {ModernStyle.PRIMARY_LIGHT};
            }}
        """)
        form_layout.addRow("自定义格式:", self.custom_formats_input)
        
        config_layout.addLayout(form_layout)
        main_layout.addWidget(config_card)
        
        # 日志区域
        log_card = CardWidget()
        log_layout = QVBoxLayout(log_card)
        log_layout.setContentsMargins(20, 15, 20, 15)
        log_layout.setSpacing(15)
        
        # 日志标题
        log_title_layout = QHBoxLayout()
        log_title = QLabel("📝 操作日志")
        log_title.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        log_title_layout.addWidget(log_title)
        
        clear_btn = OutlineButton("清空日志")
        clear_btn.setFixedWidth(80)
        clear_btn.setStyleSheet(f"""
            QPushButton {{
                padding: 4px 8px;
                min-width: 60px;
                font-size: 12px;
            }}
        """)
        clear_btn.clicked.connect(lambda: self.log_text.clear())
        log_title_layout.addWidget(clear_btn)
        log_title_layout.addStretch()
        log_layout.addLayout(log_title_layout)
        
        # 日志文本
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 10))
        self.log_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {ModernStyle.BACKGROUND};
                border: 1px solid {ModernStyle.BORDER_COLOR};
                border-radius: {ModernStyle.BORDER_RADIUS};
                padding: 12px;
                font-family: Consolas;
                font-size: 12px;
                color: {ModernStyle.TEXT_COLOR};
            }}
        """)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setFormat("准备解压...")
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {ModernStyle.BORDER_COLOR};
                border-radius: {ModernStyle.BUTTON_RADIUS};
                text-align: center;
                height: 24px;
                font-size: 12px;
                font-weight: 500;
            }}
            QProgressBar::chunk {{
                background-color: {ModernStyle.PRIMARY_COLOR};
                border-radius: {ModernStyle.BUTTON_RADIUS};
            }}
        """)
        
        log_layout.addWidget(self.log_text, 1)
        log_layout.addWidget(self.progress_bar)
        main_layout.addWidget(log_card, 1)
        
        # 操作按钮区域
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.start_btn = PrimaryButton("🚀 开始解压")
        self.start_btn.setFixedHeight(45)
        self.start_btn.setFont(QFont("Microsoft YaHei", 11, QFont.Bold))
        self.start_btn.clicked.connect(self.start_extraction)
        
        self.stop_btn = DangerButton("⏹️ 停止")
        self.stop_btn.setFixedHeight(45)
        self.stop_btn.setFont(QFont("Microsoft YaHei", 11, QFont.Bold))
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_extraction)
        
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn, 10)
        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)
        
        # 状态栏
        self.status_bar = self.statusBar()
        self.status_bar.setStyleSheet(f"""
            QStatusBar {{
                background-color: {ModernStyle.CARD_BACKGROUND};
                border-top: 1px solid {ModernStyle.BORDER_COLOR};
                padding: 4px 15px;
                font-size: 12px;
                color: {ModernStyle.TEXT_SECONDARY};
            }}
        """)
        self.status_bar.showMessage(f"就绪 | 当前目录: {self.folder_path}")
        
        # 初始化工作线程
        self.worker = None
        
        # 添加初始日志
        self.log_message("🎉 欢迎使用 ArchiveMaster 智能解压工具")
        self.log_message(f"📁 当前工作目录: {self.folder_path}")
        self.log_message(f"🔧 7-Zip 状态: {'✓ 已配置' if self.sevenzip_path else '✗ 未配置'}")
        
        if not self.sevenzip_path:
            self.log_message("⚠️  提示: 请先配置 7-Zip 路径以启用解压功能")
            self.status_bar.showMessage("⚠️  7-Zip 未配置 - 请在设置中指定路径")
        else:
            self.log_message("✅ 7-Zip 配置正常，准备就绪")
        
        self.log_message("\n💡 使用提示:")
        self.log_message("• 点击'开始解压'处理当前目录下所有压缩文件")
        self.log_message("• 支持自动识别分卷文件，无需手动选择")
        self.log_message("• 可在'自定义格式'中添加特殊扩展名进行处理\n")
    
    def get_app_icon(self):
        """获取应用程序图标"""
        from PyQt5.QtGui import QPixmap, QPainter, QColor
        from PyQt5.QtCore import Qt
        
        # 创建一个简单的现代图标
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制背景
        painter.setBrush(QColor(ModernStyle.PRIMARY_COLOR))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(4, 4, 56, 56, 12, 12)
        
        # 绘制文件图标
        painter.setBrush(Qt.white)
        painter.drawRect(20, 15, 24, 28)
        
        # 绘制折角
        painter.setBrush(QColor(200, 200, 200))
        painter.drawPolygon([
          QPoint(36, 15),
          QPoint(44, 15),
          QPoint(36, 23)
        ])
        
        # 绘制压缩符号
        painter.setPen(QColor(ModernStyle.PRIMARY_COLOR))
        painter.setBrush(Qt.NoBrush)
        painter.setFont(QFont("Arial", 10, QFont.Bold))
        painter.drawText(28, 40, "ZIP")
        
        painter.end()
        
        return QIcon(pixmap)
    
    def find_sevenzip_default(self):
        """查找默认的 7-Zip 路径"""
        # 检查PATH中的7z
        path = shutil.which('7z.exe')
        if path:
            return path
            
        # 检查默认安装路径
        default_paths = [
            r"C:\Program Files\7-Zip\7z.exe",
            r"C:\Program Files (x86)\7-Zip\7z.exe",
            os.path.expanduser(r"~\AppData\Local\Programs\7-Zip\7z.exe")
        ]
        
        for path in default_paths:
            if Path(path).exists():
                return path
                
        return None

    def select_folder(self):
        """选择工作目录"""
        folder = QFileDialog.getExistingDirectory(
            self, 
            "选择工作目录", 
            str(Path.home()),
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        if folder:
            self.folder_path = folder
            self.folder_label.setText(folder)
            self.status_bar.showMessage(f"📁 已选择目录: {folder}")
            self.log_message(f"\n📁 已切换到工作目录: {folder}")
    
    def open_settings(self):
        """打开设置对话框"""
        settings_dialog = SettingsDialog(self)
        if settings_dialog.exec_() == QDialog.Accepted:
            path = settings_dialog.get_path()
            if path:
                self.sevenzip_path = path
                self.sevenzip_label.setText(path)
                self.sevenzip_label.setStyleSheet(f"""
                    color: {ModernStyle.SUCCESS_COLOR};
                    background-color: {ModernStyle.BACKGROUND};
                    padding: 6px 10px;
                    border-radius: {ModernStyle.BUTTON_RADIUS};
                    border: 1px solid {ModernStyle.BORDER_COLOR};
                    font-weight: 500;
                """)
                self.status_bar.showMessage(f"✅ 7-Zip 路径已更新: {path}")
                self.log_message(f"\n✅ 7-Zip 配置成功: {path}")
    
    def start_extraction(self):
        """开始解压过程"""
        if self.worker and self.worker.isRunning():
            QMessageBox.warning(self, "警告", "解压任务已在进行中!")
            return
        
        # 验证7-Zip
        if not self.sevenzip_path or not Path(self.sevenzip_path).exists():
            reply = QMessageBox.question(
                self, 
                "7-Zip 未配置", 
                "7-Zip 路径未配置或不存在，无法进行解压操作。\n\n"
                "是否前往配置 7-Zip 路径？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                self.open_settings()
                return
            else:
                QMessageBox.critical(self, "错误", "必须配置有效的 7-Zip 路径才能继续")
                return
        
        # 获取配置
        extract_to_folder = self.extract_folder_cb.isChecked()
        password = self.password_input.text().strip() or None
        custom_formats = self.custom_formats_input.text().strip()
        delete_after = self.delete_after_cb.isChecked()
        
        # 删除确认
        if delete_after:
            reply = QMessageBox.warning(
                self, 
                "⚠️  确认删除操作", 
                "您已选择'解压后删除原文件及其分卷'选项！\n\n"
                "⚠️  此操作不可逆，且会永久删除所有关联的分卷文件。\n"
                "是否继续执行此操作？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return
        
        # 创建并启动工作线程
        self.worker = UnzipWorker(
            self.folder_path,
            extract_to_folder,
            password,
            custom_formats,
            self.sevenzip_path,
            delete_after
        )
        
        # 连接信号
        self.worker.signals.progress.connect(self.update_progress)
        self.worker.signals.log.connect(self.log_message)
        self.worker.signals.finished.connect(self.extraction_finished)
        self.worker.signals.error.connect(self.handle_error)
        
        # 更新UI状态
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setFormat("正在解压...")
        self.status_bar.showMessage("🔄 正在解压文件...")
        self.log_message(f"\n{'='*60}\n✅ 开始解压任务\n{'='*60}")
        
        # 启动线程
        self.worker.start()
    
    def stop_extraction(self):
        """停止解压过程"""
        if self.worker and self.worker.isRunning():          
            # 停止工作线程
            self.worker.stop()
            self.status_bar.showMessage("⏹️  正在停止解压任务...")
            self.log_message("\n⏹️  正在停止解压任务...")
            self.stop_btn.setEnabled(False)
            
            # 使用定时器检查线程是否已停止
            QTimer.singleShot(1000, self.check_thread_stopped)
    
    def check_thread_stopped(self):
        """检查线程是否已停止"""
        if self.worker and self.worker.isRunning():
            # 如果线程仍在运行，再次尝试停止
            self.worker.stop()
            QTimer.singleShot(500, self.check_thread_stopped)
        else:
            # 线程已停止，更新UI
            self.extraction_finished()
    
    def update_progress(self, current, total):
        """更新进度条"""
        if total > 0:
            progress = int((current / total) * 100)
            self.progress_bar.setValue(progress)
            self.progress_bar.setFormat(f"解压中: {current}/{total} ({progress}%)")
            self.status_bar.showMessage(f"🔄 解压中: {current}/{total} 个文件 | 目录: {self.folder_path}")
    
    def log_message(self, message):
        """添加日志消息"""
        # 根据消息内容设置不同颜色
        if message.startswith("✓") or message.startswith("✅"):
            colored_message = f'<span style="color: {ModernStyle.SUCCESS_COLOR};">{message}</span>'
        elif message.startswith("×") or message.startswith("✗") or message.startswith("⚠️"):
            colored_message = f'<span style="color: {ModernStyle.DANGER_COLOR};">{message}</span>'
        elif message.startswith("→") or message.startswith("📦"):
            colored_message = f'<span style="color: {ModernStyle.INFO_COLOR};">{message}</span>'
        else:
            colored_message = message
        
        self.log_text.append(colored_message)
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )
    
    def handle_error(self, message):
        """处理错误"""
        QMessageBox.critical(self, "错误", message)
        self.log_message(f"\n✗ 错误: {message}")
        self.status_bar.showMessage(f"❌ 操作失败 - {message}")
    
    def extraction_finished(self):
        """解压完成处理"""
        # 恢复UI状态
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        
        # 检查是否是正常完成还是被停止
        if self.worker and self.worker._is_running:
            self.progress_bar.setFormat("解压完成 ✓")
            self.progress_bar.setValue(100)
            self.log_message(f"\n{'='*60}\n✅ 所有解压任务已完成\n{'='*60}")
            self.status_bar.showMessage("✅ 解压完成 | 就绪")
            
            # 显示完成动画
            self.start_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {ModernStyle.SUCCESS_COLOR};
                    color: white;
                    font-weight: bold;
                    font-size: 14px;
                    padding: 8px 16px;
                    border-radius: {ModernStyle.BUTTON_RADIUS};
                }}
            """)
            QTimer.singleShot(2000, lambda: self.start_btn.setStyleSheet(self.start_btn.normal_style_str))
            
            QMessageBox.information(
                self, 
                "🎉 任务完成", 
                "所有解压任务已成功完成！\n\n"
                "查看日志了解详细结果。"
            )
        else:
            self.progress_bar.setFormat("已停止 ⏹️")
            self.progress_bar.setValue(0)
            self.log_message(f"\n{'='*60}\n⏹️  解压任务已被用户停止\n{'='*60}")
            self.status_bar.showMessage("⏹️  解压已停止 | 就绪")
            
            QMessageBox.information(
                self, 
                "⏹️  任务已停止", 
                "解压任务已被手动停止！\n\n"
                "部分文件可能已解压完成，"
                "您可以在日志中查看详细进度。"
            )
        
        self.worker = None

if __name__ == "__main__":
    # 设置Windows DPI感知
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
    
    app = QApplication(sys.argv)
    
    # 应用现代化样式
    ModernStyle.apply_palette(app)
    
    # 设置全局字体
    font = QFont("Microsoft YaHei", 9)
    app.setFont(font)
    
    # 添加全局样式表
    app.setStyleSheet("""
        QMainWindow {
            background-color: #f8fafc;
        }
        QGroupBox {
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            margin-top: 1ex;
            font-weight: bold;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }
        QScrollArea {
            border: none;
            background: transparent;
        }
        QScrollBar:vertical {
            border: none;
            background: #f1f5f9;
            width: 10px;
            margin: 0px 0px 0px 0px;
        }
        QScrollBar::handle:vertical {
            background: #cbd5e1;
            min-height: 20px;
            border-radius: 5px;
        }
        QScrollBar::handle:vertical:hover {
            background: #94a3b8;
        }
    """)
    
    # 创建并显示主窗口
    window = UnzipGUI()
    window.show()
    
    sys.exit(app.exec_())