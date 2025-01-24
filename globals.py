# Define global variables
ft_labels = []   # Store FT QLabel references
ft_images = [None] * 4  # Store Fourier Transform images
ft_sliders = [0, 0, 0, 0]
ft_components = [{"Magnitude": None, "Phase": None, "Real": None, "Imaginary": None} for _ in range(4)]
