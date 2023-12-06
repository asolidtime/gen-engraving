import PySide6.QtGui
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QButtonGroup,
    QRadioButton,
)
from PySide6.QtCore import QEventLoop, QTimer, QThread, Signal, Qt
from time import sleep, time
from printer_io import PrinterIO
import asyncio
from os import path, system
from generate_cell_gcode import generate_cell_gcode

pio = PrinterIO()

cell_dict = {}

gcode_filename = f"automatic-engraver-gui-{round(time())}.gcode"


def get_new_identifier(cell_id):
    # stub function
    # eventually, use the API or direct SQL access to get this
    sleep(0.5)
    identifier = "m8_F"
    cell_dict[cell_id] = identifier

    return identifier


class Worker(QThread):
    signal = Signal(str)

    def __init__(self, cell_index):
        super().__init__()
        self.cell_index = cell_index

    def run(self):
        result = (
            f"Cell {self.cell_index}\nEngraved\n{get_new_identifier(self.cell_index)}"
        )
        self.signal.emit(result)


class MainWindow(QMainWindow):
    def on_button_clicked(self, cell_index, button):
        if "fetching" not in button.text():
            if "Not Engraved" in button.text():
                worker = Worker(cell_index)
                worker.signal.connect(button.setText)
                button.setText(f"Cell {cell_index}\nEngraved\n(fetching)")
                self.workers.append(worker)
                worker.start()
            else:
                button.setText(f"Cell {cell_index}\nNot Engraved\n--")
                cell_dict[cell_index] = "notengraved"
                # TODO: update database to remove unused id 

    def on_radio_button_clicked(self, button):
        self.calibration_step = float(button.text())
        print(self.calibration_step)

    def move_up(self):
        self.printer_y += self.calibration_step
        pio.set_xy_position(self.printer_x, self.printer_y)
        self.update_coords_label()

    def move_down(self):
        self.printer_y -= self.calibration_step
        pio.set_xy_position(self.printer_x, self.printer_y)
        self.update_coords_label()

    def move_left(self):
        self.printer_x -= self.calibration_step
        pio.set_xy_position(self.printer_x, self.printer_y)
        self.update_coords_label()

    def move_right(self):
        self.printer_x += self.calibration_step
        pio.set_xy_position(self.printer_x, self.printer_y)
        self.update_coords_label()

    def update_coords_label(self):
        self.coords_label.setText(f"X: {self.printer_x:.2f}, Y: {self.printer_y:.2f}")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_W:
            self.move_up()
        elif event.key() == Qt.Key_S:
            self.move_down()
        elif event.key() == Qt.Key_A:
            self.move_left()
        elif event.key() == Qt.Key_D:
            self.move_right()
        else:
            super().keyPressEvent(event)
            
    def generate_barcodes(self):
        for key, val in cell_dict.items():
            if val != "notengraved":
                if not path.isfile(f"./barcode_cache/{val}.png"):
                    system(f"./generate_barcode_from_identifier.sh {val}")

    def generate_gcode_for_cells(self):
        self.generate_barcodes()
        gcode_initialized = False
        for idx, code in cell_dict.items():
            if code != "notengraved":
                generate_cell_gcode(should_initialize_gcode=(not gcode_initialized), input_filename=f"barcode_cache/{code}.png", gcode_out_filename=gcode_filename, cell_index=idx, calibration_spot_x=self.printer_x, calibration_spot_y=self.printer_y)
                gcode_initialized = True
    def generate_and_start_engraving(self):
        self.generate_gcode_for_cells()
        system(f"./copy_gcode.sh {gcode_filename}")
        pio.print_gcode(gcode_filename)
        
    def __init__(self):
        super().__init__()
        self.workers = []
        self.calibration_step = 10

        self.printer_x, self.printer_y, self.printer_z = pio.get_xyz_position()

        self.setWindowTitle("My App")

        button_layout = QHBoxLayout()
        for i in range(6):
            button = QPushButton(f"Cell {i}\nNot Engraved\n--")
            button.setFixedHeight(300)
            cell_dict[i] = "notengraved"
            button.clicked.connect(
                lambda i=i, button=button: self.on_button_clicked(i, button)
            )
            button_layout.addWidget(button)

        label = QLabel("Label")
        button = QPushButton("Button")

        label_button_layout = QHBoxLayout()
        label_button_layout.addWidget(label)
        label_button_layout.addWidget(button)

        arrow_buttons_layout = QHBoxLayout()
        calibration_label = QLabel("Calibration: ")
        left_button = QPushButton("←")
        up_button = QPushButton("↑")
        down_button = QPushButton("↓")
        right_button = QPushButton("→")
        up_button.clicked.connect(self.move_up)
        down_button.clicked.connect(self.move_down)
        left_button.clicked.connect(self.move_left)
        right_button.clicked.connect(self.move_right)
        arrow_buttons_layout.addWidget(calibration_label)
        arrow_buttons_layout.addWidget(left_button)
        arrow_buttons_layout.addWidget(up_button)
        arrow_buttons_layout.addWidget(down_button)
        arrow_buttons_layout.addWidget(right_button)
        self.coords_label = QLabel()

        radio_button_group = QButtonGroup(self)
        for value in [0.01, 0.1, 1, 10, 25]:
            radio_button = QRadioButton(str(value))
            if value == 1:
                radio_button.setChecked(True)
            radio_button_group.addButton(radio_button)
            arrow_buttons_layout.addWidget(radio_button)
        radio_button_group.buttonClicked.connect(self.on_radio_button_clicked)
        arrow_buttons_layout.addWidget(self.coords_label)
        
        

        main_layout = QVBoxLayout()
        
        # Create the buttons
        stub_button = QPushButton("Stub")
        generate_gcode_button = QPushButton("Generate G-Code")
        generate_and_engrave_button = QPushButton("Generate and Start Engraving")
        
        # Connect the buttons to their respective functions
        generate_gcode_button.clicked.connect(self.generate_gcode_for_cells)
        generate_and_engrave_button.clicked.connect(self.generate_and_start_engraving)
        
        # Create a horizontal layout and add the buttons to it
        run_layout = QHBoxLayout()
        run_layout.addWidget(stub_button)
        run_layout.addWidget(generate_gcode_button)
        run_layout.addWidget(generate_and_engrave_button)
        
        # Add the button layout to the main layout
        
        main_layout.addLayout(button_layout)

        main_layout.addLayout(arrow_buttons_layout)
        main_layout.addLayout(label_button_layout)
        main_layout.addLayout(run_layout)

        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.update_coords_label()

        self.setCentralWidget(main_widget)


app = QApplication([])
window = MainWindow()
window.show()
app.exec_()

print(cell_dict)
window.generate_barcodes()