from django.apps import AppConfig
import os

# Module-level globals for the food recognition model.
# Populated once by MainappConfig.ready().
food_model = None
food_class_names = None


class MainappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mainapp'

    def ready(self):
        """Load the food recognition model once at startup."""
        global food_model, food_class_names

        # Guard: skip if already loaded or inside management commands like migrate
        if food_model is not None:
            return

        model_path = os.path.join(
            os.path.dirname(__file__), 'ml_models', 'food_model.pt'
        )
        if not os.path.exists(model_path):
            print(f"[MainappConfig] Food model not found at {model_path}, skipping.")
            return

        try:
            import torch
            from torchvision import models as tv_models

            checkpoint = torch.load(model_path, map_location='cpu', weights_only=False)
            class_names = checkpoint['class_names']
            num_classes = len(class_names)

            # Build EfficientNet-B0 and replace the final classifier head
            model = tv_models.efficientnet_b0(weights=None)
            in_features = model.classifier[1].in_features  # 1280
            model.classifier[1] = torch.nn.Linear(in_features, num_classes)

            # Load trained weights
            model.load_state_dict(checkpoint['model_state'])
            model.eval()

            food_model = model
            food_class_names = class_names
            print(f"[MainappConfig] Food model loaded: {num_classes} classes.")
        except Exception as e:
            print(f"[MainappConfig] Failed to load food model: {e}")
