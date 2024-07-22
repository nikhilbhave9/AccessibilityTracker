import tensorflow as tf
from object_detection.utils import config_util
from object_detection.builders import model_builder

print("TensorFlow Version:", tf.__version__)

# Adjust the path to your actual pipeline configuration file
pipeline_config = 'models/research/object_detection/configs/tf2/ssd_mobilenet_v2_fpnlite_320x320_coco17_tpu-8.config'
configs = config_util.get_configs_from_pipeline_file(pipeline_config)
model_config = configs['model']
detection_model = model_builder.build(model_config=model_config, is_training=False)

print("Object Detection API is set up correctly.")