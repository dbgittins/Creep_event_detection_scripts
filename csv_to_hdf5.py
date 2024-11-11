import numpy as np 
import os
from collections import Counter
import h5py

def print_hdf5_structure(file_name, group_name=''):
    """
    Recursively print the structure of an HDF5 file.

    Parameters:
    - file_name (str): The path to the HDF5 file.
    - group_name (str): The name of the group to start from (default is root).
    """
    with h5py.File(file_name, 'r') as hdf_file:
        # If no group_name is provided, start from the root
        if group_name == '':
            group_name = '/'

        print(f"Group: {group_name}")

        # Iterate through the items in the specified group
        for name in hdf_file[group_name]:
            item = hdf_file[group_name][name]
            if isinstance(item, h5py.Group):
                # If it's a group, recursively print its structure
                print_hdf5_structure(file_name, group_name + name + '/')
            elif isinstance(item, h5py.Dataset):
                # If it's a dataset, print its name and shape
                print(f"  Dataset: {name}, Shape: {item.shape}, Dtype: {item.dtype}")

def find_top_modes(data, n_modes, allowed_numbers):
    # Filter the data to include only the allowed numbers
    filtered_data = [num for num in data if num in allowed_numbers]
    
    # Count occurrences of the filtered data
    data_count = Counter(filtered_data)
    
    # Get the n most common modes in sorted order
    sorted_modes = data_count.most_common(n_modes)
    return sorted_modes

def round_to_nearest_half(values):
    return np.array([round(value * 2) / 2 for value in values])

def round_to_nearest_0_1(values):
    return np.array([round(value * 10) / 10 for value in values])



def stringify(value):
    # Dictionary for common conversions
    num_to_word = {
        1: "one",
        2: "two",
        5: "five",
        10: "ten",
        30: "thirty",
        60: "sixty"
    }
    
    # Handle special cases
    if value == 0.5:
        return "half"
    elif value == 1/60:
        return "sixtieth"
    elif value == 1/6:
        return "sixth"
    elif value in num_to_word:
        return num_to_word[value]
    else:
        return str(value)  # Fallback for other numbers
    


def list_files_in_directory(directory_path):
    """
    Generate a list of all files in the specified directory.

    Parameters:
    - directory_path (str): The path to the directory.

    Returns:
    - list: A list of file names in the directory.
    """
    # Initialize an empty list to hold the file names
    file_names = []

    # List all entries in the specified directory
    for file in os.listdir(directory_path):
        full_file_name = os.path.join(directory_path, file)  # Get full file path
        if os.path.isfile(full_file_name):  # Check if it is a file
            file_names.append(file)  # Append file name to the list

    return file_names

def one_to_two(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] > 1:
            if tm_diff[i] == 2:
                if i >=1:
                    if tm_diff[i-1] != tm_diff[i+1]:
                        if i >=2:
                            if tm_diff[i-2] != tm_diff[i+2]:
                                if i >=200:
                                    if tm_diff[i-200] != tm_diff[i+200]:
                                        break
    return i  # Indicates no valid transition

def one_to_half(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] < 1:
            if tm_diff[i] == 0.5:
                if i >=1:
                    if tm_diff[i-1] != tm_diff[i+1]:
                        if i >=2:
                            if tm_diff[i-2] != tm_diff[i+2]:
                                if i >=200:
                                    if tm_diff[i-200] != tm_diff[i+200]:
                                        break

    return i  # Indicates no valid transition

def one_to_sixth(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] < 1:
            if tm_diff[i] == 1/6:
                if i >=1:
                    if tm_diff[i-1] != tm_diff[i+1]:
                        if i >=2:
                            if tm_diff[i-2] != tm_diff[i+2]:
                                if i >=200:
                                    if tm_diff[i-200] != tm_diff[i+200]:
                                        break

    return i  # Indicates no valid transition


def one_to_five(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] > 1:
            if tm_diff[i] == 5:
                if i >=1:
                    if tm_diff[i-1] != tm_diff[i+1]:
                        if i >=2:
                            if tm_diff[i-2] != tm_diff[i+2]:
                                if i >=200:
                                    if tm_diff[i-200] != tm_diff[i+200]:
                                        break
    return i  # Indicates no valid transition

def one_to_ten(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] > 1:
            if tm_diff[i] == 10:
                if i >=1:
                    if tm_diff[i-1] != tm_diff[i+1]:
                        if i >=2:
                            if tm_diff[i-2] != tm_diff[i+2]:
                                if i >=200:
                                    if tm_diff[i-200] != tm_diff[i+200]:
                                        break
    return i  # Indicates no valid transition

def one_to_thirty(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] > 1:
            if tm_diff[i] == 30:
                if i >=1:
                    if tm_diff[i-1] != tm_diff[i+1]:
                        if i >=2:
                            if tm_diff[i-2] != tm_diff[i+2]:
                                if i >=200:
                                    if tm_diff[i-200] != tm_diff[i+200]:
                                        break
    return i  # Indicates no valid transition

def one_to_sixty(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] > 1:
            if tm_diff[i] == 60:
                if i >=1:
                    if tm_diff[i-1] != tm_diff[i+1]:
                        if i >=2:
                            if tm_diff[i-2] != tm_diff[i+2]:
                                if i >=200:
                                    if tm_diff[i-200] != tm_diff[i+200]:
                                        break
    return i  # Indicates no valid transition

def five_to_one(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] < 5:
            if tm_diff[i] == 1:
                if i >=1:
                    if tm_diff[i-1] != tm_diff[i+1]:
                        if i >=2:
                            if tm_diff[i-2] != tm_diff[i+2]:
                                if i >=200:
                                    if tm_diff[i-200] != tm_diff[i+200]:
                                        break
    return i  # Indicates no valid transition

def five_to_half(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] < 5:
            if tm_diff[i] == 0.5:
                if i >=1:
                    if tm_diff[i-1] != tm_diff[i+1]:
                        if i >=2:
                            if tm_diff[i-2] != tm_diff[i+2]:
                                if i >=200:
                                    if tm_diff[i-200] != tm_diff[i+200]:
                                        break
    return i  # Indicates no valid transition

def five_to_two(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] < 5:
            if tm_diff[i] == 2:
                if i >=1:
                    if tm_diff[i-1] != tm_diff[i+1]:
                        if i >=2:
                            if tm_diff[i-2] != tm_diff[i+2]:
                                if i >=200:
                                    if tm_diff[i-200] != tm_diff[i+200]:
                                        break
    return i  # Indicates no valid transition

def five_to_ten(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] > 5:
            if tm_diff[i] == 10:
                if i >=1:
                    if tm_diff[i-1] != tm_diff[i+1]:
                        if i >=2:
                            if tm_diff[i-2] != tm_diff[i+2]:
                                if i >=200:
                                    if tm_diff[i-200] != tm_diff[i+200]:
                                        break
    return i  # Indicates no valid transition

def five_to_thirty(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] > 5:
            if tm_diff[i] == 30:
                if i >=1:
                    if tm_diff[i-1] != tm_diff[i+1]:
                        if i >=2:
                            if tm_diff[i-2] != tm_diff[i+2]:
                                if i >=200:
                                    if tm_diff[i-200] != tm_diff[i+200]:
                                        break
    return i  # Indicates no valid transition

def five_to_sixty(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] > 5:
            if tm_diff[i] == 60:
                if i >=1:
                    if tm_diff[i-1] != tm_diff[i+1]:
                        if i >=2:
                            if tm_diff[i-2] != tm_diff[i+2]:
                                if i >=200:
                                    if tm_diff[i-200] != tm_diff[i+200]:
                                        break
    return i  # Indicates no valid transition

def five_to_sixth(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] < 5:
            if tm_diff[i] == 1/6:
                if i >=1:
                    if tm_diff[i-1] != tm_diff[i+1]:
                        if i >=2:
                            if tm_diff[i-2] != tm_diff[i+2]:
                                if i >=200:
                                    if tm_diff[i-200] != tm_diff[i+200]:
                                        break

    return i  # Indicates no valid transition

def ten_to_one(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] < 10:
            if tm_diff[i] == 1:
                if i >=1:
                    if tm_diff[i-1] != tm_diff[i+1]:
                        if i >=2:
                            if tm_diff[i-2] != tm_diff[i+2]:
                                if i >=200:
                                    if tm_diff[i-200] != tm_diff[i+200]:
                                        break
    return i  # Indicates no valid transition

def ten_to_sixth(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] < 10:
            if tm_diff[i] == 1/6:
                if i >=1:
                    if tm_diff[i-1] != tm_diff[i+1]:
                        if i >=2:
                            if tm_diff[i-2] != tm_diff[i+2]:
                                if i >=200:
                                    if tm_diff[i-200] != tm_diff[i+200]:
                                        break

    return i  # Indicates no valid transition

def ten_to_five(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] < 10:
            if tm_diff[i] == 5:
                if i >=1:
                    if tm_diff[i-1] != tm_diff[i+1]:
                        if i >=2:
                            if tm_diff[i-2] != tm_diff[i+2]:
                                if i >=200:
                                    if tm_diff[i-200] != tm_diff[i+200]:
                                        break
    return i  # Indicates no valid transition

def ten_to_two(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] < 10:
            if tm_diff[i] == 2:
                if i >=1:
                    if tm_diff[i-1] != tm_diff[i+1]:
                        if i >=2:
                            if tm_diff[i-2] != tm_diff[i+2]:
                                if i >=200:
                                    if tm_diff[i-200] != tm_diff[i+200]:
                                        break
    return i  # Indicates no valid transition

def ten_to_thirty(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] > 10:
            if tm_diff[i] == 30:
                if i >=1:
                    if tm_diff[i-1] != tm_diff[i+1]:
                        if i >=2:
                            if tm_diff[i-2] != tm_diff[i+2]:
                                if i >=200:
                                    if tm_diff[i-200] != tm_diff[i+200]:
                                        break
    return i  # Indicates no valid transition

def ten_to_sixty(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] > 10:
            if tm_diff[i] == 60:
                if i >=1:
                    if tm_diff[i-1] != tm_diff[i+1]:
                        if i >=2:
                            if tm_diff[i-2] != tm_diff[i+2]:
                                if i >=200:
                                    if tm_diff[i-200] != tm_diff[i+200]:
                                        break
    return i  # Indicates no valid transition

def thirty_to_one(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] < 30:
            if tm_diff[i] == 1:
                if i >=1:
                    if tm_diff[i-1] != tm_diff[i+1]:
                        if i >=2:
                            if tm_diff[i-2] != tm_diff[i+2]:
                                if i >=200:
                                    if tm_diff[i-200] != tm_diff[i+200]:
                                        break
    return i  # Indicates no valid transition

def thirty_to_sixth(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] < 30:
            if tm_diff[i] == 1/6:
                if i >=1:
                    if tm_diff[i-1] != tm_diff[i+1]:
                        if i >=2:
                            if tm_diff[i-2] != tm_diff[i+2]:
                                if i >=200:
                                    if tm_diff[i-200] != tm_diff[i+200]:
                                        break

    return i  # Indicates no valid transition

def thirty_to_five(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] < 30:
            if tm_diff[i] == 5:
                if i >=1:
                    if tm_diff[i-1] != tm_diff[i+1]:
                        if i >=2:
                            if tm_diff[i-2] != tm_diff[i+2]:
                                if i >=200:
                                    if tm_diff[i-200] != tm_diff[i+200]:
                                        break
    return i  # Indicates no valid transition

def thirty_to_ten(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] < 30:
            if tm_diff[i] == 10:
                if i >=1:
                    if tm_diff[i-1] != tm_diff[i+1]:
                        if i >=2:
                            if tm_diff[i-2] != tm_diff[i+2]:
                                if i >=200:
                                    if tm_diff[i-200] != tm_diff[i+200]:
                                        break
    return i  # Indicates no valid transition

def thirty_to_two(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] < 30:
            if tm_diff[i] == 2:
                if i >=1:
                    if tm_diff[i-1] != tm_diff[i+1]:
                        if i >=2:
                            if tm_diff[i-2] != tm_diff[i+2]:
                                if i >=200:
                                    if tm_diff[i-200] != tm_diff[i+200]:
                                        break
    return i  # Indicates no valid transition

def thirty_to_sixty(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] > 30:
            if tm_diff[i] == 60:
                if i >=1:
                    if tm_diff[i-1] != tm_diff[i+1]:
                        if i >=2:
                            if tm_diff[i-2] != tm_diff[i+2]:
                                if i >=200:
                                    if tm_diff[i-200] != tm_diff[i+200]:
                                        break
    return i  # Indicates no valid transition

def sixty_to_one(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] < 60:
            if tm_diff[i] == 1:
                if i >=1:
                    if tm_diff[i-1] != tm_diff[i+1]:
                        if i >=2:
                            if tm_diff[i-2] != tm_diff[i+2]:
                                if i >=200:
                                    if tm_diff[i-200] != tm_diff[i+200]:
                                        break
    return i  # Indicates no valid transition

def sixty_to_sixth(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] < 60:
            if tm_diff[i] == 1/6:
                if i >=1:
                    if tm_diff[i-1] != tm_diff[i+1]:
                        if i >=2:
                            if tm_diff[i-2] != tm_diff[i+2]:
                                if i >=200:
                                    if tm_diff[i-200] != tm_diff[i+200]:
                                        break

    return i  # Indicates no valid transition

def sixty_to_five(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] < 60:
            if tm_diff[i] == 5:
                if i >=1:
                    if tm_diff[i-1] != tm_diff[i+1]:
                        if i >=2:
                            if tm_diff[i-2] != tm_diff[i+2]:
                                if i >=200:
                                    if tm_diff[i-200] != tm_diff[i+200]:
                                        break
    return i  # Indicates no valid transition

def sixty_to_two(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] < 60:
            if tm_diff[i] == 2:
                if i >=1:
                    if tm_diff[i-1] != tm_diff[i+1]:
                        if i >=2:
                            if tm_diff[i-2] != tm_diff[i+2]:
                                if i >=200:
                                    if tm_diff[i-200] != tm_diff[i+200]:
                                        break
    return i  # Indicates no valid transition

def sixty_to_ten(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] < 60:
            if tm_diff[i] == 10:
                if i >=1:
                    if tm_diff[i-1] != tm_diff[i+1]:
                        if i >=2:
                            if tm_diff[i-2] != tm_diff[i+2]:
                                if i >=200:
                                    if tm_diff[i-200] != tm_diff[i+200]:
                                        break
    return i  # Indicates no valid transition

def sixty_to_thirty(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] < 60:
            if tm_diff[i] == 30:
                if i >=1:
                    if tm_diff[i-1] != tm_diff[i+1]:
                        if i >=2:
                            if tm_diff[i-2] != tm_diff[i+2]:
                                if i >=200:
                                    if tm_diff[i-200] != tm_diff[i+200]:
                                        break
    return i  # Indicates no valid transition

def two_to_one(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] < 2:
            if tm_diff[i] == 1:
                if i >=1:
                    if tm_diff[i-1] != tm_diff[i+1]:
                        if i >=2:
                            if tm_diff[i-2] != tm_diff[i+2]:
                                if i >=200:
                                    if tm_diff[i-200] != tm_diff[i+200]:
                                        break
    return i  # Indicates no valid transition

def two_to_five(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] > 2:
            if tm_diff[i] == 5:
                if i >=1:
                    if tm_diff[i-1] != tm_diff[i+1]:
                        if i >=2:
                            if tm_diff[i-2] != tm_diff[i+2]:
                                if i >=200:
                                    if tm_diff[i-200] != tm_diff[i+200]:
                                        break
    return i  # Indicates no valid transition

def two_to_ten(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] > 2:
            if tm_diff[i] == 10:
                if i >=1:
                    if tm_diff[i-1] != tm_diff[i+1]:
                        if i >=2:
                            if tm_diff[i-2] != tm_diff[i+2]:
                                if i >=200:
                                    if tm_diff[i-200] != tm_diff[i+200]:
                                        break
    return i  # Indicates no valid transition

def two_to_thirty(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] > 2:
            if tm_diff[i] == 30:
                if i >=1:
                    if tm_diff[i-1] != tm_diff[i+1]:
                        if i >=2:
                            if tm_diff[i-2] != tm_diff[i+2]:
                                if i >=200:
                                    if tm_diff[i-200] != tm_diff[i+200]:
                                        break
    return i  # Indicates no valid transition

def two_to_sixty(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] > 2:
            if tm_diff[i] == 60:
                if i >=1:
                    if tm_diff[i-1] != tm_diff[i+1]:
                        if i >=2:
                            if tm_diff[i-2] != tm_diff[i+2]:
                                if i >=200:
                                    if tm_diff[i-200] != tm_diff[i+200]:
                                        break
    return i  # Indicates no valid transition

def two_to_sixth(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] < 2:
            if tm_diff[i] == 1/6:
                if i >=1:
                    if tm_diff[i-1] != tm_diff[i+1]:
                        if i >=2:
                            if tm_diff[i-2] != tm_diff[i+2]:
                                if i >=200:
                                    if tm_diff[i-200] != tm_diff[i+200]:
                                        break

    return i  # Indicates no valid transition


def half_to_one(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] > 0.5:
            if tm_diff[i] == 1:
                if i >=1:
                    if tm_diff[i-1] != tm_diff[i+1]:
                        if i >=2:
                            if tm_diff[i-2] != tm_diff[i+2]:
                                if i >=200:
                                    if tm_diff[i-200] != tm_diff[i+200]:
                                        break
    return i  # Indicates no valid transition

def half_to_five(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] > 0.5:
            if tm_diff[i] == 5:
                if i >=1:
                    if tm_diff[i-1] != tm_diff[i+1]:
                        if i >=2:
                            if tm_diff[i-2] != tm_diff[i+2]:
                                if i >=200:
                                    if tm_diff[i-200] != tm_diff[i+200]:
                                        break
    return i  # Indicates no valid transition

def half_to_ten(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] > 0.5:
            if tm_diff[i] == 10:
                if i >=1:
                    if tm_diff[i-1] != tm_diff[i+1]:
                        if i >=2:
                            if tm_diff[i-2] != tm_diff[i+2]:
                                if i >=200:
                                    if tm_diff[i-200] != tm_diff[i+200]:
                                        break
    return i  # Indicates no valid transition

def half_to_thirty(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] > 0.5:
            if tm_diff[i] == 30:
                if i >=1:
                    if tm_diff[i-1] != tm_diff[i+1]:
                        if i >=2:
                            if tm_diff[i-2] != tm_diff[i+2]:
                                if i >=200:
                                    if tm_diff[i-200] != tm_diff[i+200]:
                                        break
    return i  # Indicates no valid transition

def half_to_sixty(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] > 0.5:
            if tm_diff[i] == 60:
                if i >=1:
                    if tm_diff[i-1] != tm_diff[i+1]:
                        if i >=2:
                            if tm_diff[i-2] != tm_diff[i+2]:
                                if i >=200:
                                    if tm_diff[i-200] != tm_diff[i+200]:
                                        break
    return i  # Indicates no valid transition

def sixty_to_half(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] < 60:
            if tm_diff[i] == 0.5:
                if i >=1:
                    if tm_diff[i-1] != tm_diff[i+1]:
                        if i >=2:
                            if tm_diff[i-2] != tm_diff[i+2]:
                                if i >=200:
                                    if tm_diff[i-200] != tm_diff[i+200]:
                                        break
    return i  # Indicates no valid transition

def sixty_to_one_sixtieth(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] < 60:
            if tm_diff[i] == 1/60:
                if i >=1:
                    if tm_diff[i-1] != tm_diff[i+1]:
                        if i >=2:
                            if tm_diff[i-2] != tm_diff[i+2]:
                                if i >=200:
                                    if tm_diff[i-200] != tm_diff[i+200]:
                                        break
    return i  # Indicates no valid transition

def one_sixtieth_to_half(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] > 1/60:
            if tm_diff[i] == 0.5:
                if i >=1:
                    if tm_diff[i-1] != tm_diff[i+1]:
                        if i >=2:
                            if tm_diff[i-2] != tm_diff[i+2]:
                                if i >=200:
                                    if tm_diff[i-200] != tm_diff[i+200]:
                                        break
    return i  # Indicates no valid transition

def one_sixtieth_to_one(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] > 1/60:
            if tm_diff[i] == 1:
                if i >=1:
                    if tm_diff[i-1] != tm_diff[i+1]:
                        if i >=2:
                            if tm_diff[i-2] != tm_diff[i+2]:
                                if i >=200:
                                    if tm_diff[i-200] != tm_diff[i+200]:
                                        break
    return i  # Indicates no valid transition


def sixth_to_one(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] > 1/6:
            if tm_diff[i] == 1:
                if i >=1:
                    if tm_diff[i-1] != tm_diff[i+1]:
                        if i >=2:
                            if tm_diff[i-2] != tm_diff[i+2]:
                                if i >=200:
                                    if tm_diff[i-200] != tm_diff[i+200]:
                                        break
    return i  # Indicates no valid transition

def sixth_to_five(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] > 1/6:
            if tm_diff[i] == 5:
                if i >=1:
                    if tm_diff[i-1] != tm_diff[i+1]:
                        if i >=2:
                            if tm_diff[i-2] != tm_diff[i+2]:
                                if i >=200:
                                    if tm_diff[i-200] != tm_diff[i+200]:
                                        break
    return i  # Indicates no valid transition

def sixth_to_ten(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] > 1/6:
            if tm_diff[i] == 10:
                if i >=1:
                    if tm_diff[i-1] != tm_diff[i+1]:
                        if i >=2:
                            if tm_diff[i-2] != tm_diff[i+2]:
                                if i >=200:
                                    if tm_diff[i-200] != tm_diff[i+200]:
                                        break
    return i  # Indicates no valid transition

def sixth_to_thirty(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] > 1/6:
            if tm_diff[i] == 30:
                if i >=1:
                    if tm_diff[i-1] != tm_diff[i+1]:
                        if i >=2:
                            if tm_diff[i-2] != tm_diff[i+2]:
                                if i >=200:
                                    if tm_diff[i-200] != tm_diff[i+200]:
                                        break
    return i  # Indicates no valid transition

def sixth_to_sixty(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] > 1/6:
            if tm_diff[i] == 60:
                if i >=1:
                    if tm_diff[i-1] != tm_diff[i+1]:
                        if i >=2:
                            if tm_diff[i-2] != tm_diff[i+2]:
                                if i >=200:
                                    if tm_diff[i-200] != tm_diff[i+200]:
                                        break
    return i  # Indicates no valid transition
