#! /usr/bin/python
"""
    @Author_name : Arsham mohammadi nesyshabori
    @Author_email : arshammoh1998@gmail.com
    @Author_nickname : apep
    @date : 
    @version : 
"""
import sys
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QMainWindow, QAbstractItemView
from PyQt5.uic import loadUi
from PyQt5.QtGui import QStandardItemModel, QStandardItem
import json


class Lesson(object):
    days_name = ["شنبه", "یکشنبه", "دوشنبه", "سه شنبه", "چهار شنبه", "پنج شنبه", ]
    times_name = ["۸", "۱۰", "۱۲", "۱۴", "۱۶", "۱۸", ]
    hafts_name = ["هر هفته", "زوج", "فرد" ]

    def __init__(self, code, name, tname, group, vahed, days):
        self.code = code
        self.name = name
        self.tname = tname
        self.group = group
        self.vahed = vahed
        self.days = days

    def get_day_str(self):
        string = ""
        for day in self.days:
            string += Lesson.days_name[day[0]] + " "
            string += Lesson.times_name[day[1]] + " "
            string += Lesson.hafts_name[day[2]] + " "
            string += "-"
        return string
    
    def get_row(self):
        return [
            QStandardItem(self.name),
            QStandardItem(self.tname),
            QStandardItem(str(self.group)),
            QStandardItem(str(self.vahed)),
            QStandardItem(self.get_day_str()),
        ]
    
    def get_dict(self):
        return {
            "code": self.code,
            "name": self.name,
            "tname": self.tname,
            "group": self.group,
            "vahed": self.vahed,
            "days": self.days,
        }

class Main(QMainWindow):

    def __init__(self):
        super(Main, self).__init__()
        loadUi("main.ui", self)
        self.setFixedSize(self.width(), self.height())
        self.setWindowTitle("انتخاب واحد آرشام")
        self.lessons = []
        self.show_lessons = []
        self.load_lessons()
        self.lessons_barname = []
        self.barname = self.create_barname()
        self.button_save.clicked.connect(self.save_barname)
        self.button_addlesson.clicked.connect(self.add_lesson)
        self.button_add2barname.clicked.connect(self.add_to_barname)
        self.button_removelesson.clicked.connect(self.remove_lesson)
        self.buttom_remove_entekhabshode.clicked.connect(self.remove_from_barname)
        self.el_search.textChanged.connect(self.search_lesson)
        self.checkBox_show.toggled.connect(lambda : self.update_lesson_list())
        self.update_barname()
        self.update_lesson_list()


    def create_barname(self):
        out = []
        for i in range(6):
            temp = []
            for j in range(5):
                temp.append(["", ""])
            out.append(temp)
        return out

    def save_lessons(self):
        with open("lessons.json", "w", encoding="utf-8") as f_lesson:
            temp = {
                "lessons" : [i.get_dict() for i in self.lessons]
            }
            json.dump(temp, f_lesson)

    def load_lessons(self):
        with open("lessons.json", "r",encoding="utf-8") as f_lesson:
            temp = json.load(f_lesson)
            self.lessons.clear()
            for i in temp["lessons"]:
                self.lessons.append(Lesson(**i))

    @pyqtSlot()
    def save_barname(self):
        text = "کد,نام درس,استاد درس,واحد,گروه"
        with open("out.txt", "w") as f:
            f.write(text+"\n")
            for i in self.lessons_barname:
                f.write("{},{},{},{},{}".format(i.code,i.name,i.tname,i.vahed,i.group))

    @pyqtSlot()
    def add_lesson(self):
        days = self.get_days()
        group = self.group.currentIndex()
        vahed = self.vahed.currentIndex()
        if group == 0 or vahed == 0:
            return
        code = self.el_code.text()
        name = self.el_name.text()
        tname = self.el_tname.text()
        self.lessons.append(Lesson(code, name, tname, group, vahed, days))
        self.update_lesson_list()
        self.save_lessons()

    @pyqtSlot()
    def add_to_barname(self):
        data = self.table_lesson.selectionModel().selection().indexes()
        if len(data):
            index = data[0].row()
            lesson = self.show_lessons[index]
            for les in self.lessons_barname:
                if les.code == lesson.code:
                    return
                for day in les.days:
                    for day2 in lesson.days:
                        if day == day2:
                            return
            self.lessons_barname.append(lesson)
            for day in lesson.days:
                if day[-1] == 0:
                    self.barname[day[0]][day[1]] = lesson.name
                else:
                    self.barname[day[0]][day[1]][day[2]-1] = lesson.name
        self.update_barname()
        self.update_lesson_list()


    @pyqtSlot()
    def remove_lesson(self):
        data = self.table_lesson.selectionModel().selection().indexes()
        if len(data):
            index = data[0].row()
            del self.lessons[self.lessons.index(self.show_lessons[index])]
            self.update_lesson_list()
            self.save_lessons()

    @pyqtSlot()
    def search_lesson(self):
        text = self.el_search.text()
        self.update_lesson_list(search=text)

    @pyqtSlot()
    def remove_from_barname(self):
        data = self.table_entekhabshode.selectionModel().selection().indexes()
        if len(data):
            index = data[0].row()
            lesson = self.lessons_barname[index]
            for day in lesson.days:
                self.barname[day[0]][day[1]] = ["", ""]
            del self.lessons_barname[index]
            self.update_barname()
            self.update_lesson_list()

 
    def get_days(self):
        days = []
        days.append((self.day1.currentIndex(), self.time1.currentIndex(),
                     self.hafte1.currentIndex()))
        if self.day2.currentIndex() != 0:
            days.append((self.day2.currentIndex()-1, self.time2.currentIndex(),
                        self.hafte2.currentIndex()))
        return days

    def update_lesson_list(self, search=None):
        head = ["نام درس", "نام استاد", "گروه", "واحد", "روزها"]
        model = QStandardItemModel(0, len(head))
        model.setHorizontalHeaderLabels(head)
        self.show_lessons.clear()
        i = 0
        for item in self.lessons:
            if search and not (search in item.name or search in item.tname):
                continue
            if self.checkBox_show.checkState():
                if item.code in list(map(lambda x: x.code, self.lessons_barname)):
                    continue
                
            model.insertRow(i, item.get_row())
            self.show_lessons.append(item)
            i+=1

        self.table_lesson.setModel(model)
        self.table_lesson.setEditTriggers(QAbstractItemView.NoEditTriggers)
        for i in range(len(head)):
            self.table_lesson.setColumnWidth(i, (self.table_lesson.width()-50)//len(head))

        
    
    def update_barname(self):
        head = ["۸-۱۰", "۱۰-۱۲", "۱۲-۱۴", "۱۴-۱۶", "۱۶-۱۸", "۱۸-۲۰"]
        model = QStandardItemModel(0, len(head))
        model.setHorizontalHeaderLabels(head)
        for i,line in enumerate(self.barname):
            row = []
            for item in line:
                if isinstance(item, list):
                    if item[0] or item[1]:
                        text = "زوج {}\nفرد {}".format(item[0], item[1])
                    else:
                        text = ""
                else:
                    text = item
                row.append(QStandardItem(text))
            model.insertRow(i, row)
            
        model.setVerticalHeaderLabels(Lesson.days_name)

        self.table_barname.setModel(model)
        self.table_barname.setEditTriggers(QAbstractItemView.NoEditTriggers)
        for i in range(len(head)):
            self.table_barname.setColumnWidth(i, (self.table_barname.width()-50)//len(head))
        for i in range(len(self.barname)):
            self.table_barname.setRowHeight(i, (self.table_barname.height()-50)//len(self.barname))

        model2 = QStandardItemModel(0, 1)
        model2.setHorizontalHeaderLabels(["درس های انتخاب شده",])
        for i, les in enumerate(self.lessons_barname):
            model2.insertRow(i, [QStandardItem(les.name),])
        self.table_entekhabshode.setModel(model2)
        self.table_entekhabshode.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.label_jame.setText("{}".format(sum(map(lambda x: x.vahed, self.lessons_barname))))
        



app = QApplication(sys.argv)
main = Main()
main.show()
sys.exit(app.exec_())