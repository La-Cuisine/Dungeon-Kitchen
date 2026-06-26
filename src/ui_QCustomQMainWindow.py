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
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QAbstractSpinBox, QApplication, QCheckBox, QComboBox,
    QFormLayout, QFrame, QGridLayout, QHBoxLayout,
    QLabel, QLayout, QLineEdit, QListWidget,
    QListWidgetItem, QMenu, QMenuBar, QPushButton,
    QSizePolicy, QSpacerItem, QSpinBox, QStackedWidget,
    QTabWidget, QTextEdit, QVBoxLayout, QWidget)

from Custom_Widgets.QCustomQMainWindow import QCustomQMainWindow
class Ui_CustomMainWindow(object):
    def setupUi(self, CustomMainWindow):
        if not CustomMainWindow.objectName():
            CustomMainWindow.setObjectName(u"CustomMainWindow")
        CustomMainWindow.resize(800, 600)
        font = QFont()
        font.setPointSize(10)
        CustomMainWindow.setFont(font)
        self.actionNew_character = QAction(CustomMainWindow)
        self.actionNew_character.setObjectName(u"actionNew_character")
        self.actionNew_map = QAction(CustomMainWindow)
        self.actionNew_map.setObjectName(u"actionNew_map")
        self.actionOpen_character = QAction(CustomMainWindow)
        self.actionOpen_character.setObjectName(u"actionOpen_character")
        self.actionOpen_map = QAction(CustomMainWindow)
        self.actionOpen_map.setObjectName(u"actionOpen_map")
        self.actionSave = QAction(CustomMainWindow)
        self.actionSave.setObjectName(u"actionSave")
        self.actionSave_as = QAction(CustomMainWindow)
        self.actionSave_as.setObjectName(u"actionSave_as")
        self.actionClose = QAction(CustomMainWindow)
        self.actionClose.setObjectName(u"actionClose")
        self.actionUndo = QAction(CustomMainWindow)
        self.actionUndo.setObjectName(u"actionUndo")
        self.actionRedo = QAction(CustomMainWindow)
        self.actionRedo.setObjectName(u"actionRedo")
        self.actionLog_Chat = QAction(CustomMainWindow)
        self.actionLog_Chat.setObjectName(u"actionLog_Chat")
        self.actionLog_Chat.setCheckable(True)
        self.actionLog_Chat.setChecked(True)
        self.actionInfo_menu = QAction(CustomMainWindow)
        self.actionInfo_menu.setObjectName(u"actionInfo_menu")
        self.actionInfo_menu.setCheckable(True)
        self.actionInfo_menu.setChecked(True)
        self.actionNew_item = QAction(CustomMainWindow)
        self.actionNew_item.setObjectName(u"actionNew_item")
        self.actionOpen_item = QAction(CustomMainWindow)
        self.actionOpen_item.setObjectName(u"actionOpen_item")
        self.actionNew_spell = QAction(CustomMainWindow)
        self.actionNew_spell.setObjectName(u"actionNew_spell")
        self.actionOpen_spell = QAction(CustomMainWindow)
        self.actionOpen_spell.setObjectName(u"actionOpen_spell")
        self.central_widget = QWidget(CustomMainWindow)
        self.central_widget.setObjectName(u"central_widget")
        self.horizontalLayout = QHBoxLayout(self.central_widget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.sidebar = QWidget(self.central_widget)
        self.sidebar.setObjectName(u"sidebar")
        self.sidebar.setMinimumSize(QSize(110, 0))
        self.sidebar.setMaximumSize(QSize(110, 16777215))
        self.verticalLayout = QVBoxLayout(self.sidebar)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.widget_6 = QWidget(self.sidebar)
        self.widget_6.setObjectName(u"widget_6")
        self.widget_6.setMaximumSize(QSize(1666600, 166660))
        self.horizontalLayout_7 = QHBoxLayout(self.widget_6)
        self.horizontalLayout_7.setSpacing(0)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.horizontalLayout_7.setContentsMargins(0, 0, 5, 0)
        self.open_info_menu_btn = QPushButton(self.widget_6)
        self.open_info_menu_btn.setObjectName(u"open_info_menu_btn")
        self.open_info_menu_btn.setEnabled(True)
        self.open_info_menu_btn.setMinimumSize(QSize(30, 30))
        self.open_info_menu_btn.setMaximumSize(QSize(30, 30))
        icon = QIcon()
        icon.addFile(u"image/Undo.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.open_info_menu_btn.setIcon(icon)

        self.horizontalLayout_7.addWidget(self.open_info_menu_btn)


        self.verticalLayout.addWidget(self.widget_6, 0, Qt.AlignmentFlag.AlignRight)

        self.widget_2 = QWidget(self.sidebar)
        self.widget_2.setObjectName(u"widget_2")
        self.verticalLayout_2 = QVBoxLayout(self.widget_2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(5, 5, 5, 5)

        self.verticalLayout.addWidget(self.widget_2, 0, Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTop)

        self.widget_3 = QWidget(self.sidebar)
        self.widget_3.setObjectName(u"widget_3")
        self.verticalLayout_4 = QVBoxLayout(self.widget_3)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(5, 5, 5, 5)
        self.item_btn = QPushButton(self.widget_3)
        self.item_btn.setObjectName(u"item_btn")
        self.item_btn.setMinimumSize(QSize(0, 30))

        self.verticalLayout_4.addWidget(self.item_btn)

        self.spell_btn = QPushButton(self.widget_3)
        self.spell_btn.setObjectName(u"spell_btn")
        self.spell_btn.setMinimumSize(QSize(0, 30))

        self.verticalLayout_4.addWidget(self.spell_btn)

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


        self.verticalLayout.addWidget(self.widget_3, 0, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignTop)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.widget = QWidget(self.sidebar)
        self.widget.setObjectName(u"widget")
        self.verticalLayout_3 = QVBoxLayout(self.widget)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 5, 5, 5)
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


        self.verticalLayout.addWidget(self.widget, 0, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignBottom)


        self.horizontalLayout.addWidget(self.sidebar, 0, Qt.AlignmentFlag.AlignLeft)

        self.line_7 = QFrame(self.central_widget)
        self.line_7.setObjectName(u"line_7")
        self.line_7.setFrameShadow(QFrame.Shadow.Sunken)
        self.line_7.setLineWidth(1)
        self.line_7.setFrameShape(QFrame.Shape.VLine)

        self.horizontalLayout.addWidget(self.line_7)

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
        self.horizontalLayout_2.setContentsMargins(-1, 0, -1, 0)
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
        self.character_name = QTextEdit(self.character_menu)
        self.character_name.setObjectName(u"character_name")
        self.character_name.setMaximumSize(QSize(16777215, 30))
        self.character_name.setAcceptDrops(False)
        self.character_name.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.verticalLayout_12.addWidget(self.character_name)

        self.character_menu_selection_bar = QWidget(self.character_menu)
        self.character_menu_selection_bar.setObjectName(u"character_menu_selection_bar")
        self.horizontalLayout_5 = QHBoxLayout(self.character_menu_selection_bar)
        self.horizontalLayout_5.setSpacing(0)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.tabWidget = QTabWidget(self.character_menu_selection_bar)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setTabShape(QTabWidget.TabShape.Rounded)
        self.tabWidget.setElideMode(Qt.TextElideMode.ElideNone)
        self.tabWidget.setTabsClosable(False)
        self.stat = QWidget()
        self.stat.setObjectName(u"stat")
        self.verticalLayout_14 = QVBoxLayout(self.stat)
        self.verticalLayout_14.setObjectName(u"verticalLayout_14")
        self.formWidget = QWidget(self.stat)
        self.formWidget.setObjectName(u"formWidget")
        self.formWidget.setMaximumSize(QSize(16777215, 30))
        self.formLayout = QFormLayout(self.formWidget)
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        self.formLayout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.formLayout.setContentsMargins(0, 0, 0, 2)
        self.hp_label = QLabel(self.formWidget)
        self.hp_label.setObjectName(u"hp_label")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.hp_label)

        self.hp_nb = QSpinBox(self.formWidget)
        self.hp_nb.setObjectName(u"hp_nb")
        self.hp_nb.setMaximumSize(QSize(50, 16777215))
        self.hp_nb.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.hp_nb.setCorrectionMode(QAbstractSpinBox.CorrectionMode.CorrectToPreviousValue)

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.hp_nb)


        self.verticalLayout_14.addWidget(self.formWidget)

        self.line = QFrame(self.stat)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_14.addWidget(self.line)

        self.formWidget_2 = QWidget(self.stat)
        self.formWidget_2.setObjectName(u"formWidget_2")
        self.formLayout_2 = QFormLayout(self.formWidget_2)
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.formLayout_2.setSizeConstraint(QLayout.SizeConstraint.SetMaximumSize)
        self.formLayout_2.setContentsMargins(0, 2, 0, 2)
        self.str_label = QLabel(self.formWidget_2)
        self.str_label.setObjectName(u"str_label")

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.LabelRole, self.str_label)

        self.str_nb = QSpinBox(self.formWidget_2)
        self.str_nb.setObjectName(u"str_nb")
        self.str_nb.setMaximumSize(QSize(50, 16777215))
        self.str_nb.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.FieldRole, self.str_nb)

        self.dex_label = QLabel(self.formWidget_2)
        self.dex_label.setObjectName(u"dex_label")

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.LabelRole, self.dex_label)

        self.dex_nb = QSpinBox(self.formWidget_2)
        self.dex_nb.setObjectName(u"dex_nb")
        self.dex_nb.setMaximumSize(QSize(50, 16777215))
        self.dex_nb.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.FieldRole, self.dex_nb)

        self.con_nb = QSpinBox(self.formWidget_2)
        self.con_nb.setObjectName(u"con_nb")
        self.con_nb.setMaximumSize(QSize(50, 16777215))
        self.con_nb.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)

        self.formLayout_2.setWidget(2, QFormLayout.ItemRole.FieldRole, self.con_nb)

        self.int_label = QLabel(self.formWidget_2)
        self.int_label.setObjectName(u"int_label")

        self.formLayout_2.setWidget(3, QFormLayout.ItemRole.LabelRole, self.int_label)

        self.int_nb = QSpinBox(self.formWidget_2)
        self.int_nb.setObjectName(u"int_nb")
        self.int_nb.setMaximumSize(QSize(50, 16777215))
        self.int_nb.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)

        self.formLayout_2.setWidget(3, QFormLayout.ItemRole.FieldRole, self.int_nb)

        self.wis_label = QLabel(self.formWidget_2)
        self.wis_label.setObjectName(u"wis_label")

        self.formLayout_2.setWidget(4, QFormLayout.ItemRole.LabelRole, self.wis_label)

        self.wis_nb = QSpinBox(self.formWidget_2)
        self.wis_nb.setObjectName(u"wis_nb")
        self.wis_nb.setMaximumSize(QSize(50, 16777215))
        self.wis_nb.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)

        self.formLayout_2.setWidget(4, QFormLayout.ItemRole.FieldRole, self.wis_nb)

        self.cha_label = QLabel(self.formWidget_2)
        self.cha_label.setObjectName(u"cha_label")

        self.formLayout_2.setWidget(5, QFormLayout.ItemRole.LabelRole, self.cha_label)

        self.cha_nb = QSpinBox(self.formWidget_2)
        self.cha_nb.setObjectName(u"cha_nb")
        self.cha_nb.setMaximumSize(QSize(50, 16777215))
        self.cha_nb.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)

        self.formLayout_2.setWidget(5, QFormLayout.ItemRole.FieldRole, self.cha_nb)

        self.con_label = QLabel(self.formWidget_2)
        self.con_label.setObjectName(u"con_label")

        self.formLayout_2.setWidget(2, QFormLayout.ItemRole.LabelRole, self.con_label)


        self.verticalLayout_14.addWidget(self.formWidget_2)

        self.line_2 = QFrame(self.stat)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.Shape.HLine)
        self.line_2.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_14.addWidget(self.line_2)

        self.widget_7 = QWidget(self.stat)
        self.widget_7.setObjectName(u"widget_7")
        self.verticalLayout_15 = QVBoxLayout(self.widget_7)
        self.verticalLayout_15.setObjectName(u"verticalLayout_15")
        self.verticalLayout_15.setContentsMargins(0, 2, 0, 2)
        self.isNPC = QCheckBox(self.widget_7)
        self.isNPC.setObjectName(u"isNPC")

        self.verticalLayout_15.addWidget(self.isNPC)

        self.alignement_NPC = QComboBox(self.widget_7)
        self.alignement_NPC.addItem("")
        self.alignement_NPC.addItem("")
        self.alignement_NPC.addItem("")
        self.alignement_NPC.setObjectName(u"alignement_NPC")
        self.alignement_NPC.setEnabled(True)
        self.alignement_NPC.setMaximumSize(QSize(100, 16777215))
        self.alignement_NPC.setDuplicatesEnabled(True)

        self.verticalLayout_15.addWidget(self.alignement_NPC)


        self.verticalLayout_14.addWidget(self.widget_7)

        self.line_3 = QFrame(self.stat)
        self.line_3.setObjectName(u"line_3")
        self.line_3.setFrameShape(QFrame.Shape.HLine)
        self.line_3.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_14.addWidget(self.line_3)

        self.widget_5 = QWidget(self.stat)
        self.widget_5.setObjectName(u"widget_5")
        self.verticalLayout_20 = QVBoxLayout(self.widget_5)
        self.verticalLayout_20.setObjectName(u"verticalLayout_20")
        self.verticalLayout_20.setContentsMargins(0, 0, 0, 0)
        self.create_new_character_btn = QPushButton(self.widget_5)
        self.create_new_character_btn.setObjectName(u"create_new_character_btn")

        self.verticalLayout_20.addWidget(self.create_new_character_btn)

        self.save_character_btn = QPushButton(self.widget_5)
        self.save_character_btn.setObjectName(u"save_character_btn")

        self.verticalLayout_20.addWidget(self.save_character_btn)

        self.load_character_btn = QPushButton(self.widget_5)
        self.load_character_btn.setObjectName(u"load_character_btn")

        self.verticalLayout_20.addWidget(self.load_character_btn)


        self.verticalLayout_14.addWidget(self.widget_5)

        self.tabWidget.addTab(self.stat, "")
        self.inventory = QWidget()
        self.inventory.setObjectName(u"inventory")
        self.verticalLayout_18 = QVBoxLayout(self.inventory)
        self.verticalLayout_18.setObjectName(u"verticalLayout_18")
        self.verticalLayout_18.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        self.verticalLayout_18.setContentsMargins(0, 0, 0, 0)
        self.widget_8 = QWidget(self.inventory)
        self.widget_8.setObjectName(u"widget_8")
        self.widget_8.setMinimumSize(QSize(0, 100))
        self.widget_8.setMaximumSize(QSize(16777215, 100))
        self.verticalLayout_19 = QVBoxLayout(self.widget_8)
        self.verticalLayout_19.setObjectName(u"verticalLayout_19")
        self.verticalLayout_19.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.verticalLayout_19.setContentsMargins(0, 6, 0, 0)
        self.add_item_btn = QPushButton(self.widget_8)
        self.add_item_btn.setObjectName(u"add_item_btn")
        self.add_item_btn.setMaximumSize(QSize(16777215, 16777215))

        self.verticalLayout_19.addWidget(self.add_item_btn)

        self.edit_item_btn = QPushButton(self.widget_8)
        self.edit_item_btn.setObjectName(u"edit_item_btn")

        self.verticalLayout_19.addWidget(self.edit_item_btn)

        self.remove_item_btn = QPushButton(self.widget_8)
        self.remove_item_btn.setObjectName(u"remove_item_btn")
        self.remove_item_btn.setMaximumSize(QSize(16777215, 16777215))

        self.verticalLayout_19.addWidget(self.remove_item_btn)


        self.verticalLayout_18.addWidget(self.widget_8, 0, Qt.AlignmentFlag.AlignTop)

        self.line_5 = QFrame(self.inventory)
        self.line_5.setObjectName(u"line_5")
        self.line_5.setFrameShape(QFrame.Shape.HLine)
        self.line_5.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_18.addWidget(self.line_5)

        self.item_grid = QGridLayout()
        self.item_grid.setObjectName(u"item_grid")
        self.item_grid.setSizeConstraint(QLayout.SizeConstraint.SetMaximumSize)

        self.verticalLayout_18.addLayout(self.item_grid)

        self.item_desc_display = QTextEdit(self.inventory)
        self.item_desc_display.setObjectName(u"item_desc_display")
        self.item_desc_display.setMaximumSize(QSize(16777215, 100))
        self.item_desc_display.setReadOnly(True)

        self.verticalLayout_18.addWidget(self.item_desc_display)

        self.tabWidget.addTab(self.inventory, "")
        self.spell = QWidget()
        self.spell.setObjectName(u"spell")
        self.verticalLayout_16 = QVBoxLayout(self.spell)
        self.verticalLayout_16.setObjectName(u"verticalLayout_16")
        self.verticalLayout_16.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        self.verticalLayout_16.setContentsMargins(0, 0, 0, 0)
        self.widget_9 = QWidget(self.spell)
        self.widget_9.setObjectName(u"widget_9")
        self.widget_9.setMaximumSize(QSize(16777215, 100))
        self.verticalLayout_17 = QVBoxLayout(self.widget_9)
        self.verticalLayout_17.setObjectName(u"verticalLayout_17")
        self.verticalLayout_17.setContentsMargins(0, 6, 0, 0)
        self.add_spell_btn = QPushButton(self.widget_9)
        self.add_spell_btn.setObjectName(u"add_spell_btn")

        self.verticalLayout_17.addWidget(self.add_spell_btn)

        self.edit_spell_btn = QPushButton(self.widget_9)
        self.edit_spell_btn.setObjectName(u"edit_spell_btn")

        self.verticalLayout_17.addWidget(self.edit_spell_btn)

        self.remove_spell_btn = QPushButton(self.widget_9)
        self.remove_spell_btn.setObjectName(u"remove_spell_btn")

        self.verticalLayout_17.addWidget(self.remove_spell_btn)


        self.verticalLayout_16.addWidget(self.widget_9, 0, Qt.AlignmentFlag.AlignTop)

        self.line_6 = QFrame(self.spell)
        self.line_6.setObjectName(u"line_6")
        self.line_6.setFrameShape(QFrame.Shape.HLine)
        self.line_6.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_16.addWidget(self.line_6)

        self.spell_grid = QGridLayout()
        self.spell_grid.setObjectName(u"spell_grid")
        self.spell_grid.setSizeConstraint(QLayout.SizeConstraint.SetMaximumSize)

        self.verticalLayout_16.addLayout(self.spell_grid)

        self.spell_desc_display = QTextEdit(self.spell)
        self.spell_desc_display.setObjectName(u"spell_desc_display")
        self.spell_desc_display.setMaximumSize(QSize(16777215, 100))
        self.spell_desc_display.setReadOnly(True)

        self.verticalLayout_16.addWidget(self.spell_desc_display)

        self.tabWidget.addTab(self.spell, "")
        self.trait = QWidget()
        self.trait.setObjectName(u"trait")
        self.verticalLayout_23 = QVBoxLayout(self.trait)
        self.verticalLayout_23.setSpacing(0)
        self.verticalLayout_23.setObjectName(u"verticalLayout_23")
        self.verticalLayout_23.setContentsMargins(0, 0, 0, 0)
        self.clear_trait_btn = QPushButton(self.trait)
        self.clear_trait_btn.setObjectName(u"clear_trait_btn")

        self.verticalLayout_23.addWidget(self.clear_trait_btn)

        self.trait_editbox = QTextEdit(self.trait)
        self.trait_editbox.setObjectName(u"trait_editbox")

        self.verticalLayout_23.addWidget(self.trait_editbox)

        self.tabWidget.addTab(self.trait, "")

        self.horizontalLayout_5.addWidget(self.tabWidget)


        self.verticalLayout_12.addWidget(self.character_menu_selection_bar)

        self.stacked_widget.addWidget(self.character_menu)
        self.map_menu = QWidget()
        self.map_menu.setObjectName(u"map_menu")
        self.verticalLayout_13 = QVBoxLayout(self.map_menu)
        self.verticalLayout_13.setObjectName(u"verticalLayout_13")
        self.map_menu_label = QLabel(self.map_menu)
        self.map_menu_label.setObjectName(u"map_menu_label")
        self.map_menu_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_13.addWidget(self.map_menu_label, 0, Qt.AlignmentFlag.AlignTop)

        self.line_map_1 = QFrame(self.map_menu)
        self.line_map_1.setObjectName(u"line_map_1")
        self.line_map_1.setFrameShape(QFrame.Shape.HLine)
        self.line_map_1.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_13.addWidget(self.line_map_1)

        self.map_image_list_label = QLabel(self.map_menu)
        self.map_image_list_label.setObjectName(u"map_image_list_label")
        self.map_image_list_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.verticalLayout_13.addWidget(self.map_image_list_label)

        self.map_image_list = QListWidget(self.map_menu)
        self.map_image_list.setObjectName(u"map_image_list")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(1)
        sizePolicy1.setHeightForWidth(self.map_image_list.sizePolicy().hasHeightForWidth())
        self.map_image_list.setSizePolicy(sizePolicy1)
        self.map_image_list.setIconSize(QSize(32, 32))
        self.map_image_list.setUniformItemSizes(True)

        self.verticalLayout_13.addWidget(self.map_image_list)

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

        self.open_game_interface_btn = QPushButton(self.server_menu)
        self.open_game_interface_btn.setObjectName(u"open_game_interface_btn")
        self.open_game_interface_btn.setMinimumSize(QSize(0, 38))
        self.open_game_interface_btn.setMaximumSize(QSize(16777215, 38))

        self.verticalLayout_11.addWidget(self.open_game_interface_btn)

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
        self.item_menu = QWidget()
        self.item_menu.setObjectName(u"item_menu")
        self.verticalLayout_22 = QVBoxLayout(self.item_menu)
        self.verticalLayout_22.setObjectName(u"verticalLayout_22")
        self.verticalLayout_22.setContentsMargins(0, 0, 0, 0)
        self.item_name = QLineEdit(self.item_menu)
        self.item_name.setObjectName(u"item_name")

        self.verticalLayout_22.addWidget(self.item_name)

        self.item_type = QComboBox(self.item_menu)
        self.item_type.addItem("")
        self.item_type.addItem("")
        self.item_type.addItem("")
        self.item_type.addItem("")
        self.item_type.setObjectName(u"item_type")

        self.verticalLayout_22.addWidget(self.item_type)

        self.widget_10 = QWidget(self.item_menu)
        self.widget_10.setObjectName(u"widget_10")
        self.horizontalLayout_6 = QHBoxLayout(self.widget_10)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.item_img = QLabel(self.widget_10)
        self.item_img.setObjectName(u"item_img")
        self.item_img.setMaximumSize(QSize(30, 30))
        self.item_img.setPixmap(QPixmap(u"image/placeholder.png"))
        self.item_img.setScaledContents(True)

        self.horizontalLayout_6.addWidget(self.item_img)

        self.choose_item_img = QPushButton(self.widget_10)
        self.choose_item_img.setObjectName(u"choose_item_img")

        self.horizontalLayout_6.addWidget(self.choose_item_img)


        self.verticalLayout_22.addWidget(self.widget_10)

        self.item_description = QTextEdit(self.item_menu)
        self.item_description.setObjectName(u"item_description")

        self.verticalLayout_22.addWidget(self.item_description)

        self.line_4 = QFrame(self.item_menu)
        self.line_4.setObjectName(u"line_4")
        self.line_4.setFrameShape(QFrame.Shape.HLine)
        self.line_4.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_22.addWidget(self.line_4)

        self.create_new_item_btn = QPushButton(self.item_menu)
        self.create_new_item_btn.setObjectName(u"create_new_item_btn")

        self.verticalLayout_22.addWidget(self.create_new_item_btn)

        self.save_item = QPushButton(self.item_menu)
        self.save_item.setObjectName(u"save_item")

        self.verticalLayout_22.addWidget(self.save_item)

        self.load_item = QPushButton(self.item_menu)
        self.load_item.setObjectName(u"load_item")

        self.verticalLayout_22.addWidget(self.load_item)

        self.stacked_widget.addWidget(self.item_menu)
        self.spell_menu = QWidget()
        self.spell_menu.setObjectName(u"spell_menu")
        self.verticalLayout_21 = QVBoxLayout(self.spell_menu)
        self.verticalLayout_21.setObjectName(u"verticalLayout_21")
        self.verticalLayout_21.setContentsMargins(0, 0, 0, 0)
        self.spell_name = QLineEdit(self.spell_menu)
        self.spell_name.setObjectName(u"spell_name")

        self.verticalLayout_21.addWidget(self.spell_name)

        self.widget_11 = QWidget(self.spell_menu)
        self.widget_11.setObjectName(u"widget_11")
        self.widget_11.setMaximumSize(QSize(167775, 50))
        self.horizontalLayout_8 = QHBoxLayout(self.widget_11)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.horizontalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.spell_img = QLabel(self.widget_11)
        self.spell_img.setObjectName(u"spell_img")
        self.spell_img.setMaximumSize(QSize(30, 30))
        self.spell_img.setPixmap(QPixmap(u"image/placeholder.png"))
        self.spell_img.setScaledContents(True)

        self.horizontalLayout_8.addWidget(self.spell_img)

        self.choose_spell_img = QPushButton(self.widget_11)
        self.choose_spell_img.setObjectName(u"choose_spell_img")

        self.horizontalLayout_8.addWidget(self.choose_spell_img)


        self.verticalLayout_21.addWidget(self.widget_11)

        self.spell_description = QTextEdit(self.spell_menu)
        self.spell_description.setObjectName(u"spell_description")

        self.verticalLayout_21.addWidget(self.spell_description)

        self.line_8 = QFrame(self.spell_menu)
        self.line_8.setObjectName(u"line_8")
        self.line_8.setFrameShape(QFrame.Shape.HLine)
        self.line_8.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_21.addWidget(self.line_8)

        self.create_new_spell_btn = QPushButton(self.spell_menu)
        self.create_new_spell_btn.setObjectName(u"create_new_spell_btn")

        self.verticalLayout_21.addWidget(self.create_new_spell_btn)

        self.save_spell = QPushButton(self.spell_menu)
        self.save_spell.setObjectName(u"save_spell")

        self.verticalLayout_21.addWidget(self.save_spell)

        self.load_spell = QPushButton(self.spell_menu)
        self.load_spell.setObjectName(u"load_spell")

        self.verticalLayout_21.addWidget(self.load_spell)

        self.stacked_widget.addWidget(self.spell_menu)

        self.verticalLayout_5.addWidget(self.stacked_widget)


        self.horizontalLayout.addWidget(self.center_menu)

        self.main_body = QWidget(self.central_widget)
        self.main_body.setObjectName(u"main_body")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.main_body.sizePolicy().hasHeightForWidth())
        self.main_body.setSizePolicy(sizePolicy2)
        self.verticalLayout_10 = QVBoxLayout(self.main_body)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.log_view_top = QWidget(self.main_body)
        self.log_view_top.setObjectName(u"log_view_top")
        self.horizontalLayout_4 = QHBoxLayout(self.log_view_top)
        self.horizontalLayout_4.setSpacing(0)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.log_view_label = QLabel(self.log_view_top)
        self.log_view_label.setObjectName(u"log_view_label")

        self.horizontalLayout_4.addWidget(self.log_view_label)

        self.close_log_view_btn = QPushButton(self.log_view_top)
        self.close_log_view_btn.setObjectName(u"close_log_view_btn")
        self.close_log_view_btn.setMinimumSize(QSize(30, 30))
        self.close_log_view_btn.setMaximumSize(QSize(30, 30))

        self.horizontalLayout_4.addWidget(self.close_log_view_btn)


        self.verticalLayout_10.addWidget(self.log_view_top)

        self.log_view = QTextEdit(self.main_body)
        self.log_view.setObjectName(u"log_view")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.log_view.sizePolicy().hasHeightForWidth())
        self.log_view.setSizePolicy(sizePolicy3)
        self.log_view.setMinimumSize(QSize(0, 130))
        self.log_view.setMaximumSize(QSize(166666, 130))
        self.log_view.setReadOnly(True)

        self.verticalLayout_10.addWidget(self.log_view)


        self.horizontalLayout.addWidget(self.main_body)

        CustomMainWindow.setCentralWidget(self.central_widget)
        self.menuBar = QMenuBar(CustomMainWindow)
        self.menuBar.setObjectName(u"menuBar")
        self.menuBar.setGeometry(QRect(0, 0, 800, 33))
        self.menuBar.setMaximumSize(QSize(16777215, 50))
        self.menuBar.setStyleSheet(u"")
        self.menuFile = QMenu(self.menuBar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuNew = QMenu(self.menuFile)
        self.menuNew.setObjectName(u"menuNew")
        self.menuOpen = QMenu(self.menuFile)
        self.menuOpen.setObjectName(u"menuOpen")
        self.menuHelp = QMenu(self.menuBar)
        self.menuHelp.setObjectName(u"menuHelp")
        self.menuEdit = QMenu(self.menuBar)
        self.menuEdit.setObjectName(u"menuEdit")
        self.menuDisplay = QMenu(self.menuBar)
        self.menuDisplay.setObjectName(u"menuDisplay")
        CustomMainWindow.setMenuBar(self.menuBar)

        self.menuBar.addAction(self.menuFile.menuAction())
        self.menuBar.addAction(self.menuEdit.menuAction())
        self.menuBar.addAction(self.menuDisplay.menuAction())
        self.menuBar.addAction(self.menuHelp.menuAction())
        self.menuFile.addAction(self.menuNew.menuAction())
        self.menuFile.addAction(self.menuOpen.menuAction())
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionSave_as)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionClose)
        self.menuNew.addAction(self.actionNew_character)
        self.menuNew.addAction(self.actionNew_map)
        self.menuNew.addAction(self.actionNew_item)
        self.menuNew.addAction(self.actionNew_spell)
        self.menuOpen.addAction(self.actionOpen_character)
        self.menuOpen.addAction(self.actionOpen_map)
        self.menuOpen.addAction(self.actionOpen_item)
        self.menuOpen.addAction(self.actionOpen_spell)
        self.menuEdit.addAction(self.actionUndo)
        self.menuEdit.addAction(self.actionRedo)
        self.menuDisplay.addAction(self.actionLog_Chat)
        self.menuDisplay.addAction(self.actionInfo_menu)

        self.retranslateUi(CustomMainWindow)

        self.stacked_widget.setCurrentIndex(1)
        self.tabWidget.setCurrentIndex(3)


        QMetaObject.connectSlotsByName(CustomMainWindow)
    # setupUi

    def retranslateUi(self, CustomMainWindow):
        CustomMainWindow.setWindowTitle(QCoreApplication.translate("CustomMainWindow", u"Custom MainWindow", None))
        self.actionNew_character.setText(QCoreApplication.translate("CustomMainWindow", u"New character", None))
        self.actionNew_map.setText(QCoreApplication.translate("CustomMainWindow", u"New map", None))
        self.actionOpen_character.setText(QCoreApplication.translate("CustomMainWindow", u"Open character", None))
        self.actionOpen_map.setText(QCoreApplication.translate("CustomMainWindow", u"Open map", None))
        self.actionSave.setText(QCoreApplication.translate("CustomMainWindow", u"Save", None))
#if QT_CONFIG(shortcut)
        self.actionSave.setShortcut(QCoreApplication.translate("CustomMainWindow", u"Ctrl+S", None))
#endif // QT_CONFIG(shortcut)
        self.actionSave_as.setText(QCoreApplication.translate("CustomMainWindow", u"Save as...", None))
        self.actionClose.setText(QCoreApplication.translate("CustomMainWindow", u"Close", None))
#if QT_CONFIG(shortcut)
        self.actionClose.setShortcut(QCoreApplication.translate("CustomMainWindow", u"Alt+F4", None))
#endif // QT_CONFIG(shortcut)
        self.actionUndo.setText(QCoreApplication.translate("CustomMainWindow", u"Undo", None))
#if QT_CONFIG(shortcut)
        self.actionUndo.setShortcut(QCoreApplication.translate("CustomMainWindow", u"Ctrl+Z", None))
#endif // QT_CONFIG(shortcut)
        self.actionRedo.setText(QCoreApplication.translate("CustomMainWindow", u"Redo", None))
#if QT_CONFIG(shortcut)
        self.actionRedo.setShortcut(QCoreApplication.translate("CustomMainWindow", u"Ctrl+Shift+Z", None))
#endif // QT_CONFIG(shortcut)
        self.actionLog_Chat.setText(QCoreApplication.translate("CustomMainWindow", u"Log/Chat", None))
        self.actionInfo_menu.setText(QCoreApplication.translate("CustomMainWindow", u"Info menu", None))
        self.actionNew_item.setText(QCoreApplication.translate("CustomMainWindow", u"New item", None))
        self.actionOpen_item.setText(QCoreApplication.translate("CustomMainWindow", u"Open item", None))
        self.actionNew_spell.setText(QCoreApplication.translate("CustomMainWindow", u"New spell", None))
        self.actionOpen_spell.setText(QCoreApplication.translate("CustomMainWindow", u"Open spell", None))
        self.open_info_menu_btn.setText("")
        self.item_btn.setText(QCoreApplication.translate("CustomMainWindow", u"Item", None))
        self.spell_btn.setText(QCoreApplication.translate("CustomMainWindow", u"Spell", None))
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
        self.character_name.setHtml(QCoreApplication.translate("CustomMainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>", None))
        self.character_name.setPlaceholderText(QCoreApplication.translate("CustomMainWindow", u"Chraracter Name", None))
        self.hp_label.setText(QCoreApplication.translate("CustomMainWindow", u"HP:", None))
        self.str_label.setText(QCoreApplication.translate("CustomMainWindow", u"STR:", None))
        self.dex_label.setText(QCoreApplication.translate("CustomMainWindow", u"DEX:", None))
        self.int_label.setText(QCoreApplication.translate("CustomMainWindow", u"INT:", None))
        self.wis_label.setText(QCoreApplication.translate("CustomMainWindow", u"WIS:", None))
        self.cha_label.setText(QCoreApplication.translate("CustomMainWindow", u"CHA:", None))
        self.con_label.setText(QCoreApplication.translate("CustomMainWindow", u"CON:", None))
        self.isNPC.setText(QCoreApplication.translate("CustomMainWindow", u"isNPC?", None))
        self.alignement_NPC.setItemText(0, QCoreApplication.translate("CustomMainWindow", u"Ally", None))
        self.alignement_NPC.setItemText(1, QCoreApplication.translate("CustomMainWindow", u"Neutral", None))
        self.alignement_NPC.setItemText(2, QCoreApplication.translate("CustomMainWindow", u"Enemy", None))

        self.create_new_character_btn.setText(QCoreApplication.translate("CustomMainWindow", u"Create new character", None))
        self.save_character_btn.setText(QCoreApplication.translate("CustomMainWindow", u"Save character", None))
        self.load_character_btn.setText(QCoreApplication.translate("CustomMainWindow", u"Load character", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.stat), QCoreApplication.translate("CustomMainWindow", u"Stat", None))
        self.add_item_btn.setText(QCoreApplication.translate("CustomMainWindow", u"Add item", None))
        self.edit_item_btn.setText(QCoreApplication.translate("CustomMainWindow", u"Edit item", None))
        self.remove_item_btn.setText(QCoreApplication.translate("CustomMainWindow", u"Remove item", None))
        self.item_desc_display.setPlaceholderText(QCoreApplication.translate("CustomMainWindow", u"Select an item to see its description", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.inventory), QCoreApplication.translate("CustomMainWindow", u"Inventory", None))
        self.add_spell_btn.setText(QCoreApplication.translate("CustomMainWindow", u"Add Spell", None))
        self.edit_spell_btn.setText(QCoreApplication.translate("CustomMainWindow", u"Edit spell", None))
        self.remove_spell_btn.setText(QCoreApplication.translate("CustomMainWindow", u"Remove spell", None))
        self.spell_desc_display.setPlaceholderText(QCoreApplication.translate("CustomMainWindow", u"Select a spell to see its description", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.spell), QCoreApplication.translate("CustomMainWindow", u"Spell", None))
        self.clear_trait_btn.setText(QCoreApplication.translate("CustomMainWindow", u"Clear trait", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.trait), QCoreApplication.translate("CustomMainWindow", u"Trait", None))
        self.map_menu_label.setText(QCoreApplication.translate("CustomMainWindow", u"Map tools", None))
        self.map_image_list_label.setText(QCoreApplication.translate("CustomMainWindow", u"Images", None))
        self.server_state_label.setText(QCoreApplication.translate("CustomMainWindow", u"Server: closed", None))
        self.url_link_label.setText(QCoreApplication.translate("CustomMainWindow", u"URL : <a href=\"{SERVER_URL}\">{SERVER_URL}</a>", None))
        self.open_server_btn.setText(QCoreApplication.translate("CustomMainWindow", u"Open server", None))
        self.close_server_btn.setText(QCoreApplication.translate("CustomMainWindow", u"Close server", None))
        self.open_website_btn.setText(QCoreApplication.translate("CustomMainWindow", u"Open website", None))
        self.open_game_interface_btn.setText(QCoreApplication.translate("CustomMainWindow", u"Open game interface", None))
        self.information_menu_label.setText(QCoreApplication.translate("CustomMainWindow", u"Information", None))
        self.help_menu_label.setText(QCoreApplication.translate("CustomMainWindow", u"Help", None))
        self.item_name.setPlaceholderText(QCoreApplication.translate("CustomMainWindow", u"Item name", None))
        self.item_type.setItemText(0, QCoreApplication.translate("CustomMainWindow", u"Weapon", None))
        self.item_type.setItemText(1, QCoreApplication.translate("CustomMainWindow", u"Armour", None))
        self.item_type.setItemText(2, QCoreApplication.translate("CustomMainWindow", u"Consumable", None))
        self.item_type.setItemText(3, QCoreApplication.translate("CustomMainWindow", u"Miscellaneous", None))

        self.item_img.setText("")
        self.choose_item_img.setText(QCoreApplication.translate("CustomMainWindow", u"Choose item icon", None))
        self.item_description.setPlaceholderText(QCoreApplication.translate("CustomMainWindow", u"Item description", None))
        self.create_new_item_btn.setText(QCoreApplication.translate("CustomMainWindow", u"Create new item", None))
        self.save_item.setText(QCoreApplication.translate("CustomMainWindow", u"Save item", None))
        self.load_item.setText(QCoreApplication.translate("CustomMainWindow", u"Load item", None))
        self.spell_name.setPlaceholderText(QCoreApplication.translate("CustomMainWindow", u"Spell name", None))
        self.spell_img.setText("")
        self.choose_spell_img.setText(QCoreApplication.translate("CustomMainWindow", u"Choose spell icon", None))
        self.spell_description.setPlaceholderText(QCoreApplication.translate("CustomMainWindow", u"Spell description", None))
        self.create_new_spell_btn.setText(QCoreApplication.translate("CustomMainWindow", u"Create new spell", None))
        self.save_spell.setText(QCoreApplication.translate("CustomMainWindow", u"Save spell", None))
        self.load_spell.setText(QCoreApplication.translate("CustomMainWindow", u"Load spell", None))
        self.log_view_label.setText(QCoreApplication.translate("CustomMainWindow", u"Logs du serveur PHP :", None))
        self.close_log_view_btn.setText(QCoreApplication.translate("CustomMainWindow", u"\u2715", None))
        self.menuFile.setTitle(QCoreApplication.translate("CustomMainWindow", u"File", None))
        self.menuNew.setTitle(QCoreApplication.translate("CustomMainWindow", u"New...", None))
        self.menuOpen.setTitle(QCoreApplication.translate("CustomMainWindow", u"Open", None))
        self.menuHelp.setTitle(QCoreApplication.translate("CustomMainWindow", u"Help", None))
        self.menuEdit.setTitle(QCoreApplication.translate("CustomMainWindow", u"Edit", None))
        self.menuDisplay.setTitle(QCoreApplication.translate("CustomMainWindow", u"Display", None))
    # retranslateUi

