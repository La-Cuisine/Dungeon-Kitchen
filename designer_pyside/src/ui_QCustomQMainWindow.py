# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'QCustomQMainWindow.ui'
##
## Created by: Qt User Interface Compiler version 6.11.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QFrame, QHBoxLayout,
    QLabel, QPushButton, QSizePolicy, QSpacerItem,
    QStackedWidget, QTextEdit, QVBoxLayout, QWidget)

from Custom_Widgets.QCustomQMainWindow import QCustomQMainWindow

class Ui_CustomMainWindow(object):
    def setupUi(self, CustomMainWindow):
        if not CustomMainWindow.objectName():
            CustomMainWindow.setObjectName(u"CustomMainWindow")
        CustomMainWindow.resize(800, 600)
        font = QFont()
        font.setPointSize(10)
        CustomMainWindow.setFont(font)
        self.central_widget = QWidget(CustomMainWindow)
        self.central_widget.setObjectName(u"central_widget")
        self.horizontalLayout = QHBoxLayout(self.central_widget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.sidebar = QWidget(self.central_widget)
        self.sidebar.setObjectName(u"sidebar")
        self.sidebar.setMaximumSize(QSize(150, 16777215))
        self.verticalLayout = QVBoxLayout(self.sidebar)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.widget_2 = QWidget(self.sidebar)
        self.widget_2.setObjectName(u"widget_2")
        self.verticalLayout_2 = QVBoxLayout(self.widget_2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(5, 5, 5, 5)
        self.open_info_menu_btn = QPushButton(self.widget_2)
        self.open_info_menu_btn.setObjectName(u"open_info_menu_btn")
        self.open_info_menu_btn.setMaximumSize(QSize(30, 16777215))
        self.open_info_menu_btn.setAutoFillBackground(False)
        icon = QIcon()
        icon.addFile(u":/image/Redo.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.open_info_menu_btn.setIcon(icon)

        self.verticalLayout_2.addWidget(self.open_info_menu_btn)


        self.verticalLayout.addWidget(self.widget_2, 0, Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTop)

        self.widget_3 = QWidget(self.sidebar)
        self.widget_3.setObjectName(u"widget_3")
        self.verticalLayout_4 = QVBoxLayout(self.widget_3)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(5, 5, 5, 5)
        self.character_btn = QPushButton(self.widget_3)
        self.character_btn.setObjectName(u"character_btn")
        self.character_btn.setMinimumSize(QSize(0, 30))
        self.character_btn.setAutoFillBackground(False)

        self.verticalLayout_4.addWidget(self.character_btn)

        self.map_btn = QPushButton(self.widget_3)
        self.map_btn.setObjectName(u"map_btn")
        self.map_btn.setMinimumSize(QSize(0, 30))
        self.map_btn.setAutoFillBackground(False)

        self.verticalLayout_4.addWidget(self.map_btn)

        self.server_btn = QPushButton(self.widget_3)
        self.server_btn.setObjectName(u"server_btn")
        self.server_btn.setMinimumSize(QSize(0, 30))
        self.server_btn.setAutoFillBackground(False)

        self.verticalLayout_4.addWidget(self.server_btn)


        self.verticalLayout.addWidget(self.widget_3, 0, Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.widget = QWidget(self.sidebar)
        self.widget.setObjectName(u"widget")
        self.verticalLayout_3 = QVBoxLayout(self.widget)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(5, 5, 5, 5)
        self.settings_btn = QPushButton(self.widget)
        self.settings_btn.setObjectName(u"settings_btn")
        self.settings_btn.setMinimumSize(QSize(0, 30))
        self.settings_btn.setAutoFillBackground(False)

        self.verticalLayout_3.addWidget(self.settings_btn)

        self.information_btn = QPushButton(self.widget)
        self.information_btn.setObjectName(u"information_btn")
        self.information_btn.setMinimumSize(QSize(0, 30))
        self.information_btn.setAutoFillBackground(False)

        self.verticalLayout_3.addWidget(self.information_btn)

        self.help_btn = QPushButton(self.widget)
        self.help_btn.setObjectName(u"help_btn")
        self.help_btn.setMinimumSize(QSize(0, 30))
        self.help_btn.setAutoFillBackground(False)

        self.verticalLayout_3.addWidget(self.help_btn)


        self.verticalLayout.addWidget(self.widget, 0, Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignBottom)


        self.horizontalLayout.addWidget(self.sidebar, 0, Qt.AlignmentFlag.AlignLeft)

        self.center_menu = QWidget(self.central_widget)
        self.center_menu.setObjectName(u"center_menu")
        self.center_menu.setEnabled(True)
        self.center_menu.setMinimumSize(QSize(200, 200))
        self.center_menu.setMaximumSize(QSize(200, 16777215))
        self.center_menu.setAutoFillBackground(False)
        self.verticalLayout_5 = QVBoxLayout(self.center_menu)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.center_menu_top = QWidget(self.center_menu)
        self.center_menu_top.setObjectName(u"center_menu_top")
        self.center_menu_top.setMaximumSize(QSize(200, 16777215))
        self.center_menu_top.setAutoFillBackground(False)
        self.horizontalLayout_2 = QHBoxLayout(self.center_menu_top)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.center_menu_top_label = QLabel(self.center_menu_top)
        self.center_menu_top_label.setObjectName(u"center_menu_top_label")

        self.horizontalLayout_2.addWidget(self.center_menu_top_label)

        self.close_info_menu_btn = QPushButton(self.center_menu_top)
        self.close_info_menu_btn.setObjectName(u"close_info_menu_btn")
        self.close_info_menu_btn.setMinimumSize(QSize(0, 30))
        self.close_info_menu_btn.setMaximumSize(QSize(30, 16777215))
        font1 = QFont()
        font1.setPointSize(10)
        font1.setStyleStrategy(QFont.PreferAntialias)
        self.close_info_menu_btn.setFont(font1)
        self.close_info_menu_btn.setAutoFillBackground(False)

        self.horizontalLayout_2.addWidget(self.close_info_menu_btn)


        self.verticalLayout_5.addWidget(self.center_menu_top)

        self.stacked_widget = QStackedWidget(self.center_menu)
        self.stacked_widget.setObjectName(u"stacked_widget")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.stacked_widget.sizePolicy().hasHeightForWidth())
        self.stacked_widget.setSizePolicy(sizePolicy)
        self.stacked_widget.setAutoFillBackground(True)
        self.settings_menu = QWidget()
        self.settings_menu.setObjectName(u"settings_menu")
        self.verticalLayout_6 = QVBoxLayout(self.settings_menu)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_6.addItem(self.verticalSpacer_2)

        self.widget_4 = QWidget(self.settings_menu)
        self.widget_4.setObjectName(u"widget_4")
        self.verticalLayout_7 = QVBoxLayout(self.widget_4)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.settings_menu_label = QLabel(self.widget_4)
        self.settings_menu_label.setObjectName(u"settings_menu_label")
        self.settings_menu_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_7.addWidget(self.settings_menu_label)

        self.frame = QFrame(self.widget_4)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.frame)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.theme_menu_label = QLabel(self.frame)
        self.theme_menu_label.setObjectName(u"theme_menu_label")

        self.horizontalLayout_3.addWidget(self.theme_menu_label)

        self.theme_list = QComboBox(self.frame)
        self.theme_list.setObjectName(u"theme_list")

        self.horizontalLayout_3.addWidget(self.theme_list)


        self.verticalLayout_7.addWidget(self.frame)


        self.verticalLayout_6.addWidget(self.widget_4, 0, Qt.AlignmentFlag.AlignVCenter)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_6.addItem(self.verticalSpacer_3)

        self.stacked_widget.addWidget(self.settings_menu)
        self.character_menu = QWidget()
        self.character_menu.setObjectName(u"character_menu")
        self.verticalLayout_12 = QVBoxLayout(self.character_menu)
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.character_menu_label = QLabel(self.character_menu)
        self.character_menu_label.setObjectName(u"character_menu_label")
        self.character_menu_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_12.addWidget(self.character_menu_label, 0, Qt.AlignmentFlag.AlignTop)

        self.character_menu_textbox = QTextEdit(self.character_menu)
        self.character_menu_textbox.setObjectName(u"character_menu_textbox")
        self.character_menu_textbox.setReadOnly(True)

        self.verticalLayout_12.addWidget(self.character_menu_textbox)

        self.stacked_widget.addWidget(self.character_menu)
        self.map_menu = QWidget()
        self.map_menu.setObjectName(u"map_menu")
        self.verticalLayout_13 = QVBoxLayout(self.map_menu)
        self.verticalLayout_13.setObjectName(u"verticalLayout_13")
        self.map_menu_label = QLabel(self.map_menu)
        self.map_menu_label.setObjectName(u"map_menu_label")
        self.map_menu_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_13.addWidget(self.map_menu_label, 0, Qt.AlignmentFlag.AlignTop)

        self.stacked_widget.addWidget(self.map_menu)
        self.server_menu = QWidget()
        self.server_menu.setObjectName(u"server_menu")
        self.verticalLayout_11 = QVBoxLayout(self.server_menu)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.server_state_label = QLabel(self.server_menu)
        self.server_state_label.setObjectName(u"server_state_label")
        self.server_state_label.setMinimumSize(QSize(0, 20))
        self.server_state_label.setMaximumSize(QSize(16777215, 20))
        self.server_state_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_11.addWidget(self.server_state_label)

        self.url_link_label = QLabel(self.server_menu)
        self.url_link_label.setObjectName(u"url_link_label")
        self.url_link_label.setMinimumSize(QSize(0, 20))
        self.url_link_label.setMaximumSize(QSize(16777215, 20))
        self.url_link_label.setScaledContents(False)
        self.url_link_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.url_link_label.setOpenExternalLinks(True)

        self.verticalLayout_11.addWidget(self.url_link_label)

        self.verticalSpacer_5 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        self.verticalLayout_11.addItem(self.verticalSpacer_5)

        self.open_server_btn = QPushButton(self.server_menu)
        self.open_server_btn.setObjectName(u"open_server_btn")
        self.open_server_btn.setMinimumSize(QSize(0, 38))
        self.open_server_btn.setMaximumSize(QSize(16777215, 38))
        self.open_server_btn.setCheckable(False)

        self.verticalLayout_11.addWidget(self.open_server_btn)

        self.close_server_btn = QPushButton(self.server_menu)
        self.close_server_btn.setObjectName(u"close_server_btn")
        self.close_server_btn.setMinimumSize(QSize(0, 38))
        self.close_server_btn.setMaximumSize(QSize(16777215, 38))
        self.close_server_btn.setCheckable(False)
        self.close_server_btn.setChecked(False)

        self.verticalLayout_11.addWidget(self.close_server_btn)

        self.open_website_btn = QPushButton(self.server_menu)
        self.open_website_btn.setObjectName(u"open_website_btn")
        self.open_website_btn.setMinimumSize(QSize(0, 38))
        self.open_website_btn.setMaximumSize(QSize(16777215, 38))

        self.verticalLayout_11.addWidget(self.open_website_btn)

        self.verticalSpacer_4 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_11.addItem(self.verticalSpacer_4)

        self.stacked_widget.addWidget(self.server_menu)
        self.information_menu = QWidget()
        self.information_menu.setObjectName(u"information_menu")
        self.verticalLayout_8 = QVBoxLayout(self.information_menu)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.information_menu_label = QLabel(self.information_menu)
        self.information_menu_label.setObjectName(u"information_menu_label")
        self.information_menu_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_8.addWidget(self.information_menu_label, 0, Qt.AlignmentFlag.AlignVCenter)

        self.stacked_widget.addWidget(self.information_menu)
        self.help_menu = QWidget()
        self.help_menu.setObjectName(u"help_menu")
        self.verticalLayout_9 = QVBoxLayout(self.help_menu)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.help_menu_label = QLabel(self.help_menu)
        self.help_menu_label.setObjectName(u"help_menu_label")
        self.help_menu_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_9.addWidget(self.help_menu_label, 0, Qt.AlignmentFlag.AlignVCenter)

        self.stacked_widget.addWidget(self.help_menu)

        self.verticalLayout_5.addWidget(self.stacked_widget)


        self.horizontalLayout.addWidget(self.center_menu)

        self.main_body = QWidget(self.central_widget)
        self.main_body.setObjectName(u"main_body")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.main_body.sizePolicy().hasHeightForWidth())
        self.main_body.setSizePolicy(sizePolicy1)
        self.verticalLayout_10 = QVBoxLayout(self.main_body)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.widget_5 = QWidget(self.main_body)
        self.widget_5.setObjectName(u"widget_5")
        self.horizontalLayout_4 = QHBoxLayout(self.widget_5)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.log_view_label = QLabel(self.widget_5)
        self.log_view_label.setObjectName(u"log_view_label")

        self.horizontalLayout_4.addWidget(self.log_view_label)


        self.verticalLayout_10.addWidget(self.widget_5)

        self.log_view = QTextEdit(self.main_body)
        self.log_view.setObjectName(u"log_view")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.log_view.sizePolicy().hasHeightForWidth())
        self.log_view.setSizePolicy(sizePolicy2)
        self.log_view.setMaximumSize(QSize(16777215, 130))
        self.log_view.setReadOnly(True)

        self.verticalLayout_10.addWidget(self.log_view)


        self.horizontalLayout.addWidget(self.main_body)

        CustomMainWindow.setCentralWidget(self.central_widget)

        self.retranslateUi(CustomMainWindow)

        self.stacked_widget.setCurrentIndex(3)


        QMetaObject.connectSlotsByName(CustomMainWindow)
    # setupUi

    def retranslateUi(self, CustomMainWindow):
        CustomMainWindow.setWindowTitle(QCoreApplication.translate("CustomMainWindow", u"Custom MainWindow", None))
        self.open_info_menu_btn.setText("")
        self.character_btn.setText(QCoreApplication.translate("CustomMainWindow", u"Character", None))
        self.map_btn.setText(QCoreApplication.translate("CustomMainWindow", u"Map", None))
        self.server_btn.setText(QCoreApplication.translate("CustomMainWindow", u"Server", None))
        self.settings_btn.setText(QCoreApplication.translate("CustomMainWindow", u"Settings", None))
        self.information_btn.setText(QCoreApplication.translate("CustomMainWindow", u"Information", None))
        self.help_btn.setText(QCoreApplication.translate("CustomMainWindow", u"Help", None))
        self.center_menu_top_label.setText(QCoreApplication.translate("CustomMainWindow", u"Information menu", None))
        self.close_info_menu_btn.setText(QCoreApplication.translate("CustomMainWindow", u"\u2715", None))
        self.settings_menu_label.setText(QCoreApplication.translate("CustomMainWindow", u"Settings", None))
        self.theme_menu_label.setText(QCoreApplication.translate("CustomMainWindow", u"Theme", None))
        self.character_menu_label.setText(QCoreApplication.translate("CustomMainWindow", u"Character", None))
        self.map_menu_label.setText(QCoreApplication.translate("CustomMainWindow", u"Map tools ?", None))
        self.server_state_label.setText(QCoreApplication.translate("CustomMainWindow", u"Server: closed", None))
        self.url_link_label.setText(QCoreApplication.translate("CustomMainWindow", u"URL : <a href='{SERVER_URL}'>{SERVER_URL}</a>", None))
        self.open_server_btn.setText(QCoreApplication.translate("CustomMainWindow", u"Open server", None))
        self.close_server_btn.setText(QCoreApplication.translate("CustomMainWindow", u"Close server", None))
        self.open_website_btn.setText(QCoreApplication.translate("CustomMainWindow", u"Open website", None))
        self.information_menu_label.setText(QCoreApplication.translate("CustomMainWindow", u"Information", None))
        self.help_menu_label.setText(QCoreApplication.translate("CustomMainWindow", u"Help", None))
        self.log_view_label.setText(QCoreApplication.translate("CustomMainWindow", u"Logs du serveur PHP :", None))
    # retranslateUi

