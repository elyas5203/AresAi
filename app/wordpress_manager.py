import os
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost
from wordpress_xmlrpc.methods.media import UploadFile
from dotenv import load_dotenv

load_dotenv()

class WordPressManager:
    def __init__(self):
        self.wp_url = os.getenv("WP_URL")
        self.wp_username = os.getenv("WP_USERNAME")
        self.wp_password = os.getenv("WP_PASSWORD")

        if not all([self.wp_url, self.wp_username, self.wp_password]):
            raise ValueError("WordPress credentials (WP_URL, WP_USERNAME, WP_PASSWORD) are not set in the .env file.")

        self.client = Client(self.wp_url, self.wp_username, self.wp_password)

    def upload_image(self, image_path):
        """
        Uploads an image to the WordPress media library.
        Returns the attachment ID and URL.
        """
        try:
            with open(image_path, 'rb') as img:
                data = {
                    'name': os.path.basename(image_path),
                    'type': 'image/jpeg', # Adjust mime type if necessary
                    'bits': img.read(),
                    'overwrite': True
                }
            response = self.client.call(UploadFile(data))
            # response is a dict with 'id', 'file', 'url', 'type'
            return response
        except Exception as e:
            print(f"Error uploading image to WordPress: {e}")
            return None

    def create_product(self, name, description, price, image_path=None):
        """
        Creates a new WooCommerce product.
        Note: This requires the WooCommerce REST API plugin to be installed and configured
              on your WordPress site for a more robust solution.
              Using XML-RPC for products can be limited. This is a basic example
              creating a standard 'post' and setting some custom fields.
              For real WooCommerce integration, a REST API client is recommended.
        """
        post = WordPressPost()
        post.title = name
        post.content = description
        post.post_status = 'publish'
        post.terms_names = {
            'product_cat': ['لوازم تحریر'], # Example category
            'product_type': ['simple'] # for simple products
        }

        # Handle product image
        if image_path:
            image_data = self.upload_image(image_path)
            if image_data:
                post.thumbnail = image_data['id']

        # Set custom fields for WooCommerce (meta data)
        post.custom_fields = []
        post.custom_fields.append({'key': '_regular_price', 'value': str(price)})
        post.custom_fields.append({'key': '_price', 'value': str(price)})
        post.custom_fields.append({'key': '_sku', 'value': f'SKU_{name.replace(" ", "_")}'}) # Simple SKU generation
        post.custom_fields.append({'key': '_stock_status', 'value': 'instock'})

        try:
            # We need to set the post_type to 'product'
            post.id = self.client.call(NewPost(post, post_type='product'))
            print(f"Successfully created product: {name}")
            return post.id
        except Exception as e:
            print(f"Error creating product in WordPress: {e}")
            # This can fail if XML-RPC doesn't have permissions or post type is wrong
            # Check WordPress XML-RPC settings.
            return None


if __name__ == '__main__':
    # Example usage:
    # Ensure you have a .env file with WP_URL, WP_USERNAME, WP_PASSWORD
    # And make sure XML-RPC is enabled on your WordPress site (it usually is by default).
    # You might need to install a plugin to allow 'product' post type via XML-RPC.

    manager = WordPressManager()

    # Create a product without an image
    # manager.create_product("دفترچه یادداشت کلاسیک", "یک دفترچه بسیار زیبا با جلد چرمی.", "150000")

    # Create a product with an image
    # Make sure 'example_image.jpg' exists in your project directory
    # manager.create_product("خودکار رنگی فانتزی", "یک بسته خودکار 12 رنگ با کیفیت عالی.", "250000", image_path="example_image.jpg")
    print("WordPress Manager is ready. Example usage is commented out in the script.")
    # To run this, you need a dummy image file, e.g., 'example_image.jpg'
    # with open("example_image.jpg", "w") as f: f.write("dummy")
    # manager.create_product("خودکار رنگی فانتزی", "یک بسته خودکار ۱۲ رنگ.", "120000", "example_image.jpg")
