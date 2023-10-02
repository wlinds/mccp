import cv2
import numpy as np
import random
import os
import logging

logging.basicConfig(filename='./data_augmentation.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class DataAugmenter:
    def __init__(self, input_dir, output_dir, num_augmented_images=3, output_image_size=(1024, 1024), create_dir=True, logging_enabled=True):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.num_augmented_images = num_augmented_images
        self.output_image_size = output_image_size
        self.create_dir = create_dir

        self.resolution = None # Pixel res for images passing through augmenter

        self.logging_enabled = logging_enabled

        if create_dir and not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        if logging_enabled:
            self.logger = logging.basicConfig(filename='./data_augmentation.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    # Augment from dir -> dir
    def augment_images(self, selected_images=None):
        image_files = selected_images if selected_images else os.listdir(self.input_dir) # TODO might cause permission issues if called with selected_images

        for img_file in image_files:

            logging.info(f"Processing {img_file}")
            img_path = os.path.join(self.input_dir, img_file)
            img = cv2.imread(img_path)

            if self.resolution is None:
                self.resolution = img.shape[:2]

            for i in range(self.num_augmented_images):
                if self.logging_enabled:
                    logging.info(f"Augmenting {img_file}. Iteration: {i}")


                # Simulate white balance and exposure (RGB channel manipulation)
                white_balanced_img, wb_factor = self.random_white_balance(img)
                if self.logging_enabled:
                    logging.info(f"Iter. {i}: {img_file} - WB values: {wb_factor}")

                exposed_img, exposed_factor = self.random_exposure(white_balanced_img)
                if self.logging_enabled:
                    logging.info(f"Iter. {i}: {img_file} - Exposure {exposed_factor}")

                # Simulate orientation (rotation_matrix)
                rotated_img, rot_angle = self.random_rotation(exposed_img)
                if self.logging_enabled:
                    logging.info(f"Iter. {i}: {img_file} - {rot_angle=}")

                # Simulate mirror
                mirrored_img, mirrored = self.random_mirror(rotated_img)
                if self.logging_enabled:
                    logging.info(f"Iter. {i}: {img_file} - {mirrored=}")

                # Simulate focal length / warp perspective + focus (gaussian blur)
                distorted_img = self.random_lens_distortion(mirrored_img, img_file)
                if self.logging_enabled:
                    logging.info(f"Iter. {i}: {img_file} - No adjustments made.")

                blurred_img, blur_radius = self.random_gaussian_blur(distorted_img)
                if self.logging_enabled:
                    logging.info(f"Iter. {i}: {img_file} - {blur_radius=}")


                # Simulate scratches (texture overlay) # TODO
                texture_overlayed_img = self.random_texture_overlay(blurred_img)


                # Perform random crop
                cropped_img, crop_factor = self.random_crop(texture_overlayed_img)
                if self.logging_enabled:
                    logging.info(f"Iter {i}: {img_file}_{i} - {crop_factor=}.")




                output_file = os.path.splitext(img_file)[0] + f"_aug_{i}.png"
                
                output_path = os.path.join(self.output_dir, output_file)
                cv2.imwrite(output_path, texture_overlayed_img)

                if self.logging_enabled:
                    logging.info(f"Finished augmentation of {img_file} as {output_file}")
                    print((f"Finished augmentation of {img_file} as {output_file}"))
                

        print("Data augmentation complete.")

    def random_crop(self, img):
        # TODO
        x1 = random.randint(0, img.shape[1] - self.output_image_size[1]) + random.randint(-4,5)
        y1 = random.randint(0, img.shape[0] - self.output_image_size[0]) + random.randint(-4,5)
        return img[y1:y1 + self.output_image_size[0], x1:x1 + self.output_image_size[1]], [x1,y1]

    def random_white_balance(self, img):
        # Simulate white balance adjustment (rgb) TODO: Set actual kelvin values (?)
        # Split image into color channels, apply random scaling, return remerged img
        b, g, r = cv2.split(img)

        scale_r = random.uniform(0.9, 1.1)
        scale_g = random.uniform(0.9, 1.1)
        scale_b = random.uniform(0.9, 1.1)

        factor = [scale_r, scale_g, scale_b]

        balanced_r = cv2.convertScaleAbs(r, alpha=scale_r)
        balanced_g = cv2.convertScaleAbs(g, alpha=scale_g)
        balanced_b = cv2.convertScaleAbs(b, alpha=scale_b)

        img = cv2.merge((balanced_b, balanced_g, balanced_r))

        return img, factor

    def random_exposure(self, img):
        # Either under over overexposes image
        exposure_factor = 1.0

        while 0.95 <= exposure_factor <= 1.05:
            exposure_factor = np.random.uniform(0.7, 1.2)

        img = img * exposure_factor

        # Clip pixel values to ensure they are within the valid range [0, 255] # TODO check if this might cause issues
        img = np.clip(img, 0, 255).astype(np.uint8)

        return img, exposure_factor

    def random_rotation(self, img):
        angle = random.uniform(-3, 3)
        rotation_matrix = cv2.getRotationMatrix2D((img.shape[1] / 2, img.shape[0] / 2), angle, 1)
        return cv2.warpAffine(img, rotation_matrix, img.shape[1::-1], flags=cv2.INTER_LINEAR), angle

    def random_lens_distortion(self, img, file_name):
        # Generate random lens distortion parameters

        # TODO

        return img


    def random_mirror(self, img):
        if np.random.rand() < 0.5:
            return cv2.flip(img, 1), True
        return img, False

    def random_gaussian_blur(self, img):
        blur_radius = random.uniform(0, 2.0)
        return cv2.GaussianBlur(img, (0, 0), blur_radius), blur_radius

    def random_texture_overlay(self, img):
        # TODO
        return img

if __name__ == "__main__":
    input_dir = "/Users/helvetica/Desktop/train/good" # <- keep this plz
    output_dir = "/Users/helvetica/Desktop/train/aug"

    # put ut input dir here

    augmenter = DataAugmenter(input_dir, output_dir)

    augmenter.augment_images()