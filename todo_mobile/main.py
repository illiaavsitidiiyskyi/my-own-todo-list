from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from datetime import datetime, time
from database import init_db, User, Todo
import hashlib


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def check_password(password, hashed):
    return hash_password(password) == hashed


def make_button(text, bg_color=(0.25, 0.45, 0.9, 1), height=50):
    return Button(
        text=text,
        size_hint_y=None,
        height=dp(height),
        background_normal='',
        background_color=bg_color,
        color=(1, 1, 1, 1),
        font_size=dp(15),
        bold=True,
    )


def make_input(hint, password=False):
    return TextInput(
        hint_text=hint,
        password=password,
        multiline=False,
        size_hint_y=None,
        height=dp(45),
        background_color=(0.15, 0.15, 0.2, 1),
        foreground_color=(1, 1, 1, 1),
        hint_text_color=(0.5, 0.5, 0.6, 1),
        cursor_color=(1, 1, 1, 1),
        padding=[dp(10), dp(10)],
        font_size=dp(15),
    )


class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas.before:
            Color(0.08, 0.08, 0.13, 1)
            self.rect = RoundedRectangle(size=self.size, pos=self.pos)
        self.bind(size=lambda *a: setattr(self.rect, 'size', self.size))
        self.bind(pos=lambda *a: setattr(self.rect, 'pos', self.pos))

        outer = BoxLayout(orientation='vertical', padding=dp(40), spacing=dp(15))

        outer.add_widget(Label(size_hint_y=0.2))
        outer.add_widget(Label(text='TODO-LIST', font_size=dp(32), bold=True, color=(0.4, 0.6, 1, 1), size_hint_y=None, height=dp(60)))
        outer.add_widget(Label(text='Sign in to your account', font_size=dp(14), color=(0.5, 0.5, 0.6, 1), size_hint_y=None, height=dp(30)))
        outer.add_widget(Label(size_hint_y=None, height=dp(20)))

        self.username = make_input('Username')
        self.password = make_input('Password', password=True)
        self.message = Label(text='', color=(1, 0.3, 0.3, 1), size_hint_y=None, height=dp(30), font_size=dp(13))

        btn_login = make_button('Sign In', bg_color=(0.25, 0.45, 0.9, 1))
        btn_login.bind(on_press=self.login)

        btn_register = make_button("Don't have an account? Sign Up", bg_color=(0.15, 0.15, 0.2, 1))
        btn_register.bind(on_press=self.go_register)

        outer.add_widget(self.username)
        outer.add_widget(self.password)
        outer.add_widget(self.message)
        outer.add_widget(btn_login)
        outer.add_widget(btn_register)
        outer.add_widget(Label())

        self.add_widget(outer)

    def login(self, instance):
        try:
            user = User.get(User.username == self.username.text)
            if check_password(self.password.text, user.password):
                App.get_running_app().current_user = user
                self.manager.current = 'todo'
            else:
                self.message.text = 'Invalid password!'
        except User.DoesNotExist:
            self.message.text = 'User not found!'

    def go_register(self, instance):
        self.manager.current = 'register'


class RegisterScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas.before:
            Color(0.08, 0.08, 0.13, 1)
            self.rect = RoundedRectangle(size=self.size, pos=self.pos)
        self.bind(size=lambda *a: setattr(self.rect, 'size', self.size))
        self.bind(pos=lambda *a: setattr(self.rect, 'pos', self.pos))

        outer = BoxLayout(orientation='vertical', padding=dp(40), spacing=dp(15))

        outer.add_widget(Label(size_hint_y=0.2))
        outer.add_widget(Label(text='Create Account', font_size=dp(28), bold=True, color=(0.4, 0.6, 1, 1), size_hint_y=None, height=dp(60)))
        outer.add_widget(Label(size_hint_y=None, height=dp(20)))

        self.username = make_input('Username')
        self.password = make_input('Password', password=True)
        self.message = Label(text='', color=(1, 0.3, 0.3, 1), size_hint_y=None, height=dp(30), font_size=dp(13))

        btn_register = make_button('Sign Up', bg_color=(0.2, 0.7, 0.4, 1))
        btn_register.bind(on_press=self.register)

        btn_back = make_button('Back to Sign In', bg_color=(0.15, 0.15, 0.2, 1))
        btn_back.bind(on_press=self.go_back)

        outer.add_widget(self.username)
        outer.add_widget(self.password)
        outer.add_widget(self.message)
        outer.add_widget(btn_register)
        outer.add_widget(btn_back)
        outer.add_widget(Label())

        self.add_widget(outer)

    def register(self, instance):
        username = self.username.text.strip()
        password = self.password.text.strip()

        if not username or not password:
            self.message.text = 'Please fill in all fields!'
            return
        if User.select().where(User.username == username).exists():
            self.message.text = 'Username already exists!'
            return

        User.create(username=username, password=hash_password(password))
        self.message.text = ''
        self.manager.current = 'login'

    def go_back(self, instance):
        self.manager.current = 'login'


class TodoScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_date = None
        self.selected_time = None

        with self.canvas.before:
            Color(0.08, 0.08, 0.13, 1)
            self.rect = RoundedRectangle(size=self.size, pos=self.pos)
        self.bind(size=lambda *a: setattr(self.rect, 'size', self.size))
        self.bind(pos=lambda *a: setattr(self.rect, 'pos', self.pos))

        main = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))

        top_bar = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(55), spacing=dp(10))
        self.title_label = Label(text='My Tasks', font_size=dp(22), bold=True, color=(0.4, 0.6, 1, 1), halign='left')
        self.title_label.bind(size=self.title_label.setter('text_size'))
        btn_logout = make_button('Log Out', bg_color=(0.7, 0.2, 0.2, 1), height=45)
        btn_logout.size_hint_x = 0.3
        btn_logout.bind(on_press=self.logout)
        top_bar.add_widget(self.title_label)
        top_bar.add_widget(btn_logout)
        main.add_widget(top_bar)

        btn_add = make_button('+ Add New Task', bg_color=(0.25, 0.45, 0.9, 1))
        btn_add.bind(on_press=self.show_add_popup)
        main.add_widget(btn_add)

        self.scroll = ScrollView()
        self.todos_layout = GridLayout(cols=1, spacing=dp(8), size_hint_y=None, padding=[0, dp(5)])
        self.todos_layout.bind(minimum_height=self.todos_layout.setter('height'))
        self.scroll.add_widget(self.todos_layout)
        main.add_widget(self.scroll)

        self.add_widget(main)

    def on_enter(self):
        user = App.get_running_app().current_user
        self.title_label.text = f"{user.username}'s Tasks"
        self.load_todos()

    def logout(self, instance):
        App.get_running_app().current_user = None
        self.manager.current = 'login'

    def load_todos(self):
        self.todos_layout.clear_widgets()
        user = App.get_running_app().current_user
        todos = Todo.select().where(Todo.user == user).order_by(Todo.weight.desc(), Todo.deadline)

        if not todos.count():
            self.todos_layout.add_widget(
                Label(text='No tasks yet. Add your first task!', color=(0.5, 0.5, 0.6, 1),
                      size_hint_y=None, height=dp(60), font_size=dp(15))
            )
            return

        for todo in todos:
            self.add_todo_widget(todo)

    def add_todo_widget(self, todo):
        weight_colors = {
            1: (0.2, 0.5, 1, 1),
            2: (0.2, 0.7, 0.5, 1),
            3: (0.9, 0.7, 0.1, 1),
            4: (0.9, 0.4, 0.1, 1),
            5: (0.9, 0.2, 0.2, 1),
        }
        color = weight_colors.get(todo.weight, (0.5, 0.5, 0.5, 1))

        item = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(70), spacing=dp(8))

        done_text = 'Done' if todo.done else 'O'
        done_color = (0.2, 0.7, 0.4, 1) if todo.done else (0.2, 0.2, 0.3, 1)
        btn_done = Button(
            text=done_text, size_hint_x=None, width=dp(60),
            background_normal='', background_color=done_color,
            font_size=dp(13), color=(1, 1, 1, 1), bold=True,
        )
        btn_done.bind(on_press=lambda x, t=todo: self.toggle_todo(t))

        info = BoxLayout(orientation='vertical', spacing=dp(2))
        title_color = (0.5, 0.5, 0.5, 1) if todo.done else (1, 1, 1, 1)
        lbl_title = Label(text=todo.title, font_size=dp(15), bold=True, color=title_color, halign='left')
        lbl_title.bind(size=lbl_title.setter('text_size'))
        lbl_info = Label(
            text=f'Priority: {todo.weight}  |  {todo.deadline.strftime("%d.%m.%Y %H:%M")}',
            font_size=dp(12), color=color, halign='left'
        )
        lbl_info.bind(size=lbl_info.setter('text_size'))
        info.add_widget(lbl_title)
        info.add_widget(lbl_info)

        btn_delete = Button(
            text='Del', size_hint_x=None, width=dp(55),
            background_normal='', background_color=(0.6, 0.15, 0.15, 1),
            font_size=dp(13), color=(1, 1, 1, 1), bold=True,
        )
        btn_delete.bind(on_press=lambda x, t=todo: self.delete_todo(t))

        item.add_widget(btn_done)
        item.add_widget(info)
        item.add_widget(btn_delete)
        self.todos_layout.add_widget(item)

    def toggle_todo(self, todo):
        todo.done = not todo.done
        todo.save()
        self.load_todos()

    def delete_todo(self, todo):
        todo.delete_instance()
        self.load_todos()

    def show_add_popup(self, instance):
        self.selected_date = None
        self.selected_time = None

        layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(12))

        title_input = make_input('Task name')
        self.popup_deadline_label = Label(
            text='No date/time selected', color=(0.5, 0.5, 0.6, 1),
            size_hint_y=None, height=dp(30), font_size=dp(13)
        )
        self.popup_message = Label(text='', color=(1, 0.3, 0.3, 1), size_hint_y=None, height=dp(25), font_size=dp(13))

        weight_spinner = Spinner(
            text='3 - Average',
            values=['1 - Low', '2 - Below Average', '3 - Average', '4 - High', '5 - Critical'],
            size_hint_y=None, height=dp(45),
            background_normal='', background_color=(0.2, 0.2, 0.3, 1),
            color=(1, 1, 1, 1), font_size=dp(14),
        )

        btn_date = make_button('Pick Date', bg_color=(0.2, 0.35, 0.7, 1))
        btn_time = make_button('Pick Time', bg_color=(0.2, 0.35, 0.7, 1))

        btn_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(10))
        btn_cancel = make_button('Cancel', bg_color=(0.3, 0.3, 0.4, 1))
        btn_add = make_button('Add Task', bg_color=(0.25, 0.45, 0.9, 1))

        popup = Popup(
            title='New Task',
            content=layout,
            size_hint=(0.92, 0.82),
            background_color=(0.1, 0.1, 0.15, 1),
            title_color=(1, 1, 1, 1),
            title_size=dp(18),
            separator_color=(0.25, 0.45, 0.9, 1),
        )

        def pick_date(inst):
            date_layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
            today = datetime.now()

            date_layout.add_widget(Label(text='Enter date:', color=(1, 1, 1, 1), size_hint_y=None, height=dp(30)))

            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(45), spacing=dp(8))
            day_in = make_input(f'DD (e.g. {today.day:02d})')
            month_in = make_input(f'MM (e.g. {today.month:02d})')
            year_in = make_input(f'YYYY (e.g. {today.year})')
            row.add_widget(day_in)
            row.add_widget(month_in)
            row.add_widget(year_in)
            date_layout.add_widget(row)

            err = Label(text='', color=(1, 0.3, 0.3, 1), size_hint_y=None, height=dp(25))
            date_layout.add_widget(err)

            date_popup = Popup(
                title='Pick Date', content=date_layout,
                size_hint=(0.9, 0.5), background_color=(0.1, 0.1, 0.15, 1),
                title_color=(1, 1, 1, 1), separator_color=(0.25, 0.45, 0.9, 1)
            )

            def confirm_date(i):
                try:
                    d = int(day_in.text)
                    m = int(month_in.text)
                    y = int(year_in.text)
                    self.selected_date = datetime(y, m, d).date()
                    self.update_deadline_label()
                    date_popup.dismiss()
                except:
                    err.text = 'Invalid date!'

            btn_confirm = make_button('Confirm', bg_color=(0.25, 0.45, 0.9, 1))
            btn_confirm.bind(on_press=confirm_date)
            date_layout.add_widget(btn_confirm)
            date_popup.open()

        def pick_time(inst):
            time_layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
            now = datetime.now()

            time_layout.add_widget(Label(text='Enter time:', color=(1, 1, 1, 1), size_hint_y=None, height=dp(30)))

            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(45), spacing=dp(8))
            hour_in = make_input(f'HH (e.g. {now.hour:02d})')
            min_in = make_input(f'MM (e.g. {now.minute:02d})')
            row.add_widget(hour_in)
            row.add_widget(min_in)
            time_layout.add_widget(row)

            err = Label(text='', color=(1, 0.3, 0.3, 1), size_hint_y=None, height=dp(25))
            time_layout.add_widget(err)

            time_popup = Popup(
                title='Pick Time', content=time_layout,
                size_hint=(0.9, 0.45), background_color=(0.1, 0.1, 0.15, 1),
                title_color=(1, 1, 1, 1), separator_color=(0.25, 0.45, 0.9, 1)
            )

            def confirm_time(i):
                try:
                    h = int(hour_in.text)
                    m = int(min_in.text)
                    if not (0 <= h <= 23 and 0 <= m <= 59):
                        raise ValueError
                    self.selected_time = time(h, m)
                    self.update_deadline_label()
                    time_popup.dismiss()
                except:
                    err.text = 'Invalid time!'

            btn_confirm = make_button('Confirm', bg_color=(0.25, 0.45, 0.9, 1))
            btn_confirm.bind(on_press=confirm_time)
            time_layout.add_widget(btn_confirm)
            time_popup.open()

        def add_todo(inst):
            if not title_input.text.strip():
                self.popup_message.text = 'Please enter a task name!'
                return
            if not self.selected_date:
                self.popup_message.text = 'Please pick a date!'
                return
            if not self.selected_time:
                self.popup_message.text = 'Please pick a time!'
                return

            deadline = datetime.combine(self.selected_date, self.selected_time)
            weight = int(weight_spinner.text.split(' ')[0])
            Todo.create(
                title=title_input.text.strip(),
                deadline=deadline,
                weight=weight,
                user=App.get_running_app().current_user,
            )
            self.load_todos()
            popup.dismiss()

        btn_date.bind(on_press=pick_date)
        btn_time.bind(on_press=pick_time)
        btn_cancel.bind(on_press=popup.dismiss)
        btn_add.bind(on_press=add_todo)

        btn_row.add_widget(btn_cancel)
        btn_row.add_widget(btn_add)

        layout.add_widget(title_input)
        layout.add_widget(btn_date)
        layout.add_widget(btn_time)
        layout.add_widget(self.popup_deadline_label)
        layout.add_widget(weight_spinner)
        layout.add_widget(self.popup_message)
        layout.add_widget(btn_row)

        popup.open()

    def update_deadline_label(self):
        if self.selected_date and self.selected_time:
            self.popup_deadline_label.text = f'{self.selected_date.strftime("%d.%m.%Y")}  {self.selected_time.strftime("%H:%M")}'
            self.popup_deadline_label.color = (0.4, 0.8, 0.4, 1)
        elif self.selected_date:
            self.popup_deadline_label.text = f'{self.selected_date.strftime("%d.%m.%Y")} - time not set'
        elif self.selected_time:
            self.popup_deadline_label.text = f'{self.selected_time.strftime("%H:%M")} - date not set'


class TodoApp(App):
    current_user = None

    def build(self):
        init_db()
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(RegisterScreen(name='register'))
        sm.add_widget(TodoScreen(name='todo'))
        return sm


if __name__ == '__main__':
    TodoApp().run()