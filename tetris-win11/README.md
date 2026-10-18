# 星落 · Win11 俄罗斯方块

中文桌面增强版，支持 Windows 11 x64。Python 标准库 Tkinter 界面，无第三方运行依赖。提供三档难度、按难度保存最高分、系统音效开关、暂停、重新开始、下一个方块预览、落点轮廓和切出窗口自动暂停。

## 下载与运行

打开仓库 Actions → **Tetris Windows executable** → 最新绿色成功记录 → Artifacts → **TetrisWin11-Windows-x64**。登录 GitHub 后下载 ZIP，全部解压，双击 `TetrisWin11.exe`。无需安装 Python。构建产物受 GitHub 保留期限限制；过期后可 Run workflow 重新生成。

源码运行：安装包含 Tcl/Tk 的 Python 3.12，在 `tetris-win11` 目录执行 `py -3 main.py`。
本地打包：在 Windows 双击 `build.bat`；首次安装打包依赖需要网络，成功后得到 `dist\TetrisWin11.exe`。

## 操作与规则

| 按键 | 作用 |
| --- | --- |
| ← → / A D | 左右移动 |
| ↑ / W / X | 顺时针旋转 |
| Z | 逆时针旋转 |
| ↓ / S | 加速下降 |
| 空格 | 直接落底 |
| P / Esc | 暂停、继续 |
| R / Enter | 开始、重新开始 |

棋盘 10×20，七种方块使用七袋随机法，每袋各一种。旋转支持简化的墙边和地面偏移，并非完整 SRS。方块无法下降时立即固定，无锁定延迟。出生位置被占满即结束。

一次消除 1/2/3/4 行分别获得 100/300/500/800 × 当前等级分；手动下降每格 1 分，直接落底每格 2 分。每消除 10 行升一级。简单/普通/困难初始下落间隔为 800/550/330 毫秒，升级后乘以 0.85，最低 75 毫秒。

最高分保存在 `%LOCALAPPDATA%\TetrisWin11\scores.json`，与贪吃蛇分开。存档损坏会按空记录读取，无法写入时界面提示。音效采用 Windows 系统声音，取决于系统音量及声音方案。

## 每个文件的作用

| 文件 | 作用 |
| --- | --- |
| `main.py` | 程序入口、中文桌面窗口、键盘操作、绘制、定时下落、暂停及系统音效。 |
| `engine.py` | 独立游戏规则：方块、随机袋、移动旋转、碰撞、固定、消行、计分、升级和结束判定。 |
| `storage.py` | 读取、校验和原子替换最高分存档，明确使用 UTF-8。 |
| `tests/test_game.py` | 自动验证随机袋、边界、旋转及失败恢复、消行、计分、结束与存档容错。 |
| `requirements-build.txt` | 固定 PyInstaller 版本，仅供制作 exe 使用。 |
| `build.bat` | Windows 一键创建虚拟环境、安装打包工具、测试并生成 exe。 |
| `.gitignore` | 排除缓存、虚拟环境及本地打包产物。 |
| `README.md` | 下载、运行、操作、规则和文件说明，即本文档。 |
| 仓库根目录 `.github/workflows/tetris-windows.yml` | GitHub Windows 自动测试、打包、exe 启动检查及上传下载包。 |

运行 `py -3 -m unittest discover -s tests -v` 执行规则和存档测试。CI 在 Windows 上执行同样测试并检查打包程序能持续运行 8 秒；实际 Win11 的显示、操作手感、声音仍需本机验收。
