"""
Table Extraction Module

This module provides functionality for extracting tables from images, detecting table structures, and performing Optical Character Recognition (OCR) to extract text data from the tables. It includes a class `TableExtraction` that encapsulates methods for preprocessing images, detecting tables, cropping tables, extracting table structure, and performing OCR on table cells. Additionally, it defines a helper class `MaxResize` for resizing images while maintaining their aspect ratio.

Classes:
    - TableExtraction: A class for extracting tables from images and performing OCR.
    - MaxResize: A callable class to resize images while maintaining aspect ratio.

Example:
    >>> from table_extraction import TableExtraction
    >>> extractor = TableExtraction(image_dir='input_images', output_dir='output_tables')
    >>> extractor.get_table_data()

"""

# @https://github.com/microsoft/table-transformer
from transformers import AutoModelForObjectDetection
from transformers import TableTransformerForObjectDetection
import easyocr
import torch
from tqdm.auto import tqdm
import numpy as np

# Image operations
from PIL import Image
from torchvision import transforms

import csv
import json

import os

device = "cuda" if torch.cuda.is_available() else "cpu"


class MaxResize(object):
    """
    A callable class to resize an image while maintaining its aspect ratio.

    Args:
        max_size (int): The maximum size (width or height) to which the image will be resized.

    Methods:
        __call__(image):
            Resizes the input image while maintaining its aspect ratio.

    Example:
        >>> from PIL import Image
        >>> resize_transform = MaxResize(max_size=800)
        >>> image = Image.open("example.jpg")
        >>> resized_image = resize_transform(image)
    """
    def __init__(self, max_size=800):
        """
        Initializes the MaxResize object with the specified maximum size.

        Args:
            max_size (int): The maximum size (width or height) to which the image will be resized.
        """
        self.max_size = max_size

    def __call__(self, image):
        """
        Resizes the input image while maintaining its aspect ratio.

        Args:
            image (PIL.Image.Image): The input image to be resized.

        Returns:
            PIL.Image.Image: The resized image.

        Example:
            >>> from PIL import Image
            >>> resize_transform = MaxResize(max_size=800)
            >>> image = Image.open("example.jpg")
            >>> resized_image = resize_transform(image)
        """
        width, height = image.size
        current_max_size = max(width, height)
        scale = self.max_size / current_max_size
        resized_image = image.resize((int(round(scale*width)), int(round(scale*height))))

        return resized_image


class TableExtraction:
    """
    A class for extracting tables from images and performing Optical Character Recognition (OCR) on the extracted tables.

    Attributes:
        image_dir (str): The directory containing input images.
        output_dir (str): The directory where output files will be saved.

    Methods:
        __init__(image_dir, output_dir):
            Initializes the object with the specified image directory and output directory,
            and loads the necessary models for table detection, table structure recognition,
            and text extraction.

        __load_image__(file_path):
            Load an image from the specified file path and convert it to RGB format.

        __save_table_data__(data, file_name):
            Save table data to a JSON file.

        __preprocess_image__(image):
            Preprocesses the input image for detection.

        __detect_table_rescale_bboxes__(out_bbox, size):
            Rescales bounding boxes based on image size.

        __get_image_object__(outputs, img_size, id2label):
            Extracts objects detected in the image along with their labels, scores, and bounding boxes.

        __detect_table__(image, image_pixel_values):
            Detects tables in the given image.

        __crop_table__(img, objects):
            Crops detected tables from the input image.

        __get_table_structure__(tab_image):
            Extracts the structure of the table from the given table image.

        __get_cell_by_row__(table_data):
            Organizes table cells by row and column.

        __ocr_table_data__(table_cells, table_img):
            Extracts text data from the table cells using Optical Character Recognition (OCR).

        get_table_data():
            Process all images in the specified directory to extract table data.
    """

    def __init__(self, image_dir: str, output_dir: str):
        """
        Initializes the object with the specified image directory and output directory,
        and loads the necessary models for table detection, table structure recognition,
        and text extraction.

        Args:
            image_dir (str): The directory containing input images.
            output_dir (str): The directory where output files will be saved.
        """
        self.image_dir = image_dir

        self.output_dir = output_dir

        # Load table detection model
        self.table_detection_model = AutoModelForObjectDetection.from_pretrained(
            "microsoft/table-transformer-detection",
            revision="no_timm")

        # Load table structure recognition model
        self.table_structure_model = TableTransformerForObjectDetection.from_pretrained(
            "microsoft/table-structure-recognition-v1.1-all")

        # Initialize text reader for OCR
        self.table_reader = easyocr.Reader(['en'])

    @staticmethod
    def __load_image__(file_path):
        """
        Load an image from the specified file path and convert it to RGB format.

        Args:
            file_path (str): The path to the image file.

        Returns:
            PIL.Image.Image: The loaded image in RGB format.

        Example:
            >>> image_path = "path/to/image.jpg"
            >>> loaded_image = __load_image__(image_path)
        """

        image = Image.open(file_path).convert("RGB")
        return image

    @staticmethod
    def __save_table_data__(data: dict, file_name: str):
        """
        Save table data to a JSON file.

        Args:
            data (dict): The table data to be saved.
            file_name (str): The name of the output JSON file (without extension).

        Example:
            >>> table_data = {"header": ["Name", "Age", "Gender"], "rows": [["Alice", 25, "Female"], ["Bob", 30, "Male"]]}
            >>> file_name = "output_table"
            >>> __save_table_data__(table_data, file_name)
        """
        with open(f"{file_name}.json", 'w+', encoding='utf-8') as jsonf:
            jsonf.write(json.dumps(data, indent=4))

    @staticmethod
    def __preprocess_image__(image):
        """
        Preprocesses the input image for detection.

        Args:
            image (PIL.Image.Image): The input image to be preprocessed.

        Returns:
            torch.Tensor: The preprocessed image tensor suitable for detection.

        Example:
            >>> from PIL import Image
            >>> import torch
            >>> image = Image.open("example.jpg")
            >>> preprocessed_image = __preprocess_image__(image)
        """
        # transform image for detection
        detection_transform = transforms.Compose([
            MaxResize(800),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])

        detection_transform_pixel_values = detection_transform(image).unsqueeze(0)

        detection_transform_pixel_values = detection_transform_pixel_values.to(device)

        return detection_transform_pixel_values

    @staticmethod
    def __detect_table_rescale_bboxes__(out_bbox, size):
        """
        Rescales bounding boxes based on image size.

        Args:
            out_bbox (torch.Tensor): Tensor containing the bounding boxes in (x_c, y_c, w, h) format.
            size (tuple): A tuple containing the width and height of the image.

        Returns:
            torch.Tensor: Tensor containing rescaled bounding boxes.

        Example:
            >>> out_bbox = torch.tensor([[0.3, 0.4, 0.2, 0.3]])
            >>> size = (640, 480)
            >>> rescaled_bbox = __detect_table_rescale_bboxes__(out_bbox, size)
        """
        img_w, img_h = size
        x_c, y_c, w, h = out_bbox.unbind(-1)
        b = [(x_c - 0.5 * w), (y_c - 0.5 * h), (x_c + 0.5 * w), (y_c + 0.5 * h)]
        b = torch.stack(b, dim=1)
        b = b * torch.tensor([img_w, img_h, img_w, img_h], dtype=torch.float32)
        return b


    def __get_image_object__(self, outputs, img_size, id2label):
        """
        Extracts objects detected in the image along with their labels, scores, and bounding boxes.

        Args:
            outputs (dict): Model outputs containing predicted labels, scores, and bounding boxes.
            img_size (tuple): A tuple containing the width and height of the image.
            id2label (dict): A dictionary mapping class IDs to their corresponding labels.

        Returns:
            list: A list of dictionaries, each containing information about a detected object,
                  including label, score, and bounding box coordinates.

        Example:
            >>> outputs = {'logits': ..., 'pred_boxes': ..., ...}  # Model outputs
            >>> img_size = (640, 480)
            >>> id2label = {0: 'person', 1: 'car', ...}  # Mapping of class IDs to labels
            >>> detected_objects = __get_image_object__(outputs, img_size, id2label)
        """
        m = outputs.logits.softmax(-1).max(-1)
        pred_labels = list(m.indices.detach().cpu().numpy())[0]
        pred_scores = list(m.values.detach().cpu().numpy())[0]
        pred_bboxes = outputs['pred_boxes'].detach().cpu()[0]
        pred_bboxes = [elem.tolist() for elem in self.__detect_table_rescale_bboxes__(pred_bboxes, img_size)]

        objects = []
        for label, score, bbox in zip(pred_labels, pred_scores, pred_bboxes):
            class_label = id2label[int(label)]
            if not class_label == 'no object':
                objects.append({'label': class_label, 'score': float(score),
                                'bbox': [float(elem) for elem in bbox]})
        return objects

    def __detect_table__(self, image, image_pixel_values):
        """
        Detects tables in the given image.

        Args:
            image (PIL.Image.Image): The original image.
            image_pixel_values (torch.Tensor): Preprocessed image tensor for detection.

        Returns:
            list: A list of dictionaries, each containing information about a detected table object.
                Each dictionary has keys 'label' (class label), 'score' (detection score), and 'bbox' (bounding box).

        Example:
            >>> from PIL import Image
            >>> import torch
            >>> image = Image.open("example.jpg")
            >>> image_pixel_values = __preprocess_image__(image)
            >>> detected_tables = __detect_table__(image, image_pixel_values)
        """

        with torch.no_grad():
            outputs = self.table_detection_model(image_pixel_values)

        id2label = self.table_detection_model.config.id2label
        id2label[len(self.table_detection_model.config.id2label)] = "no object"

        image_object = self.__get_image_object__(outputs, image.size, id2label)

        return image_object

    def __crop_table__(self, img, objects):
        """
        Crops detected tables from the input image.

        Args:
            img (PIL.Image.Image): The original image containing tables.
            objects (list): A list of dictionaries containing information about detected table objects.

        Returns:
            list: A list of dictionaries, each containing a cropped table image and its associated tokens.

        Example:
            >>> from PIL import Image
            >>> image = Image.open("example.jpg")
            >>> detected_tables = __detect_table__(image)
            >>> cropped_tables = __crop_table__(image, detected_tables)
        """
        tokens = []
        class_thresholds = {
            "table": 0.5,
            "table rotated": 0.5,
            "no object": 10
        }
        padding = 25

        table_crops = []
        for obj in objects:
            if obj['score'] < class_thresholds[obj['label']]:
                continue

            cropped_table = {}

            bbox = obj['bbox']
            bbox = [bbox[0] - padding, bbox[1] - padding, bbox[2] + padding, bbox[3] + padding]

            cropped_img = img.crop(bbox)

            table_tokens = [token for token in tokens if iob(token['bbox'], bbox) >= 0.5]
            for token in table_tokens:
                token['bbox'] = [token['bbox'][0] - bbox[0],
                                 token['bbox'][1] - bbox[1],
                                 token['bbox'][2] - bbox[0],
                                 token['bbox'][3] - bbox[1]]

            # If table is predicted to be rotated, rotate cropped image and tokens/words:
            if obj['label'] == 'table rotated':
                cropped_img = cropped_img.rotate(270, expand=True)
                for token in table_tokens:
                    bbox = token['bbox']
                    bbox = [cropped_img.size[0] - bbox[3] - 1,
                            bbox[0],
                            cropped_img.size[0] - bbox[1] - 1,
                            bbox[2]]
                    token['bbox'] = bbox

            cropped_table['image'] = cropped_img
            cropped_table['tokens'] = table_tokens

            table_crops.append(cropped_table)

        return table_crops

    def __get_table_structure__(self, tab_image):
        """
        Extracts the structure of the table from the given table image.

        Args:
            tab_image (PIL.Image.Image): The image of the table.

        Returns:
            list: A list of dictionaries, each containing information about a detected table cell.
                Each dictionary has keys 'label' (cell label), 'score' (detection score), and 'bbox' (bounding box).

        Example:
            >>> from PIL import Image
            >>> import torch
            >>> tab_image = Image.open("table.jpg")
            >>> table_structure = __get_table_structure__(tab_image)
        """
        self.table_structure_model.to(device)

        structure_transform = transforms.Compose([
            MaxResize(800),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])

        structure_transform_pixel_values = structure_transform(tab_image).unsqueeze(0)

        structure_transform_pixel_values = structure_transform_pixel_values.to(device)

        structure_id2label = self.table_structure_model.config.id2label
        structure_id2label[len(structure_id2label)] = "no object"

        with torch.no_grad():
            outputs = self.table_structure_model(structure_transform_pixel_values)

        cells = self.__get_image_object__(outputs, tab_image.size, structure_id2label)

        return cells

    def __get_cell_by_row__(self, table_data):
        """
        Organizes table cells by row and column.

        Args:
            table_data (list): A list of dictionaries containing information about detected table objects.

        Returns:
            list: A list of dictionaries, each containing information about a row of cells in the table.
                Each dictionary has keys 'row' (row bounding box), 'cells' (list of cell dictionaries),
                and 'cell_count' (number of cells in the row).

        Example:
            >>> table_data = [{'label': 'table row', 'bbox': [100, 200, 300, 220]}, {'label': 'table column', 'bbox': [50, 200, 150, 240]}]
            >>> cell_by_row = __get_cell_by_row__(table_data)
        """
        # Extract rows and columns
        rows = [entry for entry in table_data if entry['label'] == 'table row']
        columns = [entry for entry in table_data if entry['label'] == 'table column']

        # Sort rows and columns by their Y and X coordinates, respectively
        rows.sort(key=lambda x: x['bbox'][1])
        columns.sort(key=lambda x: x['bbox'][0])

        # Function to find cell coordinates
        def find_cell_coordinates(row, column):
            """
            Finds the bounding box coordinates of a cell based on its row and column bounding boxes.

            Args:
                row (dict): A dictionary containing information about the row bounding box.
                column (dict): A dictionary containing information about the column bounding box.

            Returns:
                list: A list containing the bounding box coordinates of the cell in the format [x_min, y_min, x_max, y_max].

            Example:
                >>> row_bbox = {'bbox': [100, 200, 300, 220]}
                >>> column_bbox = {'bbox': [50, 200, 150, 240]}
                >>> cell_bbox = find_cell_coordinates(row_bbox, column_bbox)
            """
            cell_bbox = [column['bbox'][0], row['bbox'][1], column['bbox'][2], row['bbox'][3]]
            return cell_bbox

        # Generate cell coordinates and count cells in each row
        cell_coordinates = []

        for row in rows:
            row_cells = []
            for column in columns:
                cell_bbox = find_cell_coordinates(row, column)
                row_cells.append({'column': column['bbox'], 'cell': cell_bbox})

            # Sort cells in the row by X coordinate
            row_cells.sort(key=lambda x: x['column'][0])

            # Append row information to cell_coordinates
            cell_coordinates.append({'row': row['bbox'], 'cells': row_cells, 'cell_count': len(row_cells)})

        # Sort rows from top to bottom
        cell_coordinates.sort(key=lambda x: x['row'][1])

        return cell_coordinates

    def __ocr_table_data__(self, table_cells, table_img):
        """
        Extracts text data from the table cells using Optical Character Recognition (OCR).

        Args:
            table_cells (list): A list of dictionaries containing information about table cells.
            table_img (PIL.Image.Image): The image of the table.

        Returns:
            dict: A dictionary containing the OCR-extracted text data from the table cells.

        Example:
            >>> table_data = [{'label': 'table row', 'bbox': [100, 200, 300, 220]}, {'label': 'table column', 'bbox': [50, 200, 150, 240]}]
            >>> table_image = Image.open("table.jpg")
            >>> ocr_data = __ocr_table_data__(table_data, table_image)
        """
        cell_coordinates = self.__get_cell_by_row__(table_cells)
        # let's OCR row by row
        data = dict()
        max_num_columns = 0
        for idx, row in enumerate(tqdm(cell_coordinates)):
            row_text = []
            for cell in row["cells"]:
                # crop cell out of image
                cell_image = np.array(table_img.crop(cell["cell"]))
                # apply OCR
                result = self.table_reader.readtext(np.array(cell_image))
                if len(result) > 0:
                    # print([x[1] for x in list(result)])
                    text = " ".join([x[1] for x in result])
                    row_text.append(text)

            if len(row_text) > max_num_columns:
                max_num_columns = len(row_text)

            data[idx] = row_text

        print("Max number of columns:", max_num_columns)

        # pad rows which don't have max_num_columns elements
        # to make sure all rows have the same number of columns
        for row, row_data in data.copy().items():
            if len(row_data) != max_num_columns:
                row_data = row_data + ["" for _ in range(max_num_columns - len(row_data))]
            data[row] = row_data

        # Convert to desired format (each row with the table header)
        converted_json = {}
        for key, values in data.items():
            inter_json = {}
            if key:
                for ind, value in enumerate(values):
                    inter_json[data[0][ind]] = value
                converted_json[key] = inter_json

        return converted_json


    def get_table_data(self):
        """
        Process all images in the specified directory to extract table data.

        Returns:
            None

        Example:
            >>> instance = TableExtraction(image_dir='input_dir', output_dir='output_dir')
            >>> instance.get_table_data()
        """
        for imgfile in os.listdir(self.image_dir):

            if not (imgfile.lower().endswith("png") or imgfile.lower().endswith("jpg")):
                continue
            else:
                image_path = os.path.join(self.image_dir, imgfile)

            # load image
            image = self.__load_image__(image_path)

            # preprocessing image for detection -> gives image object (scaled)
            preproceesed_image_pxl_val = self.__preprocess_image__(image)

            # detect table in image -> gives table bounding box
            detected_table_obj = self.__detect_table__(image, preproceesed_image_pxl_val)

            # crop table from image -> table object (convert to image)
            table_crops = self.__crop_table__(image, detected_table_obj)

            # get table structure -> gives cells boundaries
            cropped_tables = [self.__get_table_structure__(table['image'].convert("RGB")) for table in table_crops]

            cropped_tables_data = [
                self.__ocr_table_data__(cropped_table_str, cropped_table_img['image'].convert("RGB")) for cropped_table_str, cropped_table_img in zip(cropped_tables, table_crops)
            ]

            # save data (json)
            for ind,tab_data in enumerate(cropped_tables_data):
                img_file_path = f"{self.output_dir}\\{imgfile.lower().replace('.', '_')}"

                if not os.path.exists(img_file_path):
                    os.mkdir(img_file_path)

                self.__save_table_data__(tab_data, os.path.join(img_file_path, f"image_{ind}"))

if __name__ == "__main__":

    base_path= r"C:\Users\mehul\Documents\Projects - GIT\Agents\Decompose KG from Code\pythonProject\CoderAssistants"

    TblObj = TableExtraction(image_dir= os.path.join(base_path, "sample_image"),
                             output_dir= os.path.join(base_path, "sample_images_output"))
    TblObj.get_table_data()
