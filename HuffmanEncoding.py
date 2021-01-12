# Student Name : Snehal Vijay Kulkarni
# Student ID: 801147615

import heapq
import os
import numpy as np
from PIL import Image


class HuffmanEncoding:
    def __init__(self, input_path):
        self.input_path = input_path
        self.heap = []
        self.codes = {}
        self.rev_mapping = {}

    class Node:
        def __init__(self, node_item, frequency):
            self.node_item = node_item
            self.frequency = frequency
            self.left = None
            self.right = None

        def __eq__(self, other):
            if other == None:
                return False
            if (not isinstance(other, Node)):
                return False
            return self.frequency == other.frequency

        def __lt__(self, other):
            return self.frequency < other.frequency

    # Method to compress the image.
    def freq_dictionary(self, im_pixels):
        frequency = {}
        for pixel in im_pixels:
            if not pixel in frequency:
                frequency[pixel] = 0
            frequency[pixel] += 1
        return frequency

    def create_heap(self, frequency):
        for keyItem in frequency:
            node = self.Node(keyItem, frequency[keyItem])
            heapq.heappush(self.heap, node)

    def combine_nodes(self):
        while (len(self.heap) > 1):
            node_left = heapq.heappop(self.heap)
            node_right = heapq.heappop(self.heap)

            combined = self.Node(None, node_left.frequency + node_right.frequency)
            combined.left = node_left
            combined.right = node_right

            heapq.heappush(self.heap, combined)

    def create_codes(self):
        root_node = heapq.heappop(self.heap)
        this_code = ""
        self.setup_codes(root_node, this_code)

    def setup_codes(self, root_node, this_code):
        if (root_node == None):
            return

        if (root_node.node_item != None):
            self.codes[root_node.node_item] = this_code
            self.rev_mapping[this_code] = root_node.node_item
            return

        self.setup_codes(root_node.left, this_code + "0")
        self.setup_codes(root_node.right, this_code + "1")

    def get_encoded_values(self, im_pixels):
        encoded_pixels = ""
        for pixel in im_pixels:
            encoded_pixels += self.codes[pixel]
            # print(f'{pixel}:{encoded_pixels}\n')
            # f = open("test.txt", "a")
            # f.write(f'{pixel}:{encoded_pixels}\n')
            # f.close()

        return encoded_pixels

    def add_extra_bits(self, encoded_pixels):
        extra_bits = 8 - len(encoded_pixels) % 8
        for i in range(extra_bits):
            encoded_pixels += "0"

        encoded_pixels = "{0:08b}".format(extra_bits) + encoded_pixels
        return encoded_pixels

    def get_byte_array(self, encoded_pixels):
        if (len(encoded_pixels) % 8 != 0):
            print("Encoded pixels have bits that are not divisible by 8.")
            exit(0)

        byte_array = bytearray()
        for i in range(0, len(encoded_pixels), 8):
            byte = encoded_pixels[i:i + 8]
            byte_array.append(int(byte, 2))
        return byte_array

    # Compression of the image.
    def im_compression(self):
        file_name, file_extension = os.path.splitext(self.input_path)
        output_file = file_name + ".bin"

        with open(self.input_path, 'r+') as file, open(output_file, 'wb') as output:
            pixel = file.read()
            pixel = pixel.rstrip()

            frequency = self.freq_dictionary(pixel)
            self.create_heap(frequency)
            self.combine_nodes()
            self.create_codes()

            encoded_pixel = self.get_encoded_values(pixel)
            extra_bit_encoded_pixel = self.add_extra_bits(encoded_pixel)

            byte_array = self.get_byte_array(extra_bit_encoded_pixel)
            output.write(bytes(byte_array))

        print("The input image is compressed successfully.")
        return output_file

    # Method to decompress the image.
    def remove_extra_bits(self, extra_bits_encoded_pixel):
        extra_bits_info = extra_bits_encoded_pixel[:8]
        extra_bits = int(extra_bits_info, 2)

        extra_bits_encoded_pixel = extra_bits_encoded_pixel[8:]
        encoded_pixel = extra_bits_encoded_pixel[:-1 * extra_bits]

        return encoded_pixel

    def decode_pixels(self, encoded_pixels):
        this_code = ""
        decoded_pixel = ""

        for pixel in encoded_pixels:
            this_code += pixel
            if (this_code in self.rev_mapping):
                bit = self.rev_mapping[this_code]
                decoded_pixel += bit
                this_code = ""

        return decoded_pixel

    # Decompression of the image.
    def im_decompression(self, input_file):
        file_name, file_extension = os.path.splitext(self.input_path)
        output_file = file_name + "_decompressed" + ".txt"

        with open(input_file, 'rb') as file, open(output_file, 'w') as output:
            bit_str = ""

            each_byte = file.read(1)
            while (len(each_byte) > 0):
                each_byte = ord(each_byte)
                bits = bin(each_byte)[2:].rjust(8, '0')
                bit_str += bits
                each_byte = file.read(1)

            encoded_pixes = self.remove_extra_bits(bit_str)

            decompressed_pixels = self.decode_pixels(encoded_pixes)

            output.write(decompressed_pixels)

        print("The output image is decompressed successfully.")
        return output_file


def main():
    # Read a color input image.
    input_color_image = Image.open('input_color_image.jpg')

    # Convert it into grayscale image.
    grey_image = np.mean(input_color_image, axis=2)
    grey_image = grey_image.astype("uint8")

    # Save the grayscale image.
    input_gray_image = Image.fromarray(grey_image)
    input_gray_image.save('input_grey_image.jpg')

    # Generate .txt file of the pixel of grey scale input image.
    image_pixels = list(input_gray_image.getdata())
    width, height = input_gray_image.size
    image_pixels = [image_pixels[i * width:(i + 1) * width] for i in range(height)]
    np.savetxt("input_image_pixels.txt", image_pixels, fmt='%d', delimiter=" ")

    input_file = "input_image_pixels.txt"

    # Compress the input grayscale image.
    huffman = HuffmanEncoding(input_file)
    compressed_file = huffman.im_compression()
    print("Compressed file is: " + compressed_file)

    # Decompress the compressed image.
    decompressed_file = huffman.im_decompression(compressed_file)
    print("Decompressed file is: " + decompressed_file)

    output_image_pixels = []
    for row in image_pixels:
        for tuples in row:
            output_image_pixels.append(tuples)

    output_gray_image = Image.new(input_gray_image.mode, input_gray_image.size)
    output_gray_image.putdata(output_image_pixels)
    input_gray_image.save('output_grey_image.jpg')

    if input_gray_image.size == output_gray_image.size:
        print("Both, compressed image and decompressed image have the same size.")


main()
