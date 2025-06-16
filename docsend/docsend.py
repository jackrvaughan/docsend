from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from pathlib import Path
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from PIL import Image
from requests_html import HTMLSession

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocSend:

    def __init__(self, doc_id):
        self.doc_id = doc_id.rpartition('/')[-1]
        self.url = f'https://docsend.com/view/{doc_id}'
        self.s = HTMLSession()
        self._pool = None
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504]
        )
        
        # Configure connection pooling with increased pool size
        adapter = HTTPAdapter(
            pool_connections=50,  # Increased from 10
            pool_maxsize=50,     # Increased from 10
            max_retries=retry_strategy
        )
        self.s.mount("http://", adapter)
        self.s.mount("https://", adapter)

    def fetch_meta(self):
        try:
            r = self.s.get(self.url)
            r.raise_for_status()
            self.auth_token = None
            if r.html.find('input[@name="authenticity_token"]'):
                self.auth_token = r.html.find('input[@name="authenticity_token"]')[0].attrs['value']
            self.pages = int(r.html.find('.document-thumb-container')[-1].attrs['data-page-num'])
        except Exception as e:
            logger.error(f"Failed to fetch metadata: {str(e)}")
            raise

    def authorize(self, email, passcode=None):
        try:
            form = {
                'utf8': '✓',
                '_method': 'patch',
                'authenticity_token': self.auth_token,
                'link_auth_form[email]': email,
                'link_auth_form[passcode]': passcode,
                'commit': 'Continue',
            }
            f = self.s.post(self.url, data=form)
            f.raise_for_status()
        except Exception as e:
            logger.error(f"Failed to authorize: {str(e)}")
            raise

    def fetch_images(self, batch_size=5):
        """Fetch images in batches to manage memory usage.
        
        Args:
            batch_size (int): Number of images to process in each batch
        """
        self.image_urls = []
        self.total_pages = self.pages
        self.batch_size = batch_size
        
    def _process_batch(self, start_page):
        """Process a batch of pages and return the images.
        
        Args:
            start_page (int): Starting page number for this batch
            
        Returns:
            list: List of processed images in this batch
        """
        end_page = min(start_page + self.batch_size, self.pages + 1)
        with ThreadPoolExecutor(min(self.batch_size, end_page - start_page)) as pool:
            return list(pool.map(self._fetch_image, range(start_page, end_page)))

    def _fetch_image(self, page):
        try:
            meta = self.s.get(f'{self.url}/page_data/{page}')
            meta.raise_for_status()
            data = self.s.get(meta.json()['imageUrl'])
            data.raise_for_status()
            rgba = Image.open(BytesIO(data.content))
            rgb = Image.new('RGB', rgba.size, (255, 255, 255))
            rgb.paste(rgba)
            return rgb
        except Exception as e:
            logger.error(f"Failed to fetch page {page}: {str(e)}")
            raise

    def save_pdf(self, name=None):
        try:
            # Process and save all images in batches
            all_images = []
            for start_page in range(1, self.pages + 1, self.batch_size):
                batch_images = self._process_batch(start_page)
                all_images.extend(batch_images)
                # Clear batch images from memory
                del batch_images
            
            # Save all images to PDF
            if all_images:
                all_images[0].save(
                    name,
                    format='PDF',
                    append_images=all_images[1:],
                    save_all=True
                )
                # Clear all images from memory
                del all_images
        except Exception as e:
            logger.error(f"Failed to save PDF: {str(e)}")
            raise

    def save_images(self, name):
        try:
            path = Path(name)
            path.mkdir(exist_ok=True)
            
            # Process and save images in batches
            for start_page in range(1, self.pages + 1, self.batch_size):
                batch_images = self._process_batch(start_page)
                for i, image in enumerate(batch_images, start=start_page):
                    image.save(path / f'{i}.png', format='PNG')
                # Clear batch images from memory
                del batch_images
        except Exception as e:
            logger.error(f"Failed to save images: {str(e)}")
            raise

    def __del__(self):
        if hasattr(self, 's'):
            self.s.close()
