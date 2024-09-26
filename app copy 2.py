import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from solidspy import solids_GUI
from openai import OpenAI

# Streamlit app title
st.title("2D Finite Element Analysis with SolidsPy")

# Sidebar for file uploads
st.sidebar.header("Input Files")
nodes_file = st.sidebar.file_uploader("Upload nodes.txt", type="txt")
eles_file = st.sidebar.file_uploader("Upload eles.txt", type="txt")
mater_file = st.sidebar.file_uploader("Upload mater.txt", type="txt")
loads_file = st.sidebar.file_uploader("Upload loads.txt", type="txt")


def fetch_response(user_query):
    system_prompt = """
    You are FEM expert. Your job is to generate the files for a 2D FEA simulation.
    You respond Only in valid JSON format.
    """
    user_prompt = f"""
    You generate the following files for a 2D FEA simulation:
    1. nodes_file: Contains the nodal coordinates
    2. eles_file: Contains the element connectivity
    3. mater_file: Contains the material properties
    4. loads_file: Contains the applied loads
    Below is an example of how you will perform the task:
    
    Assume that we want to find the response of the 2×2 square under unitary vertical point loads shown in the following figure. Where one corner is located at (0,0) and the opposite one at (2,2).
    ***
    - The nodes_file is composed of the following fields:

        Column 0: Nodal identifier (integer).
        Column 1: x-coordinate (float).
        Column 2: y-coordinate (float).
        Column 3: Boundary condition flag along the x-direction (0 free, -1 restrained).
        Column 4: Boundary condition flag along the y-direction (0 free, -1 restrained).
        The corresponding file has the following data

        0  0.00  0.00   0  -1
        1  2.00  0.00   0  -1
        2  2.00  2.00   0   0
        3  0.00  2.00   0   0
        4  1.00  0.00  -1  -1
        5  2.00  1.00   0   0
        6  1.00  2.00   0   0
        7  0.00  1.00   0   0
        8  1.00  1.00   0   0
        
    - The eles_file contain the element information. Each line in the file defines the information for a single element and is composed of the following fields:

        Column 0: Element identifier (integer).
        Column 1: Element type (integer):
        1 for a 4-noded quadrilateral.
        2 for a 6-noded triangle.
        3 for a 3-noded triangle.
        Column 2: Material profile for the current element (integer).
        Column 3 to end: Element connectivity, this is a list of the nodes conforming each element. The nodes should be listed in counterclockwise orientation.
        The corresponding file has the following data

        0   1   0   0   4   8   7
        1   1   0   4   1   5   8
        2   1   0   7   8   6   3
        3   1   0   8   5   2   6
        
    - The mater_file contain the material information. Each line in the file corresponds to a material profile to be assigned to the different elements in the elements file. In this example, there is one material profile. Each line in the file is composed of the following fields:

        Column 0: Young’s modulus for the current profile (float).
        Column 1: Poisson’s ratio for the current profile (float).
        The corresponding file has the following data

        1.0  0.3
        
    The load_file contains the information about the applied loads. Each line in the file is composed of the following fields:
    Column 0: Nodal identifier (integer).
    Column 1: Load magnitude for the current node along the x-direction (float).
    Column 2: Load magnitude for the current node along the y-direction (float).
    The corresponding file has the following data

    3  0.0  1.0
    6  0.0  2.0
    2  0.0  1.0
    ***
    You will be provided with a user_query that describes a mechanical system under load in laymans terms, You will use this information to generate the files for a 2D FEA simulation.
    
    use the following format to respond:
    
    {{
        "nodes_file": [
            [0, 0.00, 0.00, 0, -1],
            [1, 2.00, 0.00, 0, -1],
            [2, 2.00, 2.00, 0, 0],
            [3, 0.00, 2.00, 0, 0],
            [4, 1.00, 0.00, -1, -1],
            [5, 2.00, 1.00, 0, 0],
            [6, 1.00, 2.00, 0, 0],
            [7, 0.00, 1.00, 0, 0],
            [8, 1.00, 1.00, 0, 0]
        ],
    }}
                    

    
    """


# Function to save uploaded files locally for SolidsPy processing
def save_uploaded_file(uploaded_file, filename):
    with open(filename, "wb") as f:
        f.write(uploaded_file.getbuffer())

# Check if all files are uploaded
if nodes_file and eles_file and mater_file and loads_file:
    # Save the uploaded files
    save_uploaded_file(nodes_file, "nodes.txt")
    save_uploaded_file(eles_file, "eles.txt")
    save_uploaded_file(mater_file, "mater.txt")
    save_uploaded_file(loads_file, "loads.txt")

    # Run the FEA simulation using SolidsPy
    st.write("Running Finite Element Analysis...")
    disp = solids_GUI()  # This runs the simulation

    # Plot the displacement results
    st.write("Displacement Results")
    fig, ax = plt.subplots()
    im = ax.imshow(disp[:, :2], cmap='coolwarm', aspect='auto')
    plt.colorbar(im, ax=ax)
    ax.set_title("Displacement Contours")
    st.pyplot(fig)

else:
    st.write("Please upload all required input files (nodes.txt, eles.txt, mater.txt, loads.txt).")
