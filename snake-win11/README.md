# 青蛇 · Win11 贪吃蛇

中文桌面增强版，适用于 Windows 11 x64。深色界面，方向键或 WASD 操作，三档难度、独立最高分、音效开关、暂停与重新开始。撞墙或撞到身体结束，吃到食物加 10 分，填满棋盘获胜。

## 获取 exe

在本仓库 **Actions → Snake Windows executable** 中打开成功的运行记录，下载 **SnakeWin11-Windows-x64**，解压后双击 `SnakeWin11.exe`。exe 自带 Python 运行时，使用者无需安装 Python。首次上传代码后会自动构建，也可在 Actions 手动运行。构建产物保留时间以 GitHub 设置为准。

## 源码运行

安装 Python 3.12（Windows 官方安装程序包含 Tcl/Tk），在项目目录运行：

```powershell
py -3 main.py
```

运行无需第三方库，也无需网络。

## 本地打包

在 Windows 上安装 Python 3.12，双击 `build.bat`。脚本创建独立虚拟环境，安装固定版本 PyInstaller，运行测试并生成 `dist\SnakeWin11.exe`。首次安装打包依赖需要网络。请在 Windows 上构建 Windows exe。

## 操作

| 操作 | 按键 |
| --- | --- |
| 移动 | 方向键 / WASD |
| 暂停、继续 | 空格 / Esc |
| 开始、重新开始 | R / Enter |

难度在开始前选择：简单 180ms/步、普通 125ms/步、困难 80ms/步；一局内速度固定。切出窗口自动暂停，回来后按空格继续。连续快速按键每步最多接受一次转向，防止瞬间反向。

最高分按难度写入 `%LOCALAPPDATA%\SnakeWin11\scores.json`。文件损坏时自动按空记录载入；无法写入时界面提示，本次分数仍保留在内存。音效使用 Windows 系统提示音，声音取决于系统音量和声音方案。

## 验证

```powershell
py -3 -m unittest discover -s tests -v
```

自动测试覆盖禁止反向、连续转向、吃食增长、撞墙、撞身体、进入移走的尾格、满盘获胜、存档及损坏恢复。Windows 工作流执行相同测试并打包；窗口显示、键盘手感、系统音效仍需在实际 Win11 上验收。
