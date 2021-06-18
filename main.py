from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from datetime import date
import gspread
from time import sleep
from os.path import expanduser
import pyperclip

credentials = {<credentials>}
gc = gspread.service_account_from_dict(credentials)
home = expanduser("~")
bool = False

try:
    file = open(f'{home}/KEY_STATE.txt', 'r')
    key = file.read()
    sh = gc.open_by_key(key)
    ws = sh.sheet1
    bool = True
except:
    filew = open(f'{home}/KEY_STATE.txt', 'w')

Window.size = (450, 550)


def back_to_main(*args):
    MDApp.get_running_app().root.current = "mainScreen"


def clear_sheet(popup):
    ws.clear()
    popup.dismiss()


Button_clicked = ''
today = date.today()
today_date = today.strftime("%d/%m/%y")


class Category_Widget(GridLayout):
    def study_state(self):
        global Button_clicked
        Button_clicked = 'study'

    def work_state(self):
        global Button_clicked
        Button_clicked = "work"

    def play_state(self):
        global Button_clicked
        Button_clicked = "play"

    def rest_state(self):
        global Button_clicked
        Button_clicked = "rest"


class Timer_Widget(GridLayout):
    def __init__(self, **kwargs):
        super(Timer_Widget, self).__init__(**kwargs)
        self.seconds = 0
        self.started = False
        Clock.schedule_interval(self.update_time, 0)

    def update_time(self, nap):
        if self.started:
            self.seconds += nap
        minutes, seconds = divmod(self.seconds, 60)
        hours, minutes = divmod(minutes, 60)
        self.ids.time.text = f'{int(hours):02}:{int(minutes):02}:{int(seconds):02}'

    def start_stop(self):
        self.ids.start_stop.text = '[b]Start[/b]' if self.started else '[b]Stop[/b]'
        self.started = not self.started
        if self.started:
            self.ids.start_stop.back_color = (226/255, 45/255, 83/255, 0.9)
        else:
            self.ids.start_stop.back_color = (60/255, 218/255, 86/255, 0.9)

    def save(self):
        time = self.ids.time.text
        if time != '00:00:00':
            self.ids.start_stop.text = '[b]Start[/b]'
            self.started = False
            self.seconds = 0
            data = [today_date, Button_clicked,
                    f"{int(self.hours)*60 + int(self.minutes)}"]
            ws.append_row(data)
            self.ids.time.text = '00:00:00'
            self.ids.start_stop.back_color = (60/255, 218/255, 86/255, 0.9)

    def reset(self):
        self.started = False
        self.seconds = 0
        self.ids.time.text = '00:00:00'
        self.ids.start_stop.text = '[b]Start[/b]'
        self.ids.start_stop.back_color = (60/255, 218/255, 86/255, 0.9)

    def popup(self):
        time = self.ids.time.text
        if time != '00:00:00':
            self.hours = time[1:2] if time[0] == '0' else time[0:2]
            self.minutes = time[4:5] if time[3] == '0' else time[3:5]
            box = BoxLayout(orientation='vertical', padding=(10))
            box.add_widget(Label(text=f'You spent {self.hours} hours & \n {self.minutes} minutes [b]{Button_clicked}ing[/b]',
                                 font_size=32,
                                 markup=True))
            button_to_main = Button(text="Start a new task",
                                    font_size=25,
                                    background_color=(0, 0, 0, 0.5),
                                    size=(300, 100),
                                    size_hint=(None, None),
                                    pos_hint={'center_x': 0.5, 'center_y': 0.5})

            button_to_main.bind(on_release=back_to_main)
            button_to_main.bind(on_press=lambda x: popup.dismiss())
            box.add_widget(button_to_main)

            popup = Popup(
                title='Report',
                title_align='center',
                title_size='16sp',
                separator_color=[.9, .4, .2, 1],
                background_color=[0, 0, 0, 0.4],
                content=box,
                size=(500, 400),
                size_hint=(None, None),
            )
            popup.open()


class Report_Widget(GridLayout):
    def __init__(self, **kwargs):
        super(Report_Widget, self).__init__(**kwargs)
        self.show_result = False

    def get_report(self):
        self.show_result = not self.show_result
        if self.show_result:
            all_record = ws.get_all_values()
            self.playtime = 0
            self.studytime = 0
            self.worktime = 0
            self.resttime = 0
            for rows in all_record:
                if rows[0] == today_date:
                    if rows[1] == 'play':
                        self.playtime += int(rows[2])
                    if rows[1] == 'study':
                        self.studytime += int(rows[2])
                    if rows[1] == 'work':
                        self.worktime += int(rows[2])
                    if rows[1] == 'rest':
                        self.resttime += int(rows[2])

            self.ids.play_time.text = f"[b][u]Play time[/u][/b]: \n\n {self.playtime//60} hr {self.playtime % 60} min"
            self.ids.study_time.text = f"[b][u]Study time[/u][/b]: \n\n{self.studytime//60} hr {self.studytime % 60} min"
            self.ids.work_time.text = f"[b][u]Work time[/u][/b]: \n\n {self.worktime//60} hr {self.worktime % 60} min"
            self.ids.rest_time.text = f"[b][u]Rest time[/u][/b]: \n\n {self.resttime//60} hr {self.resttime % 60} min"
            self.ids.show_result.text = "Clear Report"
        else:
            sleep(0.5)
            self.ids.play_time.text = "[i]Play Time[/i]"
            self.ids.study_time.text = "[i]Study Time[/i]"
            self.ids.work_time.text = "[i]Work Time[/i]"
            self.ids.rest_time.text = "[i]Rest Time[/i]"
            self.ids.show_result.text = "Get Today's Report!"


class Login_Widget(GridLayout):
    def save(self):
        global ws
        global file2
        key = self.ids.key.text
        if len(key) < 44:
            self.ids.key.text = ""
            self.ids.key.hint_text = "Please enter the correct Google Sheet Key"
            self.ids.key.background_color = (1, 50/255, 50/255, 0.3)
        with open(f'{home}/KEY_STATE.txt', 'w') as f:
            f.write(key)
        sh = gc.open_by_key(key)
        ws = sh.sheet1
        MDApp.get_running_app().root.current = "mainScreen"

    def copy(self):
        pyperclip.copy("<client-email>")
        self.ids.copy_button.text = "Copied successfully"
        self.ids.copy_button.disabled = True
        self.ids.key.disabled = False
        self.ids.copy_button.back_color = 60/255, 218/255, 86/255, 0.9
        self.ids.key.hint_text = "Now, copy and paste the Google Sheet Key here \nand press 'ENTER' \n\n\n(Pssst, it can be found in the URL of your google \nsheet)"


class MainScreen(Screen):
    pass


class SecondScreen(Screen):
    def on_pre_enter(self):
        self.ids.session_name.title = Button_clicked.capitalize()


class ThirdScreen(Screen):
    def on_pre_enter(self):
        self.ids.report.title = f"Today's Report: {today_date}"

    def clear(self):
        grid = GridLayout(cols=1, padding=(10))
        box1 = BoxLayout(orientation='vertical', padding=(10))
        box2 = BoxLayout(orientation='horizontal', padding=(10))
        box1.add_widget(Label(text=f'This will clear [b]EVERYTHING[/b]',
                              font_size=32,
                              markup=True))
        clear = Button(text="Confirm clear",
                       font_size=25,
                       background_color=(0, 0, 0, 0.5),
                       size=(200, 100),
                       size_hint=(None, None),
                       pos_hint={'center_x': 0.5, 'center_y': 0.5})
        exit = Button(text="Don't clear",
                      font_size=25,
                      background_color=(0, 0, 0, 0.5),
                      size=(200, 100),
                      size_hint=(None, None),
                      pos_hint={'center_x': 0.5, 'center_y': 0.5})
        clear.bind(on_press=lambda x: clear_sheet(popup))
        exit.bind(on_press=lambda x: popup.dismiss())
        box2.add_widget(clear)
        box2.add_widget(exit)
        grid.add_widget(box1)
        grid.add_widget(box2)

        popup = Popup(
            title='Confirmation',
            title_align='center',
            title_size='16sp',
            separator_color=[.9, .4, .2, 1],
            background_color=[0, 0, 0, 0.4],
            content=grid,
            size=(500, 400),
            size_hint=(None, None),
        )
        popup.open()


class LoginScreen(Screen):
    pass


class MainApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = 'Orange'
        if bool == False:
            MyScreenManager = ScreenManager()
            MyScreenManager.add_widget(LoginScreen())
            MyScreenManager.add_widget(MainScreen())
            MyScreenManager.add_widget(SecondScreen())
            MyScreenManager.add_widget(ThirdScreen())
            return MyScreenManager
        else:
            MyScreenManager = ScreenManager()
            MyScreenManager.add_widget(MainScreen())
            MyScreenManager.add_widget(SecondScreen())
            MyScreenManager.add_widget(ThirdScreen())
            return MyScreenManager


if __name__ == "__main__":
    MainApp().run()
