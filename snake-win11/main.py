"""Chinese desktop Snake for Windows 11. Runtime: Python standard library only."""
import tkinter as tk
from tkinter import ttk

from engine import Game
from storage import LEVELS, load_scores, save_scores, score_path

try:
    import winsound
except ImportError:
    winsound = None

BG, BOARD, GREEN, TEXT = '#101a29', '#172438', '#63e6a4', '#e7efff'
CELL = 22



class App:
    def __init__(self, root):
        self.root = root
        root.title('青蛇 · 贪吃蛇')
        root.configure(bg=BG)
        root.resizable(False, False)
        self.game = Game()
        self.running = self.paused = False
        self.timer = None
        self.path = score_path()
        self.scores = load_scores(self.path)
        self.save_failed = False
        self.level = tk.StringVar(value='普通')
        self.sound = tk.BooleanVar(value=True)
        tk.Label(root, text='青蛇  /  SNAKE', font=('Microsoft YaHei UI', 23, 'bold'),
                 bg=BG, fg=GREEN).pack(anchor='w', padx=24, pady=(18, 5))
        self.info = tk.Label(root, bg=BG, fg=TEXT, font=('Microsoft YaHei UI', 12))
        self.info.pack(anchor='w', padx=24, pady=(0, 12))
        controls = tk.Frame(root, bg=BG)
        controls.pack(fill='x', padx=24, pady=(0, 12))
        tk.Label(controls, text='难度', bg=BG, fg=TEXT).pack(side='left')
        self.combo = ttk.Combobox(controls, textvariable=self.level, values=list(LEVELS),
                                  width=6, state='readonly', takefocus=False)
        self.combo.pack(side='left', padx=8)
        self.combo.bind('<<ComboboxSelected>>', lambda e: self.render())
        ttk.Button(controls, text='开始 / 重开 (R)', command=self.start, takefocus=False).pack(side='left', padx=5)
        self.pause_button = ttk.Button(controls, text='暂停 (空格)', command=self.pause, takefocus=False)
        self.pause_button.pack(side='left', padx=5)
        tk.Checkbutton(controls, text='音效', variable=self.sound, bg=BG, fg=TEXT,
                       selectcolor=BOARD, activebackground=BG, activeforeground=TEXT,
                       takefocus=False).pack(side='right')
        self.canvas = tk.Canvas(root, width=28*CELL, height=22*CELL, bg=BOARD,
                                highlightthickness=0)
        self.canvas.pack(padx=24)
        self.status = tk.Label(root, text='', bg=BG, fg=TEXT, font=('Microsoft YaHei UI', 10))
        self.status.pack(pady=12)
        root.bind('<KeyPress>', self.key)
        root.bind('<FocusOut>', self.focus_out)
        root.protocol('WM_DELETE_WINDOW', self.close)
        self.render()

    def key(self, event):
        key = event.keysym.lower()
        if key in ('r', 'return'):
            self.start()
        elif key in ('space', 'escape'):
            self.pause()
        elif self.running and not self.paused:
            self.game.turn({'w': 'Up', 's': 'Down', 'a': 'Left', 'd': 'Right'}.get(key, event.keysym))
        if event.keysym in ('Up', 'Down', 'Left', 'Right', 'space'):
            return 'break'

    def start(self):
        self.cancel_timer()
        self.game = Game()
        self.active_level = self.level.get()
        self.running, self.paused = True, False
        self.combo.configure(state='disabled')
        self.root.focus_set()
        self.render()
        self.schedule()

    def cancel_timer(self):
        if self.timer is not None:
            self.root.after_cancel(self.timer)
            self.timer = None

    def schedule(self):
        self.timer = self.root.after(LEVELS[self.active_level], self.tick)

    def pause(self):
        if not self.running:
            return
        self.paused = not self.paused
        self.cancel_timer()
        if not self.paused:
            self.schedule()
        self.render()

    def focus_out(self, event):
        # Only pause when focus leaves the application, not between its controls.
        self.root.after_idle(self.check_focus)

    def check_focus(self):
        if self.running and not self.paused and self.root.focus_displayof() is None:
            self.pause()

    def play(self, event):
        if self.sound.get() and winsound and event in ('eat', 'over', 'win'):
            try:
                # Async playback uses a Windows system sound and never blocks the UI.
                winsound.PlaySound('SystemAsterisk' if event == 'eat' else 'SystemExclamation',
                                   winsound.SND_ALIAS | winsound.SND_ASYNC | winsound.SND_NODEFAULT)
            except RuntimeError:
                pass

    def tick(self):
        self.timer = None
        if not self.running or self.paused:
            return
        event = self.game.step()
        self.play(event)
        if self.game.score > self.scores.get(self.active_level, 0):
            self.scores[self.active_level] = self.game.score
            try:
                save_scores(self.path, self.scores)
                self.save_failed = False
            except OSError:
                self.save_failed = True
        if self.game.over:
            self.running = False
            self.combo.configure(state='readonly')
        self.render()
        if self.running:
            self.schedule()

    def render(self):
        c = self.canvas
        c.delete('all')
        for x in range(0, 28*CELL, CELL):
            c.create_line(x, 0, x, 22*CELL, fill='#1d2d43')
        for y in range(0, 22*CELL, CELL):
            c.create_line(0, y, 28*CELL, y, fill='#1d2d43')
        if self.game.food:
            x, y = self.game.food
            c.create_oval(x*CELL+4, y*CELL+4, (x+1)*CELL-4, (y+1)*CELL-4, fill='#ff9478', outline='')
        for i, (x, y) in enumerate(self.game.snake):
            c.create_rectangle(x*CELL+2, y*CELL+2, (x+1)*CELL-2, (y+1)*CELL-2,
                               fill=GREEN if i == 0 else '#30b986', outline='')
        level = getattr(self, 'active_level', self.level.get()) if self.running else self.level.get()
        self.info.configure(text=f'得分  {self.game.score:04d}     /     {level}最高分  {self.scores.get(level, 0):04d}')
        overlay = '已暂停 · 空格继续' if self.paused else ('挑战成功！按 R 再玩' if self.game.won else
                  '游戏结束 · 按 R 重开' if self.game.over else '准备好了吗？点击开始' if not self.running else '')
        if overlay:
            c.create_rectangle(70, 205, 546, 278, fill=BG, outline=GREEN)
            c.create_text(308, 241, text=overlay, fill=TEXT, font=('Microsoft YaHei UI', 18, 'bold'))
        self.pause_button.configure(text='继续 (空格)' if self.paused else '暂停 (空格)')
        self.status.configure(text='最高分保存失败，本次仅保留在内存' if self.save_failed else
                              '方向键 / WASD 移动   ·   空格暂停   ·   R 重开   ·   切出窗口自动暂停')

    def close(self):
        self.cancel_timer()
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
