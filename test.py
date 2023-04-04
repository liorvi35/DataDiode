import hashlib

# Define the file paths
input_file_path = 'file'
output_file_path = 'hashed_file'

# Open the input file in binary mode and read it in chunks to avoid loading large files into memory
with open(input_file_path, 'rb') as input_file:
    chunk = input_file.read(4096)

    # Initialize the hash object with the MD5 algorithm
    md5_hash = hashlib.md5()

    # Loop through the file contents and update the hash object with each chunk
    while chunk:
        md5_hash.update(chunk)
        chunk = input_file.read(4096)


# Open the output file in write mode and write the hashed data to it
with open(output_file_path, 'w') as output_file:
    output_file.write(str(md5_hash))
