import tkinter as tk
from tkinter import messagebox, ttk
import random
import os
import sys
import time

# --- CẤU HÌNH GIAO DIỆN "PRO GAME" ---
COLOR_BG_MAIN = "#263238"
COLOR_BG_CARD = "#37474F"
COLOR_TEXT_MAIN = "#ECEFF1"
COLOR_TEXT_DIM = "#90A4AE"

COLOR_P1 = "#FFAB91"
COLOR_P2 = "#81D4FA"
COLOR_AI = "#E1BEE7"
COLOR_DRAW = "#BDBDBD" 
COLOR_TIMER_NORMAL = "#B2DFDB" 
COLOR_TIMER_URGENT = "#FF5252" 

COLOR_BTN_TEXT = "#263238"
BTN_CONFIRM_BG = "#66BB6A"
BTN_UNDO_BG = "#FFA726"
BTN_RESET_BG = "#4FC3F7"
BTN_SETUP_BG = "#CFD8DC"
BTN_GUIDE_BG = "#FFF59D"
BTN_DISABLED_BG = "#546E7A"

HEAP_COLORS = [
    "#EF5350", "#66BB6A", "#42A5F5", "#FFCA28", "#AB47BC", 
    "#26C6DA", "#EC407A", "#8D6E63", "#BDBDBD", "#D4E157"
]

class MinimaxAI:
    def nim_sum(self, heaps):
        res = 0
        for h in heaps: res ^= h
        return res

    def get_random_move(self, heaps):
        available_indices = [i for i, x in enumerate(heaps) if x > 0]
        if not available_indices: return heaps
        idx = random.choice(available_indices)
        take = random.randint(1, heaps[idx])
        new_heaps = list(heaps)
        new_heaps[idx] -= take
        return new_heaps

    def get_perfect_move(self, heaps):
        current_nim_sum = self.nim_sum(heaps)
        if current_nim_sum != 0:
            for i, count in enumerate(heaps):
                target = count ^ current_nim_sum
                if target < count:
                    new_heaps = list(heaps)
                    new_heaps[i] = target
                    return new_heaps
        return self.get_random_move(heaps)

    def get_move(self, heaps, difficulty):
        if difficulty == "Dễ": return self.get_random_move(heaps)
        elif difficulty == "Trung bình":
            return self.get_perfect_move(heaps) if random.random() < 0.75 else self.get_random_move(heaps)
        else: return self.get_perfect_move(heaps)

class SetupDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Cấu Hình Game")
        self.geometry("480x750")
        self.configure(bg=COLOR_BG_MAIN)
        self.resizable(False, False)
        self.result = None
        self.heap_entries = []
        self.transient(parent)
        self.grab_set()
        self.setup_ui()
        
    def setup_ui(self):
        tk.Label(self, text="⚙️ CÀI ĐẶT", font=("Verdana", 20, "bold"), bg=COLOR_BG_MAIN, fg=COLOR_TEXT_MAIN).pack(pady=20)
        lbl_style = {"font": ("Verdana", 11), "bg": COLOR_BG_MAIN, "fg": COLOR_TEXT_MAIN}
        
        f_mode = tk.Frame(self, bg=COLOR_BG_MAIN)
        f_mode.pack(pady=10)
        tk.Label(f_mode, text="Chế độ:", **lbl_style).pack(side=tk.LEFT)
        self.mode_var = ttk.Combobox(f_mode, values=["Người vs Máy", "Người vs Người"], state="readonly", width=15, font=("Verdana", 10))
        self.mode_var.set("Người vs Máy")
        self.mode_var.pack(side=tk.LEFT, padx=10)
        self.mode_var.bind("<<ComboboxSelected>>", self.toggle_ai_option)

        f1 = tk.Frame(self, bg=COLOR_BG_MAIN)
        f1.pack(pady=10)
        tk.Label(f1, text="Số đống (2-10):", **lbl_style).pack(side=tk.LEFT)
        self.heap_count_var = tk.IntVar(value=3)
        tk.Spinbox(f1, from_=2, to=10, textvariable=self.heap_count_var, font=("Verdana", 11), width=5, command=self.update_inputs, state="readonly").pack(side=tk.LEFT, padx=10)
        
        container = tk.Frame(self, bg=COLOR_BG_MAIN)
        container.pack(pady=5, fill="both", expand=True, padx=30)
        self.canvas = tk.Canvas(container, bg=COLOR_BG_MAIN, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.input_frame = tk.Frame(self.canvas, bg=COLOR_BG_MAIN)
        self.input_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.input_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        bottom_frame = tk.Frame(self, bg=COLOR_BG_MAIN)
        bottom_frame.pack(pady=15, fill="x", padx=30)
        tk.Label(bottom_frame, text="⚡ Cấu hình nhanh:", font=("Verdana", 10, "bold"), bg=COLOR_BG_MAIN, fg="#FFD54F").pack(anchor="w")
        f2 = tk.Frame(bottom_frame, bg=COLOR_BG_MAIN)
        f2.pack(pady=10, anchor="w")
        btn_style = {"font": ("Verdana", 9), "fg": COLOR_BTN_TEXT, "width": 8, "relief": "flat", "bg": "#CFD8DC"}
        for name, cfg in [("Dễ", [5, 10, 15]), ("Vừa", [2, 4, 6, 8, 10, 12]), ("Khó", [1, 3, 5, 7, 9, 11, 13, 15, 17, 19])]:
            tk.Button(f2, text=name, command=lambda c=cfg: self.apply_preset(c), **btn_style).pack(side=tk.LEFT, padx=3)
        tk.Button(f2, text="🎲 Random", command=self.randomize_config, font=("Verdana", 9, "bold"), bg="#FF7043", fg=COLOR_BTN_TEXT, width=10, relief="flat").pack(side=tk.LEFT, padx=10)

        self.f_ai = tk.Frame(bottom_frame, bg=COLOR_BG_MAIN)
        self.f_ai.pack(pady=10, anchor="w")
        
        tk.Label(self.f_ai, text="AI:", **lbl_style).pack(side=tk.LEFT)
        self.ai_mode = ttk.Combobox(self.f_ai, values=["Dễ", "Trung bình", "Khó"], state="readonly", width=10)
        self.ai_mode.set("Trung bình")
        self.ai_mode.pack(side=tk.LEFT, padx=5)

        tk.Label(self.f_ai, text=" |  Thời gian (s):", **lbl_style).pack(side=tk.LEFT, padx=(10, 0))
        self.time_limit_var = ttk.Combobox(self.f_ai, values=["10", "15", "20", "30", "45", "60", "90", "120"], width=5, state="readonly")
        self.time_limit_var.set("30") 
        self.time_limit_var.pack(side=tk.LEFT, padx=5)

        tk.Button(bottom_frame, text="✅ BẮT ĐẦU GAME", command=self.confirm, bg=BTN_CONFIRM_BG, fg=COLOR_BTN_TEXT, font=("Verdana", 12, "bold"), width=20, height=2, relief="flat", cursor="hand2").pack(pady=10)
        self.update_inputs()

    def toggle_ai_option(self, event=None):
        if self.mode_var.get() == "Người vs Người": self.ai_mode.config(state="disabled")
        else: self.ai_mode.config(state="readonly")

    def update_inputs(self):
        for w in self.input_frame.winfo_children(): w.destroy()
        self.heap_entries = []
        n = self.heap_count_var.get()
        for i in range(n):
            fr = tk.Frame(self.input_frame, bg=COLOR_BG_MAIN)
            fr.pack(pady=4, fill="x")
            tk.Label(fr, bg=HEAP_COLORS[i % len(HEAP_COLORS)], width=2).pack(side=tk.LEFT, padx=(0, 5))
            tk.Label(fr, text=f"Đống {i+1}:", font=("Verdana", 10), bg=COLOR_BG_MAIN, fg=COLOR_TEXT_MAIN, width=8, anchor="w").pack(side=tk.LEFT)
            e = tk.Spinbox(fr, from_=1, to=20, width=5, font=("Verdana", 10))
            val = 3 + i if (3+i) <= 20 else 20
            e.delete(0, "end"); e.insert(0, val)
            e.pack(side=tk.LEFT)
            self.heap_entries.append(e)

    def apply_preset(self, cfg):
        self.heap_count_var.set(len(cfg))
        self.update_inputs()
        for i, v in enumerate(cfg):
            if i < len(self.heap_entries):
                self.heap_entries[i].delete(0, "end")
                self.heap_entries[i].insert(0, v)

    def randomize_config(self):
        num_heaps = random.randint(2, 10)
        self.heap_count_var.set(num_heaps)
        self.update_inputs()
        for entry in self.heap_entries:
            entry.delete(0, "end")
            entry.insert(0, str(random.randint(1, 20)))

    def confirm(self):
        try:
            h = [int(e.get()) for e in self.heap_entries]
            if any(x < 1 for x in h): raise ValueError
            
            t_limit = int(self.time_limit_var.get())
            mode_str = self.mode_var.get()
            game_mode = "PvP" if mode_str == "Người vs Người" else "PvAI"
            
            self.result = {
                "heaps": h, 
                "ai_mode": self.ai_mode.get(), 
                "game_mode": game_mode,
                "time_limit": t_limit
            }
            self.destroy()
        except: messagebox.showerror("Lỗi", "Số liệu không hợp lệ")

class NimGameApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NIM MASTER - ULTIMATE EDITION")
        
        self.root.attributes('-fullscreen', True)
        self.root.bind("<Escape>", self.toggle_fullscreen)
        self.root.configure(bg=COLOR_BG_MAIN)
        
        self.ai = MinimaxAI()
        self.ai_difficulty = "Trung bình"
        self.game_mode = "PvAI" 
        self.initial_heaps = [3, 4, 5]
        self.heaps = list(self.initial_heaps)
        self.turn = "PLAYER 1" 
        self.selected_heap = -1
        self.taken_count = 0
        self.temp_heaps = list(self.heaps)
        self.stats = {"p1": 0, "p2": 0, "ai": 0, "g": 0}

        # --- BIẾN CHO ĐỒNG HỒ ---
        self.setting_time_limit = 30 
        self.time_left = self.setting_time_limit
        self.timer_id = None
        
        # --- BIẾN CHO AFK (TREO MÁY) ---
        self.last_activity_time = time.time() 

        self.setup_main_ui()
        self.reset_game()

    def toggle_fullscreen(self, event=None):
        is_fullscreen = self.root.attributes('-fullscreen')
        self.root.attributes('-fullscreen', not is_fullscreen)
        if not is_fullscreen:
            self.root.geometry("1100x850")

    def close_game(self):
        self.stop_timer() 
        if messagebox.askokcancel("Thoát", "Bạn có chắc muốn thoát game?"):
            self.root.destroy()
            sys.exit()
        else:
            # Nếu không thoát, chạy lại timer (nếu đang trong lượt người chơi)
            if self.turn != "AI":
                self.countdown()

    def setup_main_ui(self):
        top_frame = tk.Frame(self.root, bg=COLOR_BG_MAIN)
        top_frame.pack(pady=20, fill="x")
        
        exit_btn = tk.Button(top_frame, text="❌ Thoát", command=self.close_game, 
                             bg="#D32F2F", fg="white", font=("Verdana", 10, "bold"), relief="flat", cursor="hand2")
        exit_btn.pack(side=tk.RIGHT, padx=20)

        tk.Label(top_frame, text="🎲 NIM MASTER", font=("Verdana", 28, "bold"), bg=COLOR_BG_MAIN, fg="#FFD700").pack()
        
        self.lbl_status = tk.Label(top_frame, text="Sẵn sàng", font=("Verdana", 16, "bold"), bg=COLOR_BG_MAIN, fg=COLOR_P1)
        self.lbl_status.pack(pady=5)
        
        self.lbl_timer = tk.Label(top_frame, text=f"⏳ {self.setting_time_limit}s", font=("Verdana", 14, "bold"), bg=COLOR_BG_MAIN, fg=COLOR_TIMER_NORMAL)
        self.lbl_timer.pack(pady=2)

        self.lbl_info = tk.Label(top_frame, text="", bg=COLOR_BG_MAIN, fg=COLOR_TEXT_DIM, font=("Verdana", 10, "italic"))
        self.lbl_info.pack()

        score_frame = tk.Frame(top_frame, bg="#455A64", padx=15, pady=5, relief="ridge", bd=2)
        score_frame.pack(pady=10)
        self.lbl_score = tk.Label(score_frame, text="", bg="#455A64", fg="white", font=("Verdana", 11, "bold"))
        self.lbl_score.pack()

        container = tk.Frame(self.root, bg=COLOR_BG_MAIN)
        container.pack(expand=True, fill="both", padx=40, pady=10)
        self.canvas = tk.Canvas(container, bg=COLOR_BG_MAIN, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(container, orient="vertical", command=self.canvas.yview, bg=COLOR_BG_MAIN)
        self.board_frame = tk.Frame(self.canvas, bg=COLOR_BG_MAIN)
        self.board_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.board_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", expand=True, fill="both")
        self.scrollbar.pack(side="right", fill="y")

        ctrl_frame = tk.Frame(self.root, bg=COLOR_BG_MAIN, pady=20)
        ctrl_frame.pack(fill="x")
        
        self.btn_container = tk.Frame(ctrl_frame, bg=COLOR_BG_MAIN)
        self.btn_container.pack()
        
        self.action_frame = tk.Frame(self.btn_container, bg=COLOR_BG_MAIN)
        self.action_frame.pack(side=tk.LEFT, padx=10)
        
        btn_font = ("Verdana", 11, "bold")
        self.btn_undo = tk.Button(self.action_frame, text="↩️ QUAY LẠI", command=self.undo_selection, 
                                  bg=BTN_UNDO_BG, fg=COLOR_BTN_TEXT, font=btn_font, 
                                  width=14, height=2, relief="flat", cursor="hand2")
        self.btn_undo.pack(side=tk.LEFT, padx=5)

        self.btn_ok = tk.Button(self.action_frame, text="✅ XÁC NHẬN", command=self.finish_turn, 
                                bg=BTN_CONFIRM_BG, fg=COLOR_BTN_TEXT, font=btn_font, 
                                width=16, height=2, relief="flat", cursor="hand2")
        self.btn_ok.pack(side=tk.LEFT, padx=5)

        self.system_frame = tk.Frame(self.btn_container, bg=COLOR_BG_MAIN)
        self.system_frame.pack(side=tk.LEFT, padx=20)
        
        tk.Button(self.system_frame, text="🔄 Chơi lại", command=self.reset_game, 
                  bg=BTN_RESET_BG, fg=COLOR_BTN_TEXT, font=btn_font, width=12, height=2, relief="flat", cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tk.Button(self.system_frame, text="⚙️ Cài đặt", command=self.open_setup, 
                  bg=BTN_SETUP_BG, fg=COLOR_BTN_TEXT, font=btn_font, width=12, height=2, relief="flat", cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tk.Button(self.system_frame, text="📖 Hướng dẫn", command=self.show_guide, 
                  bg=BTN_GUIDE_BG, fg=COLOR_BTN_TEXT, font=btn_font, width=12, height=2, relief="flat", cursor="hand2").pack(side=tk.LEFT, padx=5)

    def show_guide(self):
        filename = "huong_dan.txt"
        default_rules = f"""🎲 LUẬT CHƠI NIM:

1️⃣ Có nhiều đống đá
2️⃣ Mỗi lượt lấy ÍT NHẤT 1 viên từ MỘT đống
3️⃣ Đồng hồ CHẠY NGAY khi bắt đầu lượt!
4️⃣ Nếu chỉ còn 1 viên duy nhất: Có 60 giây để đánh, nếu không sẽ THUA!
5️⃣ Người lấy viên CUỐI CÙNG = THẮNG
6️⃣ Nếu 2 phút không ai hoàn thành lượt đi: HÒA

💡 Chiến thuật:
- Cố gắng để lại số viên XOR = 0 cho đối thủ
- Chế độ "Khó" của AI sử dụng thuật toán Minimax hoàn hảo!

🎮 Chúc may mắn!"""

        try:
            if not os.path.exists(filename):
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(default_rules)
            with open(filename, "r", encoding="utf-8") as f:
                rules = f.read()
            messagebox.showinfo("Hướng dẫn cách chơi", rules)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không đọc được file: {e}")

    # --- CÁC HÀM XỬ LÝ ĐỒNG HỒ ---
    def start_timer(self):
        self.stop_timer()
        if self.turn == "AI": return 

        if sum(self.heaps) == 1:
            self.time_left = 60
        else:
            self.time_left = self.setting_time_limit
            
        self.update_timer_display()
        self.countdown()

    def reset_timer_ui(self):
        """Hàm này chỉ cập nhật số, không dừng timer. Vì timer luôn chạy."""
        self.time_left = self.setting_time_limit
        self.update_timer_display()

    def stop_timer(self):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

    def update_timer_display(self):
        color = COLOR_TIMER_NORMAL
        if self.time_left <= 10:
            color = COLOR_TIMER_URGENT
        
        if sum(self.heaps) == 1:
            self.lbl_timer.config(text=f"🔥 {self.time_left}s (CHỐT HẠ)", fg="#FF5252")
        else:
            self.lbl_timer.config(text=f"⏳ {self.time_left}s", fg=color)

    def countdown(self):
        # --- KIỂM TRA TREO MÁY 2 PHÚT ---
        if sum(self.heaps) > 1:
            idle_duration = time.time() - self.last_activity_time
            if idle_duration >= 120:
                self.end_game("💤 HÒA! TRÒ CHƠI KẾT THÚC DO TREO MÁY QUÁ 2 PHÚT! 💤", "DRAW")
                return
        # ---------------------------------------------

        if self.time_left > 0:
            self.time_left -= 1
            self.update_timer_display()
            self.timer_id = self.root.after(1000, self.countdown)
        else:
            self.handle_timeout()

    def handle_timeout(self):
        self.stop_timer()
        self.undo_selection() 
        
        # --- THUA KHI HẾT GIỜ Ở VIÊN CUỐI ---
        if sum(self.heaps) == 1:
            winner = ""
            loser_name = "BẠN" if self.turn == "PLAYER 1" and self.game_mode == "PvAI" else self.turn
            if self.game_mode == "PvAI":
                winner = "AI" 
                self.stats["ai"] += 1
            else:
                if self.turn == "PLAYER 1":
                    winner = "PLAYER 2"
                    self.stats["p2"] += 1
                else:
                    winner = "PLAYER 1"
                    self.stats["p1"] += 1
            
            msg = f"⌛ HẾT GIỜ! {loser_name} ĐÃ THUA VÌ KHÔNG ĐÁNH VIÊN CUỐI!"
            self.end_game(msg, winner)
            return
        # -----------------------------------------------

        # Thông báo mất lượt bình thường
        who = "BẠN" if self.turn == "PLAYER 1" and self.game_mode == "PvAI" else self.turn
        messagebox.showinfo("HẾT GIỜ!", f"Đã hết thời gian! {who} bị mất lượt.")
        
        if self.game_mode == "PvAI":
            if self.turn == "PLAYER 1":
                self.turn = "AI"
                self.prepare_next_turn()
                self.root.after(1000, self.ai_move)
        else:
            if self.turn == "PLAYER 1": self.turn = "PLAYER 2"
            else: self.turn = "PLAYER 1"
            self.prepare_next_turn()

    # --- KẾT THÚC HÀM ĐỒNG HỒ ---

    def show_action_buttons(self):
        self.action_frame.pack(side=tk.LEFT, padx=10, before=self.system_frame)

    def hide_action_buttons(self):
        self.action_frame.pack_forget()

    def update_board(self):
        for w in self.board_frame.winfo_children(): w.destroy()

        for i, count in enumerate(self.temp_heaps):
            row_bg = "#546E7A" if i == self.selected_heap else COLOR_BG_CARD
            row = tk.Frame(self.board_frame, bg=row_bg, pady=10, padx=10, relief="raised", bd=1)
            row.pack(fill="x", pady=6, padx=10)
            
            lbl_text = f"ĐỐNG {i+1}"
            tk.Label(row, text=lbl_text, font=("Verdana", 12, "bold"), bg=row_bg, fg="#FFCA28", width=8, anchor="center").pack(side=tk.LEFT, padx=10)
            tk.Label(row, text=f"({count})", font=("Verdana", 10), bg=row_bg, fg="white").pack(side=tk.LEFT, padx=5)

            btn_area = tk.Frame(row, bg=row_bg)
            btn_area.pack(side=tk.LEFT, padx=10)
            color = HEAP_COLORS[i % len(HEAP_COLORS)]
            
            disabled = False
            if self.turn == "AI": disabled = True
            elif self.selected_heap != -1 and self.selected_heap != i: disabled = True
            
            for _ in range(count):
                btn_bg = BTN_DISABLED_BG if disabled else color
                b = tk.Button(btn_area, bg=btn_bg, activebackground="white", width=3, height=1, relief="raised", borderwidth=2)
                if not disabled: b.config(command=lambda r=i: self.take_stone(r), cursor="hand2")
                b.pack(side=tk.LEFT, padx=3)

    def update_status_label(self):
        if self.game_mode == "PvAI": info_text = f"MODE: Người vs Máy | CẤP ĐỘ: {self.ai_difficulty}"
        else: info_text = "MODE: Đối Kháng 2 Người"
        self.lbl_info.config(text=info_text)

        if self.turn == "AI": self.lbl_status.config(text="🤖 AI Đang suy nghĩ...", fg=COLOR_AI)
        elif self.turn == "PLAYER 1":
            text = "👉 Lượt BẠN (Người 1)" if self.game_mode == "PvAI" else "👉 Lượt NGƯỜI 1 (Cam)"
            self.lbl_status.config(text=text, fg=COLOR_P1)
        elif self.turn == "PLAYER 2": self.lbl_status.config(text="👉 Lượt NGƯỜI 2 (Xanh)", fg=COLOR_P2)

        if self.game_mode == "PvAI": self.lbl_score.config(text=f"Bạn: {self.stats['p1']}  |  AI: {self.stats['ai']}  |  Tổng: {self.stats['g']}")
        else: self.lbl_score.config(text=f"P1: {self.stats['p1']}  |  P2: {self.stats['p2']}  |  Tổng: {self.stats['g']}")

    def take_stone(self, idx):
        if self.turn == "AI": return
        if self.selected_heap == -1: self.selected_heap = idx
        
        if self.selected_heap == idx and self.temp_heaps[idx] > 0:
            self.temp_heaps[idx] -= 1
            self.taken_count += 1
            
            # --- LOGIC MỚI: Đồng hồ đã chạy sẵn rồi, không cần kích hoạt lại ---
            if self.taken_count == 1: 
                self.show_action_buttons()
            
            self.update_board()

    def undo_selection(self):
        self.temp_heaps = list(self.heaps)
        self.selected_heap = -1
        self.taken_count = 0
        self.hide_action_buttons()
        
        # --- LOGIC MỚI: UNDO KHÔNG DỪNG ĐỒNG HỒ, NÓ VẪN CHẠY TIẾP ---
        # Chỉ reset lại hiển thị 60s nếu là vòng cuối để ép time
        if sum(self.heaps) == 1:
            self.time_left = 60
            self.update_timer_display()
        
        self.update_board()

    def finish_turn(self):
        if self.taken_count == 0: return
        self.stop_timer() 
        
        self.last_activity_time = time.time()
        
        self.heaps = list(self.temp_heaps)
        
        if sum(self.heaps) == 0:
            winner = self.turn
            msg = ""
            if self.game_mode == "PvAI":
                msg = "🏆 BẠN ĐÃ CHIẾN THẮNG! 🏆"
                self.stats["p1"] += 1
            else:
                if winner == "PLAYER 1":
                    msg = "🏆 NGƯỜI 1 THẮNG! 🏆"
                    self.stats["p1"] += 1
                else:
                    msg = "🏆 NGƯỜI 2 THẮNG! 🏆"
                    self.stats["p2"] += 1
            self.end_game(msg, winner)
            return

        if self.game_mode == "PvAI":
            self.turn = "AI"
            self.prepare_next_turn()
            self.root.after(1000, self.ai_move) 
        else:
            if self.turn == "PLAYER 1": self.turn = "PLAYER 2"
            else: self.turn = "PLAYER 1"
            self.prepare_next_turn()

    def prepare_next_turn(self):
        self.selected_heap = -1
        self.taken_count = 0
        self.hide_action_buttons()
        self.update_status_label()
        self.update_board()

        total_stones = sum(self.heaps)
        if total_stones == 1:
            messagebox.showinfo("CẢNH BÁO", "Chỉ còn 1 viên cuối cùng!\nBạn có 60 giây để đánh, nếu không bạn sẽ THUA!")
        
        # --- BẮT BUỘC CHẠY TIMER NGAY KHI CHUYỂN LƯỢT ---
        self.start_timer()

    def ai_move(self):
        self.stop_timer() 
        self.heaps = self.ai.get_move(self.heaps, self.ai_difficulty)
        self.temp_heaps = list(self.heaps)
        
        self.last_activity_time = time.time()

        if sum(self.heaps) == 0:
            self.stats["ai"] += 1
            self.end_game("💀 AI ĐÃ CHIẾN THẮNG! 💀", "AI")
        else:
            self.turn = "PLAYER 1"
            self.prepare_next_turn()

    def end_game(self, msg, winner):
        self.stop_timer()
        if winner != "DRAW":
            self.stats["g"] += 1
            
        self.update_status_label()
        color = COLOR_P1
        if winner == "AI": color = COLOR_AI
        elif winner == "PLAYER 2": color = COLOR_P2
        elif winner == "DRAW": color = COLOR_DRAW
            
        self.lbl_status.config(text=msg, fg=color)
        self.hide_action_buttons()
        messagebox.showinfo("KẾT QUẢ", msg)
        self.update_board()

    def reset_game(self):
        self.stop_timer()
        self.heaps = list(self.initial_heaps)
        self.temp_heaps = list(self.heaps)
        self.turn = "PLAYER 1"
        self.selected_heap = -1
        self.taken_count = 0
        self.hide_action_buttons()
        
        self.last_activity_time = time.time() 

        self.update_status_label()
        self.update_board()
        
        # --- BẮT BUỘC CHẠY TIMER NGAY KHI RESET ---
        self.start_timer()

    def open_setup(self):
        self.stop_timer()
        d = SetupDialog(self.root)
        self.root.wait_window(d)
        if d.result:
            self.initial_heaps = d.result["heaps"]
            self.ai_difficulty = d.result["ai_mode"]
            self.game_mode = d.result["game_mode"]
            self.setting_time_limit = d.result["time_limit"]
            self.stats = {"p1": 0, "p2": 0, "ai": 0, "g": 0}
            self.reset_game()
            mode = "Người vs Máy" if self.game_mode == "PvAI" else "Người vs Người"
            messagebox.showinfo("Cài đặt xong", f"Đã lưu: {mode}, {self.setting_time_limit}s/lượt")
        else:
            if self.turn != "AI":
                if sum(self.heaps) == 1: self.start_timer()
                elif self.taken_count > 0: self.countdown()
                else: self.start_timer() # Resume timer bình thường

if __name__ == "__main__":
    root = tk.Tk()
    NimGameApp(root)
    root.mainloop()