from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt,QRect,QThread, pyqtSignal, QObject,QCoreApplication
from PyQt5.QtGui import QPixmap,QImage,QColor, QPen,QPainter
from PIL import ImageEnhance
import numpy as np
import globals


class AdjustableLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.brightness = 1.0  # Default brightness
        self.contrast = 1.0    # Default contrast
        self.last_mouse_position = None
        self.original_image = None  # Store original image for adjustments
        self.ft_image = None        # Store the Fourier Transform of the image
        self.selected_component = "Magnitude"  # Default component to display
        self.rectangles = []  # Store rectangles for region selection

    def paintEvent(self, event):
        """Override the paintEvent to draw rectangles on the QLabel."""
        super().paintEvent(event)  # Call the base class method to handle normal painting (image display)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw the rectangles stored in self.rectangles
        for rect in self.rectangles:
            painter.setPen(QPen(Qt.green, 2))  # Green rectangle with 2px border
            painter.setBrush(QColor(0, 255, 0, 50))  # Semi-transparent green fill
            painter.drawRect(rect)  # Draw the rectangle

    def set_region(self, region_type, region_size_percentage):
        """Set the rectangle region (inner or outer) for mixing."""
        width, height = self.width(), self.height()

        region_size_x = int((region_size_percentage / 100) * width)
        region_size_y = int((region_size_percentage / 100) * height)

        # Calculate the top-left corner position to center the rectangle
        x_offset = (width - region_size_x) // 2
        y_offset = (height - region_size_y) // 2

        if region_type == 'inner':
            rect = QRect(x_offset, y_offset, region_size_x, region_size_y)  # Inner (low-frequency) region
        elif region_type == 'outer':
            rect = QRect(x_offset, y_offset, region_size_x, region_size_y)  # Outer (high-frequency) region

        # Store the rectangle for later drawing
        self.rectangles = [rect]
        self.update()  # Redraw the label (this calls paintEvent)

    def set_image(self, image,index):
        """Set the original image (Pillow Image object) and reset adjustments."""
        self.original_image = image
        self.update_image()
        # if ft_images[index] is None:
        self.calculate_ft(index)
        self.plot_ft_component("Magnitude",index)  # Plot default component after setting 

    def update_image(self):
        """Apply brightness and contrast adjustments and display the updated image."""
        if self.original_image:
            # Apply brightness and contrast adjustments
            enhanced_image = ImageEnhance.Brightness(self.original_image).enhance(self.brightness)
            enhanced_image = ImageEnhance.Contrast(enhanced_image).enhance(self.contrast)

            qimage = self.pillow_to_qimage(enhanced_image)
            pixmap = QPixmap.fromImage(qimage)

            # Resize the pixmap to the QLabel's fixed size
            resized_pixmap = pixmap.scaled(
                self.width(), self.height(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation
            )
            self.setPixmap(resized_pixmap)

    def pillow_to_qimage(self, image):
        """Convert a Pillow image to QImage."""
        data = np.array(image)
        height, width = data.shape if len(data.shape) == 2 else data.shape[:2]
        bytes_per_line = width
        return QImage(data.data, width, height, bytes_per_line, QImage.Format_Grayscale8)

    def mousePressEvent(self, event):
        """Capture the initial mouse position on press."""
        if event.button() == Qt.LeftButton:
            self.last_mouse_position = event.pos()

    def mouseMoveEvent(self, event):
        """Adjust brightness/contrast based on mouse movement."""
        if self.last_mouse_position:
            delta = event.pos() - self.last_mouse_position
            self.last_mouse_position = event.pos()

            # Adjust brightness (vertical movement)
            self.brightness += delta.y() * -0.01  # Invert for natural feel
            self.brightness = max(0.1, min(3.0, self.brightness))  # Clamp values

            # Adjust contrast (horizontal movement)
            self.contrast += delta.x() * 0.01
            self.contrast = max(0.1, min(3.0, self.contrast))  # Clamp values

            # Update the displayed image
            self.update_image()

    def calculate_ft(self,i):
        """Calculate the Fourier Transform of the current image."""
        if self.original_image:
            np_image = np.array(self.original_image)
            self.ft_image = np.fft.fftshift(np.fft.fft2(np_image))
            globals.ft_images[i]=self.ft_image
            print(f"the index is {i}")
            print(f"FT image calculated: {self.ft_image.shape}")

    def plot_ft_component(self, component,index):
        """Plot the selected Fourier Transform component."""
        if globals.ft_images[index] is None:
            print("FT image is not available.")
            return
    
        # Calculate and store FT components
        globals.ft_components[index]["Magnitude"] = np.abs(globals.ft_images[index])
        globals.ft_components[index]["Phase"] = np.angle(globals.ft_images[index])
        globals.ft_components[index]["Real"] = np.real(globals.ft_images[index])
        globals.ft_components[index]["Imaginary"] = np.imag(globals.ft_images[index])
      
        ft_component = globals.ft_components[index][component]

        if ft_component is None:
            print(f"Failed to extract {component} component.")
            return

        # Debugging: Print component details
        print(f"{component} component calculated. Shape: {ft_component.shape}, Min: {ft_component.min()}, Max: {ft_component.max()}")
        print(f"the index is {index}")
        print(f"the ft-components are {ft_component[3][0]}")

        # Apply log scale for better visibility (except for Phase, as it doesn't need scaling)
        if component != "Phase":
            ft_component = np.log1p(np.abs(ft_component))  # Add 1 to avoid log(0)

        # Normalize the component to range 0-255
        ft_component_min = np.min(ft_component)
        ft_component_max = np.max(ft_component)
        if ft_component_max == ft_component_min:  # Avoid division by zero
            print(f"{component} component has no variation (min=max). Cannot normalize.")
            return

        # Normalize to 0-255 for display
        ft_component = 255 * (ft_component - ft_component_min) / (ft_component_max - ft_component_min)
        ft_component = ft_component.astype(np.uint8)

        # Convert to QPixmap for display
        try:
            height, width = ft_component.shape
            q_image = QImage(ft_component.data,width, height, QImage.Format_Grayscale8)
            pixmap = QPixmap.fromImage(q_image)
            # Display the FT component on the corresponding label
            ft_label =globals.ft_labels[index]  # Get the target QLabel
            ft_label.setPixmap(pixmap)
            ft_label.setFixedSize(300, 200)  # Resize QLabel to match the image
            ft_label.update()  # Force the label to refresh
            print(f"{component} component successfully displayed on label {index}.")
        except Exception as e:
            print(f"Error displaying {component} component: {e}")
