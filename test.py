import tkinter as tk
from tkinter import ttk, font, Toplevel, filedialog, scrolledtext
import json
import os
import random
import platform
import shutil
import re
from datetime import datetime, time as dt_time
import time
import requests                     #사용할 때 pip install requests webbrowser feedparser beautifulsoup4 을 먼저 해주세요.
import webbrowser
import feedparser
import subprocess
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    #from webdriver_manager.chrome import ChromeDriverManager
    import pytz
except ImportError:
    pytz = None

try:
    from ctypes import windll
except ImportError:
    windll = None

# --- 전역 함수들 (Global Functions) ---
WEATHER_API_KEY = "ad5c1b86467191a4ab639840195b08c4"

def get_weather_info():
    try:
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
        if not feed.entries:
            return [{"title": "새로운 뉴스가 없습니다.", "link": ""}]
        headlines_with_links = [{"title": entry.title, "link": entry.link} for entry in feed.entries[:max_headlines]]
        return headlines_with_links
    except Exception as e:
        print(f"뉴스 정보 로딩 중 예외 발생: {e}")
        return [{"title": "주요 뉴스를 불러오는 중 오류가 발생했습니다.", "link": ""}]
    
class school_:
    @staticmethod
    def get_menu():
        url = "https://www.tw.ac.kr/diet/schedule.do?menuId=1733"
        
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # 브라우저 창을 띄우지 않음
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        # 불필요한 로그 메시지 제거
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        driver = None
        try:
            # ChromeDriver를 자동으로 설치 및 관리합니다.
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            driver.get(url)
            
            # 페이지의 식단표 테이블('tbl')이 로드될 때까지 최대 10초간 기다립니다.
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "tbl"))
            )
            
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")

            # thead의 첫 번째 tr에 있는 th들을 모두 선택 (요일)
            day_cells = soup.select("thead tr:first-child th")
            # tbody의 첫 번째 tr에 있는 td들을 모두 선택 (메뉴)
            menu_cells = soup.select("tbody tr:first-child td")

            # [진단용 출력]
            print("-" * 30)
            print(f"[진단] 찾은 요일 셀 개수: {len(day_cells)}개")
            print(f"[진단] 찾은 메뉴 셀 개수: {len(menu_cells)}개")
            
            # 첫 번째 요일 셀("구분")은 제외하고 리스트를 다시 만듭니다.
            day_cells = day_cells[1:]

            # 요일과 메뉴의 개수가 다르면 오류를 반환합니다.
            if len(day_cells) != len(menu_cells):
                print("[진단] 오류: 요일과 메뉴 셀 개수가 일치하지 않습니다.")
                return [{"day": "오류", "menu": "웹사이트 구조 분석 실패"}]

            weekly_menu = []
            for day_cell, menu_cell in zip(day_cells, menu_cells):
                # "월요일<br>09월 22일" 형태에서 "월요일"만 추출합니다.
                day_of_week = day_cell.get_text(separator=" ").split()[0]
                
                # 메뉴 셀 내부의 <br> 태그를 줄바꿈(\n) 문자로 변경합니다.
                for br in menu_cell.find_all("br"):
                    br.replace_with("\n")
                
                # 공백을 제거하여 메뉴 텍스트를 추출합니다.
                food = menu_cell.get_text(strip=True)
                
                # 메뉴 내용이 없거나 "-" 이면 "정보 없음"으로 표시합니다.
                if not food or food == "-":
                    food = "정보 없음"
                
                weekly_menu.append({"day": day_of_week, "menu": food})
            
            print("[진단] 학식 메뉴 파싱 성공!")
            return weekly_menu
            
        except Exception as e:
            print(f"[진단] 학식 메뉴 파싱 중 예외 발생: {e}")
            return [{"day": "오류", "menu": "메뉴를 불러올 수 없습니다."}]
        finally:
            # 드라이버가 실행되었다면 반드시 종료합니다.
            if driver:
                driver.quit()

# --- 코드 테스트 ---
if __name__ == '__main__':
    menus = school_.get_menu()
    for menu in menus:
        print(f"[{menu['day']}]\n{menu['menu']}\n\n")

# --- 메인 애플리케이션 클래스 ---
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
        HOVER_BG_COLOR = "#F0EDF9"  # 연한 보라색 배경
        style.configure("Hover.TFrame", background=HOVER_BG_COLOR)
        style.configure("Hover.TLabel", background=HOVER_BG_COLOR)
        
        style.configure("Main.TFrame", background=BG_COLOR)
        style.configure("Card.TFrame", background=CARD_BG_COLOR, borderwidth=1, relief="solid", bordercolor=BORDER_COLOR)
        style.configure("Header.TLabel", background=BG_COLOR, foreground=HEADER_COLOR, font=("맑은 고딕", 20, "bold"))
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
        style.configure("Modern.TEntry", bordercolor=BORDER_COLOR, lightcolor=BORDER_COLOR, darkcolor=BORDER_COLOR, fieldbackground="white", foreground=TEXT_COLOR, font=("맑은 고딕", 10))
        style.configure("Modern.Vertical.TScrollbar", troughcolor=BG_COLOR, bordercolor=BG_COLOR, background="#D3D3D3", arrowcolor=TEXT_COLOR)
        style.configure("Card.TCheckbutton", background=CARD_BG_COLOR, font=("맑은 고딕", 10), foreground=TEXT_COLOR)
        style.map('Card.TCheckbutton', indicatorcolor=[('selected', ACCENT_COLOR), ('!selected', '#d3d3d3')], background=[('active', '#f5f5f5')])

# --- 대시보드 페이지 클래스 ---
class DashboardPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, style="Main.TFrame")
        self.controller = controller
        self.todo_file = "todo_list.json"
        self.todo_items = self.load_todo_items()
        self.schedule_file = "schedule.json"
        self.schedule_data = self.load_schedule()
        self.available_timezones = {"뉴욕": "America/New_York", "런던": "Europe/London", "파리": "Europe/Paris", "도쿄": "Asia/Tokyo", "시드니": "Australia/Sydney", "베이징": "Asia/Shanghai", "모스크바": "Europe/Moscow"}
        self.selected_city_1 = tk.StringVar(value="뉴욕")
        self.selected_city_2 = tk.StringVar(value="도쿄")
        
        main_frame = ttk.Frame(self, style="Main.TFrame", padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        header_frame = ttk.Frame(main_frame, style="Main.TFrame")
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(header_frame, text="My Dashboard", style="Header.TLabel").pack(side=tk.LEFT)
        
        clock_container = ttk.Frame(header_frame, style="Main.TFrame")
        clock_container.pack(side=tk.RIGHT)
        self.main_clock_label = ttk.Label(clock_container, text="--:--:--", style="MainClock.TLabel")
        self.main_clock_label.pack(anchor="e")
        self.main_date_label = ttk.Label(clock_container, text="----년 --월 --일 (-)", style="SubClock.TLabel")
        self.main_date_label.pack(anchor="e")

        world_clock_frame_1 = ttk.Frame(clock_container, style="Main.TFrame")
        world_clock_frame_1.pack(anchor="e", pady=(5,0))
        self.world_clock_label_1 = ttk.Label(world_clock_frame_1, text="--:--", style="SubClock.TLabel", width=10, anchor="e")
        self.world_clock_label_1.pack(side=tk.RIGHT)
        city_combo_1 = ttk.Combobox(world_clock_frame_1, textvariable=self.selected_city_1, values=list(self.available_timezones.keys()), state="readonly", width=6, style="WorldClock.TCombobox")
        city_combo_1.pack(side=tk.RIGHT, padx=(0, 5))
        city_combo_1.bind("<<ComboboxSelected>>", self.clear_focus)
        
        world_clock_frame_2 = ttk.Frame(clock_container, style="Main.TFrame")
        world_clock_frame_2.pack(anchor="e")
        self.world_clock_label_2 = ttk.Label(world_clock_frame_2, text="--:--", style="SubClock.TLabel", width=10, anchor="e")
        self.world_clock_label_2.pack(side=tk.RIGHT)
        city_combo_2 = ttk.Combobox(world_clock_frame_2, textvariable=self.selected_city_2, values=list(self.available_timezones.keys()), state="readonly", width=6, style="WorldClock.TCombobox")
        city_combo_2.pack(side=tk.RIGHT, padx=(0, 5))
        city_combo_2.bind("<<ComboboxSelected>>", self.clear_focus)

        dashboard_frame = ttk.Frame(main_frame, style="Main.TFrame")
        dashboard_frame.pack(fill=tk.BOTH, expand=True)
        dashboard_frame.grid_columnconfigure(0, weight=2, uniform="group1")
        dashboard_frame.grid_columnconfigure(1, weight=3, uniform="group1")
        dashboard_frame.grid_rowconfigure(0, weight=1, minsize=200) # 최소 높이 지정
        dashboard_frame.grid_rowconfigure(1, weight=1, minsize=400) # 최소 높이 지정

        left_frame = ttk.Frame(dashboard_frame, style="Main.TFrame")
        left_frame.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 20))
        left_frame.grid_rowconfigure(0, weight=1)
        left_frame.grid_rowconfigure(1, minsize=200) # 빠른 실행 도구 최소 높이

        right_frame = ttk.Frame(dashboard_frame, style="Main.TFrame")
        right_frame.grid(row=0, column=1, rowspan=2, sticky="nsew")
        right_frame.grid_rowconfigure(0, weight=1)
        right_frame.grid_rowconfigure(1, weight=1)
        
        self.create_todo_card(left_frame).grid(row=0, column=0, sticky="nsew", pady=(0, 20))
        self.create_tools_card(left_frame).grid(row=1, column=0, sticky="nsew")
        
        self.create_briefing_card(right_frame).grid(row=0, column=0, sticky="nsew", pady=(0, 20))
        self.create_schedule_card(right_frame).grid(row=1, column=0, sticky="nsew")

        self.update_clock()
        self.after(100, self.load_initial_data)

        # 주요 배경 프레임들을 클릭했을 때 clear_selections 함수가 호출되도록 설정
        main_frame.bind("<Button-1>", self.clear_selections)
        dashboard_frame.bind("<Button-1>", self.clear_selections)

    def clear_selections(self, event=None):
       # 선택된 포커스 효과 제거
        self.focus_set()
        self.todo_listbox.selection_clear(0, tk.END)

    def clear_focus(self, event):
        self.focus_set()

    def load_initial_data(self):
        """UI가 생성된 후, 네트워크 데이터를 비동기적으로 로드합니다."""
        # 현재 날씨 업데이트
        self.weather_label.config(text=get_weather_info())

        # 뉴스 헤드라인 업데이트
        for widget in self.news_container.winfo_children():
            widget.destroy()
            
        headlines_data = get_news_headlines()
        for data in headlines_data:
            title = data["title"]
            link = data["link"]
            display_text = title if len(title) < 50 else title[:50] + "..."
            news_label = ttk.Label(self.news_container, text=f"  - {display_text}", style="CardBody.TLabel")
            news_label.pack(anchor="w", padx=10)
            news_label.bind("<Enter>", self.on_hover)
            news_label.bind("<Leave>", self.on_leave)
            news_label.bind("<Button-1>", lambda event, url=link: self.open_link(url))

        # 학식 메뉴 업데이트
        self.update_menu()
    
    def update_clock(self):
        now_local = datetime.now()
        weekday = ["월", "화", "수", "목", "금", "토", "일"][now_local.weekday()]
        main_time_str = now_local.strftime("%H:%M:%S")
        main_date_str = now_local.strftime(f"%Y년 %m월 %d일 ({weekday})")
        self.main_clock_label.config(text=main_time_str)
        self.main_date_label.config(text=main_date_str)
        if pytz:
            now_utc = datetime.now(pytz.utc)
            for city_name, city_label in [(self.selected_city_1.get(), self.world_clock_label_1), (self.selected_city_2.get(), self.world_clock_label_2)]:
                try:
                    target_tz = pytz.timezone(self.available_timezones[city_name])
                    target_time = now_utc.astimezone(target_tz)
                    city_time_str = target_time.strftime("%p %I:%M").replace("AM", "오전").replace("PM", "오후")
                    city_label.config(text=city_time_str)
                except Exception:
                    city_label.config(text="--:--")
        self.update_next_class_info(now_local, weekday)
        self.after(1000, self.update_clock)
        
    def update_next_class_info(self, now_local, today_weekday_str):
        target_class = None
        is_in_session = False  # 현재 수업 중인지 상태를 기록하는 변수

        if self.schedule_data and today_weekday_str in self.schedule_data:
            today_schedule = self.schedule_data[today_weekday_str]
            current_time = now_local.time()

            if today_schedule:
                for class_info in today_schedule:
                    start_time = dt_time.fromisoformat(class_info["start"])
                    end_time = dt_time.fromisoformat(class_info["end"]) # 종료 시간도 가져옴

                    # 1. '현재 진행 중인 수업'이 있는지 먼저 확인
                    if start_time <= current_time < end_time:
                        target_class = class_info
                        is_in_session = True
                        break  # 현재 수업을 찾았으므로 더 이상 찾을 필요 없음

                    # 2. '다가올 다음 수업'이 있는지 확인
                    if start_time > current_time:
                        target_class = class_info
                        is_in_session = False
                        break  # 가장 가까운 다음 수업을 찾았으므로 더 이상 찾을 필요 없음

        # --- 찾은 결과를 바탕으로 UI 업데이트 ---
        if target_class:
            # 'is_in_session' 값에 따라 다른 상태 메시지를 표시
            status_icon = "🔥" if is_in_session else "🕒"
            status_text = "현재 수업" if is_in_session else "다음 수업"

            self.schedule_time_label.config(text=f"{status_icon} {status_text}: {target_class['start']} ~ {target_class['end']}")
            self.schedule_subject_label.config(text=f"{target_class['subject']}")
            self.schedule_room_label.config(text=f"🏫 {target_class['room']}")
        else:
            # 보여줄 수업이 없으면 (모든 수업이 종료되었으면)
            self.schedule_time_label.config(text="✅")
            self.schedule_subject_label.config(text="오늘의 수업이 모두 종료되었습니다.")
            self.schedule_room_label.config(text="")

    def create_card_frame(self, parent, title):
        frame = ttk.Frame(parent, style="Card.TFrame", padding=20)
        ttk.Label(frame, text=title, style="CardTitle.TLabel").pack(fill=tk.X, anchor="w", pady=(0, 15))
        return frame
    
    def _on_menu_column_configure(self, event):
        # event.widget은 크기가 변경된 col_frame을 의미합니다.
        # 이 프레임의 현재 너비를 가져옵니다.
        new_width = event.widget.winfo_width()
        # 이 프레임에 연결된 menu_label을 찾아 wraplength를 업데이트합니다.
        event.widget.menu_label.config(wraplength=new_width - 10)
        
    def create_schedule_card(self, parent):
        frame = self.create_card_frame(parent, "📚 다음 수업 & 주간 학식")
        
        class_info_frame = ttk.Frame(frame, style="Card.TFrame")
        class_info_frame.pack(fill=tk.X, padx=10, pady=(0, 15))
        
        self.schedule_time_label = ttk.Label(class_info_frame, text="시간표 정보 로딩 중...", style="ScheduleTime.TLabel")
        self.schedule_time_label.pack(anchor="w")
        self.schedule_subject_label = ttk.Label(class_info_frame, text="", style="ScheduleSubject.TLabel")
        self.schedule_subject_label.pack(anchor="w")
        self.schedule_room_label = ttk.Label(class_info_frame, text="", style="CardBody.TLabel")
        self.schedule_room_label.pack(anchor="w")
        
        ttk.Separator(frame, orient='horizontal').pack(fill='x', pady=(0, 15))
        
        menu_table_frame = ttk.Frame(frame, style="Card.TFrame")
        menu_table_frame.pack(fill=tk.BOTH, expand=True, padx=10)

        for i in range(5):
            menu_table_frame.grid_columnconfigure(i, weight=1, uniform="menu_col")

        self.menu_columns = []
        days = ["월", "화", "수", "목", "금"]
        
        for i, day in enumerate(days):
            col_frame = ttk.Frame(menu_table_frame, style="Card.TFrame")
            col_frame.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 10, 0))

            day_label = ttk.Label(col_frame, text=day, style="MenuDay.TLabel")
            day_label.pack(fill=tk.X, pady=(0, 5))
            
            ttk.Separator(col_frame, orient='horizontal').pack(fill='x', pady=(0, 8))
            
            menu_label = ttk.Label(col_frame, text="로딩 중...", style="MenuBody.TLabel", justify=tk.LEFT)
            menu_label.pack(fill=tk.BOTH, expand=True)
            
            # ▼▼▼ 핵심 수정 부분 ▼▼▼
            # 각 열 프레임(col_frame)에 메뉴 라벨을 속성으로 저장
            col_frame.menu_label = menu_label 
            # 각 열 프레임의 크기가 변경될 때마다(_on_menu_column_configure) 함수를 호출하도록 연결
            col_frame.bind("<Configure>", self._on_menu_column_configure)
            # ▲▲▲ 여기까지 수정 ▲▲▲

            self.menu_columns.append({
                "frame": col_frame,
                "day_label": day_label,
                "menu_label": menu_label
            })
            
        return frame
        
    def create_briefing_card(self, parent):
        frame = self.create_card_frame(parent, "🌤️ 오늘의 브리핑")

        # --- 1. 현재 날씨 정보 ---
        # 클릭하면 날씨 사이트로 이동하도록 cursor와 bind를 추가합니다.
        self.weather_label = ttk.Label(frame, text="날씨 정보 로딩 중...", style="CardBody.TLabel", font=("맑은 고딕", 11, "bold"), cursor="hand2")
        self.weather_label.pack(anchor="w", padx=10, pady=(0, 15))
        self.weather_label.bind("<Button-1>", self.open_weather_website)

        # --- 2. 구분선 ---
        ttk.Separator(frame, orient='horizontal').pack(fill='x', pady=(0, 15))

        # --- 3. 주요 뉴스 헤드라인 ---
        ttk.Label(frame, text="📰 주요 뉴스", style="CardBody.TLabel", font=("맑은 고딕", 10, "bold")).pack(anchor="w", padx=10, pady=(0, 5))
        
        # 뉴스가 표시될 컨테이너
        self.news_container = ttk.Frame(frame, style="Card.TFrame")
        self.news_container.pack(fill=tk.X, anchor="w")
        ttk.Label(self.news_container, text="  - 로딩 중...", style="CardBody.TLabel").pack(anchor="w", padx=10)

        return frame


    def create_tools_card(self, parent):
        frame = self.create_card_frame(parent, "🛠️ 빠른 실행 도구")
        ttk.Button(frame, text="📂 파일 정리 도구 실행", command=lambda: self.controller.show_frame("FileOrganizerPage"), style="Accent.TButton").pack(fill=tk.X, ipady=8, pady=(0, 10))
        ttk.Button(frame, text="🎵 YouTube Music 열기", command=self.open_youtube_music, style="Accent.TButton").pack(fill=tk.X, ipady=8, pady=(0, 10))
        ttk.Button(frame, text="🌐 Google 열기", command=self.open_chrome, style="Accent.TButton").pack(fill=tk.X, ipady= 8)
        return frame

    def create_todo_card(self, parent):
        frame = self.create_card_frame(parent, "✅ 할 일 목록 (To-Do List)")
        list_container = ttk.Frame(frame, style="Card.TFrame")
        list_container.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        scrollbar = ttk.Scrollbar(list_container, orient=tk.VERTICAL, style="Modern.Vertical.TScrollbar")
        self.todo_listbox = tk.Listbox(list_container, yscrollcommand=scrollbar.set, font=("맑은 고딕", 10), relief=tk.FLAT, borderwidth=0, selectbackground="#E8E2F7", activestyle="none", highlightthickness=0)
        scrollbar.config(command=self.todo_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.todo_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        entry_frame = ttk.Frame(frame, style="Card.TFrame")
        entry_frame.pack(fill=tk.X, pady=(5, 0))
        entry_frame.columnconfigure(0, weight=1)
        self.todo_entry = tk.Entry(entry_frame, font=("맑은 고딕", 10), relief=tk.FLAT, bg="white", fg="#5D5D7A", highlightthickness=1, highlightbackground="#EDE9F2")
        self.todo_entry.grid(row=0, column=0, sticky="ew", ipady=5)
        ttk.Button(entry_frame, text="추가", command=self.add_todo_item, style="Card.TButton", width=5).grid(row=0, column=1, padx=(5,0))
        button_frame = ttk.Frame(frame, style="Card.TFrame")
        button_frame.pack(fill=tk.X, pady=(5, 0))
        ttk.Button(button_frame, text="선택 삭제", command=self.remove_todo_item, style="Card.TButton").pack(side=tk.RIGHT)
        ttk.Button(button_frame, text="강조/해제", command=self.highlight_todo_item, style="Card.TButton").pack(side=tk.RIGHT, padx=(0, 5))
        self.update_todo_listbox()
        return frame

    def load_schedule(self):
        if not os.path.exists(self.schedule_file):
        # 터미널에 파일이 없다고 출력합니다.
            print(f"[진단] '{self.schedule_file}' 파일을 찾을 수 없습니다. 파이썬 파일과 같은 폴더에 있는지 확인하세요.")
            return {}
        try:
            with open(self.schedule_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            # 터미널에 파일 로딩 성공 및 내용 일부를 출력합니다.
                print(f"[진단] '{self.schedule_file}' 파일을 성공적으로 불러왔습니다.")
                return data
        except (json.JSONDecodeError, FileNotFoundError):
        # 터미널에 JSON 형식 오류를 출력합니다.
            print(f"[진단] '{self.schedule_file}' 파일의 형식이 잘못되었습니다. (예: 쉼표, 괄호 문제)")
            return {}

    def load_todo_items(self):
        if not os.path.exists(self.todo_file): return []
        try:
            with open(self.todo_file, 'r', encoding='utf-8') as f: return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError): return []
    
    def open_youtube_music(self):
        webbrowser.open_new_tab("https://music.youtube.com")

    def open_chrome(self):
        webbrowser.open_new_tab("https://www.google.com")

    def on_hover(self, event):
        event.widget.configure(font=("맑은 고딕", 10, "bold"), cursor="hand2")

    def on_leave(self, event):
        event.widget.configure(font=("맑은 고딕", 10, "normal"), cursor="")

    def open_link(self, url):
        if url:
            webbrowser.open_new_tab(url)

    def update_menu(self):
        weekly_menus = school_.get_menu()
        today_weekday_str = ["월", "화", "수", "목", "금", "토", "일"][datetime.now().weekday()]

        if not weekly_menus or "오류" in weekly_menus[0]["day"]:
            error_msg = weekly_menus[0]["menu"] if weekly_menus else "학식 정보를 불러올 수 없습니다."
            for col in self.menu_columns:
                col["menu_label"].config(text=error_msg)
            return

        for i, menu_data in enumerate(weekly_menus):
            if i >= len(self.menu_columns): break

            col_ui = self.menu_columns[i]
            # wraplength 설정 코드를 여기서 제거합니다.
            col_ui["menu_label"].config(text=menu_data["menu"])

            if menu_data["day"].startswith(today_weekday_str):
                col_ui["frame"].config(style="Today.TFrame")
                col_ui["day_label"].config(style="Today.MenuDay.TLabel")
                col_ui["menu_label"].config(style="Today.MenuBody.TLabel")
            else:
                col_ui["frame"].config(style="Card.TFrame")
                col_ui["day_label"].config(style="MenuDay.TLabel")
                col_ui["menu_label"].config(style="MenuBody.TLabel")

    def open_weather_website(self, event=None):
        """OpenWeatherMap의 서울 날씨 페이지를 엽니다."""
        webbrowser.open_new_tab("https://openweathermap.org/city/1835848")

    def on_forecast_enter(self, event, widgets):
        """마우스가 위젯에 들어왔을 때 강조 효과를 적용합니다."""
        for widget in widgets:
            # ttk 위젯 종류에 따라 다른 스타일을 적용합니다.
            if isinstance(widget, ttk.Frame):
                widget.config(style="Hover.TFrame")
            else:
                widget.config(style="Hover.TLabel")

    def on_forecast_leave(self, event, widgets):
        """마우스가 위젯에서 벗어났을 때 강조 효과를 해제합니다."""
        for widget in widgets:
            # 원래의 기본 스타일로 되돌립니다.
            if isinstance(widget, ttk.Frame):
                widget.config(style="Card.TFrame")
            else:
                widget.config(style="CardBody.TLabel")
            
    def save_todo_items(self):
        with open(self.todo_file, 'w', encoding='utf-8') as f:
            json.dump(self.todo_items, f, ensure_ascii=False, indent=4)
            
    def update_todo_listbox(self):
        self.todo_listbox.delete(0, tk.END)
        for index, item in enumerate(self.todo_items):
            self.todo_listbox.insert(tk.END, " " + item["task"])
        if item.get("highlighted", False):
            # font 옵션을 제거하고 색상만 변경합니다.
            self.todo_listbox.itemconfig(index, {'fg': '#6A5ACD'})
        else:
            # font 옵션을 제거하고 기본 색상으로 되돌립니다.
            self.todo_listbox.itemconfig(index, {'fg': '#5D5D7A'})

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

# --- 파일 정리기 페이지 클래스 ---
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
        
        ttk.Button(header_frame, text="← 뒤로가기", command=lambda: controller.show_frame("DashboardPage"), style="Card.TButton").pack(side=tk.LEFT)
        ttk.Label(header_frame, text="파일 정리 도구", style="Header.TLabel").pack(side=tk.LEFT, padx=20)

        organizer_card = ttk.Frame(main_frame, style="Card.TFrame", padding=20)
        organizer_card.pack(fill=tk.BOTH, expand=True)
        
        step1_frame = ttk.Frame(organizer_card, style="Card.TFrame")
        step1_frame.pack(fill=tk.X, pady=(0, 20))
        step1_frame.columnconfigure(0, weight=1)

        ttk.Label(step1_frame, text="STEP 1: 정리할 폴더 선택", style="CardTitle.TLabel").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0,10))
        ttk.Entry(step1_frame, textvariable=self.folder_path_var, font=("맑은 고딕", 10), style="Modern.TEntry").grid(row=1, column=0, sticky="ew", ipady=5)
        ttk.Button(step1_frame, text="찾아보기...", command=self.select_folder, style="Card.TButton").grid(row=1, column=1, padx=(10,0))
        
        step2_frame = ttk.Frame(organizer_card, style="Card.TFrame")
        step2_frame.pack(fill=tk.X, pady=(0, 20))
        ttk.Label(step2_frame, text="STEP 2: 옵션 및 실행", style="CardTitle.TLabel").pack(anchor="w", pady=(0,10))
        ttk.Checkbutton(step2_frame, text="미리보기 모드 (실제 파일은 이동하지 않음)", variable=self.dry_run_var, style="Card.TCheckbutton").pack(anchor="w", pady=(0,15))
        ttk.Button(step2_frame, text="✨ 정리 시작 ✨", command=self.start_organization, style="Accent.TButton").pack(fill=tk.X, ipady=8)

        log_frame = ttk.Frame(organizer_card, style="Card.TFrame")
        log_frame.pack(fill=tk.BOTH, expand=True)
        ttk.Label(log_frame, text="진행 상황 로그", style="CardTitle.TLabel").pack(anchor="w", pady=(0,10))
        self.log_text = scrolledtext.ScrolledText(log_frame, font=("Consolas", 10), relief=tk.FLAT, bg="#fafafa", fg="#5D5D7A", borderwidth=1, state="disabled")
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def log_action(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.config(state="disabled")
        self.log_text.see(tk.END)
        self.controller.root.update_idletasks() # self.root를 self.controller.root
    
    def select_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path_var.set(folder_selected)

    def find_keyword_in_file(self, file_path, keywords):
        """TXT 파일의 내용을 읽고, 지정된 키워드 목록 중 하나라도 포함되어 있는지 확인합니다."""
        try:
            # 파일을 utf-8 형식으로 엽니다. 다른 형식의 파일이 있다면 encoding을 변경해야 할 수 있습니다.
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                for keyword in keywords:
                    if keyword in content:
                        return keyword # 키워드를 찾으면 해당 키워드를 반환
        except Exception as e:
            self.log_action(f"[경고] '{os.path.basename(file_path)}' 파일 읽기 실패: {e}")
        return None # 키워드를 찾지 못하면 None을 반환

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

        # ▼▼▼ 새로 추가된 디버깅 코드 ▼▼▼
        # 선택한 폴더에서 찾은 파일 목록을 먼저 보여줍니다.
        self.log_action(f"\n====== '{os.path.basename(target_folder)}' 폴더에서 발견된 파일 목록 ======")
        if not file_list:
            self.log_action(" -> 폴더가 비어있거나 파일을 찾을 수 없습니다.")
        else:
            for f_name in file_list:
                self.log_action(f" -> {f_name}")
        self.log_action("====================================================\n")
        # ▲▲▲ 여기까지 추가 ▲▲▲

        for file_name in file_list:
            source_path = os.path.join(target_folder, file_name)
            if os.path.isdir(source_path):
                continue

            destination_path = self.get_destination_path(target_folder, file_name)

            if destination_path:
                final_destination_file_path = os.path.join(destination_path, file_name)
                os.makedirs(destination_path, exist_ok=True)
                
                if is_dry_run:
                    self.log_action(f"[이동 계획 ✔️] '{file_name}' -> '{os.path.relpath(destination_path, target_folder)}' 폴더")
                else:
                    try:
                        shutil.move(source_path, final_destination_file_path)
                        self.log_action(f"[이동 완료 ✅] '{file_name}' -> '{os.path.relpath(destination_path, target_folder)}' 폴더")
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
                    subprocess.run(["open", target_folder])
                else:
                    subprocess.run(["xdg-open", target_folder])
            except Exception as e:
                self.log_action(f"[정보] 폴더를 여는 데 실패했습니다: {e}")

    def get_destination_path(self, target_folder, file_name):
        # --- 1순위: 과목 폴더 결정 ---
        subject_path = None
        # 이곳에 '파일이름에 포함될 키워드': '실제 생성될 폴더명'을 추가/수정하세요.
        keyword_rules = {
            '파이썬': '파이썬',
            '파이' : '파이썬',
            'python': '파이썬',
            '자바': '자바',
            'java': '자바',
            '알고리즘': '알고리즘',
            '웹 프로그래밍': '웹 프로그래밍',
            '웹프로그래밍' : '웹 프로그래밍',
            '웹 코드' : '웹 프로그래밍'
        }

        for keyword, folder_name in keyword_rules.items():
            if keyword in file_name.lower():
                subject_path = os.path.join(target_folder, folder_name)
                break
        
        if not subject_path:
            subject_path = os.path.join(target_folder, '미분류')

        # --- 2순위: 날짜 폴더 결정 ---
        date_folder_name = ""
        date_pattern = re.compile(r'(\d{4}|\d{2})[-._]?(\d{2})[-._]?(\d{2})')
        match = date_pattern.search(file_name)

        if match:
            year, month, day = match.groups()
            year = "20" + year if len(year) == 2 else year
            date_folder_name = f"{year}.{month}.{day}"
        else:
            date_folder_name = datetime.now().strftime('%Y.%m.%d')
            
        path_with_date = os.path.join(subject_path, date_folder_name)

        # --- 3순위: 확장자 폴더 결정 ---
        ext = os.path.splitext(file_name)[1].lower().strip('.')
        
        # ▼▼▼ 오타 수정 부분 ▼▼▼
        if not ext:
            # 확장자가 없는 파일은 날짜 폴더 경로를 바로 반환
            return path_with_date # 'path_with_data' -> 'path_with_date'로 수정
        
        final_path = os.path.join(path_with_date, ext)
        
        return final_path

if __name__ == "__main__":
    if platform.system() == "Windows" and windll is not None:
        try:
            windll.shcore.SetProcessDPIAwareness(1)
        except AttributeError: pass

    root = tk.Tk()
    app = DesktopAssistant(root)
    root.mainloop()