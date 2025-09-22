import tkinter as tk
from tkinter import ttk, font, Toplevel, filedialog, scrolledtext
import json
import os
import random
import platform
import shutil
import re
from datetime import datetime, time
import requests
import webbrowser
import feedparser
from bs4 import BeautifulSoup
try:
    import pytz
except ImportError:
    pytz = None

try:
    from ctypes import windll
except ImportError:
    windll = None
WEATHER_API_KEY = "ad5c1b86467191a4ab639840195b08c4"

def get_weather_info():
        try:
        # 서울의 위도와 경도
            lat, lon = 37.5665, 126.9780 
            url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric&lang=kr"
        
            response = requests.get(url, timeout=5).json()
        
            description = response['weather'][0]['description']
            temp = response['main']['temp']
            return f"서울: {description}, 현재 기온: {temp:.1f}°C"
        except Exception as e:
            print(f"날씨 정보 로딩 실패: {e}")
            return "날씨 정보를 불러올 수 없습니다."

def get_news_headlines(max_headlines=5):
    RSS_URL = "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko"
    try:
        feed = feedparser.parse(RSS_URL)
        
        # 피드 파싱에 실패했거나, 뉴스 항목이 없는 경우를 대비
        if not feed.entries:
            print("뉴스 피드를 파싱했으나 내용이 없습니다.")
            return [{"title": "새로운 뉴스가 없습니다.", "link": ""}]

        headlines_with_links = []
        for entry in feed.entries[:max_headlines]:
            headlines_with_links.append({
                "title": entry.title,
                "link": entry.link
            })
        return headlines_with_links

    except Exception as e:
        print(f"뉴스 정보 로딩 중 예외 발생: {e}")
        # ✅ 예외가 발생했을 때도 비어있지 않은 리스트를 반환하도록 수정
        return [{"title": "주요 뉴스를 불러오는 중 오류가 발생했습니다.", "link": ""}]
        
class school_:
    @staticmethod
    def get_menu():
        url = "https://www.tw.ac.kr/diet/schedule.do?menuId=1733"
        try:
            res = requests.get(url, timeout=5)
            res.encoding = "utf-8"  # 한글 깨짐 방지
            soup = BeautifulSoup(res.text, "html.parser")

            menu_table = soup.select("table.tbl tbody tr")
            menus = []
            for row in menu_table:
                cols = row.find_all("td")
                if len(cols) > 1:
                    date = cols[0].get_text(strip=True)
                    food = cols[1].get_text(strip=True)
                    menus.append(f"{date}: {food}")
            return menus
        except Exception as e:
            return [f"메뉴 불러오기 실패: {e}"]



class DesktopAssistant:
    def __init__(self, root):
        self.root = root
        self.root.title("✨ My Desktop Assistant v3.5")
        self.root.geometry("1100x800")
        self.root.configure(bg="#F7F2FA")
        self.setup_styles()
        container = ttk.Frame(root, style="Main.TFrame")
        container.pack(fill=tk.BOTH, expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.frames = {}
        for F in (DashboardPage, FileOrganizerPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame("DashboardPage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

    def setup_styles(self):
        style = ttk.Style(self.root)
        style.theme_use('clam')
        BG_COLOR = "#F7F2FA"
        CARD_BG_COLOR = "#FFFFFF"
        ACCENT_COLOR = "#A594F9"
        ACCENT_ACTIVE_COLOR = "#8E7DF7"
        TEXT_COLOR = "#5D5D7A"
        HEADER_COLOR = "#4B4B7F"
        BORDER_COLOR = "#EDE9F2"
        SECONDARY_BG_COLOR = "#F0F0F0"
        
        style.configure("Main.TFrame", background=BG_COLOR)
        style.configure("Card.TFrame", background=CARD_BG_COLOR, borderwidth=1, relief="solid", bordercolor=BORDER_COLOR)
        style.configure("Header.TLabel", background=BG_COLOR, foreground=HEADER_COLOR, font=("맑은 고딕", 20, "bold"))
        
        # --- [수정] 새로운 시계 스타일 ---
        style.configure("MainClock.TLabel", background=BG_COLOR, foreground=HEADER_COLOR, font=("맑은 고딕", 14, "bold"))
        style.configure("SubClock.TLabel", background=BG_COLOR, foreground=TEXT_COLOR, font=("맑은 고딕", 9))
        style.configure("WorldClock.TCombobox", foreground=TEXT_COLOR)

        style.configure("CardTitle.TLabel", background=CARD_BG_COLOR, foreground=HEADER_COLOR, font=("맑은 고딕", 14, "bold"))
        style.configure("CardBody.TLabel", background=CARD_BG_COLOR, foreground=TEXT_COLOR, font=("맑은 고딕", 10))
        style.configure("ScheduleTime.TLabel", background=CARD_BG_COLOR, foreground=ACCENT_COLOR, font=("맑은 고딕", 11, "bold"))
        style.configure("ScheduleSubject.TLabel", background=CARD_BG_COLOR, foreground=HEADER_COLOR, font=("맑은 고딕", 12, "bold"))
        style.configure("Accent.TButton", font=("맑은 고딕", 11, "bold"), background=ACCENT_COLOR, foreground="white", borderwidth=0, padding=10)
        style.map("Accent.TButton", background=[('active', ACCENT_ACTIVE_COLOR)])
        style.configure("Card.TButton", font=("맑은 고딕", 10), background=SECONDARY_BG_COLOR, foreground=TEXT_COLOR, borderwidth=1, bordercolor="#DCDCDC")
        style.map("Card.TButton", background=[('active', '#E0E0E0')])
        style.configure("Modern.TEntry", bordercolor=BORDER_COLOR, lightcolor=BORDER_COLOR, darkcolor=BORDER_COLOR, fieldbackground="white", foreground=TEXT_COLOR)
        style.configure("Modern.Vertical.TScrollbar", troughcolor=BG_COLOR, bordercolor=BG_COLOR, background="#D3D3D3", arrowcolor=TEXT_COLOR)
        style.configure("Card.TCheckbutton", background=CARD_BG_COLOR, font=("맑은 고딕", 10), foreground=TEXT_COLOR)
        style.map('Card.TCheckbutton',
          indicatorcolor=[('selected', ACCENT_COLOR), ('!selected', '#d3d3d3')],
          background=[('active', '#f5f5f5')])


# --- 대시보드 페이지 ---
class DashboardPage(ttk.Frame):
    def clear_focus(self, event):
        """이벤트가 발생한 위젯의 포커스를 해제하고 메인 프레임으로 옮깁니다."""
        self.focus_set()
    
    def __init__(self, parent, controller):
        super().__init__(parent, style="Main.TFrame")
        self.controller = controller

        self.todo_file = "todo_list.json"
        self.todo_items = self.load_todo_items()
        
        self.schedule_file = "schedule.json"
        self.schedule_data = self.load_schedule()

        self.available_timezones = {
            "뉴욕": "America/New_York", "런던": "Europe/London", "파리": "Europe/Paris",
            "도쿄": "Asia/Tokyo", "시드니": "Australia/Sydney", "베이징": "Asia/Shanghai",
            "모스크바": "Europe/Moscow"
        }
        self.selected_city_1 = tk.StringVar(value="뉴욕")
        self.selected_city_2 = tk.StringVar(value="도쿄")
        
        main_frame = ttk.Frame(self, style="Main.TFrame", padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # --- [수정] 헤더 UI 구성 ---
        header_frame = ttk.Frame(main_frame, style="Main.TFrame")
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(header_frame, text="My Dashboard", style="Header.TLabel").pack(side=tk.LEFT)
        
        # 시계를 담을 컨테이너 프레임
        clock_container = ttk.Frame(header_frame, style="Main.TFrame")
        clock_container.pack(side=tk.RIGHT)

        # 메인 시계 (대한민국)
        self.main_clock_label = ttk.Label(clock_container, text="--:--:--", style="MainClock.TLabel")
        self.main_clock_label.pack(anchor="e")
        self.main_date_label = ttk.Label(clock_container, text="----년 --월 --일 (-)", style="SubClock.TLabel")
        self.main_date_label.pack(anchor="e")

        # 세계 시계 1
        world_clock_frame_1 = ttk.Frame(clock_container, style="Main.TFrame")
        world_clock_frame_1.pack(anchor="e", pady=(5,0))
        self.world_clock_label_1 = ttk.Label(world_clock_frame_1, text="--:--", style="SubClock.TLabel", width=10, anchor="e")
        self.world_clock_label_1.pack(side=tk.RIGHT)
        city_combo_1 = ttk.Combobox(world_clock_frame_1, textvariable=self.selected_city_1, 
                                    values=list(self.available_timezones.keys()), state="readonly", 
                                    width=6, style="WorldClock.TCombobox")
        city_combo_1.pack(side=tk.RIGHT, padx=(0, 5))
        city_combo_1.bind("<<ComboboxSelected>>", self.clear_focus) # 강조 해제용
        
        # 세계 시계 2
        world_clock_frame_2 = ttk.Frame(clock_container, style="Main.TFrame")
        world_clock_frame_2.pack(anchor="e")
        self.world_clock_label_2 = ttk.Label(world_clock_frame_2, text="--:--", style="SubClock.TLabel", width=10, anchor="e")
        self.world_clock_label_2.pack(side=tk.RIGHT)
        city_combo_2 = ttk.Combobox(world_clock_frame_2, textvariable=self.selected_city_2,
                                    values=list(self.available_timezones.keys()), state="readonly", 
                                    width=6, style="WorldClock.TCombobox")
        city_combo_2.pack(side=tk.RIGHT, padx=(0, 5))
        city_combo_2.bind("<<ComboboxSelected>>", self.clear_focus)

        dashboard_frame = ttk.Frame(main_frame, style="Main.TFrame")
        dashboard_frame.pack(fill=tk.BOTH, expand=True)
     
        dashboard_frame.grid_columnconfigure(0, weight=2, uniform="group1")
        dashboard_frame.grid_columnconfigure(1, weight=3, uniform="group1")
        dashboard_frame.grid_rowconfigure(0, weight=1)
        dashboard_frame.grid_rowconfigure(1, weight=1)

        left_frame = ttk.Frame(dashboard_frame, style="Main.TFrame")
        left_frame.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 20))
        left_frame.grid_rowconfigure(0, weight=1)
        left_frame.grid_rowconfigure(1, weight=1)

        right_frame = ttk.Frame(dashboard_frame, style="Main.TFrame")
        right_frame.grid(row=0, column=1, rowspan=2, sticky="nsew")
        right_frame.grid_rowconfigure(0, weight=1)
        right_frame.grid_rowconfigure(1, weight=1)
        
        self.create_todo_card(left_frame).grid(row=0, column=0, sticky="nsew", pady=(0, 20))
        self.create_tools_card(left_frame).grid(row=1, column=0, sticky="nsew")
        
        self.create_briefing_card(right_frame).grid(row=0, column=0, sticky="nsew", pady=(0, 20))
        self.create_schedule_card(right_frame).grid(row=1, column=0, sticky="nsew")

        self.update_clock()

    def update_clock(self):
        now_local = datetime.now()
        
        weekday_map = ["월", "화", "수", "목", "금", "토", "일"]
        weekday = weekday_map[now_local.weekday()]
        
        # --- 메인 시계 ---
        main_time_str = now_local.strftime("%H:%M:%S")
        main_date_str = now_local.strftime(f"%Y년 %m월 %d일 ({weekday})")
        self.main_clock_label.config(text=main_time_str)
        self.main_date_label.config(text=main_date_str)

        # --- 세계 시계 ---
        if pytz:
            now_utc = datetime.now(pytz.utc)
            cities_to_display = [
                (self.selected_city_1.get(), self.world_clock_label_1),
                (self.selected_city_2.get(), self.world_clock_label_2)
            ]
            for city_name, city_label in cities_to_display:
                try:
                    timezone_str = self.available_timezones[city_name]
                    target_tz = pytz.timezone(timezone_str)
                    target_time = now_utc.astimezone(target_tz)
                    city_time_str = target_time.strftime("%p %I:%M").replace("AM", "오전").replace("PM", "오후")
                    city_label.config(text=city_time_str)
                except Exception:
                    city_label.config(text="--:--")
        
        self.update_next_class_info(now_local, weekday)
        self.after(1000, self.update_clock)
        
    def update_next_class_info(self, now_local, today_weekday_str):
        next_class = None
        if self.schedule_data and today_weekday_str in self.schedule_data:
            today_schedule = self.schedule_data[today_weekday_str]
            current_time = now_local.time()
            for class_info in today_schedule:
                start_time = time.fromisoformat(class_info["start"])
                if start_time > current_time:
                    next_class = class_info
                    break
        if next_class:
            self.schedule_time_label.config(text=f"🕒 {next_class['start']} ~ {next_class['end']}")
            self.schedule_subject_label.config(text=f"{next_class['subject']}")
            self.schedule_room_label.config(text=f"🏫 {next_class['room']}")
        else:
            self.schedule_time_label.config(text="✅")
            self.schedule_subject_label.config(text="오늘의 수업이 모두 종료되었습니다.")
            self.schedule_room_label.config(text="")

    def create_schedule_card(self, parent):
        frame = self.create_card_frame(parent, "📚 다음 수업 & 학식")

        # --- 1. 다음 수업 정보 표시 부분 ---
        self.schedule_time_label = ttk.Label(frame, text="시간표 정보 로딩 중...", style="ScheduleTime.TLabel")
        self.schedule_time_label.pack(anchor="w", padx=10, pady=(0, 5))
        
        self.schedule_subject_label = ttk.Label(frame, text="", style="ScheduleSubject.TLabel")
        self.schedule_subject_label.pack(anchor="w", padx=10, pady=(0, 5))
        
        self.schedule_room_label = ttk.Label(frame, text="", style="CardBody.TLabel")
        self.schedule_room_label.pack(anchor="w", padx=10)

        # --- 2. 구분선 ---
        ttk.Separator(frame, orient='horizontal').pack(fill='x', pady=15)

        # --- 3. 학식 정보 표시 부분 ---
        self.menu_label = ttk.Label(frame, text="🍚 오늘의 학식: 로딩 중...", style="CardBody.TLabel")
        self.menu_label.pack(anchor="w", padx=10)

        # --- 4. 카드 생성 시 바로 학식 메뉴 업데이트 실행 ---
        self.update_menu()

        return frame
        
    def load_schedule(self):
        if not os.path.exists(self.schedule_file): return {}
        try:
            with open(self.schedule_file, 'r', encoding='utf-8') as f: return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError): return {}

    def create_card_frame(self, parent, title):
        frame = ttk.Frame(parent, style="Card.TFrame", padding=20)
        ttk.Label(frame, text=title, style="CardTitle.TLabel").pack(fill=tk.X, anchor="w", pady=(0, 15))
        return frame
    
    def create_tools_card(self, parent):
        frame = self.create_card_frame(parent, "🛠️ 빠른 실행 도구")
        ttk.Button(frame, text="📂 파일 정리 도구 실행", 
                   command=lambda: self.controller.show_frame("FileOrganizerPage"), 
                   style="Accent.TButton").pack(fill=tk.X, ipady=8, pady=(0, 10))
        ttk.Button(frame, text="🎵 YouTube Music 열기", 
                   command=self.open_youtube_music, 
                   style="Accent.TButton").pack(fill=tk.X, ipady=8, pady=(0, 10))
        ttk.Button(frame, text="🌐 Google 열기", 
                   command=self.open_chrome, 
                   style="Accent.TButton").pack(fill=tk.X, ipady= 8)
        return frame
    def open_youtube_music(self):
        webbrowser.open_new_tab("https://music.youtube.com")

    def open_chrome(self):
        webbrowser.open_new_tab("https://www.google.com")

    def create_todo_card(self, parent):
        frame = self.create_card_frame(parent, "✅ 할 일 목록 (To-Do List)")
        list_frame = ttk.Frame(frame, style="Card.TFrame")
        list_frame.pack(fill=tk.BOTH, expand=True)
        # ... (이하 할 일 목록 UI 및 로직은 이전과 동일)
        return frame

    def on_hover(self, event):
        event.widget.configure(font=("맑은 고딕", 10, "bold"), cursor="hand2")

    def on_leave(self, event):
        event.widget.configure(font=("맑은 고딕", 10, "normal"), cursor="")

    def open_link(self, url):
        if url:
            webbrowser.open_new_tab(url)

    def create_briefing_card(self, parent):
        frame = self.create_card_frame(parent, "🌤️ 오늘의 브리핑")
        ttk.Label(frame, text="날씨 정보 로딩 중...", style="CardBody.TLabel").pack(padx=10, pady=10)
        # --- 날씨 정보 표시 ---
        weather_label = ttk.Label(frame, text="날씨 정보 로딩 중...", style="CardBody.TLabel", font=("맑은 고딕", 11, "bold"))
        weather_label.pack(anchor="w", padx=10, pady=(0, 15))
        weather_label.config(text=get_weather_info()) # 함수 호출하여 날씨 업데이트

        # --- 구분선 ---
        ttk.Separator(frame, orient='horizontal').pack(fill='x', pady=(0, 15))

        # --- 주요 뉴스 헤드라인 표시 ---
        news_title_label = ttk.Label(frame, text="📰 주요 뉴스", style="CardBody.TLabel", font=("맑은 고딕", 10, "bold"))
        news_title_label.pack(anchor="w", padx=10, pady=(0, 5))

        # --- [수정] 뉴스 헤드라인 표시 루프 변경 ---
        headlines_data = get_news_headlines() # 이제 제목과 링크가 함께 들어옴
        
        for data in headlines_data:
            title = data["title"]
            link = data["link"]

            display_text = title if len(title) < 50 else title[:50] + "..."
            news_label = ttk.Label(frame, text=f"  - {display_text}", style="CardBody.TLabel")
            news_label.pack(anchor="w", padx=10)
            
            # --- 이벤트 바인딩 추가 ---
            # 1. 마우스를 올렸을 때 (Enter)
            news_label.bind("<Enter>", self.on_hover)
            # 2. 마우스가 벗어났을 때 (Leave)
            news_label.bind("<Leave>", self.on_leave)
            # 3. 마우스를 클릭했을 때 (Button-1)
            # lambda를 사용하여 클릭 시 실행될 함수에 현재 'link'를 전달
            news_label.bind("<Button-1>", lambda event, url=link: self.open_link(url))

        return frame
        
    def load_todo_items(self):
        if not os.path.exists(self.todo_file): return []
        try:
            with open(self.todo_file, 'r', encoding='utf-8') as f: return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError): return []

        # --- 학식 표시 부분 ---
        self.menu_label = ttk.Label(frame, text="🍚 오늘의 학식: 로딩 중...", style="CardBody.TLabel")
        self.menu_label.pack(anchor="w", padx=10)

        # 카드 생성 시 바로 학식 불러오기
        self.update_menu()

        return frame

    # DashboardPage 클래스 내부

    # DashboardPage 클래스 내부에 추가 (기존 것은 삭제)

    def update_menu(self):
        menus = school_.get_menu()
        if menus and "메뉴 불러오기 실패" not in menus[0]:
            today_str = datetime.now().strftime("%m/%d")
            
            found_menu = None
            for menu_string in menus:
                # "09/21(일): 메뉴..." 형식에서 날짜 부분("09/21")만 추출
                date_part = menu_string.split('(')[0]
                if date_part == today_str:
                    found_menu = menu_string
                    break
            
            if found_menu:
                display_menu = found_menu.split(': ', 1)[1]
                self.menu_label.config(text="🍚 오늘의 학식: " + display_menu)
            else:
                self.menu_label.config(text="🍚 오늘의 학식 정보를 찾을 수 없습니다.")
        else:
            self.menu_label.config(text=menus[0] if menus else "🍚 메뉴를 불러올 수 없습니다.")


# --- FileOrganizerPage 클래스 (이전과 동일) ---
class FileOrganizerPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, style="Main.TFrame")
        # ... (이하 파일 정리기 페이지의 모든 UI와 로직은 이전과 동일)

if __name__ == "__main__":
    if platform.system() == "Windows" and windll is not None:
        try:
            windll.shcore.SetProcessDPIAwareness(1)
        except AttributeError: pass

    root = tk.Tk()
    app = DesktopAssistant(root)
    root.mainloop()

    def save_todo_items(self):
        with open(self.todo_file, 'w', encoding='utf-8') as f:
            json.dump(self.todo_items, f, ensure_ascii=False, indent=4)
            
    def update_todo_listbox(self):
        self.todo_listbox.delete(0, tk.END)
        for item in self.todo_items:
            self.todo_listbox.insert(tk.END, " " + item["task"])
            if item.get("highlighted", False):
                self.todo_listbox.itemconfig(tk.END, {'fg': '#6A5ACD', 'font': ("맑은 고딕", 11, "bold")})
    
    def add_todo_item(self):
        task = self.todo_entry.get()
        if task:
            self.todo_items.append({"task": task, "highlighted": False})
            self.save_todo_items()
            self.update_todo_listbox()
            self.todo_entry.delete(0, tk.END)

    def remove_todo_item(self):
        selected_indices = self.todo_listbox.curselection()
        if not selected_indices: return
        for index in sorted(selected_indices, reverse=True): del self.todo_items[index]
        self.save_todo_items()
        self.update_todo_listbox()
        
    def highlight_todo_item(self):
        selected_indices = self.todo_listbox.curselection()
        if not selected_indices: return
        for index in selected_indices:
            item = self.todo_items[index]
            item["highlighted"] = not item.get("highlighted", False)
        self.save_todo_items()
        self.update_todo_listbox()


# --- FileOrganizerPage 클래스 ---
class FileOrganizerPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, style="Main.TFrame")
        self.controller = controller
        
        self.folder_path_var = tk.StringVar()
        self.dry_run_var = tk.BooleanVar(value=True)
        
        main_frame = ttk.Frame(self, style="Main.TFrame", padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        header_frame = ttk.Frame(main_frame, style="Main.TFrame")
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        back_button = ttk.Button(header_frame, text="← 뒤로가기", 
                                 command=lambda: controller.show_frame("DashboardPage"),
                                 style="Card.TButton")
        back_button.pack(side=tk.LEFT)
        
        header_label = ttk.Label(header_frame, text="파일 정리 도구", style="Header.TLabel")
        header_label.pack(side=tk.LEFT, padx=20)

        organizer_card = ttk.Frame(main_frame, style="Card.TFrame", padding=20)
        organizer_card.pack(fill=tk.BOTH, expand=True)
        
        step1_frame = ttk.Frame(organizer_card, style="Card.TFrame")
        step1_frame.pack(fill=tk.X, pady=(0, 20))
        step1_frame.columnconfigure(0, weight=1)

        ttk.Label(step1_frame, text="STEP 1: 정리할 폴더 선택", style="CardTitle.TLabel").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0,10))
        entry = ttk.Entry(step1_frame, textvariable=self.folder_path_var, font=("맑은 고딕", 10), style="Modern.TEntry")
        entry.grid(row=1, column=0, sticky="ew", ipady=5)
        button = ttk.Button(step1_frame, text="찾아보기...", command=self.select_folder, style="Card.TButton")
        button.grid(row=1, column=1, padx=(10,0))
        
        step2_frame = ttk.Frame(organizer_card, style="Card.TFrame")
        step2_frame.pack(fill=tk.X, pady=(0, 20))
        ttk.Label(step2_frame, text="STEP 2: 옵션 및 실행", style="CardTitle.TLabel").pack(anchor="w", pady=(0,10))
        ttk.Checkbutton(step2_frame, text="미리보기 모드 (실제 파일은 이동하지 않음)", variable=self.dry_run_var, style="Card.TCheckbutton").pack(anchor="w", pady=(0,15))
        ttk.Button(step2_frame, text="✨ 정리 시작 ✨", command=self.start_organization, style="Accent.TButton").pack(fill=tk.X, ipady=8)

        log_frame = ttk.Frame(organizer_card, style="Card.TFrame")
        log_frame.pack(fill=tk.BOTH, expand=True)
        ttk.Label(log_frame, text="진행 상황 로그", style="CardTitle.TLabel").pack(anchor="w", pady=(0,10))
        self.log_text = scrolledtext.ScrolledText(log_frame, font=("Consolas", 10), relief=tk.FLAT, 
                                                 bg="#fafafa", fg="#5D5D7A", borderwidth=1, state="disabled")
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def log_action(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.config(state="disabled")
        self.log_text.see(tk.END)
        self.controller.root.update_idletasks()
    
    def select_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path_var.set(folder_selected)

    def start_organization(self):
        target_folder = self.folder_path_var.get()
        if not target_folder:
            self.log_action("[에러] 정리할 폴더를 선택해주세요.")
            return

        is_dry_run = self.dry_run_var.get()
        mode = "미리보기" if is_dry_run else "실제 이동"
        self.log_text.config(state="normal")
        self.log_text.delete('1.0', tk.END)
        self.log_text.config(state="disabled")
        self.log_action(f"====== 파일 정리 작업을 시작합니다. (모드: {mode}) ======")

        try:
            file_list = os.listdir(target_folder)
        except FileNotFoundError:
            self.log_action(f"[에러] '{target_folder}' 폴더를 찾을 수 없습니다.")
            return

        for file_name in file_list:
            source_path = os.path.join(target_folder, file_name)
            if os.path.isdir(source_path):
                continue

            destination_path = self.get_destination_path(target_folder, file_name)

            if destination_path:
                final_destination = os.path.join(destination_path, file_name)
                os.makedirs(destination_path, exist_ok=True)
                
                if is_dry_run:
                    self.log_action(f"[이동 계획 ✔️] '{file_name}' -> '{destination_path}'")
                else:
                    try:
                        shutil.move(source_path, final_destination)
                        self.log_action(f"[이동 완료 ✅] '{file_name}' -> '{destination_path}'")
                    except Exception as e:
                        self.log_action(f"[에러] '{file_name}' 이동 실패: {e}")
            else:
                self.log_action(f"[패스 ❔] '{file_name}' (적용 규칙 없음)")

        self.log_action("====== 파일 정리 작업이 모두 완료되었습니다. ======")
        
        if not is_dry_run:
            try:
                if platform.system() == "Windows":
                    os.startfile(target_folder)
                elif platform.system() == "Darwin":
                    import subprocess
                    subprocess.call(["open", target_folder])
                else:
                    import subprocess
                    subprocess.call(["xdg-open", target_folder])
            except Exception as e:
                self.log_action(f"[정보] 폴더를 여는 데 실패했습니다: {e}")

    def get_destination_path(self, target_folder, file_name):
        base_dest_path = None
        
        keyword_rules = {
            '파이썬': os.path.join(target_folder, '파이썬'),
            '자바': os.path.join(target_folder, '자바'),
            '알고리즘': os.path.join(target_folder, '알고리즘'),
        }

        for keyword, path in keyword_rules.items():
            if keyword in file_name.lower():
                base_dest_path = path
                break
        
        date_pattern = re.compile(r'(\d{4}|\d{2})[-._]?(\d{2})[-._]?(\d{2})')
        match = date_pattern.search(file_name)

        if base_dest_path:
            if match:
                year, month, _ = match.groups()
                year = "20" + year if len(year) == 2 else year
                return os.path.join(base_dest_path, f'{year}년', f'{month}월')
            
            ext = file_name.split('.')[-1].lower()
            subfolder_rules = {
                'pdf': '문서', 'docx': '문서', 'pptx': '문서',
                'jpg': '이미지', 'png': '이미지', 'gif': '이미지',
                'txt': '노트'
            }
            if ext in subfolder_rules:
                return os.path.join(base_dest_path, subfolder_rules[ext])
            
            return base_dest_path
        else:
            if match:
                year, month, _ = match.groups()
                year = "20" + year if len(year) == 2 else year
                return os.path.join(target_folder, '날짜별 정리', f'{year}년', f'{month}월')

            ext = file_name.split('.')[-1].lower()
            ext_rules = {
                'pdf': '문서', 'docx': '문서', 'pptx': '문서',
                'jpg': '이미지', 'png': '이미지', 'gif': '이미지',
                'txt': '노트',
                'zip': '압축파일', 'rar': '압축파일'
            }
            if ext in ext_rules:
                return os.path.join(target_folder, ext_rules[ext])
        
        return None

