# -*- coding: utf-8 -*-
from fpdf import FPDF
import os

# Find a CJK font on Windows
font_dir = r"C:\Windows\Fonts"
font_path = os.path.join(font_dir, "msyh.ttc")  # Microsoft YaHei
if not os.path.exists(font_path):
    font_path = os.path.join(font_dir, "simsun.ttc")
if not os.path.exists(font_path):
    font_path = os.path.join(font_dir, "simhei.ttf")


class PDF(FPDF):
    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("CJK", "", 8)
        self.set_text_color(150, 160, 175)
        self.cell(0, 8, "ClipboardManager — 静默剪贴板管理器", align="R")
        self.ln(12)
        self.set_draw_color(220, 225, 235)
        self.set_line_width(0.3)
        self.line(20, self.get_y(), 190, self.get_y())
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font("CJK", "", 8)
        self.set_text_color(150, 160, 175)
        self.cell(0, 10, f"— {self.page_no()} —", align="C")

    def section_title(self, title):
        self.ln(4)
        self.set_font("CJK", "B", 15)
        self.set_text_color(30, 60, 120)
        self.cell(0, 10, title)
        self.ln(8)
        # Accent line
        self.set_fill_color(80, 160, 255)
        self.rect(20, self.get_y(), 40, 2, style="F")
        self.ln(6)

    def body_text(self, text):
        self.set_font("CJK", "", 10.5)
        self.set_text_color(55, 60, 70)
        self.multi_cell(0, 6.5, text)
        self.ln(2)

    def bullet(self, text):
        self.set_font("CJK", "", 10.5)
        self.set_text_color(55, 60, 70)
        x = self.get_x()
        self.set_text_color(80, 160, 255)
        self.cell(6, 6.5, "•")
        self.set_text_color(55, 60, 70)
        self.multi_cell(0, 6.5, text)
        self.ln(1)

    def kv_table(self, rows):
        for k, v in rows:
            self.set_font("CJK", "B", 10)
            self.set_text_color(40, 50, 70)
            self.cell(50, 7, k, border=0)
            self.set_font("CJK", "", 10)
            self.set_text_color(80, 85, 95)
            self.cell(0, 7, v, border=0)
            self.ln(8)

    def quote_box(self, text):
        self.set_fill_color(240, 245, 252)
        self.set_draw_color(80, 160, 255)
        self.set_line_width(0.5)
        x = self.get_x()
        y = self.get_y()
        self.set_font("CJK", "I", 11)
        self.set_text_color(50, 70, 110)
        self.multi_cell(0, 7, f"  {text}", fill=True)
        self.ln(4)

    def code_block(self, text):
        self.set_fill_color(245, 246, 250)
        self.set_font("Courier", "", 9)
        self.set_text_color(60, 70, 90)
        for line in text.split("\n"):
            self.cell(0, 5.5, f"  {line}", fill=True)
            self.ln(5.5)
        self.ln(3)


pdf = PDF()
pdf.add_font("CJK", "", font_path)
pdf.add_font("CJK", "B", font_path)
pdf.add_font("CJK", "I", font_path)
pdf.set_auto_page_break(auto=True, margin=20)
pdf.set_margins(20, 20, 20)

# ======== Page 1: Cover ========
pdf.add_page()
pdf.set_y(60)
pdf.set_font("CJK", "B", 36)
pdf.set_text_color(30, 60, 120)
pdf.cell(0, 18, "ClipboardManager", align="C")
pdf.ln(22)

pdf.set_font("CJK", "", 18)
pdf.set_text_color(80, 100, 130)
pdf.cell(0, 12, "静默剪贴板管理器", align="C")
pdf.ln(20)

# Decorative line
pdf.set_draw_color(80, 160, 255)
pdf.set_line_width(1)
mid = 105
pdf.line(mid - 30, pdf.get_y(), mid + 30, pdf.get_y())
pdf.ln(10)

pdf.set_font("CJK", "", 12)
pdf.set_text_color(120, 130, 145)
pdf.cell(0, 8, "轻量 · 优雅 · 常驻后台", align="C")
pdf.ln(6)
pdf.cell(0, 8, "支持文本的剪贴板历史管理工具", align="C")

pdf.ln(40)
pdf.set_font("CJK", "", 10)
pdf.set_text_color(160, 165, 175)
pdf.cell(0, 7, "作者：征酱", align="C")
pdf.ln(7)
pdf.cell(0, 7, "技术栈：Python 3.14 + PySide6 (Qt6) + PyInstaller", align="C")

# ======== Page 2: Product Overview ========
pdf.add_page()
pdf.section_title("产品简介")
pdf.quote_box("安静地帮你记住每一次复制。")
pdf.ln(2)
pdf.body_text(
    "ClipboardManager 是一款桌面剪贴板历史管理工具，支持文本的自动记录与快速恢复。"
    "程序静默常驻系统托盘，按快捷键即可唤出搜索面板，无需切换窗口即可从历史记录中查找并粘贴之前复制过的内容。"
)
pdf.ln(2)
pdf.body_text(
    "灵感源自 Windows 自带的 Win+V 剪贴板历史，但提供了更灵活的自定义能力和更精致的视觉体验。"
    "半透明毛玻璃风格界面，圆角边框，自动采集屏幕背景模糊渲染，兼具美观与实用。"
)

# ======== Page 3: Core Features ========
pdf.add_page()
pdf.section_title("核心功能")

pdf.set_font("CJK", "B", 12)
pdf.set_text_color(40, 50, 70)
pdf.cell(0, 8, "1. 剪贴板历史记录")
pdf.ln(9)
pdf.bullet("自动捕获每一次文本复制操作")
pdf.bullet("默认保存 200 条，可在设置中调整（10 — 10000 条）")

pdf.ln(2)
pdf.set_font("CJK", "B", 12)
pdf.set_text_color(40, 50, 70)
pdf.cell(0, 8, "2. 快速搜索")
pdf.ln(9)
pdf.bullet("输入关键词即时过滤历史记录")
pdf.bullet("Enter 恢复选中项到剪贴板，Esc 清空并收起")

pdf.ln(2)
pdf.set_font("CJK", "B", 12)
pdf.set_text_color(40, 50, 70)
pdf.cell(0, 8, "3. 全局快捷键")
pdf.ln(9)
pdf.kv_table([("Ctrl + Shift + V", "唤出 / 收起搜索面板（任意应用中全局生效）")])

# ======== Page 4: More Features ========
pdf.add_page()
pdf.section_title("更多功能")

pdf.set_font("CJK", "B", 12)
pdf.set_text_color(40, 50, 70)
pdf.cell(0, 8, "4. 平滑下拉动画")
pdf.ln(9)
pdf.bullet("展开 / 收起列表时采用 280ms 平滑缓动动画")
pdf.bullet("OutCubic 展开，InCubic 收起，自然流畅")

pdf.ln(2)
pdf.set_font("CJK", "B", 12)
pdf.set_text_color(40, 50, 70)
pdf.cell(0, 8, "5. 设置面板")
pdf.ln(9)
pdf.kv_table([
    ("最大储存条数", "超出上限自动清除最早记录（10 — 10000）"),
    ("储存位置", "自定义数据存放路径（重启后生效）"),
    ("开机自启动", "勾选后随 Windows 启动自动运行"),
    ("显示关闭按钮", "勾选后状态栏出现 X 按钮，点击退出程序"),
])

pdf.ln(2)
pdf.set_font("CJK", "B", 12)
pdf.set_text_color(40, 50, 70)
pdf.cell(0, 8, "6. 系统托盘")
pdf.ln(9)
pdf.bullet("程序常驻系统托盘，右键菜单提供完整操作")
pdf.bullet("显示 / 隐藏搜索框、清空全部历史、开机自启、退出")

# ======== Page 5: Usage ========
pdf.add_page()
pdf.section_title("使用方法")

pdf.set_font("CJK", "B", 12)
pdf.set_text_color(40, 50, 70)
pdf.cell(0, 8, "基本流程")
pdf.ln(9)

steps = [
    ("1. 启动程序", "双击 ClipboardManager.exe，程序静默启动并驻留系统托盘"),
    ("2. 正常复制", "在任意应用中 Ctrl+C 复制文本，内容自动记录"),
    ("3. 唤出面板", "按下 Ctrl+Shift+V，搜索面板从屏幕右下角弹出"),
    ("4. 查找内容", "在搜索框输入关键词过滤，或直接浏览列表"),
    ("5. 恢复内容", "点击列表项或按 Enter，内容恢复到剪贴板，即可 Ctrl+V 粘贴"),
    ("6. 收起面板", "按 Esc 或再次按 Ctrl+Shift+V"),
]
for title, desc in steps:
    pdf.set_font("CJK", "B", 10.5)
    pdf.set_text_color(30, 60, 120)
    pdf.cell(0, 7, title)
    pdf.ln(7)
    pdf.set_font("CJK", "", 10)
    pdf.set_text_color(80, 85, 95)
    pdf.multi_cell(0, 6, f"     {desc}")
    pdf.ln(2)

pdf.ln(2)
pdf.set_font("CJK", "B", 12)
pdf.set_text_color(40, 50, 70)
pdf.cell(0, 8, "窗口拖拽")
pdf.ln(9)
pdf.bullet("搜索栏左侧有拖拽手柄，按住可将面板拖动到屏幕任意位置，位置自动记忆")

# ======== Page 6: Data & Tech ========
pdf.add_page()
pdf.section_title("数据存储")
pdf.kv_table([
    ("配置文件", "%APPDATA%\\ClipboardManager\\config.json"),
    ("窗口位置", "%APPDATA%\\ClipboardManager\\window_pos.json"),
    ("历史记录", "数据目录下的 history.json"),
])
pdf.ln(2)
pdf.body_text("默认数据目录为程序所在目录，可在设置中修改。")

pdf.ln(4)
pdf.section_title("技术栈")
pdf.bullet("Python 3.14 + PySide6 (Qt6) GUI 框架")
pdf.bullet("PyInstaller 打包为单文件 exe，无需安装 Python 环境")
pdf.bullet("全局热键通过 Windows API (RegisterHotKey) 注册")
pdf.bullet("界面采用 QPainter 自定义绘制，毛玻璃模糊效果")

# ======== Page 7: Notes & Summary ========
pdf.add_page()
pdf.section_title("注意事项")
pdf.bullet("首次运行时 Windows SmartScreen 可能拦截，点击「仍要运行」即可")
pdf.bullet("开机自启动通过注册表 HKCU\\...\\Run 实现，不含任何后台联网行为")
pdf.bullet("程序不联网、不上传任何数据，所有记录保存在本地")

pdf.ln(8)
pdf.section_title("总结")
pdf.quote_box("ClipboardManager — 安静地帮你记住每一次复制。")
pdf.ln(2)
pdf.body_text(
    "轻量、优雅、常驻后台，支持文本的完整剪贴板历史管理。"
    "平滑动画、灵活设置、全局快捷键，完全本地化运行，零隐私泄露风险。"
    "适合所有需要频繁复制粘贴的 Windows 用户。"
)

# Save
output = r"C:\Users\Administrator\Desktop\ClipboardManager产品介绍.pdf"
pdf.output(output)
print(f"PDF saved: {output}")
