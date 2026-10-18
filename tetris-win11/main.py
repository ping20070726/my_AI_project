"""Windows desktop interface. No third-party runtime dependencies."""
import tkinter as tk
from tkinter import ttk
from engine import Game, SHAPES, COLORS, SPEEDS
from storage import score_path, load_scores, save_scores
try:
    import winsound
except ImportError:
    winsound = None

BG, PANEL, TEXT, ACCENT = '#101928', '#19263a', '#e8efff', '#65dfad'
CELL = 26


class App:
    def __init__(self, root):
        self.root = root
        root.title('星落 · 俄罗斯方块')
        root.configure(bg=BG)
        root.resizable(False, False)
        self.game = Game()
        self.running = self.paused = False
        self.timer = None
        self.path = score_path()
        self.scores = load_scores(self.path)
        self.save_error = False
        self.difficulty = tk.StringVar(value='普通')
        self.sound = tk.BooleanVar(value=True)
        tk.Label(root, text='星落 / FALLING BLOCKS', bg=BG, fg=ACCENT,
                 font=('Microsoft YaHei UI', 20, 'bold')).pack(anchor='w', padx=20, pady=(16, 12))
        bar = tk.Frame(root, bg=BG)
        bar.pack(fill='x', padx=20, pady=(0, 12))
        tk.Label(bar, text='难度', bg=BG, fg=TEXT).pack(side='left')
        self.combo = ttk.Combobox(bar, textvariable=self.difficulty, values=list(SPEEDS),
                                 state='readonly', width=5, takefocus=False)
        self.combo.pack(side='left', padx=8)
        self.combo.bind('<<ComboboxSelected>>', lambda e: self.render())
        ttk.Button(bar, text='开始 / 重开', command=self.start, takefocus=False).pack(side='left', padx=4)
        self.pause_btn = ttk.Button(bar, text='暂停', command=self.pause, takefocus=False)
        self.pause_btn.pack(side='left', padx=4)
        tk.Checkbutton(bar, text='音效', variable=self.sound, bg=BG, fg=TEXT, selectcolor=PANEL,
                       activebackground=BG, activeforeground=TEXT, takefocus=False).pack(side='left')
        content = tk.Frame(root, bg=BG)
        content.pack(padx=20)
        self.canvas = tk.Canvas(content, width=260, height=520, bg=PANEL, highlightthickness=0)
        self.canvas.pack(side='left')
        side = tk.Frame(content, bg=BG, width=200)
        side.pack(side='left', fill='y', padx=(18, 0))
        self.info = tk.Label(side, bg=BG, fg=TEXT, justify='left', font=('Microsoft YaHei UI', 12))
        self.info.pack(anchor='w', pady=10)
        tk.Label(side, text='下一个', bg=BG, fg=ACCENT, font=('Microsoft YaHei UI', 12)).pack(anchor='w', pady=8)
        self.preview = tk.Canvas(side, width=156, height=90, bg=PANEL, highlightthickness=0)
        self.preview.pack(anchor='w')
        tk.Label(side, text='← → / A D  移动\n↑ / W / X  顺时针\nZ  逆时针旋转\n↓ / S  加速下降\n空格  直接落底\nP / Esc  暂停继续\nR  重新开始\n\n每消除 10 行升级\n切出窗口自动暂停', bg=BG, fg=TEXT,
                 justify='left', font=('Microsoft YaHei UI', 10)).pack(anchor='w', pady=16)
        self.status = tk.Label(root, bg=BG, fg=TEXT, font=('Microsoft YaHei UI', 10))
        self.status.pack(pady=12)
        root.bind('<KeyPress>', self.key)
        root.bind('<FocusOut>', lambda e: root.after_idle(self.focus_check))
        root.protocol('WM_DELETE_WINDOW', self.close)
        self.render()

    def cancel(self):
        if self.timer is not None:
            self.root.after_cancel(self.timer)
            self.timer = None

    def schedule(self):
        self.timer = self.root.after(self.game.interval, self.tick)

    def start(self):
        self.cancel()
        self.game = Game(self.difficulty.get())
        self.running, self.paused = True, False
        self.combo.configure(state='disabled')
        self.root.focus_set()
        self.render()
        self.schedule()

    def pause(self):
        if not self.running:
            return
        self.paused = not self.paused
        self.cancel()
        if not self.paused:
            self.schedule()
        self.render()

    def focus_check(self):
        if self.running and not self.paused and self.root.focus_displayof() is None:
            self.pause()

    def key(self, e):
        key = e.keysym.lower()
        if key in ('r', 'return'):
            self.start()
        elif key in ('p', 'escape'):
            self.pause()
        elif self.running and not self.paused:
            result = None
            if key in ('left', 'a'):
                self.game.move(-1, 0)
            elif key in ('right', 'd'):
                self.game.move(1, 0)
            elif key in ('up', 'w', 'x', 'z'):
                self.game.rotate(key != 'z')
            elif key in ('down', 's'):
                result = self.game.step(soft=True)
            elif key == 'space':
                result = self.game.hard_drop()
            self.update_game(result)
            # A newly spawned piece receives a full gravity interval.
            if result is not None and self.running:
                self.cancel()
                self.schedule()
        if key in ('left', 'right', 'up', 'down', 'space'):
            return 'break'

    def tick(self):
        self.timer = None
        if not self.running or self.paused:
            return
        self.update_game(self.game.step())
        if self.running:
            self.schedule()

    def update_game(self, cleared):
        if self.sound.get() and winsound and (cleared is not None or self.game.over):
            try:
                winsound.PlaySound('SystemExclamation' if self.game.over else 'SystemAsterisk' if cleared else 'SystemDefault',
                                   winsound.SND_ALIAS | winsound.SND_ASYNC | winsound.SND_NODEFAULT)
            except RuntimeError:
                pass
        level = self.game.difficulty
        if self.game.score > self.scores.get(level, 0):
            self.scores[level] = self.game.score
            try:
                save_scores(self.path, self.scores)
                self.save_error = False
            except OSError:
                self.save_error = True
        if self.game.over:
            self.running = False
            self.cancel()
            self.combo.configure(state='readonly')
        self.render()

    @staticmethod
    def block(canvas, x, y, color, ghost=False, cell=CELL):
        canvas.create_rectangle(x*cell+1, y*cell+1, (x+1)*cell-1, (y+1)*cell-1,
                                fill='' if ghost else color, outline=color if ghost else BG, width=2)
        if not ghost:
            canvas.create_line(x*cell+4, y*cell+4, (x+1)*cell-5, y*cell+4, fill='#e8efff')

    def render(self):
        c, g = self.canvas, self.game
        c.delete('all')
        for x in range(11):
            c.create_line(x*CELL, 0, x*CELL, 520, fill='#223149')
        for y in range(21):
            c.create_line(0, y*CELL, 260, y*CELL, fill='#223149')
        for y, row in enumerate(g.board):
            for x, kind in enumerate(row):
                if kind:
                    self.block(c, x, y, COLORS[kind])
        if not g.over:
            for x, y in g.cells(y=g.ghost_y()):
                self.block(c, x, y, COLORS[g.kind], ghost=True)
            for x, y in g.cells():
                self.block(c, x, y, COLORS[g.kind])
        overlay = '已暂停\nP / Esc 继续' if self.paused else '游戏结束\n按 R 重开' if g.over else '点击开始\n或按 Enter' if not self.running else ''
        if overlay:
            c.create_rectangle(12, 204, 248, 306, fill=BG, outline=ACCENT)
            c.create_text(130, 255, text=overlay, fill=TEXT, font=('Microsoft YaHei UI', 18, 'bold'), justify='center')
        difficulty = g.difficulty if self.running else self.difficulty.get()
        self.info.configure(text=f'得分  {g.score:,}\n\n{difficulty}最高分  {self.scores.get(difficulty, 0):,}\n\n等级  {g.level}    消行  {g.lines}')
        self.preview.delete('all')
        for x, y in SHAPES[g.next_kind]:
            self.block(self.preview, x+1, y+1, COLORS[g.next_kind], cell=22)
        self.pause_btn.configure(text='继续' if self.paused else '暂停')
        self.status.configure(text='最高分写入失败，本次记录仅保留在内存' if self.save_error else '填满一行即可消除 · 轮廓显示落点 · 挑战你的最高分')

    def close(self):
        self.cancel()
        if winsound:
            winsound.PlaySound(None, 0)
        self.root.destroy()


def main():
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except (AttributeError, OSError):
        pass
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == '__main__':
    main()
