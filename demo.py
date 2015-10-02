import TrivialUI

from PyQt5.QtWidgets import QApplication

class MainWindow(TrivialUI.MainWindow):
    pass

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(640, 480)
    window.show()
    sys.exit(app.exec_())
