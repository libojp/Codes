#!/usr/bin/python3
#-*- coding: utf-8 -*-



from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QApplication, QDialog, QLabel
from PyQt5.QtGui import QFont, QIcon, QPixmap, QPainter, QLinearGradient
from PyQt5.QtCore import *
from PyQt5.QtCore import pyqtSignal
import sys



class AboutUsDialog(QDialog):
    def __init__(self, parent=None):
        super(AboutUsDialog, self).__init__(parent)

        self.title_label = QLabel(self);
        self.title_label.setFixedHeight(30);
        self.title_label.setStyleSheet('color:white');

        self.title_icon_label = QLabel(self);
        self.title_icon_label.setPixmap(QPixmap('./icon/logo2.ico'));
        self.title_icon_label.setFixedSize(16, 16);
        self.title_icon_label.setScaledContents(True);

        self.close_button = QPushButton(self);
        # self.close_button.loadPixmap('./icon/close.png')
        self.close_button.setAutoFillBackground(False);
        self.close_button.setStyleSheet(self.tr("background:transparent"))
        self.close_button.setText(self.tr(""));
        icon = QIcon();
        icon.addPixmap(QPixmap(self.tr('./icon/4505.png')), QIcon.Normal, QIcon.Off);
        # icon.addPixmap(QPixmap(self.tr('./icon/11.png')), QIcon.Normal, QIcon.On) ;
        self.close_button.setIcon(icon);
        self.close_button.setIconSize(QSize(25, 22))

        self.title_info_label = QLabel(self);
        self.title_info_label.setStyleSheet('color:rgb(30, 170, 60)');
        self.title_info_label.setFont(QFont('微软雅黑', 14, QFont.Bold, False));

        self.info_label = QLabel(self);
        self.info_label.setContentsMargins(0, 0, 0, 40);
        self.info_label.setStyleSheet("color:rgb(30,170,60)");
        self.info_label.setFont(QFont("微软雅黑", 10, QFont.Bold, False));
        self.info_label.setContentsMargins(0, 0, 0, 40);

        self.version_label = QLabel(self);

        self.mummy_label = QLabel(self);

        self.copyright_label = QLabel(self);
        self.copyright_label.setStyleSheet('color:gray');

        self.icon_label = QLabel(self);
        self.pixmap = QPixmap('./icon/kanMai_1.png');
        self.icon_label.setPixmap(self.pixmap);
        self.icon_label.setFixedSize(self.pixmap.size());

        self.ok_button = QPushButton(self);
        self.ok_button.setFixedSize(75, 25);
        self.ok_button.setStyleSheet("QPushButton{border:1px solid lightgray;background:rgb(230,230,230)}"
                                     "QPushButton:hover{border-color:green;background:transparent}");

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog);
        # 布局标题
        self.title_layout = QHBoxLayout()
        self.title_layout.addWidget(self.title_icon_label, 0, Qt.AlignVCenter)
        self.title_layout.addWidget(self.title_icon_label, 0, Qt.AlignVCenter)
        self.title_layout.addWidget(self.title_label, 0, Qt.AlignVCenter)
        self.title_layout.addStretch()  # 平均
        self.title_layout.addWidget(self.close_button, 0, Qt.AlignTop)

        # 布局信息列表
        self.vl_layout = QVBoxLayout();
        self.vl_layout.addWidget(self.title_info_label);
        self.vl_layout.addWidget(self.info_label);
        self.vl_layout.setSpacing(10);

        self.v2_laoyout = QVBoxLayout();
        self.v2_laoyout.addWidget(self.version_label);
        self.v2_laoyout.addWidget(self.mummy_label);
        self.v2_laoyout.addWidget(self.copyright_label);
        self.v2_laoyout.setSpacing(10);

        self.v_layout = QVBoxLayout();
        self.v_layout.addLayout(self.vl_layout);
        self.v_layout.addLayout(self.v2_laoyout);
        self.v_layout.addStretch()  # 平均分配
        self.v_layout.addSpacing(50);
        self.v_layout.setContentsMargins(0, 15, 0, 0)  # 设置距离边界的值

        # 布局地下配置
        self.bottom_layout = QHBoxLayout();
        self.bottom_layout.addStretch();
        self.bottom_layout.addWidget(self.ok_button);
        self.bottom_layout.setSpacing(0);
        self.bottom_layout.setContentsMargins(0, 0, 30, 20);

        self.h_layout = QHBoxLayout();
        self.h_layout.addLayout(self.v_layout);
        self.h_layout.addWidget(self.icon_label);
        self.h_layout.setSpacing(0);
        self.h_layout.setContentsMargins(40, 0, 20, 10);

        self.main_layout = QVBoxLayout();
        self.main_layout.addLayout(self.title_layout);
        self.main_layout.addStretch();
        self.main_layout.addLayout(self.h_layout);
        self.main_layout.addLayout(self.bottom_layout);
        self.main_layout.setSpacing(0);
        self.main_layout.setContentsMargins(0, 0, 0, 0);

        self.setLayout(self.main_layout);

        self.title_layout.setSpacing(0);
        self.title_layout.setContentsMargins(10, 0, 5, 0);

        self.translateLanguage();
        self.resize(520, 290);

        # self.connect(self.ok_button, SIGNAL('clicked()'), self, SLOT('hide()'));
        # self.connect(self.close_button, SIGNAL('clicked()'), self, SLOT('close()'));
        self.ok_button.clicked.connect(self.close)
        self.close_button.clicked.connect(self.close)

    def paintEvent(self, event):
        self.painter = QPainter();
        self.painter.begin(self);
        self.painter.drawPixmap(self.rect(), QPixmap('./icon/Dlight 3.png'));
        self.painter.end();
        linear2 = QLinearGradient(QPoint(self.rect().topLeft()), QPoint(self.rect().bottomLeft()));
        linear2.start();
        linear2.setColorAt(0, Qt.white);
        linear2.setColorAt(0.5, Qt.white);
        linear2.setColorAt(1, Qt.white);
        linear2.finalStop();
        self.painter2 = QPainter();
        self.painter2.begin(self);
        self.painter2.setPen(Qt.white);
        self.painter2.setBrush(linear2);
        self.painter2.drawRect(QRect(0, 30, self.width(), self.height() - 30));
        self.painter2.end();

        self.painter3 = QPainter();
        self.painter3.begin(self);
        self.painter3.setPen(Qt.gray);
        self.painter3.drawPolyline(QPointF(0, 30), QPointF(0, self.height() - 1),
                                   QPointF(self.width() - 1, self.height() - 1), QPointF(self.width() - 1, 30))
        self.painter3.end();

    def translateLanguage(self):
        self.title_label.setText(u"D*Light")
        self.title_info_label.setText(u"D Light")
        self.info_label.setText(u"A Brighter Future")
        self.version_label.setText(u"主程序版本:1.0.1.2018")
        self.mummy_label.setText(u"A Global Leader in Solar Power for Off-Grid Families")
        self.copyright_label.setText(u"Copyright(c) dlight.com Inc.All Rights Reserved.")
        # self.close_button.setToolTip(self.tr("close"))
        self.ok_button.setText(u"确定")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragPosition = event.globalPos() - self.frameGeometry().topLeft()
            QApplication.postEvent(self, QEvent(174))
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.dragPosition)
            event.accept()

    def isInTitle(self, xPos, yPos):
        return yPos < 30 and xPos < 456






if __name__ == '__main__':
    app = QApplication(sys.argv)
    aboutUS = AboutUsDialog()
    aboutUS.show()
    sys.exit(app.exec_())