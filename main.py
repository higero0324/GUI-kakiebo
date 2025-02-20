import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox,
    QComboBox, QMenu, QStyledItemDelegate, QAbstractItemView  # 追加
)
from PySide6.QtCharts import QChart, QChartView, QPieSeries
from PySide6.QtCore import Qt, QTimer  # 追加

# 追加: ジャンル用デリゲートの定義
class GenreDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        editor.addItems(["未分類", "食費", "交通費", "娯楽費", "その他", "収入"])
        return editor

    def setEditorData(self, editor, index):
        value = index.data() or ""
        pos = editor.findText(value)
        if pos < 0:
            pos = 0
        editor.setCurrentIndex(pos)

    def setModelData(self, editor, model, index):
        model.setData(index, editor.currentText())

# DraggableTableWidget を定義して、InternalMove を使わずにドラッグ＆ドロップを実装
class DraggableTableWidget(QTableWidget):
    def dropEvent(self, event):
        # ドロップ先の行を取得。-1の場合は末尾に挿入
        drop_row = self.indexAt(event.pos()).row()
        if drop_row == -1:
            drop_row = self.rowCount()
        # 現在選択している行を移動対象とする
        row_to_move = self.currentRow()
        if row_to_move < 0:
            return super().dropEvent(event)
        # ドロップ先が同じ行、または直下の場合は何もしない
        if row_to_move == drop_row or row_to_move + 1 == drop_row:
            return
        # 移動対象行の内容を保存
        rowData = []
        for col in range(self.columnCount()):
            item = self.item(row_to_move, col)
            rowData.append(item.text() if item else "")
        # 移動対象行を削除して再挿入
        self.removeRow(row_to_move)
        if row_to_move < drop_row:
            drop_row -= 1
        self.insertRow(drop_row)
        for col in range(self.columnCount()):
            self.setItem(drop_row, col, QTableWidgetItem(rowData[col]))
        event.accept()

# DashboardWidget の正しい定義例
class DashboardWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.series = QPieSeries()
        self.chart = QChart()
        self.chart.addSeries(self.series)
        self.chart.setTitle("ジャンル別内訳")
        self.chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)
        self.chart_view = QChartView(self.chart)
        layout = QVBoxLayout(self)
        layout.addWidget(self.chart_view)

    def update_chart(self, category_totals):
        self.series.clear()
        colors = {
            "食費": "#FFC0CB",
            "交通費": "#ADD8E6",
            "娯楽費": "#FFB6C1",
            "その他": "#FFDAB9",
            "残金": "#90EE90",
            "なし": "#D3D3D3",
            "収入": "#FFD700"
        }
        if not category_totals:
            category_totals = {"なし": 1}
        for cat, value in category_totals.items():
            pie_slice = self.series.append(cat, value)
            pie_slice.setColor(colors.get(cat, "#FFE4E1"))
        self.chart_view.repaint()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("家計簿アプリ")
        self.resize(600, 500)
        self.initUI()

    def initUI(self):
        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        # QHBoxLayout に変更して、左側に入力エリア、右側にダッシュボードを配置
        main_layout = QHBoxLayout(centralWidget)
        
        # 入力エリアのウィジェット作成（従来の input_tab の内容）
        input_widget = QWidget()
        input_layout = QVBoxLayout(input_widget)
        # ...入力フォーム部分の設定（既存のform_layout および関連ウィジェット）...
        form_layout = QHBoxLayout()
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("🌟 項目名")
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("💰 金額")
        self.category_combo = QComboBox()
        self.category_combo.addItems(["未分類", "食費", "交通費", "娯楽費", "その他"])  # 追加
        income_button = QPushButton("収入")
        income_button.clicked.connect(self.addIncome)
        expense_button = QPushButton("支出")
        expense_button.clicked.connect(self.addExpense)
        form_layout.addWidget(self.description_input)
        form_layout.addWidget(self.amount_input)
        form_layout.addWidget(self.category_combo)  # 追加
        form_layout.addWidget(income_button)
        form_layout.addWidget(expense_button)
        input_layout.addLayout(form_layout)
        # テーブル部分
        self.table = DraggableTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["項目名", "金額", "ジャンル"])  # 更新
        self.table.setItemDelegateForColumn(2, GenreDelegate())
        # ドラッグ＆ドロップ用の設定（InternalMove 設定は削除済み）
        self.table.setDragEnabled(True)
        self.table.setAcceptDrops(True)
        self.table.setDropIndicatorShown(True)
        self.table.customContextMenuRequested.connect(self.tableContextMenu)
        self.table.itemChanged.connect(self.updateTotal)
        input_layout.addWidget(self.table)
        # 合計表示とリセットボタンの設定
        summary_layout = QHBoxLayout()
        self.total_label = QLabel("合計: 0 円")
        self.total_label.setStyleSheet("color: #FF1493; font-size: 18px;")
        reset_button = QPushButton("リセット")
        reset_button.clicked.connect(self.resetTable)
        summary_layout.addWidget(self.total_label)
        summary_layout.addStretch()
        summary_layout.addWidget(reset_button)
        input_layout.addLayout(summary_layout)
        
        # DashboardWidget のインスタンス作成（self.dashboard_tab として保持）
        self.dashboard_tab = DashboardWidget(self)
        
        # 左右にウィジェットを追加
        main_layout.addWidget(input_widget)
        main_layout.addWidget(self.dashboard_tab)

    def tableContextMenu(self, pos):
        # 対象セルの位置取得
        index = self.table.indexAt(pos)
        if not index.isValid():
            return
        row = index.row()
        menu = QMenu(self.table)
        deleteAction = menu.addAction("この行を削除")
        action = menu.exec(self.table.viewport().mapToGlobal(pos))
        if action == deleteAction:
            self.table.removeRow(row)
            self.updateTotal()

    def moveRowUp(self, row):
        if row <= 0:
            return
        for col in range(self.table.columnCount()):
            item_current = self.table.takeItem(row, col)
            item_above = self.table.takeItem(row - 1, col)
            self.table.setItem(row - 1, col, item_current)
            self.table.setItem(row, col, item_above)
        self.updateTotal()

    def moveRowDown(self, row):
        if row >= self.table.rowCount() - 1:
            return
        for col in range(self.table.columnCount()):
            item_current = self.table.takeItem(row, col)
            item_below = self.table.takeItem(row + 1, col)
            self.table.setItem(row + 1, col, item_current)
            self.table.setItem(row, col, item_below)
        self.updateTotal()

    def addIncome(self):
        description = self.description_input.text()
        amount_text = self.amount_input.text()
        category = self.category_combo.currentText()  # 追加
        if not description or not amount_text:
            QMessageBox.warning(self, "入力エラー", "項目名と金額を入力してください。")
            return
        try:
            amount = float(amount_text)
        except ValueError:
            QMessageBox.warning(self, "入力エラー", "金額は数値で入力してください。")
            return
        self._addEntry(description, amount, category)

    def addExpense(self):
        description = self.description_input.text()
        amount_text = self.amount_input.text()
        category = self.category_combo.currentText()  # 追加
        if not description or not amount_text:
            QMessageBox.warning(self, "入力エラー", "項目名と金額を入力してください。")
            return
        try:
            amount = float(amount_text)
        except ValueError:
            QMessageBox.warning(self, "入力エラー", "金額は数値で入力してください。")
            return
        amount = -abs(amount)  # 支出はマイナス
        self._addEntry(description, amount, category)

    def _addEntry(self, description, amount, category):
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)
        self.table.setItem(row_position, 0, QTableWidgetItem(description))
        self.table.setItem(row_position, 1, QTableWidgetItem(str(amount)))
        # 収入の場合、ジャンルは「収入」にする
        if amount > 0:
            self.table.setItem(row_position, 2, QTableWidgetItem("収入"))
        else:
            self.table.setItem(row_position, 2, QTableWidgetItem(category))
        self.description_input.clear()
        self.amount_input.clear()
        self.updateTotal()

    def updateTotal(self):
        # 各行の金額セルをジャンルに応じて修正（収入は強制プラス、その他は強制マイナス）
        for row in range(self.table.rowCount()):
            item_amount = self.table.item(row, 1)
            item_genre = self.table.item(row, 2)
            if item_amount is None or item_genre is None:
                continue
            try:
                current = float(item_amount.text())
            except ValueError:
                continue
            new_val = abs(current) if item_genre.text() == "収入" else -abs(current)
            if new_val != current:
                self.table.blockSignals(True)
                item_amount.setText(str(new_val))
                self.table.blockSignals(False)
        # 以下、合計計算処理（そのまま）
        income_total = 0
        expense_by_category = {}
        for row in range(self.table.rowCount()):
            item_amount = self.table.item(row, 1)
            item_cat = self.table.item(row, 2)
            if item_amount is None or item_cat is None:
                continue
            try:
                amount = float(item_amount.text())
                cat = item_cat.text()
            except ValueError:
                continue
            if amount > 0:
                income_total += amount
            else:
                expense_by_category[cat] = expense_by_category.get(cat, 0) + abs(amount)
        total_expense = sum(expense_by_category.values())
        residual = income_total - total_expense

        self.total_label.setText(f"残金: {residual} 円")
        if income_total > 0:
            chart_data = expense_by_category.copy()
            chart_data["残金"] = max(residual, 0)
        else:
            chart_data = {"なし": 1}
        # QTimer.singleShot を使って非同期でチャートを更新
        QTimer.singleShot(0, lambda: self.dashboard_tab.update_chart(chart_data))

    def resetTable(self):
        self.table.setRowCount(0)
        self.updateTotal()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    app.setStyle("Fusion")
    # さらにかわいいUIにするためのスタイルシート更新
    app.setStyleSheet("""
        QMainWindow {
            background-color: #FFF0F5;
            font-size: 16px;
            font-family: "Comic Sans MS", cursive;
        }
        QPushButton {
            background-color: #FFB6C1;
            border: none;
            border-radius: 20px;
            padding: 10px;
            font-weight: bold;
            font-size: 18px;
        }
        QPushButton:hover {
            background-color: #FF69B4;
        }
        QLineEdit, QComboBox {
            background-color: #FFF8F0;
            border: 2px solid #FFC0CB;
            border-radius: 15px;
            padding: 8px;
            font-size: 16px;
        }
        QTableWidget {
            background-color: #FFF0F5;
            border: 2px solid #FFB6C1;
            border-radius: 10px;
            font-size: 16px;
        }
        QHeaderView::section {
            background-color: #FFB6C1;
            border: none;
            border-radius: 8px;
            padding: 4px;
            font-size: 16px;
            font-family: "Comic Sans MS", cursive;
        }
    """)
    window.show()
    sys.exit(app.exec())
