import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget,QLabel,
                             QHBoxLayout,QGridLayout,QPushButton,QSlider, QComboBox,QCheckBox,QGroupBox,QFileDialog,QProgressBar,QSpacerItem,QSizePolicy)
from PyQt5.QtCore import Qt,QRect,QThread, pyqtSignal, QObject,QCoreApplication
from PyQt5.QtGui import QPixmap,QImage,QColor, QPen,QPainter
from PIL import Image,ImageEnhance
import os
import numpy as np
import globals
from adjustable_label import AdjustableLabel

class ImageEqualizer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Equalizer")
        self.setGeometry(200,200,1500,1000)
        self.smallest_width = None
        self.smallest_height = None
        self.image_labels=[]  # Store all image labels for resizing
        self.combos=[]
        
        self.initUi()
       

    def initUi(self):
        main_window=QWidget()
        container=QGridLayout()
        main_window.setLayout(container)
        self.setCentralWidget(main_window)


        for i in range(4):
            groupBox=self.create_input_viewer(f"Image {i+1}",i)
            container.addWidget(groupBox,i//2,i%2)

        output_viewer=self.create_output_viewer()
        container.addWidget(output_viewer,2,0)
        

        mixer_controls=self.create_mixer_controls()
        container.addWidget(mixer_controls,2,1)
        container.setColumnStretch(0,1)
        container.setColumnStretch(1,1)

        self.update_modes()

        # Styling
        self.setStyleSheet("""
            QLabel{
                font-size:17px;
                color:white;     
                    }
            QPushButton{
                    font-size:15px;
                    padding:10px;
                    border:white 1px solid;
                    border-radius:15px;
                    background-color:white;
                    color:black;         
                        }
            QCheckBox{
                    font-size:20px;
                           }
            QComboBox{
                font-size:17px;           
                     }
        """)
        

    def create_input_viewer(self, title,index):
        # Group box for input viewer
        group_box = QGroupBox()
        ver_layout=QVBoxLayout()
        hor_layout1=QHBoxLayout()
        hor_layout2 = QHBoxLayout()

        title_label=QLabel(title)

        # Image viewer
        image_label = AdjustableLabel("Image Viewer")
        image_label.setStyleSheet("background-color: lightgray; border: 1px solid black;")
        image_label.setAlignment(Qt.AlignCenter)
        image_label.mouseDoubleClickEvent = lambda event: self.upload_image(image_label,index)

        self.image_labels.append(image_label)  # Add to the list for later resizing

        # FT Component Viewer
        ft_label = AdjustableLabel("FT Component Viewer")
        ft_label.setStyleSheet("background-color: black; border: 1px solid black;")
        ft_label.setAlignment(Qt.AlignCenter)

        globals.ft_labels.append(ft_label)

        # Dropdown for FT component selection
        ft_selector = QComboBox()
        ft_selector.addItems(["Magnitude", "Phase", "Real", "Imaginary"])
        ft_selector.currentIndexChanged.connect(
        lambda _, label=ft_label: label.plot_ft_component(ft_selector.currentText(), index)
        )
        ft_selector.currentIndexChanged.connect(self.apply_mixing)
        self.ft_selector=ft_selector

        self.combos.append(ft_selector)  # Track the dropdowns globally
        

        #component slider
        component_slider=QSlider()
        component_slider.setMaximumHeight(300)
        component_slider.setRange(0, 100)  # Slider range from 0% to 100%
        component_slider.setValue(0)  # Default weight is 25%
        component_slider.valueChanged.connect(lambda: self.update_slider_value(index, component_slider.value(),"first"))
        component_slider.sliderReleased.connect(self.apply_mixing)

        hor_layout1.addWidget(title_label)
        hor_layout1.addWidget(ft_selector)

        # Arrange components
        hor_layout2.addWidget(image_label)
        hor_layout2.addWidget(ft_label)
        hor_layout2.addWidget(component_slider)

        ver_layout.addLayout(hor_layout1)
        ver_layout.addLayout(hor_layout2)

        group_box.setLayout(ver_layout)
        return group_box


    def create_output_viewer(self):
        group_box = QGroupBox()

        labels_layout=QHBoxLayout()
        labels_layout.addWidget(QLabel("Output 1"))
        labels_layout.addWidget(QLabel("Output 2"))

        output_layout=QHBoxLayout()
        # Image viewer
        self.image_label1 = QLabel("Output 1")
        self.image_label1.setStyleSheet("background-color: lightgray; border: 1px solid black;")
        self.image_label1.setFixedHeight(300)  # Adjust size as needed
        self.image_label1.setAlignment(Qt.AlignCenter)
        self.image_label1.setObjectName("Output 1")  # Set object name for findChild
        self.output1_label = self.image_label1  # Save reference for later use
        

        # Image viewer
        self.image_label2 = QLabel("Output 2")
        self.image_label2.setStyleSheet("background-color: lightgray; border: 1px solid black;")
        self.image_label2.setFixedHeight(300)  # Adjust size as needed
        self.image_label2.setAlignment(Qt.AlignCenter)
        self.image_label2.setObjectName("Output 2")  # Set object name for findChild
        self.output2_label = self.image_label2  # Save reference for later use

        # # Progress bar for real-time mixing
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(700)
        self.progress_bar.setValue(0)  # Initialize at 0%
        self.progress_bar.setTextVisible(True)  # Ensure the percentage text is visible
        self.progress_bar.setAlignment(Qt.AlignCenter)  # Optional: Center-align the text

        output_layout.addWidget(self.image_label1)
        output_layout.addWidget(self.image_label2)

        ver_layout=QVBoxLayout()
        ver_layout.addLayout(labels_layout)
        ver_layout.addLayout(output_layout)
        ver_layout.addWidget(self.progress_bar)

        group_box.setLayout(ver_layout)

        return group_box
    
    def create_mixer_controls(self):
        group_box=QGroupBox()
        controls_layout=QVBoxLayout()

        outputs_menu=QComboBox()
        outputs_menu.addItems(["Output 1","Output 2"])
        self.outputs_menu = outputs_menu  # Save reference for later use

        self.mode_selector = QComboBox()
        self.mode_selector.addItems(["Mag/Phase", "Real/Imag"])  # Add the two modes
        self.mode_selector.setCurrentIndex(0)  # Default to "Mag/Phase"

        # Add the combo box to the layout
        both_modes = QVBoxLayout()
        both_modes.addWidget(QLabel("Mode:"))  # Optional label for clarity
        both_modes.addWidget(self.mode_selector)


        self.region_selector=QComboBox()
        self.region_selector.addItems(["Whole FT","Inner region","Outer region"])
        self.region_selector.setCurrentIndex(0)
        region_layout=QVBoxLayout()
        region_layout.addWidget(QLabel("Select region:"))
        region_layout.addWidget(self.region_selector)

        #Slider for region size
        self.region_size_slider = QSlider()
        self.region_size_slider.setMaximumHeight(300)
        self.region_size_slider.setRange(0, 100)  # Percentage range
        self.region_size_slider.setValue(50)  # Default 50%
        self.region_size_slider.sliderReleased.connect(self.apply_mixing)

        regions_slider_layout=QHBoxLayout()
        regions_slider_layout.addLayout(region_layout)
        regions_slider_layout.addWidget(self.region_size_slider)

        modes_regions_layout=QVBoxLayout()
        modes_regions_layout.addLayout(both_modes)
        modes_regions_layout.addLayout(regions_slider_layout)

       
        # check_boxes_layout.addWidget(self.region_size_slider)

    
        apply_button=QPushButton("Apply")
        apply_button.setMaximumWidth(120)
        apply_button.clicked.connect(self.apply_mixing)  # Connect to mixing function
        reset_button=QPushButton("Reset")
        reset_button.setMaximumWidth(120)
        reset_button.clicked.connect(self.reset)

        buttons_layout=QHBoxLayout()
        # buttons_layout.addWidget(apply_button)
        buttons_layout.addWidget(reset_button)


        controls_layout.addWidget(outputs_menu)
        controls_layout.addStretch(1)
        controls_layout.addLayout(modes_regions_layout)
        # controls_layout.addWidget(self.region_size_slider)
        controls_layout.addStretch(1)
        controls_layout.addLayout(buttons_layout)
        controls_layout.addStretch(1)

        group_box.setLayout(controls_layout)

        # Connect the combo box to the update function
        self.mode_selector.currentIndexChanged.connect(self.update_modes)

        self.region_selector.currentIndexChanged.connect(self.update_regions)
        self.region_size_slider.valueChanged.connect(self.update_regions)

        return group_box
        
    def upload_image(self, label, index):
        """Open a file dialog to upload an image, convert it to grayscale, and resize all labels."""
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Image File", "", "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)", options=options
        )
        if file_path:
            # Convert image to grayscale using Pillow
            image = Image.open(file_path).convert("L")
            width, height = image.size

            print(f"Uploaded image dimensions: {width}x{height}")  # Debugging print

            # Save temporarily in memory to convert to QPixmap
            temp_path = "temp_grayscale.png"
            image.save(temp_path)

            # Add the new image to the list of uploaded images
            if not hasattr(self, 'uploaded_images'):
                self.uploaded_images = [None] * 4  # Initialize a list to store uploaded images
            self.uploaded_images[index] = image

            # Update the smallest dimensions across all uploaded images
            self.update_smallest_dimensions()

            # Resize all uploaded images to the smallest dimensions
            for i, img in enumerate(self.uploaded_images):
                if img is not None:  # Resize only if an image is present
                    resized_image = img.resize((self.smallest_width, self.smallest_height), Image.Resampling.LANCZOS)

                    # Update the label's image
                    if isinstance(self.image_labels[i], AdjustableLabel):
                        self.image_labels[i].set_image(resized_image, i)

                    # Load as QPixmap
                    resized_temp_path = f"temp_resized_{i}.png"
                    resized_image.save(resized_temp_path)
                    pixmap = QPixmap(resized_temp_path)
                    os.remove(resized_temp_path)  # Clean up temporary file

                    # Resize pixmap to fit the smallest dimensions
                    pixmap = pixmap.scaled(
                        self.smallest_width, self.smallest_height, Qt.KeepAspectRatio, Qt.SmoothTransformation
                    )
                    self.image_labels[i].setPixmap(pixmap)
                    self.resize_all_labels()
    # def upload_image(self, label,index):
    #     """Open a file dialog to upload an image, convert it to grayscale, and resize all labels."""
    #     options = QFileDialog.Options()
    #     file_path, _ = QFileDialog.getOpenFileName(
    #         self, "Select Image File", "", "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)", options=options
    #     )
    #     if file_path:
    #         # Convert image to grayscale using Pillow
    #         image = Image.open(file_path).convert("L")
    #         width, height = image.size

    #         print(f"Uploaded image dimensions: {width}x{height}")  # Debugging print

    #         # Save temporarily in memory to convert to QPixmap
    #         temp_path = "temp_grayscale.png"
    #         image.save(temp_path)

    #         # Update the smallest dimensions
    #         self.update_smallest_dimensions(width,height)
    #         resized_image = image.resize((self.smallest_width, self.smallest_height), Image.Resampling.LANCZOS)

    #          # Set the original image in the label
    #         if isinstance(label, AdjustableLabel):
    #             label.set_image(resized_image,index)
            

    #         # Load as QPixmap
    #         pixmap = QPixmap(temp_path)
    #         os.remove(temp_path)  # Clean up temporary file

    #         # Resize pixmap to fit the smallest dimensions
    #         pixmap = pixmap.scaled(
    #             self.smallest_width, self.smallest_height, Qt.KeepAspectRatio, Qt.SmoothTransformation
    #         )
    #         label.setPixmap(pixmap)

    #         # Update all other labels to match the smallest dimensions
    #         self.resize_all_labels()
    #     self.progress_bar.setValue(0)

    
            
    def update_smallest_dimensions(self):
        """Update the smallest dimensions across all uploaded images."""
        self.smallest_width = float('inf')
        self.smallest_height = float('inf')

        for img in self.uploaded_images:
            if img is not None:
                width, height = img.size
                if width < self.smallest_width:
                    self.smallest_width = width
                if height < self.smallest_height:
                    self.smallest_height = height

        # Handle the case where no images are uploaded yet
        if self.smallest_width == float('inf'):
            self.smallest_width = None
        if self.smallest_height == float('inf'):
            self.smallest_height = None
    # def update_smallest_dimensions(self, width, height):
    #     """Update the smallest dimensions across all uploaded images."""
    #     if self.smallest_width is None or width < self.smallest_width:
    #         self.smallest_width = width
    #     if self.smallest_height is None or height < self.smallest_height:
    #         self.smallest_height = height

    def resize_all_labels(self):
        """Resize all image labels to match the smallest dimensions."""
        for label in self.image_labels:
            pixmap = label.pixmap()
            if pixmap:  # Resize only if an image has been uploaded
                print(f"Resizing label to: {self.smallest_width}x{self.smallest_height}")  # Debugging print
                resized_pixmap = pixmap.scaled(
                    self.smallest_width, self.smallest_height, Qt.IgnoreAspectRatio, Qt.SmoothTransformation
                )
                label.setPixmap(resized_pixmap)
                label.setFixedSize(self.smallest_width, self.smallest_height)  # Adjust QLabel size
                print(f"Label size after resizing: {label.size().width()}x{label.size().height()}")

    def update_slider_value(self, index, value,which):
        """Update the slider value for the given image index."""
        if which=="first":
            globals.ft_sliders[index] = value / 100.0  # Normalize to range [0, 1]

    def apply_mixing(self):
        """Mix the FT components based on slider values and display the result."""
        if not any(img is not None and img.size > 0 for img in globals.ft_images):
            print("No valid Fourier Transforms available for mixing.")
            return

        # Check which output to use
        selected_output = self.outputs_menu.currentText()
        output_label = None
        output_label = self.findChild(QLabel, selected_output)  # Find the label using object name


        if output_label is None:
            print(f"Invalid output label: {selected_output}")
            return
        
        # mixed_ft = None  # Initialize the mixed FT
        # region_size_percentage = self.region_size_slider.value()

        # for i, weight in enumerate(ft_sliders):
        #     if ft_components[i]["Magnitude"] is not None:
        #         component = self.combos[i].currentText()
        #         print(f"Selected component for viewer {i}: {component}")

        #         # Reconstruct the complex FT based on the selected component type
        #         if component in ["Magnitude", "Phase"]:
        #             selected_magnitude = ft_components[i]["Magnitude"]
        #             selected_phase = ft_components[i]["Phase"]
        #             complex_ft = selected_magnitude * np.exp(1j * selected_phase)
        #         elif component in ["Real", "Imaginary"]:
        #             selected_real = ft_components[i]["Real"]
        #             selected_imaginary = ft_components[i]["Imaginary"]
        #             complex_ft = selected_real + 1j * selected_imaginary
        #         else:
        #             print(f"Unknown component: {component}")
        #             continue

        #         # Apply the region selection (whole, inner, or outer) based on combo box selection
        #         region_selection = self.region_selector.currentText()
        #         if region_selection == "Inner region":
        #             # Only select low frequencies (inner region)
        #             complex_ft = self.apply_region(complex_ft, region_size_percentage, region_type='inner')
        #         elif region_selection == "Outer region":
        #             # Only select high frequencies (outer region)
        #             complex_ft = self.apply_region(complex_ft, region_size_percentage, region_type='outer')
        #         # If "Whole FT", do nothing (default behavior)

        #         # Apply weight and combine
        #         weighted_ft = weight * complex_ft
        #         if mixed_ft is None:
        #             mixed_ft = weighted_ft
        #         else:
        #             mixed_ft += weighted_ft

        mixed_ft = None  # Initialize the mixed FT
        region_size_percentage = self.region_size_slider.value()

        total_magnitude = np.zeros_like(globals.ft_components[0]["Magnitude"])
        total_phase = np.zeros_like(globals.ft_components[0]["Phase"])        
        magnitude_count = 0
        phase_count = 0

        for i, weight in enumerate(globals.ft_sliders):
            if globals.ft_components[i]["Magnitude"] is not None:
                component = self.combos[i].currentText()
                print(f"Selected component for viewer {i}: {component}")

                # Initialize complex_ft for this image
                complex_ft = np.zeros_like(globals.ft_components[i]["Magnitude"], dtype=complex)

                if component in ["Magnitude", "Phase"]:
                    if component == "Magnitude":
                                # Accumulate weighted magnitude
                                selected_magnitude = globals.ft_components[i]["Magnitude"]
                                total_magnitude += weight * selected_magnitude
                                magnitude_count += 1

                    elif component == "Phase":
                                # Accumulate weighted phase
                                selected_phase = globals.ft_components[i]["Phase"]
                                total_phase += weight * selected_phase
                                phase_count += 1

                    # Compute the averages
                    
                    avg_magnitude = total_magnitude / max(magnitude_count, 1)  # Avoid division by 0
                    avg_phase = total_phase / max(phase_count, 1)  # Avoid division by 0

                    if magnitude_count==0:
                        avg_magnitude=globals.ft_components[0]["Magnitude"]

                    # Construct the final mixed FT
                    mixed_ft = avg_magnitude * np.exp(1j * avg_phase)
                    # Apply region selection (optional)
                    region_selection = self.region_selector.currentText()
                    if region_selection == "Inner region":
                        mixed_ft = self.apply_region(mixed_ft, region_size_percentage, region_type="inner")
                    elif region_selection == "Outer region":
                        mixed_ft = self.apply_region(mixed_ft, region_size_percentage, region_type="outer")


                elif component in ["Real", "Imaginary"]:
                    if component == "Real":
                        # Take the real component, apply the weight, and set imaginary part to 0
                        selected_real = globals.ft_components[i]["Real"]
                        complex_ft = weight * selected_real + 1j * 0

                    elif component == "Imaginary":
                        # Take the imaginary component, apply the weight, and set real part to 0
                        selected_imaginary = globals.ft_components[i]["Imaginary"]
                        complex_ft = 0 + 1j * (weight * selected_imaginary)

                    else:
                        print(f"Unknown component: {component}")
                        continue
                    
                    # Enforce Hermitian symmetry to avoid mirroring artifacts
                    # complex_ft = self.enforce_hermitian_symmetry(complex_ft)

                    # Apply the region selection (whole, inner, or outer) based on combo box selection
                    region_selection = self.region_selector.currentText()
                    if region_selection == "Inner region":
                        # Only select low frequencies (inner region)
                        complex_ft = self.apply_region(complex_ft, region_size_percentage, region_type='inner')
                    elif region_selection == "Outer region":
                        # Only select high frequencies (outer region)
                        complex_ft = self.apply_region(complex_ft, region_size_percentage, region_type='outer')
                    # If "Whole FT", do nothing (default behavior)

                    # Combine this image's contribution to the mixed FT
                    if mixed_ft is None:
                        mixed_ft = complex_ft
                    else:
                        mixed_ft += complex_ft



        if mixed_ft is None:
            print("No valid FT components were mixed.")
            return

        # Apply inverse FFT to get the result
        mixed_image = np.fft.ifft2(np.fft.ifftshift(mixed_ft)).real
        mixed_image = np.clip(mixed_image, 0, 255).astype(np.uint8)  # Ensure valid range

        # Convert to QPixmap and display in the output label
        height, width = mixed_image.shape
        q_image = QImage(mixed_image.data, width, height, width, QImage.Format_Grayscale8)
        pixmap = QPixmap.fromImage(q_image)

        if pixmap.isNull():
            print("Failed to create QPixmap from mixed image.")
            return

        output_label.setPixmap(pixmap)
        output_label.setFixedSize(width, height)
        output_label.update()
        print(f"Mixed image displayed in {selected_output}.")

        # self.progress_bar.setValue(100)  # Set progress bar to 100%
        # print(f"Progress bar set to 100%. Mixed image displayed in {selected_output}.")
        self.progress_bar.setValue(0)  # Reset to 0%
        # Simulate progress
        for value in range(0, 101, 20):  # Simulating progress in steps
            self.progress_bar.setValue(value)
            QCoreApplication.processEvents()  # Process events to update UI

    def enforce_hermitian_symmetry(self, complex_ft):
        """Enforce Hermitian symmetry on the Fourier Transform to avoid mirroring artifacts."""
        height, width = complex_ft.shape

        # Top-left quadrant remains unchanged
        top_left = complex_ft[: height // 2 + 1, : width // 2 + 1]

        # Reflect top-left to bottom-right
        bottom_right = np.conj(np.flip(np.flip(top_left, axis=0), axis=1))

        # Create a new array for symmetric FT
        symmetric_ft = np.zeros_like(complex_ft, dtype=complex)

        # Top-left quadrant
        symmetric_ft[: height // 2 + 1, : width // 2 + 1] = top_left

        # Bottom-right quadrant (ensure correct indexing for odd sizes)
        symmetric_ft[height // 2 + 1 :, width // 2 + 1 :] = bottom_right[
            : height - (height // 2 + 1), : width - (width // 2 + 1)
        ]

        # Handle vertical symmetry for the middle column (if width is odd)
        if width % 2 == 1:
            symmetric_ft[height // 2 + 1 :, width // 2] = np.conj(
                np.flip(top_left[:, width // 2], axis=0)
            )[: height - (height // 2 + 1)]

        # Handle horizontal symmetry for the middle row (if height is odd)
        if height % 2 == 1:
            symmetric_ft[height // 2, width // 2 + 1 :] = np.conj(
                np.flip(top_left[height // 2, :], axis=0)
            )[: width - (width // 2 + 1)]

        return symmetric_ft



    def apply_region(self, complex_ft, region_size_percentage, region_type):
        """Apply the region selection (inner or outer) to the FT component."""
        # Get the size of the FT component
        width, height = complex_ft.shape

        # Calculate region size as a percentage of the total dimensions
        region_size_x = int((region_size_percentage / 100) * width / 2)  # Half-size for inner region
        region_size_y = int((region_size_percentage / 100) * height / 2)

        # Center of the Fourier Transform
        center_x, center_y = width // 2, height // 2

        if region_type == 'inner':
            # Keep only the low frequencies (center region), set everything else to 0
            mask = np.zeros_like(complex_ft, dtype=bool)
            mask[
                center_x - region_size_x : center_x + region_size_x,
                center_y - region_size_y : center_y + region_size_y,
            ] = True
            complex_ft[~mask] = 0  # Zero out everything outside the mask

        elif region_type == 'outer':
            # Keep only the high frequencies (outer region), set the center region to 0
            mask = np.ones_like(complex_ft, dtype=bool)
            mask[
                center_x - region_size_x : center_x + region_size_x,
                center_y - region_size_y : center_y + region_size_y,
            ] = False
            complex_ft[~mask] = 0  # Zero out the center region

        return complex_ft

    # def apply_region(self, complex_ft, region_size_percentage, region_type):
    #     """Apply the region selection to the FT component."""
    #     # Get the size of the FT component
    #     width, height = complex_ft.shape

    #     region_size_x = int((region_size_percentage / 100) * width)
    #     region_size_y = int((region_size_percentage / 100) * height)

    #     if region_type == 'inner':
    #         # Crop or filter the low-frequency components
    #         complex_ft[:region_size_x, :region_size_y] = 0
    #     elif region_type == 'outer':
    #         # Crop or filter the high-frequency components
    #         complex_ft[region_size_x:, region_size_y:] = 0

    #     return complex_ft


    # def update_modes(self):
    #     """Enable or disable dropdown items based on the selected mode."""
    #     if self.mag_phase_box.isChecked():
    #         self.real_imag_box.setChecked(False)  # Uncheck the other box
    #         for combo in self.combos:  # self.combos contains all the dropdowns
    #             combo.model().item(0).setEnabled(True)  # Enable "Magnitude"
    #             combo.model().item(1).setEnabled(True)  # Enable "Phase"
    #             combo.model().item(2).setEnabled(False)  # Disable "Real"
    #             combo.model().item(3).setEnabled(False)  # Disable "Imaginary"

    #     elif self.real_imag_box.isChecked():
    #         self.mag_phase_box.setChecked(False)  # Uncheck the other box
    #         for combo in self.combos:
    #             combo.model().item(0).setEnabled(False)  # Disable "Magnitude"
    #             combo.model().item(1).setEnabled(False)  # Disable "Phase"
    #             combo.model().item(2).setEnabled(True)  # Enable "Real"
    #             combo.model().item(3).setEnabled(True)  # Enable "Imaginary"
    def update_modes(self):
        """Enable or disable dropdown items based on the selected mode."""
        selected_mode = self.mode_selector.currentText()  # Get the selected mode

        if selected_mode == "Mag/Phase":
            for combo in self.combos:  # self.combos contains all the dropdowns
                combo.model().item(0).setEnabled(True)   # Enable "Magnitude"
                combo.model().item(1).setEnabled(True)   # Enable "Phase"
                combo.model().item(2).setEnabled(False)  # Disable "Real"
                combo.model().item(3).setEnabled(False)  # Disable "Imaginary"

        elif selected_mode == "Real/Imag":
            for combo in self.combos:
                combo.model().item(0).setEnabled(False)  # Disable "Magnitude"
                combo.model().item(1).setEnabled(False)  # Disable "Phase"
                combo.model().item(2).setEnabled(True)   # Enable "Real"
                combo.model().item(3).setEnabled(True)   # Enable "Imaginary"


    def update_regions(self):
        """Update the region selection based on the combo box and slider values."""
        selected_region = self.region_selector.currentText()  # Get the selected region
        region_size_percentage = self.region_size_slider.value()  # Get the percentage size of the rectangle
        print(f"Region Size: {region_size_percentage}%")
        print(f"item selected:{selected_region}")

        if selected_region == "Whole FT":
            self.clear_regions()  # Clear any selected regions (reset to default mode)
            print("No region selected, applying mixing to the whole FT.")
        elif selected_region == "Inner region":
            # Draw the inner region (low-frequency part of the FT)
            self.draw_regions('inner', region_size_percentage)
        elif selected_region == "Outer region":
            # Draw the outer region (high-frequency part of the FT)
            self.draw_regions('outer', region_size_percentage)

    def clear_regions(self):
        """Clear any drawn rectangles to reset to the default mode."""
        for ft_label in globals.ft_labels:
            ft_label.rectangles = []  # Clear the stored rectangles for each FT label
            ft_label.update()  # Redraw the FT label without the rectangles

    def draw_regions(self, region_type, region_size_percentage):
        """Draw the selected region on all FT component plots."""
        for ft_label in globals.ft_labels:
            ft_label.set_region(region_type, region_size_percentage)  # Set region for each FT label

    def reset(self):
        """Reset the mixer controls, clearing all images and data."""
        # global ft_labels, ft_images, ft_components, ft_sliders

        # Reinitialize global variables
        globals.ft_labels = []
        globals.ft_images = [None] * 4
        self.image_labels=[]  # Store all image labels for resizing
        globals.ft_sliders = [0,0,0,0]
        self.combos=[]
        globals.ft_components = [{"Magnitude": None, "Phase": None, "Real": None, "Imaginary": None} for _ in range(4)]

        # Reset dimensions
        self.smallest_width = None
        self.smallest_height = None

        # Reset uploaded images list
        self.uploaded_images = [None] * 4
        # Clear and reset image labels
        for label in self.image_labels:
            label.clear()  # Clear the QLabel content
            label.original_image = None  # Reset stored image
            label.ft_image = None  # Reset Fourier Transform
            label.rectangles = []  # Clear any drawn rectangles
            label.setFixedSize(300, 200)  # Reset QLabel to default size
            label.update()

        # Clear and reset FT labels
        for label in globals.ft_labels:
            label.clear()  # Clear the QLabel content
            label.setFixedSize(300, 200)  # Reset QLabel to default size
            label.update()
         # Reset UI elements
        self.mode_selector.setCurrentIndex(0)
        self.region_selector.setCurrentIndex(0)
        self.region_size_slider.setValue(50)  # Reset region slider

        self.initUi()

        print("Mixer controls and image labels have been reset.")
