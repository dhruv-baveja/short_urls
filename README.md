# Short URLs

This application allows you to minify or shorten your URLs. You can create short URLs 
for multiple long URLs at once. It also allows you to get long URLs corresponding to your short URLs in bulk.

Available API's:
- /urls/long/
  - POST method
  - JSON format
  ```
  {"long_urls": ["http://www.example.com/", "https://www.example.com/"]}
  ```
- /urls/short/
  - POST method
  - JSON format
  ```
  {"short_urls": ["er23hf65", "Er47hF90"]}
  ```
- /<short_url>/
  - GET method
  - redirects to the long url

## Architecture
To come up with the architecture below, I researched and tested for which database and cache to use. 
For more details regarding the thinking involved here, please look [here](https://github.com/dhruv-baveja/short_urls/blob/master/ARCHITECTURE.md).

### Components

- #### Database
	- MongoDB
- #### Cache
	- Redis
- #### Language/Framework
	- Python/Django
- #### Additional Tools
	- Celery, RabbitMQ 
