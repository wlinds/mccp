import logging
import os
import random
import cv2
import numpy as np

class DataAugmenter:
    def __init__(
        self,
        input_dir,
        output_dir,
        num_augmented_images=3,
        output_image_size=(640, 480),
        create_dir=True,
        temperature=1.0,
        logging_enabled=True,
    ):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.num_augmented_images = num_augmented_images
        self.output_image_size = output_image_size
        self.create_dir = create_dir
        self.temperature = temperature
        self.resolution = None
        self.logging_enabled = logging_enabled

        if create_dir and not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        if logging_enabled:
            logging.basicConfig(
                filename="./data_augmentation.log",
                level=logging.DEBUG,
                format="%(asctime)s - %(levelname)s - %(message)s",
            )

    def process_image(self, img, filename):
        if img is None:
            logging.error(f"Image is None for {filename}")
            return

        for i in range(self.num_augmented_images):
            logging.info(f"Augmenting {filename}. Iteration: {i}")

            img, val = self.random_white_balance(img)
            logging.info(f"Iter. {i}: {filename} - RGB vals: {val}")

            img, val = self.random_exposure(img)
            logging.info(f"Iter. {i}: {filename} - Exposure: {val}")

            img, val = self.random_rotation(img)
            logging.info(f"Iter. {i}: {filename} - Rotation: {val}")

            img, val = self.random_mirror(img)
            logging.info(f"Iter. {i}: {filename} - Mirrored: {val}")

            img, val = self.random_lens_distortion(img, filename)
            logging.info(f"Iter. {i}: {filename} - Perspect: {val}")

            img, val = self.random_gaussian_blur(img)
            logging.info(f"Iter. {i}: {filename} - Blur rad: {val}")

            # img, val = self.random_texture_overlay(img)

            # img, val = self.random_crop(img)
            # logging.info(f"Iter. {i}: {filename} - Crop factor: {val}")

            if img is None:
                logging.error(f"Image is None after augmentation for {filename}")
                return

            output_file = os.path.splitext(filename)[0] + f"_aug_{i}.png"
            output_path = os.path.join(self.output_dir, output_file)
            cv2.imwrite(output_path, img)

            if self.logging_enabled:
                logging.info(f"Finished augmentation of {filename} as {output_file}")
                print(f"Finished augmentation of {filename} as {output_file}")


    def augment_images(self, selected_images=None):
        image_files = selected_images if selected_images else os.listdir(self.input_dir)

        for img_file in image_files:
            logging.info(f"Processing {img_file}")
            img_path = os.path.join(self.input_dir, img_file)
            img = cv2.imread(img_path)

            if self.resolution is None:
                self.resolution = img.shape[:2]

            self.process_image(img, img_file)

        print("Data augmentation complete.")

    def random_crop(self, img):
        # TODO
        return img

    def random_white_balance(self, img):
        # TODO: Set actual kelvin values (?)
        b, g, r = cv2.split(img)

        factor = self.temperature * 0.02

        scale_r = random.uniform(0.98 + factor, 1.02)
        scale_g = random.uniform(0.98 - factor, 1.02)
        scale_b = random.uniform(0.98 - factor, 1.02)

        balanced_r = cv2.convertScaleAbs(r, alpha=scale_r)
        balanced_g = cv2.convertScaleAbs(g, alpha=scale_g)
        balanced_b = cv2.convertScaleAbs(b, alpha=scale_b)

        img = cv2.merge((balanced_b, balanced_g, balanced_r))

        factor_str = f"R: {scale_r:.3f}, G: {scale_g:.3f}, B: {scale_b:.3f}"

        return img, factor_str



    def random_exposure(self, img):
        # Higher temperature values overexposes, lower temperature values underexposes
        exposure_factor = 1.0

        while 1 - (abs(self.temperature * 0.01)) <= exposure_factor <= 1 + (abs(self.temperature * 0.04)):
            exposure_factor = np.random.uniform(1.0 - (abs(self.temperature * 0.1)), 1.0) + (self.temperature * 0.1)

        img = img * exposure_factor

        return img, exposure_factor

    def random_rotation(self, img):
        angle = random.uniform(-abs(self.temperature) + 1, abs(self.temperature) - 1)
        angle = angle + (abs(self.temperature) % 3)
        rotation_matrix = cv2.getRotationMatrix2D(
            (img.shape[1] / 2, img.shape[0] / 2), angle, 1
        )
        return (
            cv2.warpAffine(
                img, rotation_matrix, img.shape[1::-1], flags=cv2.INTER_LINEAR
            ),
            angle,
        )

    def random_lens_distortion(self, img, file_name):
        min_distortion_factor = 0.99 - (abs(self.temperature)) * 0.02
        max_distortion_factor = 1.01 + (abs(self.temperature)) * 0.02

        distortion_factor_x = np.random.uniform(min_distortion_factor, max_distortion_factor)
        distortion_factor_y = np.random.uniform(min_distortion_factor, max_distortion_factor)

        height, width = img.shape[:2]

        # perspective transformation matrix
        distortion_matrix = np.array([
            [distortion_factor_x, 0, 0],
            [0, distortion_factor_y, 0],
        ], dtype=np.float32)

        distorted_img = cv2.warpAffine(img, distortion_matrix, (width, height))

        return distorted_img, distortion_matrix

    def random_mirror(self, img):
        if np.random.rand() < 0.5:
            return cv2.flip(img, 1), True
        return img, False

    def random_gaussian_blur(self, img):
        blur_radius = random.uniform(0, 1.0)
        return cv2.GaussianBlur(img, (0, 0), blur_radius), f"{blur_radius:.5f}"

    def random_texture_overlay(self, img):
        # TODO
        return img


if __name__ == "__main__":
    input_dir = "/Users/helvetica/_anodet/data/purple_duck/train/good/test_0"
    output_dir = "/Users/helvetica/_anodet/data/purple_duck/train/good/aug"

    augmenter = DataAugmenter(input_dir, output_dir, temperature=1.1)

    augmenter.augment_images()
