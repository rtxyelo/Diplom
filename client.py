from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen

from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.core.window import Window
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
import socket
import time


# Create both screens. Please note the root.manager.current: this is how
# you can control the ScreenManager from kv. Each screen has by default a
# property manager that gives you the instance of the ScreenManager used.
Builder.load_string("""
<ScreenManagement>:
    SettingsScreen2:
        id: settings2
        name: 'settings2'

    MenuScreen:
        id: name
        name: 'menu'
        
    SettingsScreen:
        id: settings
        name: 'settings'

<SettingsScreen2>:
    mylabel2: mylabel2
    BoxLayout:
        orientation: 'vertical'
        padding: 5, 5        
        Label:
            id: mylabel2
            color: '#000000'
            #size_hint_y: None
            #height: self.texture_size[1]
            #text_size: self.width, None
            padding: 10, 10
            
        Button:
            text: 'Обновить новостную ленту'
            size_hint: (1.,.10)
            background_color: '#AFEEEE'
            on_press: 
                root.manager.ids.settings.update_news() 
                root.manager.ids.settings2.updated_news()


        Button:
            text: 'Перейти к новостям'
            size_hint: (1.,.10)
            background_color: '#AFEEEE'
            on_press:
                root.manager.current = 'menu'
                root.manager.ids.settings.connect()
            on_release: 
                root.manager.ids.name.upd_wait()
  
<MenuScreen>:
    mainlabel: mainlabel
    BoxLayout:
        orientation: 'vertical'
        padding: 10, 10
        Label:
            id: mainlabel
            #text: 'Выберите тему новости'
            color: '#000000'
        Button:
            text: 'Мир'
            background_color: '#AFEEEE'
            on_release: 
                root.manager.current = 'settings'
                root.manager.ids.settings.button_pressed(self)    # optional: passing Button instance
                
        Button:
            text: 'Культура'
            background_color: '#AFEEEE'
            on_release: 
                root.manager.current = 'settings'
                root.manager.ids.settings.button_pressed(self)    # optional: passing Button instance
                
        Button:
            text: 'Бывший СССР'
            background_color: '#AFEEEE'
            on_release:
                root.manager.current = 'settings'
                root.manager.ids.settings.button_pressed(self)    # optional: passing Button instance
        
        Button:
            text: 'Из жизни'
            background_color: '#AFEEEE'
            on_release:
                root.manager.current = 'settings'
                root.manager.ids.settings.button_pressed(self)    # optional: passing Button instance
                
        Button:
            text: 'Интернет и СМИ'
            background_color: '#AFEEEE'
            on_release:
                root.manager.current = 'settings'
                root.manager.ids.settings.button_pressed(self)    # optional: passing Button instance

        Button:
            text: 'Наука и техника'
            background_color: '#AFEEEE'
            on_release:
                root.manager.current = 'settings'
                root.manager.ids.settings.button_pressed(self)    # optional: passing Button instance
              
        Button:
            text: 'Россия'
            background_color: '#AFEEEE'
            on_release:
                root.manager.current = 'settings'
                root.manager.ids.settings.button_pressed(self)    # optional: passing Button instance
                
        Button:
            text: 'Силовые структуры'
            background_color: '#AFEEEE'
            on_release:
                root.manager.current = 'settings'
                root.manager.ids.settings.button_pressed(self)    # optional: passing Button instance
                
        Button:
            text: 'Спорт'
            background_color: '#AFEEEE'
            on_release:
                root.manager.current = 'settings'
                root.manager.ids.settings.button_pressed(self)    # optional: passing Button instance
                
        Button:
            text: 'Экономика'
            background_color: '#AFEEEE'
            on_release:
                root.manager.current = 'settings'
                root.manager.ids.settings.button_pressed(self)    # optional: passing Button instance


<SettingsScreen>:
    mylabel: mylabel
    BoxLayout:
        orientation: 'vertical'
        padding: 5, 5       
        Button:
            text: 'Главное меню'
            size_hint: (1.,.10)
            background_color: '#AFEEEE'
            on_press: 
                root.manager.current = 'menu'
                root.manager.ids.settings.clear_scroll()
                
        ScrollView:
            do_scroll_x: False
            do_scroll_y: True

            Label:
                id: mylabel
                color: '#000000'
                size_hint_y: None
                height: self.texture_size[1]
                text_size: self.width, None
                padding: 10, 10
                text: 'Новость'        
        
        Button:
            text: 'Далее'
            size_hint: (1.,.15)
            background_color: '#AFEEEE'
            on_press: root.manager.ids.settings.recieve_news()
""")


class SettingsScreen2(Screen):
    mylabel2 = ObjectProperty()  
    def updated_news(self):
        self.mylabel2.text = 'Переходите к просмотру новостей'

# Declare both screens
class MenuScreen(Screen):
    mainlabel = ObjectProperty()
    def upd_wait(self):
        #self.mainlabel.text = 'Подождите обновления ленты!'
        #time.sleep(5)
        self.mainlabel.text = 'Выберите тему новости'    

class SettingsScreen(Screen):
    mylabel = ObjectProperty()
    updt_flag = False
    mainlabel = ObjectProperty()
    def update_news(self):
        self.updt = 'update'
        self.updt_flag = True
        
    def connect(self):
        host = '192.168.0.115'
        port = 3930
        #print('Host: ', host, ' Port: ', port)
  
        #print('Begin...')
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #print('Socket is create...')
        self.s.connect((host, port))
        #print('Connected...')
        
        if self.updt_flag:
            self.s.send(self.updt.encode('cp1251'))
            #print('News updating...')
            
            
    def button_pressed(self, instance):
        print(f"Нажата кнопка из темы: {instance.text}")
        self.topic = instance.text
        self.s.send(instance.text.encode('cp1251'))
        strreply = self.s.recv(2048).decode('cp1251')
        self.mylabel.text = strreply

    def recieve_news(self):
        print('Нажата кнопка Делее')
        self.s.send(self.topic.encode('cp1251'))
        strreply = self.s.recv(2048).decode('cp1251')
        self.mylabel.text = strreply
    
    def clear_scroll(self):
        print('Нажата кнопка Главное меню')
        self.msg = 'clean'
        self.s.send(self.msg.encode('cp1251'))

# Create the screen manager
class ScreenManagement(ScreenManager):
    pass


class TestApp(App):

    def build(self):
        Window.clearcolor = ('#F0E68C')
        return ScreenManagement()


if __name__ == '__main__':
    TestApp().run()