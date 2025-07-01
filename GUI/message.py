import sys
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidgetItem
from GUI.UI_Message import Ui_MainWindow
from util.QtFunc import upWindowsh


class LabelInputDialog(QMainWindow, Ui_MainWindow):
    confirmed = pyqtSignal(str)  # 定义一个自定义信号
    def __init__(self, parent=None):
        super(LabelInputDialog, self).__init__(parent)
        self.setupUi(self)
        self.history = self.load_history()
        self.setup_label_list()

        self.text = None

        self.pushButton.clicked.connect(self.on_confirm)
        self.pushButton_2.clicked.connect(self.reject)
        
        # 双击列表项也触发确认动作
        self.listWidget.itemDoubleClicked.connect(lambda: self.on_confirm())

    def load_history(self):
        try:
            with open('GUI/history.txt', 'r', encoding='utf-8') as file:
                return [line.strip() for line in file.readlines()]
        except FileNotFoundError:
            return []

    def setup_label_list(self):
        # 将历史标签添加到列表控件中
        for label in self.history:
            self.addLabel(label)
            
    def addLabel(self, label_text):
        """添加标签到列表中"""
        item = QListWidgetItem(label_text)
        self.listWidget.addItem(item)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            self.on_confirm()
            return
        elif event.key() == Qt.Key_Escape:
            self.reject()
            return
        super(LabelInputDialog, self).keyPressEvent(event)

    def on_confirm(self):
        selected_label = self.getSelectedLabel()

        if selected_label:  # 检查是否有选中的标签
            self.confirmed.emit(selected_label)  # 发出信号，并传递文本
            if selected_label not in self.history:
                self.history.append(selected_label)

            self.save_history()
            self.close()  # 关闭对话框
        else:
            upWindowsh("请选择一个标签")
            
    def getSelectedLabel(self):
        """获取当前选中的标签文本"""
        selected_items = self.listWidget.selectedItems()
        if selected_items:
            return selected_items[0].text()
        return None

    def save_history(self):
        try:
            with open('GUI/history.txt', 'w', encoding='utf-8') as file:
                for item in self.history:
                    file.write(f"{item}\n")
        except IOError as e:
            upWindowsh(f"保存历史记录失败：{e}")

    def reject(self):
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    dialog = LabelInputDialog()
    dialog.show()
    sys.exit(app.exec_())



