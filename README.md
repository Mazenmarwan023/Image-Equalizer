# Image Equalizer

## Description

This project implements an interactive desktop application for exploring the Fourier Transform (FT) components of grayscale images. The application allows users to manipulate and visualize the importance of magnitude and phase or real and imaginary components, enabling a deeper understanding of the impact of each on the signal. Users can also customize the mixing of different frequency regions for advanced visualization and analysis.

## Features

### 1. **Image Viewing**
- **Four Image Viewers**: View up to four grayscale images simultaneously, with unified sizes across all images.
  - If a colored image is uploaded, it is automatically converted to grayscale.
- **FT Component Display**: Select from the following FT components to display in any viewport:
  - Magnitude
  - Phase
  - Real
  - Imaginary
- **Brightness/Contrast Adjustment**: Adjust the brightness and contrast of any image or component using mouse drag gestures.

### 2. **Mixing Components**
- **Two Modes**:
  - Magnitude and Phase
  - Real and Imaginary
- **Customizable Weights**: Adjust weights for each FT component using intuitive sliders to mix components and generate a new output image.
- **Output Viewports**: View the mixing results in one of two output viewports, with full control over where the result is displayed.

### 3. **Region-Based Mixing**
- **Inner and Outer Region Selection**:
  - Use a rectangular selector to highlight and include either the inner (low frequencies) or outer (high frequencies) region of the FT components.
  - Customize the size of the region using a slider or resize handles.
  - Unified selection across all input images for consistent mixing.

### 4. **Real-Time Mixing**
- **Interactive Updates**:
  - Mixing is performed in real-time using inverse Fourier Transform (IFFT).
  - A progress bar shows the operation's status for lengthy computations.
  - If a new mixing operation is requested, the previous operation is canceled and the new one starts immediately, ensuring responsive performance.

## Screenshots

1. **Application UI on Startup**
   
   <img width="1500" alt="UI" src="https://github.com/user-attachments/assets/74f2428f-ada6-4005-9060-5ce4ff2de1cb" />


3. **Equalizing Using Magnitude and Phase Mode**
   
   <img width="1500" alt="Mag:phase_sameimage" src="https://github.com/user-attachments/assets/305e960c-d81d-4340-92ff-301df3b77c0e" />

   <img width="1500" alt="Mag:phase" src="https://github.com/user-attachments/assets/cd56b5c4-45ed-4308-9a46-a60616c02c80" />


5. **Equalizing Using Real and Imaginary Mode**
   
    <img width="1500" alt="Real:imag" src="https://github.com/user-attachments/assets/57631af4-9e5b-4201-a676-57dde5d7049d" />


7. **Inner Region Frequency Equalizing**
   
   <img width="1500" alt="Inner_region" src="https://github.com/user-attachments/assets/5c1480ca-a94f-4244-ac4c-c810e552fd80" />


9. **Outer Region Frequency Equalizing**
    
   <img width="1500" alt="outer_region" src="https://github.com/user-attachments/assets/3a7ee2f6-2346-4416-8f33-6ea34b407715" />


## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/Mazenmarwan023/image-equalizer.git
    ```

2. Navigate to the project directory:
    ```bash
    cd image-equalizer
    ```

3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. Run the application:
    ```bash
    python app.py
    ```

2. Upload up to four grayscale images. 
3. Select an FT component (Magnitude, Phase, Real, or Imaginary) from the dropdown menu for each image.
4. Adjust the sliders to customize mixing weights or region selection.
5. View the mixing results in the output viewport.

## Contributors

- [Mazen marwan](https://github.com/Mazenmarwan023)
- [Saif mohamed](https://github.com/seiftaha)
- [Mahmoud mohamed](https://github.com/mahmoudmo22)
- [Farha](https://github.com/farha1010)
- [Eman emad](https://github.com/alyaaa20)

## License

This project is licensed under the MIT License.
