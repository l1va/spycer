import vtk
from PyQt5 import QtCore
from PyQt5.QtWidgets import (QMainWindow, QWidget, QLabel, QLineEdit, QComboBox, QGridLayout, QSlider,
                             QCheckBox, QVBoxLayout,
                             QPushButton, QFileDialog, QScrollArea, QGroupBox, QAction)
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

from src import locales, gui_utils
from src.gui_utils import plane_tf
from src.settings import sett, get_color

NothingState = "nothing"
GCodeState = "gcode"
StlState = "stl"
BothState = "both"


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Spycer')
        # self.statusBar().showMessage('Ready')

        self.locale = locales.getLocale()

        # Menu
        bar = self.menuBar()
        file_menu = bar.addMenu('File')
        self.open_action = QAction('Open', self)
        # close_action = QAction('Close', self)
        file_menu.addAction(self.open_action)
        # file_menu.addAction(close_action)
        settings_menu = bar.addMenu('Settings')
        self.save_sett_action = QAction('Save', self)
        settings_menu.addAction(self.save_sett_action)

        # main parts
        central_widget = QWidget()
        main_grid = QGridLayout()
        main_grid.addWidget(self.init3d_widget(), 0, 0, 20, 5)
        main_grid.addWidget(self.init_right_panel(), 0, 5, 20, 2)
        main_grid.addWidget(self.init_bottom_panel(), 20, 0, 2, 7)
        central_widget.setLayout(main_grid)
        self.setCentralWidget(central_widget)

        self.state_nothing()

        # ###################TODO:

        # self.openedStl = "/home/l1va/Downloads/1_odn2.stl"  # TODO: removeme
        # self.loadSTL(self.openedStl)
        # self.colorizeModel()

        # close_action.triggered.connect(self.close)

        ####################

    def init3d_widget(self):
        widget3d = QVTKRenderWindowInteractor()
        widget3d.Initialize()
        widget3d.Start()
        self.render = vtk.vtkRenderer()
        self.render.SetBackground(get_color(sett().colors.background))
        widget3d.GetRenderWindow().AddRenderer(self.render)
        self.interactor = widget3d.GetRenderWindow().GetInteractor()
        self.interactor.GetInteractorStyle().SetCurrentStyleToTrackballCamera()
        self.axesWidget = gui_utils.createAxes(self.interactor)

        self.planeActor = gui_utils.createPlaneActorCircle()
        self.planeTransform = vtk.vtkTransform()
        self.render.AddActor(self.planeActor)
        self.boxActors = gui_utils.createBoxActors()
        for b in self.boxActors:
            self.render.AddActor(b)

        self.splanes_actors = []

        self.render.ResetCamera()
        self.render.SetUseDepthPeeling(True)
        return widget3d

    def init_right_panel(self):
        right_panel = QGridLayout()
        right_panel.setSpacing(5)
        # right_panel.setColumnStretch(0, 2)

        # Front-end development at its best
        self.cur_row = 1

        def get_next_row():
            self.cur_row += 1
            return self.cur_row

        def get_cur_row():
            return self.cur_row

        layer_height_label = QLabel(self.locale.LayerHeight)
        self.layer_height_value = QLineEdit(str(sett().slicing.layer_height))
        right_panel.addWidget(layer_height_label, get_next_row(), 1)
        right_panel.addWidget(self.layer_height_value, get_cur_row(), 2)

        print_speed_label = QLabel(self.locale.PrintSpeed)
        self.print_speed_value = QLineEdit(str(sett().slicing.print_speed))
        right_panel.addWidget(print_speed_label, get_next_row(), 1)
        right_panel.addWidget(self.print_speed_value, get_cur_row(), 2)

        print_speed_layer1_label = QLabel(self.locale.PrintSpeedLayer1)
        self.print_speed_layer1_value = QLineEdit(str(sett().slicing.print_speed_layer1))
        right_panel.addWidget(print_speed_layer1_label, get_next_row(), 1)
        right_panel.addWidget(self.print_speed_layer1_value, get_cur_row(), 2)

        print_speed_wall_label = QLabel(self.locale.PrintSpeedWall)
        self.print_speed_wall_value = QLineEdit(str(sett().slicing.print_speed_wall))
        right_panel.addWidget(print_speed_wall_label, get_next_row(), 1)
        right_panel.addWidget(self.print_speed_wall_value, get_cur_row(), 2)

        extruder_temp_label = QLabel(self.locale.ExtruderTemp)
        self.extruder_temp_value = QLineEdit(str(sett().slicing.extruder_temperature))
        right_panel.addWidget(extruder_temp_label, get_next_row(), 1)
        right_panel.addWidget(self.extruder_temp_value, get_cur_row(), 2)

        bed_temp_label = QLabel(self.locale.BedTemp)
        self.bed_temp_value = QLineEdit(str(sett().slicing.bed_temperature))
        right_panel.addWidget(bed_temp_label, get_next_row(), 1)
        right_panel.addWidget(self.bed_temp_value, get_cur_row(), 2)

        fill_density_label = QLabel(self.locale.FillDensity)
        self.fill_density_value = QLineEdit(str(sett().slicing.fill_density))
        right_panel.addWidget(fill_density_label, get_next_row(), 1)
        right_panel.addWidget(self.fill_density_value, get_cur_row(), 2)

        wall_thickness_label = QLabel(self.locale.WallThickness)
        self.wall_thickness_value = QLineEdit(str(sett().slicing.wall_thickness))
        right_panel.addWidget(wall_thickness_label, get_next_row(), 1)
        right_panel.addWidget(self.wall_thickness_value, get_cur_row(), 2)

        line_width_label = QLabel(self.locale.LineWidth)
        self.line_width_value = QLineEdit(str(sett().slicing.line_width))
        right_panel.addWidget(line_width_label, get_next_row(), 1)
        right_panel.addWidget(self.line_width_value, get_cur_row(), 2)

        filling_type_label = QLabel(self.locale.FillingType)
        right_panel.addWidget(filling_type_label, get_next_row(), 1)
        # todo fix displaying shifting (feature is below - line_width_value again to cut view of dropbox)
        right_panel.addWidget(QLineEdit("0"), get_cur_row(), 2)
        filling_type_values_widget = QWidget()
        self.filling_type_values = QComboBox(filling_type_values_widget)
        self.filling_type_values.addItems(self.locale.FillingTypeValues)
        ind = locales.getLocaleByLang("en").FillingTypeValues.index(sett().slicing.filling_type)
        self.filling_type_values.setCurrentIndex(ind)
        right_panel.addWidget(filling_type_values_widget, get_cur_row(), 2)

        retraction_on_label = QLabel(self.locale.Retraction)
        self.retraction_on_box = QCheckBox()
        if sett().slicing.retraction_on:
            self.retraction_on_box.setCheckState(QtCore.Qt.Checked)
        right_panel.addWidget(retraction_on_label, get_next_row(), 1)
        right_panel.addWidget(self.retraction_on_box, get_cur_row(), 2)

        retraction_distance_label = QLabel(self.locale.RetractionDistance)
        self.retraction_distance_value = QLineEdit(str(sett().slicing.retraction_distance))
        right_panel.addWidget(retraction_distance_label, get_next_row(), 1)
        right_panel.addWidget(self.retraction_distance_value, get_cur_row(), 2)

        retraction_speed_label = QLabel(self.locale.RetractionSpeed)
        self.retraction_speed_value = QLineEdit(str(sett().slicing.retraction_speed))
        right_panel.addWidget(retraction_speed_label, get_next_row(), 1)
        right_panel.addWidget(self.retraction_speed_value, get_cur_row(), 2)

        support_offset_label = QLabel(self.locale.SupportOffset)
        self.support_offset_value = QLineEdit(str(sett().slicing.support_offset))
        right_panel.addWidget(support_offset_label, get_next_row(), 1)
        right_panel.addWidget(self.support_offset_value, get_cur_row(), 2)

        skirt_line_count_label = QLabel(self.locale.SkirtLineCount)
        self.skirt_line_count_value = QLineEdit(str(sett().slicing.skirt_line_count))
        right_panel.addWidget(skirt_line_count_label, get_next_row(), 1)
        right_panel.addWidget(self.skirt_line_count_value, get_cur_row(), 2)

        fan_off_layer1_label = QLabel(self.locale.FanOffLayer1)
        self.fan_off_layer1_box = QCheckBox()
        if sett().slicing.fan_off_layer1:
            self.fan_off_layer1_box.setCheckState(QtCore.Qt.Checked)
        right_panel.addWidget(fan_off_layer1_label, get_next_row(), 1)
        right_panel.addWidget(self.fan_off_layer1_box, get_cur_row(), 2)

        supports_on_label = QLabel(self.locale.SupportsOn)
        self.supports_on_box = QCheckBox()
        if sett().slicing.supports_on:
            self.supports_on_box.setCheckState(QtCore.Qt.Checked)
        right_panel.addWidget(supports_on_label, get_next_row(), 1)
        right_panel.addWidget(self.supports_on_box, get_cur_row(), 2)

        # BUTTONS
        buttons_layout = QGridLayout()
        buttons_layout.setSpacing(5)
        # buttons_layout.setColumnStretch(0, 2)

        self.model_switch_box = QCheckBox(self.locale.ShowStl)
        buttons_layout.addWidget(self.model_switch_box, get_next_row(), 1)

        self.slider_label = QLabel(self.locale.LayersCount)
        self.layers_number_label = QLabel()
        buttons_layout.addWidget(self.slider_label, get_next_row(), 1)
        buttons_layout.addWidget(self.layers_number_label, get_cur_row(), 2)

        self.picture_slider = QSlider()
        self.picture_slider.setOrientation(QtCore.Qt.Horizontal)
        self.picture_slider.setMinimum(1)
        self.picture_slider.setValue(1)
        buttons_layout.addWidget(self.picture_slider, get_next_row(), 1, 1, 2)

        self.x_position_value = QLineEdit("0")
        buttons_layout.addWidget(self.x_position_value, get_next_row(), 1)
        self.y_position_value = QLineEdit("0")
        buttons_layout.addWidget(self.y_position_value, get_cur_row(), 2)
        self.z_position_value = QLineEdit("0")
        buttons_layout.addWidget(self.z_position_value, get_next_row(), 1)
        self.move_button = QPushButton(self.locale.MoveModel)
        buttons_layout.addWidget(self.move_button, get_cur_row(), 2, 1, 1)

        self.load_model_button = QPushButton(self.locale.OpenModel)
        buttons_layout.addWidget(self.load_model_button, get_next_row(), 1, 1, 1)

        self.edit_planes_button = QPushButton(self.locale.EditPlanes)
        buttons_layout.addWidget(self.edit_planes_button, get_cur_row(), 2, 1, 1)

        self.slice3a_button = QPushButton(self.locale.Slice3Axes)
        buttons_layout.addWidget(self.slice3a_button, get_next_row(), 1, 1, 1)

        self.slice_vip_button = QPushButton(self.locale.SliceVip)
        buttons_layout.addWidget(self.slice_vip_button, get_cur_row(), 2, 1, 1)

        self.save_gcode_button = QPushButton(self.locale.SaveGCode)
        buttons_layout.addWidget(self.save_gcode_button, get_next_row(), 1, 1, 1)

        self.analyze_model_button = QPushButton(self.locale.Analyze)
        buttons_layout.addWidget(self.analyze_model_button, get_cur_row(), 2, 1, 1)

        self.colorize_angle_value = QLineEdit(str(sett().slicing.angle))
        buttons_layout.addWidget(self.colorize_angle_value, get_next_row(), 1)

        self.color_model_button = QPushButton(self.locale.ColorModel)
        buttons_layout.addWidget(self.color_model_button, get_cur_row(), 2, 1, 1)

        panel_widget = QWidget()
        panel_widget.setLayout(right_panel)

        scroll = QScrollArea()
        scroll.setWidget(panel_widget)
        scroll.setWidgetResizable(True)
        # scroll.setFixedHeight(400)

        v_layout = QVBoxLayout()
        v_layout.addWidget(scroll)
        settings_group = QGroupBox('Settings')  # TODO: locale
        settings_group.setLayout(v_layout)

        buttons_group = QWidget()
        buttons_group.setLayout(buttons_layout)

        high_layout = QVBoxLayout()
        high_layout.addWidget(settings_group)
        high_layout.addWidget(buttons_group)
        high_widget = QWidget()
        high_widget.setLayout(high_layout)

        return high_widget

    def init_bottom_panel(self):
        bottom_layout = QGridLayout()
        bottom_layout.setSpacing(5)
        bottom_layout.setColumnStretch(7, 1)

        self.add_plane_button = QPushButton(self.locale.AddPlane)
        bottom_layout.addWidget(self.add_plane_button, 1, 0)

        combo_widget = QWidget()
        self.combo_box = QComboBox(combo_widget)
        bottom_layout.addWidget(combo_widget, 0, 0, 1, 2)

        self.remove_plane_button = QPushButton(self.locale.DeletePlane)
        bottom_layout.addWidget(self.remove_plane_button, 2, 0)

        self.tilted_checkbox = QCheckBox(self.locale.Tilted)
        bottom_layout.addWidget(self.tilted_checkbox, 0, 3)

        x_label = QLabel("X:")
        bottom_layout.addWidget(x_label, 0, 4)
        self.x_value = QLineEdit("3.0951")
        bottom_layout.addWidget(self.x_value, 0, 5)

        y_label = QLabel("Y:")
        bottom_layout.addWidget(y_label, 1, 4)
        self.y_value = QLineEdit("5.5910")
        bottom_layout.addWidget(self.y_value, 1, 5)

        z_label = QLabel("Z:")
        bottom_layout.addWidget(z_label, 2, 4)
        self.z_value = QLineEdit("89.5414")
        bottom_layout.addWidget(self.z_value, 2, 5)

        rotated_label = QLabel(self.locale.Rotated)
        bottom_layout.addWidget(rotated_label, 3, 4)
        self.rotated_value = QLineEdit("31.0245")
        bottom_layout.addWidget(self.rotated_value, 3, 5)

        self.xSlider = QSlider()
        self.xSlider.setOrientation(QtCore.Qt.Horizontal)
        self.xSlider.setMinimum(-100)
        self.xSlider.setMaximum(100)
        self.xSlider.setValue(1)
        bottom_layout.addWidget(self.xSlider, 0, 6, 1, 2)
        self.ySlider = QSlider()
        self.ySlider.setOrientation(QtCore.Qt.Horizontal)
        self.ySlider.setMinimum(-100)
        self.ySlider.setMaximum(100)
        self.ySlider.setValue(1)
        bottom_layout.addWidget(self.ySlider, 1, 6, 1, 2)
        self.zSlider = QSlider()
        self.zSlider.setOrientation(QtCore.Qt.Horizontal)
        self.zSlider.setMinimum(0)
        self.zSlider.setMaximum(200)
        self.zSlider.setValue(1)
        bottom_layout.addWidget(self.zSlider, 2, 6, 1, 2)
        self.rotSlider = QSlider()
        self.rotSlider.setOrientation(QtCore.Qt.Horizontal)
        self.rotSlider.setMinimum(-180)
        self.rotSlider.setMaximum(180)
        self.rotSlider.setValue(0)
        bottom_layout.addWidget(self.rotSlider, 3, 6, 1, 2)

        bottom_panel = QWidget()
        bottom_panel.setLayout(bottom_layout)
        bottom_panel.setEnabled(False)
        self.bottom_panel = bottom_panel
        return bottom_panel

    def show_stl_hide_gcode(self):
        for actor in self.actors:
            actor.VisibilityOff()
        self.stlActor.VisibilityOn()

    def show_gcode_hide_stl(self):
        for layer in range(self.picture_slider.value()):
            self.actors[layer].VisibilityOn()
        self.stlActor.VisibilityOff()

    def clear_scene(self):
        self.render.RemoveAllViewProps()
        self.render.AddActor(self.planeActor)
        for b in self.boxActors:
            self.render.AddActor(b)

    def reload_scene(self):
        self.render.Modified()
        self.interactor.Render()

    def change_layer_view(self, prev_value, gcd):
        new_slider_value = self.picture_slider.value()

        self.actors[new_slider_value - 1].GetProperty().SetColor(get_color(sett().colors.last_layer))
        self.actors[new_slider_value - 1].GetProperty().SetLineWidth(4)
        self.actors[prev_value - 1].GetProperty().SetColor(get_color(sett().colors.layer))
        self.actors[prev_value - 1].GetProperty().SetLineWidth(1)

        self.layers_number_label.setText(str(new_slider_value))

        if new_slider_value < prev_value:
            for layer in range(new_slider_value, prev_value):
                self.actors[layer].VisibilityOff()
        else:
            for layer in range(prev_value, new_slider_value):
                self.actors[layer].VisibilityOn()

        if gcd.lays2rots[new_slider_value - 1] != gcd.lays2rots[prev_value - 1]:
            curr_rotation = gcd.rotations[gcd.lays2rots[new_slider_value - 1]]
            for block in range(new_slider_value):
                # revert prev rotation firstly and then apply current
                tf = gui_utils.prepareTransform(gcd.rotations[gcd.lays2rots[block]], curr_rotation)
                self.actors[block].SetUserTransform(tf)

            self.rotate_plane(plane_tf(curr_rotation))
            # for i in range(len(self.planes)):
            #     self.rotateAnyPlane(self.planesActors[i], self.planes[i], currRotation)
        self.reload_scene()
        return new_slider_value

    def move_stl(self, tf):
        self.stlActor.SetUserTransform(tf)
        self.reload_scene()

    def open_dialog(self):
        return QFileDialog.getOpenFileName(None, self.locale.OpenModel, "/home/l1va/Downloads/5axes_3d_printer/test",
                                           "STL (*.stl *.STL);;Gcode (*.gcode)")[0]  # TODO: fix path

    def load_stl(self, stl_actor, stl_translation):
        self.clear_scene()
        self.stlActor = stl_actor

        self.x_position_value.setText(str(stl_translation[0])[:10])
        self.y_position_value.setText(str(stl_translation[1])[:10])
        self.z_position_value.setText(str(stl_translation[2])[:10])

        self.render.AddActor(self.stlActor)
        self.state_stl()
        self.render.ResetCamera()
        self.reload_scene()

    def reload_splanes(self, splanes):
        self._recreate_splanes(splanes)
        self.combo_box.clear()
        for i in range(len(splanes)):
            self.combo_box.addItem(self.locale.Plane + " " + str(i + 1))

    def _recreate_splanes(self, splanes):
        for p in self.splanes_actors:
            self.render.RemoveActor(p)
        self.splanes_actors = []
        for p in splanes:
            act = gui_utils.create_splane_actor([p.x, p.y, p.z], -60 if p.tilted else 0, p.rot)
            self.splanes_actors.append(act)
            self.render.AddActor(act)
        self.reload_scene()

    def update_splane(self, sp, ind):
        self.render.RemoveActor(self.splanes_actors[ind])
        act = gui_utils.create_splane_actor([sp.x, sp.y, sp.z], -60 if sp.tilted else 0, sp.rot)
        self.splanes_actors[ind] = act
        self.render.AddActor(act)
        sel = self.combo_box.currentIndex()
        if sel == ind:
            self.splanes_actors[sel].GetProperty().SetColor(get_color(sett().colors.last_layer))
        self.reload_scene()

    def change_combo_select(self, plane, ind):
        self.tilted_checkbox.setChecked(plane.tilted)
        self.rotated_value.setText(str(plane.rot))
        self.x_value.setText(str(plane.x))
        self.y_value.setText(str(plane.y))
        self.z_value.setText(str(plane.z))
        self.xSlider.setValue(plane.x)
        self.ySlider.setValue(plane.y)
        self.zSlider.setValue(plane.z)
        self.rotSlider.setValue(plane.rot)
        for p in self.splanes_actors:
            p.GetProperty().SetColor(get_color(sett().colors.splane))
        self.splanes_actors[ind].GetProperty().SetColor(get_color(sett().colors.last_layer))
        self.reload_scene()

    def load_gcode(self, actors, is_from_stl, plane_tf):
        self.clear_scene()
        if is_from_stl:
            self.stlActor.VisibilityOff()
            self.render.AddActor(self.stlActor)

        self.rotate_plane(plane_tf)

        self.actors = actors
        for actor in self.actors:
            self.render.AddActor(actor)

        if is_from_stl:
            self.state_both(len(self.actors))
        else:
            self.state_gcode(len(self.actors))

        self.render.ResetCamera()
        self.reload_scene()

    def rotate_plane(self, tf):
        self.planeActor.SetUserTransform(tf)
        self.planeTransform = tf

    def save_gcode_dialog(self):
        return QFileDialog.getSaveFileName(None, self.locale.SaveGCode, "", "Gcode (*.gcode)")[0]

    def state_nothing(self):
        self.model_switch_box.setEnabled(False)
        self.model_switch_box.setChecked(False)
        self.slider_label.setEnabled(False)
        self.layers_number_label.setEnabled(False)
        self.layers_number_label.setText(" ")
        self.picture_slider.setEnabled(False)
        self.picture_slider.setSliderPosition(0)
        self.move_button.setEnabled(False)
        self.slice3a_button.setEnabled(False)
        self.color_model_button.setEnabled(False)
        self.analyze_model_button.setEnabled(False)
        self.edit_planes_button.setEnabled(False)
        self.slice_vip_button.setEnabled(False)
        self.save_gcode_button.setEnabled(False)
        self.bottom_panel.setEnabled(False)
        self.state = NothingState

    def state_gcode(self, layers_count):
        self.model_switch_box.setEnabled(False)
        self.model_switch_box.setChecked(False)
        self.slider_label.setEnabled(True)
        self.layers_number_label.setEnabled(True)
        self.layers_number_label.setText(str(layers_count))
        self.picture_slider.setEnabled(True)
        self.picture_slider.setMaximum(layers_count)
        self.picture_slider.setSliderPosition(layers_count)
        self.move_button.setEnabled(False)
        self.slice3a_button.setEnabled(False)
        self.color_model_button.setEnabled(False)
        self.analyze_model_button.setEnabled(False)
        self.edit_planes_button.setEnabled(True)
        self.slice_vip_button.setEnabled(False)
        self.save_gcode_button.setEnabled(True)
        self.bottom_panel.setEnabled(False)
        self.state = GCodeState

    def state_stl(self):
        self.model_switch_box.setEnabled(False)
        self.model_switch_box.setChecked(False)
        self.slider_label.setEnabled(False)
        self.layers_number_label.setEnabled(False)
        self.layers_number_label.setText(" ")
        self.picture_slider.setEnabled(False)
        self.picture_slider.setSliderPosition(0)
        self.move_button.setEnabled(True)
        self.slice3a_button.setEnabled(True)
        self.color_model_button.setEnabled(True)
        self.analyze_model_button.setEnabled(True)
        self.edit_planes_button.setEnabled(False)
        self.slice_vip_button.setEnabled(True)
        self.save_gcode_button.setEnabled(False)
        self.bottom_panel.setEnabled(True)
        self.state = StlState

    def state_both(self, layers_count):
        self.model_switch_box.setEnabled(True)
        self.model_switch_box.setChecked(False)
        self.slider_label.setEnabled(True)
        self.layers_number_label.setEnabled(True)
        self.layers_number_label.setText(str(layers_count))
        self.picture_slider.setEnabled(True)
        self.picture_slider.setMaximum(layers_count)
        self.picture_slider.setSliderPosition(layers_count)
        self.move_button.setEnabled(True)
        self.slice3a_button.setEnabled(True)
        self.color_model_button.setEnabled(True)
        self.analyze_model_button.setEnabled(True)
        self.edit_planes_button.setEnabled(True)
        self.slice_vip_button.setEnabled(True)
        self.save_gcode_button.setEnabled(True)
        self.bottom_panel.setEnabled(True)
        self.state = BothState
