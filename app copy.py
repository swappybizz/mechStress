import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from solidspy import solids_GUI
from openai import OpenAI
import json

# Streamlit app title
st.title("2D Finite Element Analysis with SolidsPy")

# Sidebar for file uploads

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
        "eles_file": [
            [0, 1, 0, 0, 4, 8, 7],
            [1, 1, 0, 4, 1, 5, 8],
            [2, 1, 0, 7, 8, 6, 3],
            [3, 1, 0, 8, 5, 2, 6]
        ],
        "mater_file": [
            [1.0, 0.3]
        ],
        "loads_file": [
            [3, 0.0, 1.0],
            [6, 0.0, 2.0],
            [2, 0.0, 1.0]
        ]
        "explain": "The user had provided the following mechnical system...which can be imagined as a 2x2 square under unitary point loads... from this information I generated the files for a 2D FEA simulation"
    }}
    
    Here is the user_query:
    ###
    {user_query}
    ###
    
    Respond Only in valid JSON format.
    Do not add any additional information.

    """
    model = "gpt-4o"
    client = OpenAI(api_key=st.secrets["openai_api_key"])
    completion = client.chat.completions.create(
        model="gpt-4o",
        response_format = {"type": "json_object"},
        messages=[
                    {
                        "role":"system",
                        "content": system_prompt
                    },
                    {
                        "role":"user",
                        "content": user_prompt
                    },
                ]
    )
    res = completion.choices[0].message.content
    response = json.loads(res)
    # print(f"Response: {response}")
    if response:
        try:
            nodes_file = response["nodes_file"]
            eles_file = response["eles_file"]
            mater_file = response["mater_file"]
            loads_file = response["loads_file"]
            explain = response["explain"]
            return nodes_file, eles_file, mater_file, loads_file, explain
        except KeyError:
            return None
    else:
        return None
    
    
        
        
        
        
# Text input for user query
user_query = st.text_area("Describe your mechanical system:")

# Button to generate FEA files
# Button to generate FEA files
if st.button("Generate FEA Files"):
    if user_query:
        # Fetch response from LLM
        nodes_file, eles_file, mater_file, loads_file, explain = fetch_response(user_query)
        
        if nodes_file and eles_file and mater_file and loads_file:
            # Save the generated files in session state
            st.session_state['nodes_file'] = nodes_file
            st.session_state['eles_file'] = eles_file
            st.session_state['mater_file'] = mater_file
            st.session_state['loads_file'] = loads_file
            st.session_state['explain'] = explain

            st.write("FEA files generated successfully. Click 'ready to run' to proceed.")

# Button to run the simulation
if st.button("ready to run"):
    if 'nodes_file' in st.session_state and 'eles_file' in st.session_state:
        # Save the files from session state
        with open("nodes.txt", "w") as f:
            for line in st.session_state['nodes_file']:
                f.write(" ".join(map(str, line)) + "\n")
                
        with open("eles.txt", "w") as f:
            for line in st.session_state['eles_file']:
                f.write(" ".join(map(str, line)) + "\n")
                
        with open("mater.txt", "w") as f:
            for line in st.session_state['mater_file']:
                f.write(" ".join(map(str, line)) + "\n")
                
        with open("loads.txt", "w") as f:
            for line in st.session_state['loads_file']:
                f.write(" ".join(map(str, line)) + "\n")
                
        # Run the FEA simulation
        st.write("Running Finite Element Analysis...")
        disp = solids_GUI()  # This runs the simulation

        # Plot the displacement results
        st.write("Displacement Results")
        fig, ax = plt.subplots()
        im = ax.imshow(disp[:, :2], cmap='coolwarm', aspect='auto')
        plt.colorbar(im, ax=ax)
        ax.set_title("Displacement Contours")
        st.pyplot(fig)
        
        # Display explanation
        st.write("Explanation:")
        st.write(st.session_state['explain'])
    else:
        st.write("FEA files not found. Please generate the files first.")