from utils.logger import setup_logger

class AsyncImageHandler:
    def __init__(self, photo_service, image_url):
        self.photo_service = photo_service
        self.image_url = image_url
        self.logger = setup_logger()

    async def process(self):
        if self.image_url:
            self.logger.info(f"Обработка изображения по URL: {self.image_url}")
            image_response = await self.photo_service.process_image_from_url(self.image_url)
            self.logger.info(f"Ответ по изображению: {image_response}")
            return image_response
        else:
            self.logger.info("URL изображения не указан. Пропуск обработки изображения.")
            return None
