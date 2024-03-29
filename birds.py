"""
Mask R-CNN
Train on the toy Balloon dataset and implement color splash effect.

Copyright (c) 2018 Matterport, Inc.
Licensed under the MIT License (see LICENSE for details)
Written by Waleed Abdulla

------------------------------------------------------------

Usage: import the module (see Jupyter notebooks for examples), or run from
       the command line as such:

    # Train a new model starting from pre-trained COCO weights
    python3 birds.py train --dataset=../../dataset/birds --weights=coco

    # Resume training a model that you had trained earlier
    python3 birds.py train --dataset=../../dataset/birds --weights=last

    # Train a new model starting from ImageNet weights
    python3 birds.py train --dataset=../../dataset/birds --weights=imagenet

    # Apply color splash to an image
    python3 balloon.py splash --weights=/path/to/weights/file.h5 --image=<URL or path to file>

    # Apply color splash to video using the last weights you trained
    python3 balloon.py splash --weights=last --video=<URL or path to file>
"""

import os
import sys
import json
import datetime
import numpy as np
import skimage.draw
import imgaug
from imgaug import augmenters as iaa
# Root directory of the project
ROOT_DIR = os.path.abspath("../..")

# Import Mask RCNN
sys.path.append(ROOT_DIR)  # To find local version of the library
from mrcnn.config import Config
from mrcnn import model as modellib, utils

# Path to trained weights file
Birds_MODEL_PATH = os.path.join("mask_rcnn_birds_0197.h5")

# Directory to save logs and model checkpoints, if not provided
# through the command line argument --logs
DEFAULT_LOGS_DIR = os.path.join(ROOT_DIR, "logs")

############################################################
#  Configurations
############################################################


class BirdsConfig(Config):
    """Configuration for training on the toy  dataset.
    Derives from the base Config class and overrides some values.
    """
    # Give the configuration a recognizable name
    NAME = "birds"

    # We use a GPU with 12GB memory, which can fit two images.
    # Adjust down if you use a smaller GPU.
    IMAGES_PER_GPU = 2
    #GPU_COUNT = 1

    # Number of classes (including background)
    NUM_CLASSES = 1 + 100  # Background + balloon


    # Skip detections with < 90% confidence
    DETECTION_MIN_CONFIDENCE = 0.5


############################################################
#  Dataset
############################################################
class BirdsDataset(utils.Dataset):
    def load_birds(self, dataset_dir, subset):

        """Load a subset of the Balloon dataset.
        dataset_dir: Root directory of the dataset.
        subset: Subset to load: train or val
        """
        # Add classes. We have only one class to add.
        self.add_class("birds", 1, "Acadian_Flycatcher")
        self.add_class("birds", 2, "American_Crow")
        self.add_class("birds", 3, "American_Goldfinch")
        self.add_class("birds", 4, "Anna_Hummingbird")
        self.add_class("birds", 5, "Baltimore_Oriole")
        self.add_class("birds", 6, "Belted_Kingfisher")
        self.add_class("birds", 7, "Black_Billed_Cuckoo")
        self.add_class("birds", 8, "Black_Footed_Albatross")
        self.add_class("birds", 9, "Blue_Grosbeak")
        self.add_class("birds", 10, "Blue_Jay")
        self.add_class("birds", 11, "Boat_Tailed_Grackle")
        self.add_class("birds", 12, "Bobolink") 
        self.add_class("birds", 13, "Brandt_Cormorant")
        self.add_class("birds", 14, "Brewer_Blackbird")
        self.add_class("birds", 15, "Bronzed_Cowbird")
        self.add_class("birds", 16, "Brown_Creeper")
        self.add_class("birds", 17, "Brown_Pelican")
        self.add_class("birds", 18, "California_Gull")
        self.add_class("birds", 19, "Cardinal")
        self.add_class("birds", 20, "Chuck_Will_Widow")
        self.add_class("birds", 21, "Clark_Nutcracker")
        self.add_class("birds", 22, "Crested_Auklet")
        self.add_class("birds", 23, "Dark_Eyed_Junco")
        self.add_class("birds", 24, "Eared_Grebe")
        self.add_class("birds", 25, "Eastern_Towhee")
        self.add_class("birds", 26, "European_Goldfinch")
        self.add_class("birds", 27, "Evening_Grosbeak")
        self.add_class("birds", 28, "Fish_Crow")
        self.add_class("birds", 29, "Florida_Jay")
        self.add_class("birds", 30, "Frigatebird")
        self.add_class("birds", 31, "Gadwall")
        self.add_class("birds", 32, "Glaucous_Winged_Gul")
        self.add_class("birds", 33, "Gray_Catbird")
        self.add_class("birds", 34, "Gray_Crowned_Rosy_Finch")
        self.add_class("birds", 35, "Gray_Kingbird")
        self.add_class("birds", 36, "Great_Crested_Flycatcher")
        self.add_class("birds", 37, "Green_Jay")
        self.add_class("birds", 38, "Green_Kingfisher")
        self.add_class("birds", 39, "Green_Violetear")
        self.add_class("birds", 40, "Groove_Billed_Ani")
        self.add_class("birds", 41, "Heermann_Gull")
        self.add_class("birds", 42, "Herring_Gull")
        self.add_class("birds", 43, "Hooded_Merganser")
        self.add_class("birds", 44, "Hooded_Oriole") 
        self.add_class("birds", 45, "Horned_Grebe")
        self.add_class("birds", 46, "Horned_Lark")
        self.add_class("birds", 47, "Indigo_Bunting")
        self.add_class("birds", 48, "Ivory_Gull")
        self.add_class("birds", 49, "Laysan_Albatross")
        self.add_class("birds", 50, "Lazuli_Bunting")
        self.add_class("birds", 51, "Least_Auklet")
        self.add_class("birds", 52, "Least_Flycatcher")
        self.add_class("birds", 53, "Long_Tailed_Jaeger")
        self.add_class("birds", 54, "Mallard")
        self.add_class("birds", 55, "Mangrove_Cuckoo")
        self.add_class("birds", 56, "Mockingbird")
        self.add_class("birds", 57, "Nighthawk")
        self.add_class("birds", 58, "Northern_Flicker")
        self.add_class("birds", 59, "Northern_Fulmar")
        self.add_class("birds", 60, "Olive_Sided_Flycatcher")
        self.add_class("birds", 61, "Orchard_Oriole")
        self.add_class("birds", 62, "Ovenbird")
        self.add_class("birds", 63, "Pacific_Loon")
        self.add_class("birds", 64, "Painted_Bunting")
        self.add_class("birds", 65, "Parakeet_Auklet")
        self.add_class("birds", 66, "Pelagic_Cormorant")
        self.add_class("birds", 67, "Pied_Billed_Grebe") 
        self.add_class("birds", 68, "Pied_Kingfisher") 
        self.add_class("birds", 69, "Pigeon_Guillemot") 
        self.add_class("birds", 70, "Pine_Grosbeak") 
        self.add_class("birds", 71, "Pomarine_Jaeger") 
        self.add_class("birds", 72, "Purple_Finch") 
        self.add_class("birds", 73, "Red_Breasted_Merganser")        
        self.add_class("birds", 74, "Red_Faced_Cormorant") 
        self.add_class("birds", 75, "Red_Legged_Kittiwake") 
        self.add_class("birds", 76, "Red_Winged_Blackbird") 
        self.add_class("birds", 77, "Rhinoceros_Auklet") 
        self.add_class("birds", 78, "Ring_Billed_Gull") 
        self.add_class("birds", 79, "Ringed_Kingfisher") 
        self.add_class("birds", 80, "Rose_Breasted_Grosbeak") 
        self.add_class("birds", 81, "Ruby_Throated_Hummingbird") 
        self.add_class("birds", 82, "Rufous_Humming") 
        self.add_class("birds", 83, "Rusty_Blackbird") 
        self.add_class("birds", 84, "Scissor_Tailed_Flycatcher") 
        self.add_class("birds", 85, "Scott_Oriole") 
        self.add_class("birds", 86, "Shiny_Cowbird") 
        self.add_class("birds", 87, "Slaty_Backed_Gull") 
        self.add_class("birds", 88, "Sooty_Albatross") 
        self.add_class("birds", 89, "Spotted_Catbird") 
        self.add_class("birds", 90, "Tropical_Kingbird") 
        self.add_class("birds", 91, "Vermilion_Flycatcher") 
        self.add_class("birds", 92, "Western_Grebe") 
        self.add_class("birds", 93, "Western_Gull") 
        self.add_class("birds", 94, "Western_Meadowlark") 
        self.add_class("birds", 95, "White_Breasted_Kingfisher") 
        self.add_class("birds", 96, "White_Breasted_Nuthatch") 
        self.add_class("birds", 97, "Yellow_Bellied_Flycatcher") 
        self.add_class("birds", 98, "Yellow_Billed_Cuckoo") 
        self.add_class("birds", 99, "Yellow_Breasted_Chat") 
        self.add_class("birds", 100, "Yellow_Headed_Blackbird") 
        

        # Train or validation dataset?
        assert subset in ["train", "val"]
        dataset_dir = os.path.join(dataset_dir, subset)

        # Load annotations
        # VGG Image Annotator saves each image in the form:
        # { 'filename': '28503151_5b5b7ec140_b.jpg',
        #   'regions': {
        #       '0': {
        #           'region_attributes': {},
        #           'shape_attributes': {
        #               'all_points_x': [...],
        #               'all_points_y': [...],
        #               'name': 'polygon'}},
        #       ... more regions ...
        #   },
        #   'size': 100202
        # }
        # We mostly care about the x and y coordinates of each region
        annotations = json.load(open(os.path.join(dataset_dir, "via_region_data.json")))
        annotations = list(annotations.values())  # don't need the dict keys

        # The VIA tool saves images in the JSON even if they don't have any
        # annotations. Skip unannotated images.
        annotations = [a for a in annotations if a['regions']]

         # Add images
        for a in annotations:
            # Get the x, y coordinaets of points of the polygons that make up
            # the outline of each object instance. There are stores in the
            # shape_attributes (see json format above)
            if type(a['regions']) is dict:
                polygons = [r['shape_attributes'] for r in a['regions'].values()]
                objects = [s['region_attributes'] for s in a['regions'].values()]
            else:
                polygons = [r['shape_attributes'] for r in a['regions']] 
                objects = [s['region_attributes'] for s in a['regions']]

            # load_mask() needs the image size to convert polygons to masks.
            # Unfortunately, VIA doesn't include it in JSON, so we must read
            num_ids = [int(n['birds']) for n in objects]
            # the image. This is only managable since the dataset is tiny.
            image_path = os.path.join(dataset_dir, a['filename'])
            image = skimage.io.imread(image_path)
            height, width = image.shape[:2]

            self.add_image(
                "birds",
                image_id=a['filename'],  # use file name as a unique image id
                path=image_path,
                width=width, height=height,
                polygons=polygons,num_ids=num_ids)

    def load_mask(self, image_id):
        """Generate instance masks for an image.
       Returns:
        masks: A bool array of shape [height, width, instance count] with
            one mask per instance.
        class_ids: a 1D array of class IDs of the instance masks.
        """
        # If not a balloon dataset image, delegate to parent class.
        #image_info = self.image_info[image_id]
        info = self.image_info[image_id]
        if info["source"] != "birds":
            return super(self.__class__, self).load_mask(image_id)
        num_ids = info['num_ids']
        # Convert polygons to a bitmap mask of shape
        # [height, width, instance_count]
        #info = self.image_info[image_id]
        mask = np.zeros([info["height"], info["width"], len(info["polygons"])],
                        dtype=np.uint8)

        for i, p in enumerate(info["polygons"]):
            # Get indexes of pixels inside the polygon and set them to 1
            rr, cc = skimage.draw.polygon(p['all_points_y'], p['all_points_x'])
            mask[rr, cc, i] = 1

        # Return mask, and array of class IDs of each instance. Since we have
        # one class ID only, we return an array of 1s
        num_ids = np.array(num_ids, dtype=np.int32)
        return mask, num_ids

    def image_reference(self, image_id):
        """Return the path of the image."""
        info = self.image_info[image_id]
        if info["source"] == "birds":
            return info["path"]
        else:
            super(self.__class__, self).image_reference(image_id)


def train(model):
    """Train the model."""
    # Training dataset.
    dataset_train = BirdsDataset()
    dataset_train.load_birds(args.dataset, "train")
    dataset_train.prepare()

    # Validation dataset
    dataset_val = BirdsDataset()
    dataset_val.load_birds(args.dataset, "val")
    dataset_val.prepare()

    # *** This training schedule is an example. Update to your needs ***
    # Since we're using a very small dataset, and starting from
    # COCO trained weights, we don't need to train too long. Also,
    # no need to train all layers, just the heads should do it.
    print("Training network heads")
    model.train(dataset_train, dataset_val,
                learning_rate=config.LEARNING_RATE,
                epochs=30,
                layers='heads')


def color_splash(image, mask):
    """Apply color splash effect.
    image: RGB image [height, width, 3]
    mask: instance segmentation mask [height, width, instance count]

    Returns result image.
    """
    # Make a grayscale copy of the image. The grayscale copy still
    # has 3 RGB channels, though.
    gray = skimage.color.gray2rgb(skimage.color.rgb2gray(image)) * 255
    # Copy color pixels from the original color image where mask is set
    if mask.shape[-1] > 0:
        # We're treating all instances as one, so collapse the mask into one layer
        mask = (np.sum(mask, -1, keepdims=True) >= 1)
        splash = np.where(mask, image, gray).astype(np.uint8)
    else:
        splash = gray.astype(np.uint8)
    return splash


def detect_and_color_splash(model, image_path=None, video_path=None):
    assert image_path or video_path

    # Image or video?
    if image_path:
        # Run model detection and generate the color splash effect
        print("Running on {}".format(args.image))
        # Read image
        image = skimage.io.imread(args.image)
        # Detect objects
        r = model.detect([image], verbose=1)[0]
        # Color splash
        splash = color_splash(image, r['masks'])
        # Save output
        file_name = "splash_{:%Y%m%dT%H%M%S}.png".format(datetime.datetime.now())
        skimage.io.imsave(file_name, splash)
    elif video_path:
        import cv2
        # Video capture
        vcapture = cv2.VideoCapture(video_path)
        width = int(vcapture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(vcapture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = vcapture.get(cv2.CAP_PROP_FPS)

        # Define codec and create video writer
        file_name = "splash_{:%Y%m%dT%H%M%S}.avi".format(datetime.datetime.now())
        vwriter = cv2.VideoWriter(file_name,
                                  cv2.VideoWriter_fourcc(*'MJPG'),
                                  fps, (width, height))

        count = 0
        success = True
        while success:
            print("frame: ", count)
            # Read next image
            success, image = vcapture.read()
            if success:
                # OpenCV returns images as BGR, convert to RGB
                image = image[..., ::-1]
                # Detect objects
                r = model.detect([image], verbose=0)[0]
                # Color splash
                splash = color_splash(image, r['masks'])
                # RGB -> BGR to save image to video
                splash = splash[..., ::-1]
                # Add image to video writer
                vwriter.write(splash)
                count += 1
        vwriter.release()
    print("Saved to ", file_name)


############################################################
#  Training
############################################################

if __name__ == '__main__':
    import argparse

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Train Mask R-CNN to detect birds.')
    parser.add_argument("command",
                        metavar="<command>",
                        help="'train' or 'splash'")
    parser.add_argument('--dataset', required=False,
                        metavar="/path/to/birds/dataset/",
                        help='Directory of the birds dataset')
    parser.add_argument('--weights', required=True,
                        metavar="/path/to/mask_rcnn_coco.h5",
                        help="Path to weights .h5 file or 'coco'")
    parser.add_argument('--logs', required=False,
                        default=DEFAULT_LOGS_DIR,
                        metavar="/path/to/logs/",
                        help='Logs and checkpoints directory (default=logs/)')
    parser.add_argument('--image', required=False,
                        metavar="path or URL to image",
                        help='Image to apply the color splash effect on')
    parser.add_argument('--video', required=False,
                        metavar="path or URL to video",
                        help='Video to apply the color splash effect on')
    args = parser.parse_args()

    # Validate arguments
    if args.command == "train":
        assert args.dataset, "Argument --dataset is required for training"
    elif args.command == "splash":
        assert args.image or args.video,\
               "Provide --image or --video to apply color splash"

    print("Weights: ", args.weights)
    print("Dataset: ", args.dataset)
    print("Logs: ", args.logs)

    # Configurations
    if args.command == "train":
        config = BirdsConfig()
    else:
        class InferenceConfig(BirdsConfig):
            # Set batch size to 1 since we'll be running inference on
            # one image at a time. Batch size = GPU_COUNT * IMAGES_PER_GPU
            GPU_COUNT = 1
            IMAGES_PER_GPU = 1
            DETECTION_MIN_CONFIDENCE = 0
        config = InferenceConfig()
    config.display()

    # Create model
    if args.command == "train":
        model = modellib.MaskRCNN(mode="training", config=config,
                                  model_dir=args.logs)
    else:
        model = modellib.MaskRCNN(mode="inference", config=config,
                                  model_dir=args.logs)

    # Select weights file to load
    if args.weights.lower() == "coco":
        weights_path = COCO_WEIGHTS_PATH
        # Download weights file
        if not os.path.exists(weights_path):
            utils.download_trained_weights(weights_path)
    elif args.weights.lower() == "last":
        # Find last trained weights
        weights_path = model.find_last()
    elif args.weights.lower() == "imagenet":
        # Start from ImageNet trained weights
        weights_path = model.get_imagenet_weights()
    else:
        weights_path = args.weights

    # Load weights
    print("Loading weights ", weights_path)
    if args.weights.lower() == "coco":
        # Exclude the last layers because they require a matching
        # number of classes
        model.load_weights(weights_path, by_name=True, exclude=[
            "mrcnn_class_logits", "mrcnn_bbox_fc",
            "mrcnn_bbox", "mrcnn_mask"])
    else:
        model.load_weights(weights_path, by_name=True)

    # Train or evaluate
    if args.command == "train":
        # Training dataset. Use the training set and 35K from the
        # validation set, as as in the Mask RCNN paper.
        dataset_train = BirdsDataset()
        dataset_train.load_birds(args.dataset, "train")
        dataset_train.prepare()

        # Validation dataset
        dataset_val = BirdsDataset()
        val_type = "val" 
        dataset_val.load_birds(args.dataset, val_type)
        dataset_val.prepare()

        # Image Augmentation
        # Right/Left flip 50% of the time

        augmentation = iaa.SomeOf(2, [
            iaa.Fliplr(0.5),
            iaa.Flipud(0.5),
            iaa.Dropout(p=(0, 0.2))
        ])
        # *** This training schedule is an example. Update to your needs ***

        # Training - Stage 1
        print("Training network heads")
        model.train(dataset_train, dataset_val,
                    learning_rate=config.LEARNING_RATE,
                    epochs=40,
                    layers='heads',
                    augmentation=augmentation)

        # Training - Stage 2
        # Finetune layers from ResNet stage 4 and up
        print("Fine tune Resnet stage 4 and up")
        model.train(dataset_train, dataset_val,
                    learning_rate=config.LEARNING_RATE,
                    epochs=70,
                    layers='4+',
                    augmentation=augmentation)
        # Training - Stage 3
        # Fine tune all layers
        print("Fine tune all layers")
        model.train(dataset_train, dataset_val,
                    learning_rate=config.LEARNING_RATE / 10,
                    epochs=250,
                    layers='all',
                    augmentation=augmentation)
        
    elif args.command == "evaluate":
        # Validation dataset
        dataset_val = BirdsDataset()
        val_type = "val" 
        birds = dataset_val.load_birds(args.dataset, val_type,  return_birds=True)
        dataset_val.prepare()
        print("Running birds evaluation on {} images.".format(args.limit))
        evaluate_birds(model, dataset_val, birds, "bbox", limit=int(args.limit))
    else:
        print("'{}' is not recognized. "
              "Use 'train' or 'evaluate'".format(args.command))