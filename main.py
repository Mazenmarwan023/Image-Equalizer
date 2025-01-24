from PyQt5.QtWidgets import QApplication
from Image_equalizer import ImageEqualizer

if __name__ == "__main__":
    app = QApplication([])
    window = ImageEqualizer()
    window.show()
    app.exec_()